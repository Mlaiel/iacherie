"""
⚙️ Vector Database Configuration
================================

Default configuration templates for the ultra-advanced vector database system.
Provides optimized settings for different deployment scenarios.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""

from typing import Dict, Any
from pathlib import Path

# Default configuration for development environment
DEVELOPMENT_CONFIG: Dict[str, Any] = {
    'environment': 'development',
    
    # Core embeddings configuration
    'embeddings': {
        'audio_embedding_dim': 512,
        'video_embedding_dim': 1024,
        'image_embedding_dim': 768,
        'text_embedding_dim': 384,
        'composite_embedding_dim': 1536,
        'use_clip': True,
        'use_sentence_transformers': True,
        'sentence_model': 'all-MiniLM-L6-v2',
        'cache_embeddings': True,
        'embedding_cache_size': 1000
    },
    
    # Vector store configuration (FAISS)
    'vector_store': {
        'backend': 'faiss',
        'dimension': 512,
        'index_type': 'IndexFlatL2',  # Simple for development
        'storage_path': './data/vector_db_dev',
        'persist_index': True,
        'max_workers': 2
    },
    
    # Search engine configuration
    'search': {
        'similarity_metric': 'cosine',
        'min_similarity': 0.6,
        'exact_threshold': 0.98,
        'near_duplicate_threshold': 0.90,
        'similar_threshold': 0.75,
        'related_threshold': 0.60,
        'cache_max_size': 1000,
        'enable_cross_modal': False
    },
    
    # Index manager configuration
    'index_manager': {
        'auto_create_indexes': True,
        'index_optimization': False,  # Disabled for dev
        'backup_interval_hours': 24,
        'max_indexes': 5
    },
    
    # Query engine configuration
    'query_engine': {
        'enable_optimization': False,  # Disabled for dev
        'enable_caching': True,
        'enable_parallel_execution': False,
        'optimizer': {
            'auto_optimize': False,
            'max_query_time_ms': 10000
        },
        'cache': {
            'max_cache_size': 1000,
            'default_ttl_seconds': 300
        }
    },
    
    # Analytics configuration
    'analytics': {
        'auto_reporting': False,  # Disabled for dev
        'report_interval_hours': 24,
        'enable_visualizations': False,
        'metrics': {
            'buffer_size': 1000,
            'aggregation_interval_seconds': 300,
            'retention_days': 7
        },
        'patterns': {
            'min_pattern_frequency': 3,
            'enable_clustering': False
        }
    },
    
    # Optimization configuration
    'optimization': {
        'auto_optimization': False,  # Disabled for dev
        'optimization_interval_hours': 24,
        'min_improvement_threshold': 10.0
    },
    
    # Replication configuration
    'replication': {
        'enabled': False,  # Disabled for dev
        'local_node_id': 'dev_node',
        'replication_mode': 'master_slave',
        'cluster_nodes': []
    }
}

# Production configuration for high-performance deployment
PRODUCTION_CONFIG: Dict[str, Any] = {
    'environment': 'production',
    
    # Core embeddings configuration
    'embeddings': {
        'audio_embedding_dim': 512,
        'video_embedding_dim': 1024,
        'image_embedding_dim': 768,
        'text_embedding_dim': 384,
        'composite_embedding_dim': 1536,
        'use_clip': True,
        'use_sentence_transformers': True,
        'sentence_model': 'all-MiniLM-L6-v2',
        'cache_embeddings': True,
        'embedding_cache_size': 50000
    },
    
    # Vector store configuration (FAISS optimized)
    'vector_store': {
        'backend': 'faiss',
        'dimension': 512,
        'index_type': 'IndexIVFPQ',  # Optimized for production
        'storage_path': '/data/vector_db_prod',
        'persist_index': True,
        'nlist': 4096,  # For large datasets
        'pq_m': 8,
        'pq_nbits': 8,
        'max_workers': 8
    },
    
    # Search engine configuration
    'search': {
        'similarity_metric': 'cosine',
        'min_similarity': 0.7,
        'exact_threshold': 0.98,
        'near_duplicate_threshold': 0.92,
        'similar_threshold': 0.80,
        'related_threshold': 0.70,
        'cache_max_size': 100000,
        'enable_cross_modal': True
    },
    
    # Index manager configuration
    'index_manager': {
        'auto_create_indexes': True,
        'index_optimization': True,
        'backup_interval_hours': 6,
        'max_indexes': 50
    },
    
    # Query engine configuration
    'query_engine': {
        'enable_optimization': True,
        'enable_caching': True,
        'enable_parallel_execution': True,
        'optimizer': {
            'auto_optimize': True,
            'max_query_time_ms': 5000
        },
        'cache': {
            'max_cache_size': 100000,
            'default_ttl_seconds': 600
        }
    },
    
    # Analytics configuration
    'analytics': {
        'auto_reporting': True,
        'report_interval_hours': 6,
        'enable_visualizations': True,
        'metrics': {
            'buffer_size': 50000,
            'aggregation_interval_seconds': 60,
            'retention_days': 30
        },
        'patterns': {
            'min_pattern_frequency': 10,
            'enable_clustering': True,
            'cluster_eps': 0.3,
            'cluster_min_samples': 5
        }
    },
    
    # Optimization configuration
    'optimization': {
        'auto_optimization': True,
        'optimization_interval_hours': 12,
        'min_improvement_threshold': 5.0,
        'analyzer': {
            'analysis_cache_ttl': 300
        },
        'optimizer': {
            'test_query_count': 200,
            'test_timeout_seconds': 120
        },
        'benchmark': {
            'warmup_queries': 20,
            'benchmark_iterations': 10
        }
    },
    
    # Replication configuration
    'replication': {
        'enabled': True,
        'local_node_id': 'prod_primary',
        'replication_mode': 'master_slave',
        'sync_interval_seconds': 30,
        'heartbeat_interval_seconds': 10,
        'max_retry_attempts': 3,
        'operation_timeout_seconds': 60,
        'cluster_nodes': [
            {
                'node_id': 'prod_replica_1',
                'role': 'slave',
                'endpoint': 'https://replica1.vectordb.com',
                'region': 'us-east-1',
                'priority': 1
            },
            {
                'node_id': 'prod_replica_2',
                'role': 'slave',
                'endpoint': 'https://replica2.vectordb.com',
                'region': 'eu-west-1',
                'priority': 2
            }
        ],
        'conflict_resolution': {
            'default_strategy': 'last_write_wins'
        }
    }
}

# High-performance configuration for enterprise deployment
ENTERPRISE_CONFIG: Dict[str, Any] = {
    'environment': 'enterprise',
    
    # Core embeddings configuration (optimized)
    'embeddings': {
        'audio_embedding_dim': 1024,  # Higher dimension for better accuracy
        'video_embedding_dim': 2048,
        'image_embedding_dim': 1024,
        'text_embedding_dim': 768,
        'composite_embedding_dim': 3072,
        'use_clip': True,
        'use_sentence_transformers': True,
        'sentence_model': 'all-mpnet-base-v2',  # Better model
        'cache_embeddings': True,
        'embedding_cache_size': 100000
    },
    
    # Vector store configuration (FAISS enterprise)
    'vector_store': {
        'backend': 'faiss',
        'dimension': 1024,
        'index_type': 'IndexHNSWFlat',  # Best for enterprise
        'storage_path': '/enterprise/vector_db',
        'persist_index': True,
        'ef_construction': 500,
        'ef_search': 100,
        'max_workers': 16
    },
    
    # Search engine configuration (optimized)
    'search': {
        'similarity_metric': 'cosine',
        'min_similarity': 0.75,
        'exact_threshold': 0.99,
        'near_duplicate_threshold': 0.95,
        'similar_threshold': 0.85,
        'related_threshold': 0.75,
        'cache_max_size': 500000,
        'enable_cross_modal': True
    },
    
    # Index manager configuration (enterprise)
    'index_manager': {
        'auto_create_indexes': True,
        'index_optimization': True,
        'backup_interval_hours': 2,
        'max_indexes': 200
    },
    
    # Query engine configuration (enterprise)
    'query_engine': {
        'enable_optimization': True,
        'enable_caching': True,
        'enable_parallel_execution': True,
        'optimizer': {
            'auto_optimize': True,
            'max_query_time_ms': 2000
        },
        'cache': {
            'max_cache_size': 500000,
            'default_ttl_seconds': 1800
        }
    },
    
    # Analytics configuration (comprehensive)
    'analytics': {
        'auto_reporting': True,
        'report_interval_hours': 2,
        'enable_visualizations': True,
        'metrics': {
            'buffer_size': 100000,
            'aggregation_interval_seconds': 30,
            'retention_days': 90
        },
        'patterns': {
            'min_pattern_frequency': 5,
            'enable_clustering': True,
            'cluster_eps': 0.2,
            'cluster_min_samples': 3
        }
    },
    
    # Optimization configuration (aggressive)
    'optimization': {
        'auto_optimization': True,
        'optimization_interval_hours': 4,
        'min_improvement_threshold': 2.0,
        'analyzer': {
            'analysis_cache_ttl': 600
        },
        'optimizer': {
            'test_query_count': 500,
            'test_timeout_seconds': 300
        },
        'benchmark': {
            'warmup_queries': 50,
            'benchmark_iterations': 20
        }
    },
    
    # Replication configuration (multi-region)
    'replication': {
        'enabled': True,
        'local_node_id': 'enterprise_primary',
        'replication_mode': 'master_master',
        'sync_interval_seconds': 10,
        'heartbeat_interval_seconds': 5,
        'max_retry_attempts': 5,
        'operation_timeout_seconds': 30,
        'cluster_nodes': [
            {
                'node_id': 'enterprise_eu',
                'role': 'master',
                'endpoint': 'https://eu.enterprise-vectordb.com',
                'region': 'eu-central-1',
                'priority': 1
            },
            {
                'node_id': 'enterprise_us',
                'role': 'master',
                'endpoint': 'https://us.enterprise-vectordb.com',
                'region': 'us-west-2',
                'priority': 1
            },
            {
                'node_id': 'enterprise_asia',
                'role': 'replica',
                'endpoint': 'https://asia.enterprise-vectordb.com',
                'region': 'ap-southeast-1',
                'priority': 2
            }
        ],
        'conflict_resolution': {
            'default_strategy': 'vector_version_priority'
        }
    }
}

# Testing configuration for automated tests
TESTING_CONFIG: Dict[str, Any] = {
    'environment': 'testing',
    
    # Minimal configuration for fast tests
    'embeddings': {
        'audio_embedding_dim': 128,
        'video_embedding_dim': 256,
        'image_embedding_dim': 256,
        'text_embedding_dim': 128,
        'composite_embedding_dim': 512,
        'use_clip': False,  # Disabled for speed
        'use_sentence_transformers': False,
        'cache_embeddings': False
    },
    
    'vector_store': {
        'backend': 'faiss',
        'dimension': 128,
        'index_type': 'IndexFlatL2',
        'storage_path': '/tmp/vector_db_test',
        'persist_index': False,  # In-memory for tests
        'max_workers': 1
    },
    
    'search': {
        'similarity_metric': 'cosine',
        'min_similarity': 0.5,
        'cache_max_size': 100,
        'enable_cross_modal': False
    },
    
    'query_engine': {
        'enable_optimization': False,
        'enable_caching': False,
        'cache': {'max_cache_size': 10}
    },
    
    'analytics': {
        'auto_reporting': False,
        'enable_visualizations': False,
        'metrics': {'buffer_size': 100}
    },
    
    'optimization': {
        'auto_optimization': False
    },
    
    'replication': {
        'enabled': False
    }
}


def get_config(environment: str = 'development') -> Dict[str, Any]:
    """
    Get configuration for specified environment.
    
    Args:
        environment: Environment name (development, production, enterprise, testing)
        
    Returns:
        Configuration dictionary for the specified environment
    """
    configs = {
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
        'enterprise': ENTERPRISE_CONFIG,
        'testing': TESTING_CONFIG
    }
    
    if environment not in configs:
        raise ValueError(f"Unknown environment: {environment}. Available: {list(configs.keys())}")
    
    return configs[environment].copy()


def create_custom_config(
    base_environment: str = 'development',
    overrides: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create custom configuration by overriding base environment settings.
    
    Args:
        base_environment: Base environment to start with
        overrides: Dictionary of settings to override
        
    Returns:
        Custom configuration dictionary
    """
    config = get_config(base_environment)
    
    if overrides:
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(config, overrides)
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration dictionary for required settings.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ['embeddings', 'vector_store', 'search']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate vector store settings
    vector_store = config['vector_store']
    if 'dimension' not in vector_store or vector_store['dimension'] <= 0:
        raise ValueError("vector_store.dimension must be a positive integer")
    
    if 'index_type' not in vector_store:
        raise ValueError("vector_store.index_type is required")
    
    # Validate embedding dimensions match vector store
    embeddings = config['embeddings']
    expected_dims = {
        'audio_embedding_dim', 'video_embedding_dim', 
        'image_embedding_dim', 'text_embedding_dim'
    }
    
    for dim_key in expected_dims:
        if dim_key in embeddings and embeddings[dim_key] <= 0:
            raise ValueError(f"embeddings.{dim_key} must be a positive integer")
    
    return True


# Export configuration functions
__all__ = [
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG', 
    'ENTERPRISE_CONFIG',
    'TESTING_CONFIG',
    'get_config',
    'create_custom_config',
    'validate_config'
]
