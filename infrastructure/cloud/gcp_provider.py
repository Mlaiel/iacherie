"""
Google Cloud Platform Infrastructure Provider
Enterprise-grade GCP infrastructure management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from datetime import datetime, timedelta

try:
    from google.cloud import compute_v1, storage, container_v1, sql_v1
    from google.cloud import functions_v1, monitoring_v3, logging as gcp_logging
    from google.cloud import aiplatform, bigquery, pubsub_v1
    from google.oauth2 import service_account
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logging.warning("GCP SDK not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


class GCPRegion(Enum):
    """GCP regions for global deployment"""
    US_CENTRAL1 = "us-central1"
    US_EAST1 = "us-east1"  
    US_WEST1 = "us-west1"
    EUROPE_WEST1 = "europe-west1"
    EUROPE_WEST3 = "europe-west3"
    ASIA_SOUTHEAST1 = "asia-southeast1"
    ASIA_NORTHEAST1 = "asia-northeast1"


class GCPZone(Enum):
    """GCP availability zones"""
    US_CENTRAL1_A = "us-central1-a"
    US_CENTRAL1_B = "us-central1-b"
    US_CENTRAL1_C = "us-central1-c"
    EUROPE_WEST1_B = "europe-west1-b"
    ASIA_SOUTHEAST1_A = "asia-southeast1-a"


@dataclass
class GCPCredentials:
    """GCP authentication credentials"""
    project_id: str
    service_account_path: Optional[str] = None
    service_account_info: Optional[Dict] = None
    location: str = "us-central1"


@dataclass
class GCPComputeConfig:
    """GCP Compute Engine configuration"""
    machine_type: str = "e2-medium"
    zone: str = GCPZone.US_CENTRAL1_A.value
    boot_disk_type: str = "pd-standard"
    boot_disk_size: int = 20
    network: str = "default"
    subnetwork: Optional[str] = None
    preemptible: bool = False
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class GKEClusterConfig:
    """Google Kubernetes Engine cluster configuration"""
    cluster_name: str
    zone: str = GCPZone.US_CENTRAL1_A.value
    node_count: int = 3
    machine_type: str = "e2-medium"
    disk_size_gb: int = 100
    auto_scaling: bool = True
    min_nodes: int = 1
    max_nodes: int = 10
    enable_autoupgrade: bool = True
    enable_autorepair: bool = True


@dataclass
class CloudSQLConfig:
    """Cloud SQL database configuration"""
    instance_id: str
    database_version: str = "POSTGRES_13"
    tier: str = "db-f1-micro"
    region: str = GCPRegion.US_CENTRAL1.value
    backup_enabled: bool = True
    high_availability: bool = False
    storage_size: int = 10
    storage_type: str = "PD_SSD"


@dataclass
class GCPStorageConfig:
    """Google Cloud Storage configuration"""
    bucket_name: str
    location: str = "US"
    storage_class: str = "STANDARD"
    lifecycle_rules: List[Dict] = field(default_factory=list)
    cors_config: Optional[Dict] = None
    versioning_enabled: bool = False


class GCPProvider:
    """
    Google Cloud Platform infrastructure provider
    
    Provides enterprise-grade GCP infrastructure management for:
    - Compute Engine instances and managed instance groups
    - Google Kubernetes Engine (GKE) clusters
    - Cloud SQL databases
    - Cloud Storage buckets
    - AI Platform services for ML workloads
    - BigQuery for analytics
    - Pub/Sub for messaging
    - Cloud Functions for serverless computing
    - Monitoring and logging
    """
    
    def __init__(self, credentials: GCPCredentials):
        """Initialize GCP provider with credentials"""
        self.credentials = credentials
        self.project_id = credentials.project_id
        self.clients = {}
        self._initialize_clients()
        
        # Ainflue-specific configurations
        self.creator_services = {
            "content_processing": {
                "machine_type": "n1-standard-4",
                "gpu_type": "nvidia-tesla-t4",
                "gpu_count": 1
            },
            "ai_analysis": {
                "machine_type": "n1-highmem-8", 
                "gpu_type": "nvidia-tesla-v100",
                "gpu_count": 2
            },
            "streaming_infrastructure": {
                "machine_type": "c2-standard-16",
                "network_tier": "PREMIUM"
            }
        }
        
    def _initialize_clients(self):
        """Initialize GCP service clients"""
        if not GCP_AVAILABLE:
            logger.warning("GCP SDK not available. Using simulation mode.")
            return
            
        try:
            # Load credentials
            if self.credentials.service_account_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials.service_account_path
                )
            elif self.credentials.service_account_info:
                credentials = service_account.Credentials.from_service_account_info(
                    self.credentials.service_account_info
                )
            else:
                credentials = None
                
            # Initialize clients
            self.clients = {
                'compute': compute_v1.InstancesClient(credentials=credentials),
                'storage': storage.Client(credentials=credentials, project=self.project_id),
                'container': container_v1.ClusterManagerClient(credentials=credentials),
                'sql': sql_v1.SqlInstancesServiceClient(credentials=credentials),
                'functions': functions_v1.CloudFunctionsServiceClient(credentials=credentials),
                'monitoring': monitoring_v3.MetricServiceClient(credentials=credentials),
                'logging': gcp_logging.Client(credentials=credentials, project=self.project_id),
                'aiplatform': aiplatform,
                'bigquery': bigquery.Client(credentials=credentials, project=self.project_id),
                'pubsub': pubsub_v1.PublisherClient(credentials=credentials)
            }
            
            # Initialize AI Platform
            if credentials:
                aiplatform.init(project=self.project_id, credentials=credentials)
            else:
                aiplatform.init(project=self.project_id)
                
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {e}")
            
    async def create_compute_instance(self, config: GCPComputeConfig, 
                                    instance_name: str) -> Dict[str, Any]:
        """Create a new Compute Engine instance"""
        if not GCP_AVAILABLE:
            return self._simulate_compute_creation(instance_name, config)
            
        try:
            # Instance configuration for Ainflue content processing
            instance_config = {
                'name': instance_name,
                'machine_type': f"zones/{config.zone}/machineTypes/{config.machine_type}",
                'disks': [{
                    'boot': True,
                    'auto_delete': True,
                    'initialize_params': {
                        'source_image': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts',
                        'disk_size_gb': config.boot_disk_size,
                        'disk_type': f"zones/{config.zone}/diskTypes/{config.boot_disk_type}"
                    }
                }],
                'network_interfaces': [{
                    'network': f"global/networks/{config.network}",
                    'access_configs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
                }],
                'metadata': {
                    'items': [
                        {'key': 'startup-script', 'value': self._get_ainflue_startup_script()},
                        {'key': 'creator-platform', 'value': 'ainflue'},
                        {'key': 'content-processing', 'value': 'enabled'}
                    ]
                },
                'labels': {
                    'platform': 'ainflue',
                    'creator-economy': 'true',
                    **config.labels
                },
                'scheduling': {'preemptible': config.preemptible}
            }
            
            operation = self.clients['compute'].insert(
                project=self.project_id,
                zone=config.zone,
                instance_resource=instance_config
            )
            
            return {
                'instance_name': instance_name,
                'operation_id': operation.name,
                'status': 'creating',
                'zone': config.zone,
                'machine_type': config.machine_type,
                'labels': config.labels
            }
            
        except Exception as e:
            logger.error(f"Failed to create GCP instance {instance_name}: {e}")
            raise
            
    async def create_gke_cluster(self, config: GKEClusterConfig) -> Dict[str, Any]:
        """Create a Google Kubernetes Engine cluster"""
        if not GCP_AVAILABLE:
            return self._simulate_gke_creation(config)
            
        try:
            # GKE cluster optimized for Ainflue creator workloads
            cluster_config = {
                'name': config.cluster_name,
                'initial_node_count': config.node_count,
                'node_config': {
                    'machine_type': config.machine_type,
                    'disk_size_gb': config.disk_size_gb,
                    'oauth_scopes': [
                        'https://www.googleapis.com/auth/cloud-platform'
                    ],
                    'labels': {
                        'platform': 'ainflue',
                        'content-processing': 'enabled',
                        'creator-services': 'true'
                    },
                    'metadata': {
                        'disable-legacy-endpoints': 'true',
                        'creator-platform': 'ainflue'
                    }
                },
                'addons_config': {
                    'http_load_balancing': {'disabled': False},
                    'horizontal_pod_autoscaling': {'disabled': False},
                    'kubernetes_dashboard': {'disabled': True},  # Security best practice
                    'istio_config': {'disabled': False}  # Service mesh for microservices
                },
                'network_policy': {
                    'enabled': True,
                    'provider': 'CALICO'
                },
                'ip_allocation_policy': {
                    'use_ip_aliases': True
                },
                'master_auth': {
                    'client_certificate_config': {'issue_client_certificate': False}
                },
                'logging_service': 'logging.googleapis.com/kubernetes',
                'monitoring_service': 'monitoring.googleapis.com/kubernetes'
            }
            
            # Auto-scaling configuration for creator traffic spikes
            if config.auto_scaling:
                cluster_config['node_config']['disk_type'] = 'pd-ssd'
                cluster_config['cluster_autoscaling'] = {
                    'enable_node_autoprovisioning': True,
                    'autoscaling_profile': 'OPTIMIZE_UTILIZATION',
                    'resource_limits': [{
                        'resource_type': 'cpu',
                        'minimum': config.min_nodes * 2,
                        'maximum': config.max_nodes * 4
                    }, {
                        'resource_type': 'memory',
                        'minimum': config.min_nodes * 8,
                        'maximum': config.max_nodes * 32
                    }]
                }
                
            parent = f"projects/{self.project_id}/locations/{config.zone}"
            operation = self.clients['container'].create_cluster(
                parent=parent,
                cluster=cluster_config
            )
            
            return {
                'cluster_name': config.cluster_name,
                'operation_id': operation.name,
                'zone': config.zone,
                'status': 'creating',
                'node_count': config.node_count,
                'machine_type': config.machine_type,
                'auto_scaling': config.auto_scaling
            }
            
        except Exception as e:
            logger.error(f"Failed to create GKE cluster {config.cluster_name}: {e}")
            raise
            
    async def create_cloud_sql_instance(self, config: CloudSQLConfig) -> Dict[str, Any]:
        """Create a Cloud SQL database instance"""
        if not GCP_AVAILABLE:
            return self._simulate_cloudsql_creation(config)
            
        try:
            # Cloud SQL configuration for Ainflue creator data
            sql_config = {
                'name': config.instance_id,
                'database_version': config.database_version,
                'region': config.region,
                'settings': {
                    'tier': config.tier,
                    'disk_size': config.storage_size,
                    'disk_type': config.storage_type,
                    'disk_autoresize': True,
                    'disk_autoresize_limit': 100,
                    'backup_configuration': {
                        'enabled': config.backup_enabled,
                        'start_time': '03:00',  # Low traffic time
                        'location': config.region,
                        'point_in_time_recovery_enabled': True,
                        'transaction_log_retention_days': 7
                    },
                    'availability_type': 'REGIONAL' if config.high_availability else 'ZONAL',
                    'database_flags': [
                        {'name': 'max_connections', 'value': '200'},
                        {'name': 'shared_preload_libraries', 'value': 'pg_stat_statements'},
                        {'name': 'log_statement', 'value': 'all'}  # For audit
                    ],
                    'ip_configuration': {
                        'ipv4_enabled': True,
                        'require_ssl': True,
                        'authorized_networks': []  # Configured separately
                    },
                    'maintenance_window': {
                        'hour': 4,  # 4 AM UTC
                        'day': 7,   # Sunday
                        'update_track': 'stable'
                    },
                    'user_labels': {
                        'platform': 'ainflue',
                        'environment': 'production',
                        'creator-data': 'true'
                    }
                }
            }
            
            operation = self.clients['sql'].insert(
                project=self.project_id,
                body=sql_config
            )
            
            return {
                'instance_id': config.instance_id,
                'operation_id': operation.name,
                'status': 'creating',
                'database_version': config.database_version,
                'region': config.region,
                'tier': config.tier,
                'backup_enabled': config.backup_enabled
            }
            
        except Exception as e:
            logger.error(f"Failed to create Cloud SQL instance {config.instance_id}: {e}")
            raise
            
    async def create_storage_bucket(self, config: GCPStorageConfig) -> Dict[str, Any]:
        """Create a Google Cloud Storage bucket"""
        if not GCP_AVAILABLE:
            return self._simulate_storage_creation(config)
            
        try:
            bucket = self.clients['storage'].bucket(config.bucket_name)
            bucket.storage_class = config.storage_class
            bucket.location = config.location
            
            # Ainflue creator content storage configuration
            if config.versioning_enabled:
                bucket.versioning_enabled = True
                
            # Lifecycle management for cost optimization
            if config.lifecycle_rules:
                bucket.lifecycle_rules = config.lifecycle_rules
            else:
                # Default lifecycle for creator content
                bucket.lifecycle_rules = [
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
                        'condition': {'age': 30}
                    },
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'COLDLINE'},
                        'condition': {'age': 90}
                    },
                    {
                        'action': {'type': 'Delete'},
                        'condition': {'age': 365}
                    }
                ]
                
            # CORS configuration for web uploads
            if config.cors_config:
                bucket.cors = [config.cors_config]
            else:
                bucket.cors = [{
                    'origin': ['*'],
                    'method': ['GET', 'POST', 'PUT', 'DELETE'],
                    'responseHeader': ['Content-Type', 'x-goog-resumable'],
                    'maxAgeSeconds': 3600
                }]
                
            # Labels for organization
            bucket.labels = {
                'platform': 'ainflue',
                'content-type': 'creator-uploads',
                'cost-center': 'infrastructure'
            }
            
            bucket = self.clients['storage'].create_bucket(bucket)
            
            return {
                'bucket_name': config.bucket_name,
                'location': config.location,
                'storage_class': config.storage_class,
                'versioning_enabled': config.versioning_enabled,
                'lifecycle_rules': len(bucket.lifecycle_rules),
                'status': 'created'
            }
            
        except Exception as e:
            logger.error(f"Failed to create storage bucket {config.bucket_name}: {e}")
            raise
            
    async def setup_ai_platform_environment(self, region: str = "us-central1") -> Dict[str, Any]:
        """Setup AI Platform environment for Ainflue ML workloads"""
        if not GCP_AVAILABLE:
            return self._simulate_ai_platform_setup(region)
            
        try:
            # Configure AI Platform for creator content analysis
            config = {
                'region': region,
                'staging_bucket': f"gs://ainflue-ml-staging-{self.project_id}",
                'training': {
                    'machine_type': 'n1-standard-4',
                    'accelerator_type': 'NVIDIA_TESLA_T4',
                    'accelerator_count': 1,
                    'python_version': '3.8'
                },
                'prediction': {
                    'machine_type': 'n1-standard-2',
                    'min_nodes': 1,
                    'max_nodes': 10,
                    'accelerator_type': 'NVIDIA_TESLA_T4',
                    'accelerator_count': 1
                },
                'vertex_ai': {
                    'enable_custom_training': True,
                    'enable_auto_ml': True,
                    'enable_feature_store': True,
                    'enable_model_registry': True
                }
            }
            
            return {
                'status': 'configured',
                'region': region,
                'training_config': config['training'],
                'prediction_config': config['prediction'],
                'vertex_ai_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Failed to setup AI Platform: {e}")
            raise
            
    async def create_pubsub_topic(self, topic_name: str, 
                                 subscription_name: Optional[str] = None) -> Dict[str, Any]:
        """Create Pub/Sub topic for real-time messaging"""
        if not GCP_AVAILABLE:
            return self._simulate_pubsub_creation(topic_name, subscription_name)
            
        try:
            # Create topic for Ainflue real-time events
            topic_path = self.clients['pubsub'].topic_path(self.project_id, topic_name)
            
            topic_config = {
                'name': topic_path,
                'labels': {
                    'platform': 'ainflue',
                    'event-type': 'creator-activity',
                    'real-time': 'true'
                }
            }
            
            topic = self.clients['pubsub'].create_topic(request={'name': topic_path})
            
            result = {
                'topic_name': topic_name,
                'topic_path': topic.name,
                'status': 'created',
                'labels': topic_config['labels']
            }
            
            # Create subscription if specified
            if subscription_name:
                subscriber = pubsub_v1.SubscriberClient()
                subscription_path = subscriber.subscription_path(
                    self.project_id, subscription_name
                )
                
                subscription = subscriber.create_subscription(
                    request={
                        'name': subscription_path,
                        'topic': topic_path,
                        'ack_deadline_seconds': 60,
                        'message_retention_duration': {'seconds': 604800},  # 7 days
                        'labels': {
                            'platform': 'ainflue',
                            'subscriber-type': 'creator-events'
                        }
                    }
                )
                
                result['subscription'] = {
                    'name': subscription_name,
                    'path': subscription.name,
                    'status': 'created'
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to create Pub/Sub topic {topic_name}: {e}")
            raise
            
    def _get_ainflue_startup_script(self) -> str:
        """Get startup script for Ainflue compute instances"""
        return """#!/bin/bash
        
        # Ainflue Creator Platform Instance Setup
        apt-get update
        apt-get install -y docker.io nginx python3-pip
        
        # Install creator content processing tools
        pip3 install tensorflow opencv-python pillow ffmpeg-python
        
        # Configure for creator uploads
        mkdir -p /opt/ainflue/{uploads,processing,cache}
        chown -R www-data:www-data /opt/ainflue
        
        # Setup monitoring agent
        curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
        bash add-google-cloud-ops-agent-repo.sh --also-install
        
        # Start services
        systemctl enable docker nginx
        systemctl start docker nginx
        
        # Creator platform ready
        echo "Ainflue creator processing node ready" > /opt/ainflue/status
        """
        
    def _simulate_compute_creation(self, instance_name: str, 
                                  config: GCPComputeConfig) -> Dict[str, Any]:
        """Simulate compute instance creation"""
        return {
            'instance_name': instance_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'zone': config.zone,
            'machine_type': config.machine_type,
            'simulation': True
        }
        
    def _simulate_gke_creation(self, config: GKEClusterConfig) -> Dict[str, Any]:
        """Simulate GKE cluster creation"""
        return {
            'cluster_name': config.cluster_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'zone': config.zone,
            'node_count': config.node_count,
            'simulation': True
        }
        
    def _simulate_cloudsql_creation(self, config: CloudSQLConfig) -> Dict[str, Any]:
        """Simulate Cloud SQL creation"""
        return {
            'instance_id': config.instance_id,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'database_version': config.database_version,
            'simulation': True
        }
        
    def _simulate_storage_creation(self, config: GCPStorageConfig) -> Dict[str, Any]:
        """Simulate storage bucket creation"""
        return {
            'bucket_name': config.bucket_name,
            'location': config.location,
            'storage_class': config.storage_class,
            'status': 'simulated',
            'simulation': True
        }
        
    def _simulate_ai_platform_setup(self, region: str) -> Dict[str, Any]:
        """Simulate AI Platform setup"""
        return {
            'status': 'simulated',
            'region': region,
            'vertex_ai_enabled': True,
            'simulation': True
        }
        
    def _simulate_pubsub_creation(self, topic_name: str, 
                                 subscription_name: Optional[str]) -> Dict[str, Any]:
        """Simulate Pub/Sub creation"""
        result = {
            'topic_name': topic_name,
            'status': 'simulated',
            'simulation': True
        }
        
        if subscription_name:
            result['subscription'] = {
                'name': subscription_name,
                'status': 'simulated'
            }
            
        return result
        
    async def get_resource_status(self, resource_type: str, 
                                resource_name: str) -> Dict[str, Any]:
        """Get status of GCP resource"""
        if not GCP_AVAILABLE:
            return {'status': 'simulation_mode', 'resource': resource_name}
            
        try:
            if resource_type == 'compute':
                # Get compute instance status
                zones = [zone.value for zone in GCPZone]
                for zone in zones:
                    try:
                        instance = self.clients['compute'].get(
                            project=self.project_id,
                            zone=zone,
                            instance=resource_name
                        )
                        return {
                            'resource_type': 'compute',
                            'name': resource_name,
                            'status': instance.status,
                            'zone': zone,
                            'machine_type': instance.machine_type.split('/')[-1],
                            'created': instance.creation_timestamp
                        }
                    except:
                        continue
                        
            elif resource_type == 'gke':
                # Get GKE cluster status
                zones = [zone.value for zone in GCPZone]
                for zone in zones:
                    try:
                        parent = f"projects/{self.project_id}/locations/{zone}"
                        cluster = self.clients['container'].get_cluster(
                            name=f"{parent}/clusters/{resource_name}"
                        )
                        return {
                            'resource_type': 'gke',
                            'name': resource_name,
                            'status': cluster.status,
                            'zone': zone,
                            'node_count': cluster.current_node_count,
                            'created': cluster.create_time
                        }
                    except:
                        continue
                        
            elif resource_type == 'cloudsql':
                # Get Cloud SQL status
                instance = self.clients['sql'].get(
                    project=self.project_id,
                    instance=resource_name
                )
                return {
                    'resource_type': 'cloudsql',
                    'name': resource_name,
                    'status': instance.state,
                    'database_version': instance.database_version,
                    'tier': instance.settings.tier,
                    'created': instance.create_time
                }
                
            elif resource_type == 'storage':
                # Get storage bucket status
                bucket = self.clients['storage'].bucket(resource_name)
                if bucket.exists():
                    return {
                        'resource_type': 'storage',
                        'name': resource_name,
                        'status': 'active',
                        'location': bucket.location,
                        'storage_class': bucket.storage_class,
                        'created': bucket.time_created
                    }
                    
            return {'status': 'not_found', 'resource': resource_name}
            
        except Exception as e:
            logger.error(f"Failed to get status for {resource_type}/{resource_name}: {e}")
            return {'status': 'error', 'error': str(e)}
            
    async def cleanup_resources(self, resource_filter: Dict[str, str] = None) -> Dict[str, Any]:
        """Cleanup GCP resources based on filter"""
        if not GCP_AVAILABLE:
            return {'status': 'simulation', 'cleaned': 0}
            
        cleaned_resources = []
        
        try:
            # Default filter for Ainflue resources
            if not resource_filter:
                resource_filter = {'platform': 'ainflue'}
                
            # Cleanup compute instances
            zones = [zone.value for zone in GCPZone]
            for zone in zones:
                try:
                    instances = self.clients['compute'].list(
                        project=self.project_id, zone=zone
                    )
                    
                    for instance in instances:
                        if self._matches_filter(instance.labels, resource_filter):
                            operation = self.clients['compute'].delete(
                                project=self.project_id,
                                zone=zone,
                                instance=instance.name
                            )
                            cleaned_resources.append({
                                'type': 'compute',
                                'name': instance.name,
                                'operation': operation.name
                            })
                except:
                    continue
                    
            return {
                'status': 'completed',
                'cleaned_resources': cleaned_resources,
                'count': len(cleaned_resources)
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup resources: {e}")
            return {'status': 'error', 'error': str(e)}
            
    def _matches_filter(self, labels: Dict[str, str], 
                       filter_criteria: Dict[str, str]) -> bool:
        """Check if resource labels match filter criteria"""
        if not labels or not filter_criteria:
            return False
            
        for key, value in filter_criteria.items():
            if key not in labels or labels[key] != value:
                return False
                
        return True
        
    def get_ainflue_optimized_configs(self) -> Dict[str, Any]:
        """Get Ainflue-optimized GCP configurations"""
        return {
            'content_processing': {
                'compute': GCPComputeConfig(
                    machine_type="n1-standard-4",
                    zone=GCPZone.US_CENTRAL1_A.value,
                    boot_disk_size=50,
                    labels={'service': 'content-processing', 'platform': 'ainflue'}
                ),
                'storage': GCPStorageConfig(
                    bucket_name=f"ainflue-content-{self.project_id}",
                    storage_class="STANDARD",
                    versioning_enabled=True
                )
            },
            'ai_processing': {
                'compute': GCPComputeConfig(
                    machine_type="n1-highmem-8",
                    zone=GCPZone.US_CENTRAL1_A.value,
                    boot_disk_size=100,
                    labels={'service': 'ai-processing', 'platform': 'ainflue'}
                ),
                'gke': GKEClusterConfig(
                    cluster_name=f"ainflue-ai-cluster",
                    machine_type="n1-standard-4",
                    node_count=3,
                    auto_scaling=True,
                    max_nodes=20
                )
            },
            'database': {
                'cloudsql': CloudSQLConfig(
                    instance_id=f"ainflue-db-{self.project_id}",
                    database_version="POSTGRES_13",
                    tier="db-custom-4-16384",
                    high_availability=True,
                    backup_enabled=True
                )
            }
        }