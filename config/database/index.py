#!/usr/bin/env python3
"""
Database Index Configuration
Created by: Fahed Mlaiel <mlaiel@live.de>
Professional Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and belongs to Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
"""

from typing import Dict, List, Optional, Any
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class IndexType(Enum):
    """Database index types for optimization"""
    BTREE = "btree"
    HASH = "hash" 
    GIST = "gist"
    SPGIST = "spgist"
    GIN = "gin"
    BRIN = "brin"
    VECTOR = "vector"
    TEXT = "text"
    GEOSPATIAL = "geospatial"

class DatabaseIndexManager:
    """
    Professional database index management for IA Influencer Agent platform
    Handles multi-database indexing strategies for optimal performance
    """
    
    def __init__(self):
        self.postgresql_indexes = self._get_postgresql_indexes()
        self.mongodb_indexes = self._get_mongodb_indexes()
        self.redis_indexes = self._get_redis_indexes()
        self.elasticsearch_indexes = self._get_elasticsearch_indexes()
        self.vector_db_indexes = self._get_vector_db_indexes()
    
    def _get_postgresql_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """PostgreSQL optimized indexes for content protection and user management"""



        return {
            "users": [
                {
                    "name": "idx_users_email_active",
                    "columns": ["email", "is_active"],
                    "type": IndexType.BTREE,
                    "unique": True,
                    "where": "is_active = true"
                },
                {
                    "name": "idx_users_subscription_tier",
                    "columns": ["subscription_tier", "created_at"],
                    "type": IndexType.BTREE,
                    "partial": "subscription_tier IS NOT NULL"
                },
                {
                    "name": "idx_users_full_text_search",
                    "columns": ["to_tsvector('english', username || ' ' || display_name)"],
                    "type": IndexType.GIN
                }
            ],
            "content_items": [
                {
                    "name": "idx_content_protection_status",
                    "columns": ["protection_status", "created_at"],
                    "type": IndexType.BTREE,
                    "include": ["content_hash", "ai_fingerprint_id"]
                },
                {
                    "name": "idx_content_hash_unique",
                    "columns": ["content_hash"],
                    "type": IndexType.HASH,
                    "unique": True
                },
                {
                    "name": "idx_content_ai_fingerprint",
                    "columns": ["ai_fingerprint_id", "status"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_content_metadata_gin",
                    "columns": ["metadata"],
                    "type": IndexType.GIN,
                    "expression": "metadata jsonb_ops"
                },
                {
                    "name": "idx_content_full_text",
                    "columns": ["to_tsvector('english', title || ' ' || description)"],
                    "type": IndexType.GIN
                }
            ],
            "ai_fingerprints": [
                {
                    "name": "idx_fingerprint_hash_algorithm",
                    "columns": ["fingerprint_hash", "algorithm_type"],
                    "type": IndexType.BTREE,
                    "unique": True
                },
                {
                    "name": "idx_fingerprint_content_type",
                    "columns": ["content_type", "created_at"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_fingerprint_features_vector",
                    "columns": ["feature_vector"],
                    "type": IndexType.GIST,
                    "operator_class": "vector_cosine_ops"
                }
            ],
            "collaborations": [
                {
                    "name": "idx_collaboration_users",
                    "columns": ["creator_id", "collaborator_id", "status"],
                    "type": IndexType.BTREE,
                    "unique": True
                },
                {
                    "name": "idx_collaboration_content",
                    "columns": ["content_id", "collaboration_type"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_collaboration_revenue_sharing",
                    "columns": ["revenue_share_percentage", "status"],
                    "type": IndexType.BTREE,
                    "where": "status = 'active'"
                }
            ],
            "monetization_analytics": [
                {
                    "name": "idx_monetization_user_date",
                    "columns": ["user_id", "analytics_date"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_monetization_revenue_period",
                    "columns": ["revenue_amount", "period_start", "period_end"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_monetization_platform_performance",
                    "columns": ["platform_name", "conversion_rate"],
                    "type": IndexType.BTREE
                }
            ],
            "protection_violations": [
                {
                    "name": "idx_violations_content_severity",
                    "columns": ["content_id", "violation_severity", "detected_at"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_violations_source_platform",
                    "columns": ["violation_source", "platform_detected"],
                    "type": IndexType.BTREE
                },
                {
                    "name": "idx_violations_status_resolution",
                    "columns": ["resolution_status", "resolved_at"],
                    "type": IndexType.BTREE,
                    "where": "resolved_at IS NOT NULL"
                }
            ]
        }
    
    def _get_mongodb_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """MongoDB indexes for media storage and analytics"""



        return {
            "media_files": [
                {
                    "name": "idx_media_content_hash",
                    "keys": {"content_hash": 1},
                    "unique": True,
                    "sparse": False
                },
                {
                    "name": "idx_media_user_upload_date",
                    "keys": {"user_id": 1, "upload_date": -1},
                    "background": True
                },
                {
                    "name": "idx_media_type_status",
                    "keys": {"media_type": 1, "processing_status": 1},
                    "background": True
                },
                {
                    "name": "idx_media_geospatial",
                    "keys": {"metadata.location": "2dsphere"},
                    "sparse": True
                },
                {
                    "name": "idx_media_full_text",
                    "keys": {
                        "title": "text",
                        "description": "text",
                        "tags": "text"
                    },
                    "default_language": "english"
                }
            ],
            "ai_processing_jobs": [
                {
                    "name": "idx_jobs_status_priority",
                    "keys": {"status": 1, "priority": -1, "created_at": 1},
                    "background": True
                },
                {
                    "name": "idx_jobs_user_type",
                    "keys": {"user_id": 1, "job_type": 1},
                    "background": True
                },
                {
                    "name": "idx_jobs_processing_node",
                    "keys": {"processing_node_id": 1, "status": 1},
                    "background": True
                }
            ],
            "analytics_events": [
                {
                    "name": "idx_events_user_timestamp",
                    "keys": {"user_id": 1, "timestamp": -1},
                    "expireAfterSeconds": 7776000,  # 90 days
                    "background": True
                },
                {
                    "name": "idx_events_type_platform",
                    "keys": {"event_type": 1, "platform": 1, "timestamp": -1},
                    "background": True
                },
                {
                    "name": "idx_events_session_tracking",
                    "keys": {"session_id": 1, "timestamp": 1},
                    "expireAfterSeconds": 2592000,  # 30 days
                    "background": True
                }
            ],
            "content_distribution": [
                {
                    "name": "idx_distribution_content_platform",
                    "keys": {"content_id": 1, "platform_name": 1},
                    "unique": True,
                    "background": True
                },
                {
                    "name": "idx_distribution_status_scheduled",
                    "keys": {"distribution_status": 1, "scheduled_at": 1},
                    "background": True
                },
                {
                    "name": "idx_distribution_performance_metrics",
                    "keys": {"platform_name": 1, "engagement_rate": -1},
                    "background": True
                }
            ]
        }
    
    def _get_redis_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Redis indexes for caching and real-time data"""



        return {
            "user_sessions": [
                {
                    "name": "idx_session_user",
                    "pattern": "session:user:*",
                    "ttl": 86400,  # 24 hours
                    "type": "hash"
                },
                {
                    "name": "idx_session_active",
                    "pattern": "session:active:*",
                    "ttl": 3600,  # 1 hour
                    "type": "sorted_set"
                }
            ],
            "content_cache": [
                {
                    "name": "idx_content_thumbnails",
                    "pattern": "thumbnail:*",
                    "ttl": 604800,  # 7 days
                    "type": "string"
                },
                {
                    "name": "idx_content_metadata",
                    "pattern": "metadata:content:*",
                    "ttl": 3600,  # 1 hour
                    "type": "hash"
                }
            ],
            "real_time_analytics": [
                {
                    "name": "idx_realtime_user_activity",
                    "pattern": "activity:user:*",
                    "ttl": 300,  # 5 minutes
                    "type": "stream"
                },
                {
                    "name": "idx_realtime_platform_metrics",
                    "pattern": "metrics:platform:*",
                    "ttl": 900,  # 15 minutes
                    "type": "hash"
                }
            ]
        }
    
    def _get_elasticsearch_indexes(self) -> Dict[str, Dict[str, Any]]:
        """Elasticsearch indexes for advanced search and analytics"""



        return {
            "content_search": {
                "mappings": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "standard",
                            "search_analyzer": "standard"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "english"
                        },
                        "tags": {
                            "type": "keyword",
                            "fields": {
                                "suggest": {
                                    "type": "completion"
                                }
                            }
                        },
                        "content_type": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "engagement_score": {"type": "float"},
                        "protection_level": {"type": "keyword"},
                        "location": {"type": "geo_point"},
                        "ai_generated_tags": {
                            "type": "text",
                            "analyzer": "keyword"
                        }
                    }
                },
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1,
                    "refresh_interval": "30s"
                }
            },
            "collaboration_matching": {
                "mappings": {
                    "properties": {
                        "user_profile": {
                            "type": "nested",
                            "properties": {
                                "skills": {"type": "keyword"},
                                "specialties": {"type": "keyword"},
                                "experience_level": {"type": "keyword"},
                                "collaboration_preferences": {"type": "keyword"}
                            }
                        },
                        "content_preferences": {
                            "type": "keyword"
                        },
                        "location": {"type": "geo_point"},
                        "availability": {"type": "boolean"},
                        "rating": {"type": "float"},
                        "successful_collaborations": {"type": "integer"}
                    }
                },
                "settings": {
                    "number_of_shards": 2,
                    "number_of_replicas": 1
                }
            },
            "analytics_insights": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "user_id": {"type": "keyword"},
                        "content_id": {"type": "keyword"},
                        "platform": {"type": "keyword"},
                        "metrics": {
                            "type": "nested",
                            "properties": {
                                "views": {"type": "long"},
                                "likes": {"type": "long"},
                                "shares": {"type": "long"},
                                "comments": {"type": "long"},
                                "revenue": {"type": "double"}
                            }
                        },
                        "ai_insights": {
                            "type": "text",
                            "analyzer": "english"
                        }
                    }
                },
                "settings": {
                    "number_of_shards": 5,
                    "number_of_replicas": 1,
                    "refresh_interval": "10s"
                }
            }
        }
    
    def _get_vector_db_indexes(self) -> Dict[str, Dict[str, Any]]:
        """FAISS Vector DB indexes for AI similarity matching"""



        return {
            "content_similarity": {
                "dimension": 768,  # BERT/Transformer embeddings
                "index_type": "IVF",
                "metric": "cosine",
                "nlist": 100,
                "nprobe": 10,
                "description": "Content similarity matching for duplicate detection"
            },
            "audio_fingerprints": {
                "dimension": 512,
                "index_type": "HNSW",
                "metric": "L2",
                "M": 16,
                "efConstruction": 200,
                "efSearch": 50,
                "description": "Audio fingerprint similarity for music protection"
            },
            "image_features": {
                "dimension": 2048,  # ResNet features
                "index_type": "IVF",
                "metric": "cosine",
                "nlist": 50,
                "nprobe": 5,
                "description": "Image feature matching for visual content protection"
            },
            "user_preferences": {
                "dimension": 256,
                "index_type": "Flat",
                "metric": "cosine",
                "description": "User preference vectors for collaboration matching"
            },
            "content_embeddings": {
                "dimension": 1024,
                "index_type": "IVF",
                "metric": "inner_product",
                "nlist": 200,
                "nprobe": 20,
                "description": "Multi-modal content embeddings for comprehensive search"
            }
        }
    
    def get_index_creation_sql(self, database_type: str, table_name: str) -> List[str]:
        """Generate SQL statements for index creation"""
        if database_type.lower() == "postgresql":
            return self._generate_postgresql_indexes(table_name)
        return []
    
    def _generate_postgresql_indexes(self, table_name: str) -> List[str]:
        """Generate PostgreSQL index creation statements"""
        if table_name not in self.postgresql_indexes:
            return []
        
        sql_statements = []
        for index_config in self.postgresql_indexes[table_name]:
            sql = self._build_postgresql_index_sql(table_name, index_config)
            if sql:
                sql_statements.append(sql)
        
        return sql_statements
    
    def _build_postgresql_index_sql(self, table_name: str, config: Dict[str, Any]) -> Optional[str]:
        """Build individual PostgreSQL index creation statement"""



        try:
            sql_parts = ["CREATE"]
            
            if config.get("unique"):
                sql_parts.append("UNIQUE")
            
            sql_parts.append("INDEX")
            sql_parts.append(f'"{config["name"]}"')
            sql_parts.append("ON")
            sql_parts.append(f'"{table_name}"')
            
            # Index type
            if "type" in config and config["type"] != IndexType.BTREE:
                sql_parts.append(f"USING {config['type'].value}")
            
            # Columns or expression
            columns = config["columns"]
            if isinstance(columns, list):
                if len(columns) == 1 and columns[0].startswith("to_tsvector"):
                    # Full-text search expression
                    sql_parts.append(f"({columns[0]})")
                else:
                    # Regular columns
                    quoted_columns = [f'"{col}"' for col in columns]
                    sql_parts.append(f'({", ".join(quoted_columns)})')
            
            # Include columns (PostgreSQL 11+)
            if "include" in config:
                quoted_include = [f'"{col}"' for col in config["include"]]
                include_cols = ", ".join(quoted_include)
                sql_parts.append(f"INCLUDE ({include_cols})")
            
            # Partial index condition
            if "where" in config:
                sql_parts.append(f"WHERE {config['where']}")
            elif "partial" in config:
                sql_parts.append(f"WHERE {config['partial']}")
            
            return " ".join(sql_parts) + ";"
            
        except Exception as e:
            logger.error(f"Error building index SQL for {config.get('name', 'unknown')}: {e}")
            return None
    
    def get_mongodb_index_specs(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get MongoDB index specifications for collection"""



        return self.mongodb_indexes.get(collection_name, [])
    
    def get_redis_cache_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get Redis caching patterns and TTL configurations"""



        return self.redis_indexes
    
    def get_elasticsearch_mappings(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get Elasticsearch index mappings"""



        return self.elasticsearch_indexes.get(index_name)
    
    def get_vector_index_config(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get Vector DB index configuration"""



        return self.vector_db_indexes.get(index_name)

# Global index manager instance
index_manager = DatabaseIndexManager()

def get_index_manager() -> DatabaseIndexManager:
    """Get the global database index manager instance"""



    return index_manager

# Quick access functions for different database types
def get_postgresql_indexes(table_name: str) -> List[str]:
    """Get PostgreSQL index creation SQL for table"""



    return index_manager.get_index_creation_sql("postgresql", table_name)

def get_mongodb_indexes(collection_name: str) -> List[Dict[str, Any]]:
    """Get MongoDB index specifications for collection"""



    return index_manager.get_mongodb_index_specs(collection_name)

def get_redis_patterns() -> Dict[str, List[Dict[str, Any]]]:
    """Get Redis caching patterns"""



    return index_manager.get_redis_cache_patterns()

def get_elasticsearch_mapping(index_name: str) -> Optional[Dict[str, Any]]:
    """Get Elasticsearch index mapping"""



    return index_manager.get_elasticsearch_mappings(index_name)

def get_vector_config(index_name: str) -> Optional[Dict[str, Any]]:
    """Get Vector DB index configuration"""



    return index_manager.get_vector_index_config(index_name)
