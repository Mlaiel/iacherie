"""IA Influencer Agent - Elasticsearch Logging Manager
Advanced Elasticsearch integration for centralized logging

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
from elasticsearch import AsyncElasticsearch, exceptions as es_exceptions
from elasticsearch.helpers import async_bulk, async_scan

from ...core.config import settings
from ...core.exceptions import LoggingError, ElasticsearchError
from .log_aggregator import LogEntry, LogLevel


class IndexStrategy(str, Enum):
    """
Elasticsearch index strategies"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    SINGLE = "single"


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration"""
    hosts: List[str]
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = True
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True


class IndexTemplate:
    """
Elasticsearch index template management"""
    
    def __init__(self, template_name: str = "ia-influencer-logs"):
        self.template_name = template_name
    
    def get_template(self) -> Dict[str, Any]:
        """Get index template configuration"""
        return {
            "index_patterns": [f"{self.template_name}-*"],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "index.refresh_interval": "5s",
                "index.max_result_window": 50000,
                "analysis": {
                    "analyzer": {
                        "log_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "timestamp": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "level": {
                        "type": "keyword"
                    },
                    "message": {
                        "type": "text",
                        "analyzer": "log_analyzer",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "service": {
                        "type": "keyword"
                    },
                    "module": {
                        "type": "keyword"
                    },
                    "user_id": {
                        "type": "keyword"
                    },
                    "session_id": {
                        "type": "keyword"
                    },
                    "trace_id": {
                        "type": "keyword"
                    },
                    "span_id": {
                        "type": "keyword"
                    },
                    "environment": {
                        "type": "keyword"
                    },
                    "metadata": {
                        "type": "object",
                        "enabled": True,
                        "dynamic": True
                    },
                    "fingerprint_hash": {
                        "type": "keyword"
                    },
                    "content_type": {
                        "type": "keyword"
                    },
                    "platform": {
                        "type": "keyword"
                    },
                    "revenue_amount": {
                        "type": "float"
                    },
                    "similarity_score": {
                        "type": "float"
                    },
                    "processing_time_ms": {
                        "type": "integer"
                    },
                    "error_code": {
                        "type": "keyword"
                    },
                    "stack_trace": {
                        "type": "text",
                        "index": False
                    }
                }
            }
        }


class QueryBuilder:
    """Elasticsearch query builder for logs"""
    
    def __init__(self):
        self.query = {"bool": {"must": [], "filter": [], "should": [], "must_not": []}}
    
    def add_time_range(self, start_time: datetime, end_time: datetime):
        """Add time range filter"""
        self.query["bool"]["filter"].append({
            "range": {
                "timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat()
                }
            }
        })
        return self
    
    def add_service_filter(self, services: Union[str, List[str]]):
        """Add service filter"""
        if isinstance(services, str):
            services = [services]
        
        self.query["bool"]["filter"].append({
            "terms": {"service": services}
        })
        return self
    
    def add_level_filter(self, levels: Union[LogLevel, List[LogLevel]]):
        """Add log level filter"""
        if isinstance(levels, LogLevel):
            levels = [levels]
        
        level_values = [level.value for level in levels]
        self.query["bool"]["filter"].append({
            "terms": {"level": level_values}
        })
        return self
    
    def add_user_filter(self, user_ids: Union[str, List[str]]):
        """Add user ID filter"""
        if isinstance(user_ids, str):
            user_ids = [user_ids]
        
        self.query["bool"]["filter"].append({
            "terms": {"user_id": user_ids}
        })
        return self
    
    def add_text_search(self, text: str, fields: Optional[List[str]] = None):
        """Add full-text search"""
        if not fields:
            fields = ["message", "metadata.*"]
        
        self.query["bool"]["must"].append({
            "multi_match": {
                "query": text,
                "fields": fields,
                "type": "best_fields"
            }
        })
        return self
    
    def add_metadata_filter(self, metadata_filters: Dict[str, Any]):
        """Add metadata filters"""
        for key, value in metadata_filters.items():
            self.query["bool"]["filter"].append({
                "term": {f"metadata.{key}": value}
            })
        return self
    
    def add_aggregation(self, name: str, agg_config: Dict[str, Any]):
        """Add aggregation to query"""
        if "aggs" not in self.query:
            self.query["aggs"] = {}
        self.query["aggs"][name] = agg_config
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build final query"""
        return self.query


class ElasticsearchManager:
    """
Advanced Elasticsearch manager for IA Influencer Agent logging"""
    
    def __init__(self, config: ElasticsearchConfig):
        self.config = config
        self.client: Optional[AsyncElasticsearch] = None
        self.template_manager = IndexTemplate()
        self.index_strategy = IndexStrategy.DAILY
        self.base_index_name = "ia-influencer-logs"
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to Elasticsearch cluster"""
        try:
            client_config = {
                'hosts': self.config.hosts,
                'timeout': self.config.timeout,
                'max_retries': self.config.max_retries,
                'retry_on_timeout': self.config.retry_on_timeout
            }
            
            if self.config.username and self.config.password:
                client_config['http_auth'] = (self.config.username, self.config.password)
            
            if self.config.use_ssl:
                client_config['use_ssl'] = True
                client_config['verify_certs'] = self.config.verify_certs
                
                if self.config.ca_certs:
                    client_config['ca_certs'] = self.config.ca_certs
                if self.config.client_cert:
                    client_config['client_cert'] = self.config.client_cert
                if self.config.client_key:
                    client_config['client_key'] = self.config.client_key
            
            self.client = AsyncElasticsearch(**client_config)
            
            # Test connection
            await self.client.ping()
            self.is_connected = True
            
            # Setup index template
            await self._setup_index_template()
            
            logging.info("Connected to Elasticsearch cluster")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to Elasticsearch: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Elasticsearch"""
        if self.client:
            await self.client.close()
            self.is_connected = False
            logging.info("Disconnected from Elasticsearch")
    
    async def _setup_index_template(self):
        """Setup index template for log indices"""
        try:
            template = self.template_manager.get_template()
            
            await self.client.indices.put_index_template(
                name=self.template_manager.template_name,
                body=template
            )
            
            logging.info(f"Index template '{self.template_manager.template_name}' created/updated")
            
        except Exception as e:
            logging.error(f"Failed to setup index template: {e}")
            raise ElasticsearchError(f"Template setup failed: {e}")
    
    def _get_index_name(self, timestamp: datetime) -> str:
        """Generate index name based on strategy and timestamp"""
        if self.index_strategy == IndexStrategy.DAILY:
            suffix = timestamp.strftime("%Y.%m.%d")
        elif self.index_strategy == IndexStrategy.WEEKLY:
            year, week, _ = timestamp.isocalendar()
            suffix = f"{year}.W{week:02d}"
        elif self.index_strategy == IndexStrategy.MONTHLY:
            suffix = timestamp.strftime("%Y.%m")
        elif self.index_strategy == IndexStrategy.YEARLY:
            suffix = timestamp.strftime("%Y")
        else:  # SINGLE
            suffix = "all"
        
        return f"{self.base_index_name}-{suffix}"
    
    async def index_log(self, log_entry: LogEntry) -> bool:
        """Index a single log entry"""
        if not self.is_connected:
            raise ElasticsearchError("Not connected to Elasticsearch")
        
        try:
            index_name = self._get_index_name(log_entry.timestamp)
            
            response = await self.client.index(
                index=index_name,
                body=log_entry.to_dict()
            )
            
            return response['result'] in ['created', 'updated']
            
        except Exception as e:
            logging.error(f"Failed to index log entry: {e}")
            return False
    
    async def bulk_index_logs(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Bulk index multiple log entries"""
        if not self.is_connected:
            raise ElasticsearchError("Not connected to Elasticsearch")
        
        if not log_entries:
            return {"indexed": 0, "errors": 0}
        
        try:
            actions = []
            for log_entry in log_entries:
                index_name = self._get_index_name(log_entry.timestamp)
                
                action = {
                    "_index": index_name,
                    "_source": log_entry.to_dict()
                }
                actions.append(action)
            
            success_count, errors = await async_bulk(
                self.client,
                actions,
                chunk_size=1000,
                request_timeout=30
            )
            
            return {
                "indexed": success_count,
                "errors": len(errors) if errors else 0,
                "error_details": errors if errors else []
            }
            
        except Exception as e:
            logging.error(f"Failed to bulk index logs: {e}")
            return {"indexed": 0, "errors": len(log_entries), "error_details": [str(e)]}
    
    async def search_logs(self, 
                         query_builder: QueryBuilder,
                         size: int = 100,
                         from_: int = 0,
                         sort: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Search logs using query builder"""
        if not self.is_connected:
            raise ElasticsearchError("Not connected to Elasticsearch")
        
        try:
            search_body = {
                "query": query_builder.build(),
                "size": size,
                "from": from_
            }
            
            if sort:
                search_body["sort"] = sort
            else:
                search_body["sort"] = [{"timestamp": {"order": "desc"}}]
            
            # Include aggregations if present
            query = query_builder.build()
            if "aggs" in query:
                search_body["aggs"] = query["aggs"]
            
            response = await self.client.search(
                index=f"{self.base_index_name}-*",
                body=search_body
            )
            
            return {
                "total": response["hits"]["total"]["value"],
                "hits": [hit["_source"] for hit in response["hits"]["hits"]],
                "aggregations": response.get("aggregations", {})
            }
            
        except Exception as e:
            logging.error(f"Failed to search logs: {e}")
            raise ElasticsearchError(f"Search failed: {e}")
    
    async def get_log_statistics(self, 
                                start_time: datetime,
                                end_time: datetime) -> Dict[str, Any]:
        """Get log statistics for time range"""
        query = QueryBuilder().add_time_range(start_time, end_time)
        
        # Add aggregations for statistics
        query.add_aggregation("levels", {
            "terms": {"field": "level", "size": 10}
        })
        
        query.add_aggregation("services", {
            "terms": {"field": "service", "size": 20}
        })
        
        query.add_aggregation("hourly_counts", {
            "date_histogram": {
                "field": "timestamp",
                "interval": "1h",
                "format": "yyyy-MM-dd HH:mm:ss"
            }
        })
        
        query.add_aggregation("error_rate", {
            "filter": {"terms": {"level": ["ERROR", "CRITICAL"]}},
            "aggs": {
                "hourly_errors": {
                    "date_histogram": {
                        "field": "timestamp",
                        "interval": "1h"
                    }
                }
            }
        })
        
        result = await self.search_logs(query, size=0)
        
        return {
            "total_logs": result["total"],
            "level_distribution": result["aggregations"]["levels"]["buckets"],
            "service_distribution": result["aggregations"]["services"]["buckets"],
            "hourly_distribution": result["aggregations"]["hourly_counts"]["buckets"],
            "error_rate": result["aggregations"]["error_rate"]
        }
    
    async def get_recent_errors(self, 
                               hours: int = 24,
                               size: int = 100) -> List[Dict[str, Any]]:
        """Get recent error logs"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        query = (QueryBuilder()
                .add_time_range(start_time, end_time)
                .add_level_filter([LogLevel.ERROR, LogLevel.CRITICAL]))
        
        result = await self.search_logs(query, size=size)
        return result["hits"]
    
    async def cleanup_old_indices(self, retention_days: int = 30):
        """Cleanup old log indices based on retention policy"""
        if not self.is_connected:
            raise ElasticsearchError("Not connected to Elasticsearch")
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            
            # Get all indices matching our pattern
            indices = await self.client.indices.get(f"{self.base_index_name}-*")
            
            deleted_indices = []
            for index_name in indices.keys():
                # Extract date from index name and check if it's old
                try:
                    if self.index_strategy == IndexStrategy.DAILY:
                        date_str = index_name.split("-")[-1]  # Get YYYY.MM.DD part
                        index_date = datetime.strptime(date_str, "%Y.%m.%d")
                    else:
                        continue  # Other strategies not implemented for cleanup
                    
                    if index_date.replace(tzinfo=timezone.utc) < cutoff_date:
                        await self.client.indices.delete(index_name)
                        deleted_indices.append(index_name)
                        logging.info(f"Deleted old index: {index_name}")
                
                except (ValueError, IndexError):
                    logging.warning(f"Could not parse date from index name: {index_name}")
                    continue
            
            return deleted_indices
            
        except Exception as e:
            logging.error(f"Failed to cleanup old indices: {e}")
            raise ElasticsearchError(f"Cleanup failed: {e}")
    
    async def get_cluster_health(self) -> Dict[str, Any]:
        """Get Elasticsearch cluster health"""
        if not self.is_connected:
            raise ElasticsearchError("Not connected to Elasticsearch")
        
        try:
            health = await self.client.cluster.health()
            stats = await self.client.cluster.stats()
            
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"],
                "number_of_data_nodes": health["number_of_data_nodes"],
                "active_primary_shards": health["active_primary_shards"],
                "active_shards": health["active_shards"],
                "relocating_shards": health["relocating_shards"],
                "initializing_shards": health["initializing_shards"],
                "unassigned_shards": health["unassigned_shards"],
                "delayed_unassigned_shards": health["delayed_unassigned_shards"],
                "number_of_pending_tasks": health["number_of_pending_tasks"],
                "number_of_in_flight_fetch": health["number_of_in_flight_fetch"],
                "task_max_waiting_in_queue_millis": health["task_max_waiting_in_queue_millis"],
                "active_shards_percent_as_number": health["active_shards_percent_as_number"],
                "total_storage": stats["indices"]["store"]["size_in_bytes"],
                "total_documents": stats["indices"]["docs"]["count"]
            }
            
        except Exception as e:
            logging.error(f"Failed to get cluster health: {e}")
            raise ElasticsearchError(f"Health check failed: {e}")
    
    async def create_dashboard_queries(self) -> Dict[str, QueryBuilder]:
        """Create predefined queries for dashboard"""
        queries = {}
        
        # Recent activity (last 24 hours)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        queries["recent_activity"] = (QueryBuilder()
                                    .add_time_range(start_time, end_time))
        
        # Error trends
        queries["error_trends"] = (QueryBuilder()
                                 .add_time_range(start_time, end_time)
                                 .add_level_filter([LogLevel.ERROR, LogLevel.CRITICAL]))
        
        # Service performance
        queries["service_performance"] = (QueryBuilder()
                                        .add_time_range(start_time, end_time)
                                        .add_aggregation("services", {
                                            "terms": {"field": "service", "size": 10}
                                        }))
        
        # User activity
        queries["user_activity"] = (QueryBuilder()
                                  .add_time_range(start_time, end_time)
                                  .add_aggregation("active_users", {
                                      "cardinality": {"field": "user_id"}
                                  }))
        
        return queries
