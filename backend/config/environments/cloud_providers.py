"""Cloud Providers Configuration
=================================

Multi-cloud provider configuration supporting AWS, Azure, and GCP
for the IA-Influencer Agent Platform deployment across different cloud environments.

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

from typing import Dict, Any, Optional
import os

def get_config(provider: str = 'aws') -> Dict[str, Any]:
    """Get cloud provider configuration"""
    
    if provider.lower() == 'aws':
        return get_aws_config()
    elif provider.lower() == 'azure':
        return get_azure_config()
    elif provider.lower() == 'gcp':
        return get_gcp_config()
    else:
        raise ValueError(f"Unsupported cloud provider: {provider}")

def get_aws_config() -> Dict[str, Any]:
    """Get AWS cloud configuration"""
    return {
        'provider': 'aws',
        'region': os.getenv('AWS_REGION', 'eu-central-1'),
        'availability_zones': ['eu-central-1a', 'eu-central-1b', 'eu-central-1c'],
        
        # Compute services
        'compute': {
            'ec2': {
                'instance_types': {
                    'web_servers': 't3.medium',
                    'api_servers': 't3.large',
                    'ai_workers': 'p3.2xlarge',
                    'background_workers': 't3.small'
                },
                'auto_scaling': {
                    'min_size': 2,
                    'max_size': 10,
                    'desired_capacity': 3
                }
            },
            'ecs': {
                'cluster_name': 'ainflue-cluster',
                'service_discovery': True,
                'load_balancer_type': 'application'
            },
            'lambda': {
                'runtime': 'python3.9',
                'timeout': 300,
                'memory_size': 1024
            }
        },
        
        # Storage services
        'storage': {
            's3': {
                'bucket_name': os.getenv('AWS_S3_BUCKET', ''),
                'encryption': 'AES256',
                'versioning': True,
                'lifecycle_policies': True,
                'cdn': {
                    'cloudfront_distribution': True,
                    'cache_behaviors': ['*.jpg', '*.png', '*.mp3', '*.mp4']
                }
            },
            'efs': {
                'file_system_id': os.getenv('AWS_EFS_ID', ''),
                'performance_mode': 'generalPurpose',
                'throughput_mode': 'provisioned'
            }
        },
        
        # Database services
        'database': {
            'rds': {
                'engine': 'postgres',
                'version': '14.9',
                'instance_class': 'db.t3.micro',
                'multi_az': True,
                'backup_retention': 7,
                'encryption': True
            },
            'elasticache': {
                'engine': 'redis',
                'version': '7.0',
                'node_type': 'cache.t3.micro',
                'cluster_mode': True,
                'encryption_at_rest': True,
                'encryption_in_transit': True
            }
        },
        
        # Networking
        'networking': {
            'vpc_id': os.getenv('AWS_VPC_ID', ''),
            'subnet_ids': os.getenv('AWS_SUBNET_IDS', '').split(','),
            'security_groups': {
                'web': os.getenv('AWS_WEB_SG_ID', ''),
                'api': os.getenv('AWS_API_SG_ID', ''),
                'database': os.getenv('AWS_DB_SG_ID', '')
            },
            'load_balancer': {
                'type': 'application',
                'scheme': 'internet-facing',
                'ssl_certificate_arn': os.getenv('AWS_SSL_CERT_ARN', '')
            }
        },
        
        # AI/ML services
        'ai_ml': {
            'sagemaker': {
                'execution_role': os.getenv('AWS_SAGEMAKER_ROLE_ARN', ''),
                'instance_types': {
                    'training': 'ml.p3.2xlarge',
                    'inference': 'ml.t3.medium'
                }
            },
            'bedrock': {
                'models': ['anthropic.claude-v2', 'amazon.titan-tg1-large'],
                'provisioned_throughput': False
            }
        },
        
        # Monitoring and logging
        'monitoring': {
            'cloudwatch': {
                'log_groups': ['/aws/lambda/ainflue', '/aws/ecs/ainflue'],
                'retention_days': 14,
                'metrics_enabled': True
            },
            'x_ray': {
                'tracing_enabled': True,
                'sampling_rate': 0.1
            }
        }
    }

def get_azure_config() -> Dict[str, Any]:
    """Get Azure cloud configuration"""
    return {
        'provider': 'azure',
        'region': os.getenv('AZURE_REGION', 'West Europe'),
        'resource_group': os.getenv('AZURE_RESOURCE_GROUP', 'ainflue-rg'),
        
        # Compute services
        'compute': {
            'virtual_machines': {
                'vm_sizes': {
                    'web_servers': 'Standard_B2s',
                    'api_servers': 'Standard_B4ms',
                    'ai_workers': 'Standard_NC6s_v3'
                },
                'availability_set': True
            },
            'container_instances': {
                'resource_requests': {
                    'cpu': 1,
                    'memory': 2
                }
            },
            'functions': {
                'runtime': 'python',
                'version': '3.9',
                'consumption_plan': True
            }
        },
        
        # Storage services
        'storage': {
            'blob_storage': {
                'account_name': os.getenv('AZURE_STORAGE_ACCOUNT', ''),
                'container_name': 'ainflue-content',
                'access_tier': 'Hot',
                'encryption': True
            },
            'file_storage': {
                'share_name': 'ainflue-files',
                'tier': 'Premium'
            }
        },
        
        # Database services
        'database': {
            'postgresql': {
                'server_name': os.getenv('AZURE_POSTGRES_SERVER', ''),
                'version': '14',
                'sku_name': 'GP_Gen5_2',
                'backup_retention': 7,
                'ssl_enforcement': True
            },
            'redis_cache': {
                'name': os.getenv('AZURE_REDIS_NAME', ''),
                'sku_name': 'Standard',
                'sku_family': 'C',
                'sku_capacity': 1,
                'ssl_port': 6380
            }
        },
        
        # Networking
        'networking': {
            'virtual_network': os.getenv('AZURE_VNET_ID', ''),
            'subnets': {
                'web': os.getenv('AZURE_WEB_SUBNET', ''),
                'api': os.getenv('AZURE_API_SUBNET', ''),
                'database': os.getenv('AZURE_DB_SUBNET', '')
            },
            'load_balancer': {
                'sku': 'Standard',
                'type': 'Public'
            }
        },
        
        # AI/ML services
        'ai_ml': {
            'machine_learning': {
                'workspace_name': os.getenv('AZURE_ML_WORKSPACE', ''),
                'compute_targets': {
                    'cpu_cluster': 'STANDARD_DS3_V2',
                    'gpu_cluster': 'STANDARD_NC6s_v3'
                }
            },
            'cognitive_services': {
                'text_analytics': True,
                'computer_vision': True,
                'speech_services': True
            }
        }
    }

def get_gcp_config() -> Dict[str, Any]:
    """Get Google Cloud Platform configuration"""
    return {
        'provider': 'gcp',
        'project_id': os.getenv('GCP_PROJECT_ID', ''),
        'region': os.getenv('GCP_REGION', 'europe-west3'),
        'zones': ['europe-west3-a', 'europe-west3-b', 'europe-west3-c'],
        
        # Compute services
        'compute': {
            'compute_engine': {
                'machine_types': {
                    'web_servers': 'n1-standard-2',
                    'api_servers': 'n1-standard-4',
                    'ai_workers': 'n1-standard-8-nvidia-tesla-k80'
                },
                'instance_groups': {
                    'min_size': 2,
                    'max_size': 10
                }
            },
            'cloud_run': {
                'max_instances': 100,
                'memory': '2Gi',
                'cpu': '2'
            },
            'cloud_functions': {
                'runtime': 'python39',
                'timeout': '300s',
                'memory': '1024MB'
            }
        },
        
        # Storage services
        'storage': {
            'cloud_storage': {
                'bucket_name': os.getenv('GCP_STORAGE_BUCKET', ''),
                'location': 'EUROPE-WEST3',
                'storage_class': 'STANDARD',
                'uniform_bucket_level_access': True
            },
            'filestore': {
                'instance_id': os.getenv('GCP_FILESTORE_ID', ''),
                'tier': 'STANDARD',
                'capacity': '1024'
            }
        },
        
        # Database services
        'database': {
            'cloud_sql': {
                'instance_id': os.getenv('GCP_SQL_INSTANCE', ''),
                'database_version': 'POSTGRES_14',
                'tier': 'db-n1-standard-2',
                'backup_enabled': True,
                'ssl_required': True
            },
            'memorystore': {
                'instance_id': os.getenv('GCP_REDIS_INSTANCE', ''),
                'tier': 'STANDARD_HA',
                'memory_size_gb': 4,
                'auth_enabled': True
            }
        },
        
        # Networking
        'networking': {
            'vpc_network': os.getenv('GCP_VPC_NETWORK', ''),
            'subnets': {
                'web': os.getenv('GCP_WEB_SUBNET', ''),
                'api': os.getenv('GCP_API_SUBNET', ''),
                'database': os.getenv('GCP_DB_SUBNET', '')
            },
            'load_balancer': {
                'type': 'EXTERNAL',
                'ssl_certificates': [os.getenv('GCP_SSL_CERT', '')]
            }
        },
        
        # AI/ML services
        'ai_ml': {
            'vertex_ai': {
                'location': 'europe-west3',
                'machine_types': {
                    'training': 'n1-standard-8',
                    'prediction': 'n1-standard-4'
                }
            },
            'ai_platform': {
                'models': ['text-bison', 'chat-bison'],
                'endpoints': True
            }
        }
    }

def get_multi_cloud_config() -> Dict[str, Any]:
    """Get multi-cloud configuration for hybrid deployments"""
    return {
        'primary_provider': os.getenv('PRIMARY_CLOUD_PROVIDER', 'aws'),
        'secondary_provider': os.getenv('SECONDARY_CLOUD_PROVIDER', 'azure'),
        'disaster_recovery_provider': os.getenv('DR_CLOUD_PROVIDER', 'gcp'),
        
        'failover': {
            'automatic': True,
            'health_check_interval': 30,
            'failover_threshold': 3
        },
        
        'data_replication': {
            'enabled': True,
            'sync_interval': 300,
            'conflict_resolution': 'primary_wins'
        },
        
        'cost_optimization': {
            'spot_instances': True,
            'reserved_instances': True,
            'auto_scaling': True
        }
    }