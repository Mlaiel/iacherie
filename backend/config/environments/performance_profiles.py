"""Performance Profiles Configuration
====================================

Performance profiles for different deployment scenarios and workload types
for the IA-Influencer Agent Platform.

Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, Any
import os

def get_config(profile: str = 'balanced') -> Dict[str, Any]:
    """Get performance profile configuration"""
    
    profiles = {
        'high_performance': get_high_performance_profile(),
        'balanced': get_balanced_profile(),
        'cost_optimized': get_cost_optimized_profile(),
        'ai_intensive': get_ai_intensive_profile()
    }
    
    return profiles.get(profile, get_balanced_profile())

def get_high_performance_profile() -> Dict[str, Any]:
    """High performance profile for demanding workloads"""
    return {
        'profile': 'high_performance',
        'description': 'Maximum performance configuration',
        
        'compute': {
            'instance_types': {
                'web': 'c5.4xlarge',
                'api': 'c5.9xlarge',
                'workers': 'm5.12xlarge',
                'ai_processing': 'p3.8xlarge'
            },
            'auto_scaling': {
                'scale_up_cooldown': 60,
                'scale_down_cooldown': 300,
                'target_cpu_utilization': 50
            }
        },
        
        'database': {
            'instance_class': 'db.r5.4xlarge',
            'read_replicas': 3,
            'connection_pool_size': 50,
            'query_timeout': 10
        },
        
        'cache': {
            'instance_type': 'cache.r6g.4xlarge',
            'cluster_nodes': 6,
            'ttl_seconds': 7200,
            'memory_policy': 'allkeys-lru'
        },
        
        'networking': {
            'enhanced_networking': True,
            'placement_group': 'cluster',
            'bandwidth_limit': None
        },
        
        'storage': {
            'storage_type': 'io2',
            'iops': 10000,
            'throughput': 1000,
            'multi_attach': True
        }
    }

def get_balanced_profile() -> Dict[str, Any]:
    """Balanced profile for general workloads"""
    return {
        'profile': 'balanced',
        'description': 'Balanced performance and cost',
        
        'compute': {
            'instance_types': {
                'web': 't3.large',
                'api': 'm5.xlarge',
                'workers': 'm5.2xlarge',
                'ai_processing': 'p3.2xlarge'
            },
            'auto_scaling': {
                'scale_up_cooldown': 180,
                'scale_down_cooldown': 600,
                'target_cpu_utilization': 70
            }
        },
        
        'database': {
            'instance_class': 'db.t3.large',
            'read_replicas': 1,
            'connection_pool_size': 20,
            'query_timeout': 30
        },
        
        'cache': {
            'instance_type': 'cache.t3.medium',
            'cluster_nodes': 2,
            'ttl_seconds': 3600,
            'memory_policy': 'allkeys-lru'
        },
        
        'networking': {
            'enhanced_networking': False,
            'placement_group': None,
            'bandwidth_limit': '10Gbps'
        },
        
        'storage': {
            'storage_type': 'gp3',
            'iops': 3000,
            'throughput': 125,
            'multi_attach': False
        }
    }

def get_cost_optimized_profile() -> Dict[str, Any]:
    """Cost-optimized profile for budget-conscious deployments"""
    return {
        'profile': 'cost_optimized',
        'description': 'Minimum cost configuration',
        
        'compute': {
            'instance_types': {
                'web': 't3.small',
                'api': 't3.medium',
                'workers': 't3.large',
                'ai_processing': 'g4dn.xlarge'
            },
            'auto_scaling': {
                'scale_up_cooldown': 300,
                'scale_down_cooldown': 900,
                'target_cpu_utilization': 80
            },
            'spot_instances': True,
            'reserved_instances': True
        },
        
        'database': {
            'instance_class': 'db.t3.micro',
            'read_replicas': 0,
            'connection_pool_size': 5,
            'query_timeout': 60
        },
        
        'cache': {
            'instance_type': 'cache.t3.micro',
            'cluster_nodes': 1,
            'ttl_seconds': 1800,
            'memory_policy': 'volatile-lru'
        },
        
        'networking': {
            'enhanced_networking': False,
            'placement_group': None,
            'bandwidth_limit': '1Gbps'
        },
        
        'storage': {
            'storage_type': 'gp2',
            'iops': 100,
            'throughput': 50,
            'multi_attach': False
        }
    }

def get_ai_intensive_profile() -> Dict[str, Any]:
    """AI-intensive profile optimized for machine learning workloads"""
    return {
        'profile': 'ai_intensive',
        'description': 'Optimized for AI/ML workloads',
        
        'compute': {
            'instance_types': {
                'web': 'm5.large',
                'api': 'm5.xlarge',
                'workers': 'c5.4xlarge',
                'ai_processing': 'p4d.24xlarge',
                'training': 'p4d.24xlarge',
                'inference': 'inf1.6xlarge'
            },
            'auto_scaling': {
                'scale_up_cooldown': 300,
                'scale_down_cooldown': 1800,
                'target_gpu_utilization': 80,
                'target_cpu_utilization': 60
            }
        },
        
        'database': {
            'instance_class': 'db.r5.2xlarge',
            'read_replicas': 2,
            'connection_pool_size': 30,
            'query_timeout': 20
        },
        
        'cache': {
            'instance_type': 'cache.r6g.2xlarge',
            'cluster_nodes': 3,
            'ttl_seconds': 3600,
            'memory_policy': 'allkeys-lru'
        },
        
        'ai_specific': {
            'model_cache_size': '100GB',
            'gpu_memory_optimization': True,
            'mixed_precision_training': True,
            'distributed_training': True,
            'model_parallelism': True,
            'gradient_checkpointing': True
        },
        
        'storage': {
            'storage_type': 'io2',
            'iops': 8000,
            'throughput': 500,
            'model_storage': 'efs',
            'dataset_storage': 's3'
        }
    }