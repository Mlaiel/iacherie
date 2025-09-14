"""Infrastructure Deployment Module - Main Index

This index file provides a convenient entry point for the IA Influencer Agent
infrastructure deployment system with comprehensive cloud provider support,
container orchestration, database provisioning, monitoring, and security.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Import all infrastructure components
from .cloud_provider import (
    CloudProviderManager, 
    CloudProvider, 
    AWSProvider, 
    GCPProvider, 
    AzureProvider,
    CloudCredentials,
    InfrastructureSpec
)

from .container_orchestration import (
    ContainerOrchestrator,
    ServiceSpec,
    DeploymentSpec,
    K8sManifestGenerator
)

from .database_provisioning import (
    DatabaseProvisioner,
    DatabaseConfig,
    PostgreSQLProvisioner,
    RedisProvisioner,
    MongoDBProvisioner,
    ElasticsearchProvisioner
)

from .load_balancing import (
    LoadBalancerManager,
    LoadBalancerConfig,
    NginxIngressController,
    TraefikIngressController,
    IstioIngressController
)

from .monitoring_stack import (
    MonitoringStackManager,
    MonitoringConfig,
    PrometheusConfig,
    GrafanaConfig,
    JaegerConfig,
    AlertManagerConfig
)

from .networking import (
    NetworkingManager,
    VPCSpec,
    SecurityGroupSpec,
    ServiceMeshConfig
)

from .resource_scaling import (
    ResourceScalingManager,
    HPASpec,
    VPASpec,
    ClusterAutoscalerConfig
)

from .service_mesh import (
    ServiceMeshManager,
    ServiceMeshType,
    ServiceMeshConfig,
    VirtualServiceSpec,
    DestinationRuleSpec,
    GatewaySpec,
    ServiceEntrySpec,
    AuthorizationPolicySpec
)

from .storage_management import (
    StorageManager,
    StorageType,
    StorageClass,
    BackupStrategy,
    DataTier,
    StorageConfig,
    ObjectStorageConfig,
    BackupConfig,
    PersistentVolumeSpec,
    PersistentVolumeClaimSpec
)

from .vector_database import (
    VectorDatabaseManager,
    VectorDatabaseType,
    IndexType,
    DistanceMetric,
    VectorIndexSpec,
    VectorDatabaseConfig,
    EmbeddingConfig
)

logger = logging.getLogger(__name__)

class DeploymentMode(Enum):
    """
Infrastructure deployment modes"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class DeploymentEnvironment(Enum):
    """Deployment environments"""

    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"
    MULTI_CLOUD = "multi_cloud"

@dataclass
class IAInfluencerInfrastructureConfig:
    """Complete infrastructure configuration for IA Influencer platform"""
    deployment_mode: DeploymentMode
    environment: DeploymentEnvironment
    cloud_provider: CloudProvider
    region: str
    namespace: str = "ia-influencer"
    
    # Infrastructure specifications
    enable_vector_database: bool = True
    enable_monitoring: bool = True
    enable_service_mesh: bool = True
    enable_auto_scaling: bool = True
    enable_backup: bool = True
    enable_ssl: bool = True
    
    # Security and compliance
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    enable_rbac: bool = True
    
    # Performance settings
    min_replicas: int = 2
    max_replicas: int = 10
    cpu_limit: str = "2000m"
    memory_limit: str = "4Gi"
    
    # Storage settings
    storage_class: str = "fast-ssd"
    backup_retention_days: int = 30
    
    # Custom configuration
    custom_configs: Dict[str, Any] = field(default_factory=dict)

class IAInfluencerInfrastructureManager:
    """
    Comprehensive infrastructure manager for IA Influencer Agent platform
    
    This manager orchestrates the deployment of all infrastructure components
    required for the IA Influencer Agent platform including:
    - Multi-cloud provider support
    - Vector databases for AI content fingerprinting
    - Monitoring and observability stack
    - Container orchestration with Kubernetes
    - Database provisioning and management
    - Storage management with backup strategies
    - Security and compliance features
    """
    
    def __init__(self, config -> None: IAInfluencerInfrastructureConfig) -> None:
        self.config = config
        self.cloud_manager = CloudProviderManager()
        self.container_orchestrator = ContainerOrchestrator()
        self.database_provisioner = DatabaseProvisioner()
        self.vector_db_manager = VectorDatabaseManager()
        self.monitoring_manager = MonitoringStackManager()
        self.storage_manager = StorageManager()
        self.load_balancer_manager = LoadBalancerManager()
        self.networking_manager = NetworkingManager()
        self.service_mesh_manager = ServiceMeshManager()
        self.scaling_manager = ResourceScalingManager()
        
        self.deployment_status = {
            'cloud_provider': False,
            'networking': False,
            'storage': False,
            'databases': False,
            'vector_databases': False,
            'container_orchestration': False,
            'service_mesh': False,
            'monitoring': False,
            'load_balancer': False,
            'auto_scaling': False
        }
    
    async def deploy_complete_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete IA Influencer infrastructure
        
        This method orchestrates the deployment of all infrastructure components
        in the correct order with proper dependencies and health checks.
        """
        try:
            results = {}
            logger.info(f"Starting complete infrastructure deployment for IA Influencer platform")
            logger.info(f"Mode: {self.config.deployment_mode.value}, Environment: {self.config.environment.value}")
            
            # Step 1: Setup cloud provider
            cloud_result = await self._setup_cloud_provider()
            results['cloud_provider'] = cloud_result
            self.deployment_status['cloud_provider'] = cloud_result.get('status') == 'success'
            
            # Step 2: Setup networking infrastructure
            if self.deployment_status['cloud_provider']:
                networking_result = await self._setup_networking()
                results['networking'] = networking_result
                self.deployment_status['networking'] = networking_result.get('status') == 'success'
            
            # Step 3: Setup storage infrastructure
            if self.deployment_status['networking']:
                storage_result = await self._setup_storage()
                results['storage'] = storage_result
                self.deployment_status['storage'] = storage_result.get('status') == 'success'
            
            # Step 4: Deploy databases
            if self.deployment_status['storage']:
                database_result = await self._deploy_databases()
                results['databases'] = database_result
                self.deployment_status['databases'] = database_result.get('status') == 'success'
            
            # Step 5: Deploy vector databases for AI fingerprinting
            if self.config.enable_vector_database and self.deployment_status['databases']:
                vector_db_result = await self._deploy_vector_databases()
                results['vector_databases'] = vector_db_result
                self.deployment_status['vector_databases'] = vector_db_result.get('status') == 'success'
            
            # Step 6: Setup container orchestration
            if self.deployment_status['databases']:
                container_result = await self._setup_container_orchestration()
                results['container_orchestration'] = container_result
                self.deployment_status['container_orchestration'] = container_result.get('status') == 'success'
            
            # Step 7: Deploy service mesh
            if self.config.enable_service_mesh and self.deployment_status['container_orchestration']:
                service_mesh_result = await self._deploy_service_mesh()
                results['service_mesh'] = service_mesh_result
                self.deployment_status['service_mesh'] = service_mesh_result.get('status') == 'success'
            
            # Step 8: Setup monitoring and observability
            if self.config.enable_monitoring:
                monitoring_result = await self._setup_monitoring()
                results['monitoring'] = monitoring_result
                self.deployment_status['monitoring'] = monitoring_result.get('status') == 'success'
            
            # Step 9: Deploy load balancer
            if self.deployment_status['container_orchestration']:
                load_balancer_result = await self._deploy_load_balancer()
                results['load_balancer'] = load_balancer_result
                self.deployment_status['load_balancer'] = load_balancer_result.get('status') == 'success'
            
            # Step 10: Setup auto-scaling
            if self.config.enable_auto_scaling and self.deployment_status['container_orchestration']:
                scaling_result = await self._setup_auto_scaling()
                results['auto_scaling'] = scaling_result
                self.deployment_status['auto_scaling'] = scaling_result.get('status') == 'success'
            
            # Validate complete deployment
            deployment_success = all(
                status for component, status in self.deployment_status.items()
                if component != 'service_mesh' or self.config.enable_service_mesh
            )
            
            if deployment_success:
                logger.info("Complete IA Influencer infrastructure deployment successful")
                return {
                    'status': 'success',
                    'deployment_mode': self.config.deployment_mode.value,
                    'environment': self.config.environment.value,
                    'components': results,
                    'deployment_status': self.deployment_status,
                    'endpoints': await self._get_deployment_endpoints()
                }
            else:
                logger.error("Infrastructure deployment failed - some components not deployed successfully")
                return {
                    'status': 'partial_failure',
                    'deployment_status': self.deployment_status,
                    'components': results,
                    'failed_components': [
                        component for component, status in self.deployment_status.items()
                        if not status
                    ]
                }
                
        except Exception as e:
            logger.error(f"Infrastructure deployment failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'deployment_status': self.deployment_status
            }
    
    async def _setup_cloud_provider(self) -> Dict[str, Any]:
        """Setup cloud provider infrastructure"""
        try:
            logger.info(f"Setting up {self.config.cloud_provider.value} cloud provider")
            
            # Register cloud provider based on configuration
            if self.config.cloud_provider == CloudProvider.AWS:
                credentials = CloudCredentials(
                    provider=CloudProvider.AWS,
                    region=self.config.region
                )
                self.cloud_manager.register_provider(CloudProvider.AWS, credentials)
                self.cloud_manager.set_active_provider(CloudProvider.AWS)
            
            elif self.config.cloud_provider == CloudProvider.GCP:
                credentials = CloudCredentials(
                    provider=CloudProvider.GCP,
                    region=self.config.region,
                    project_id=self.config.custom_configs.get('gcp_project_id')
                )
                self.cloud_manager.register_provider(CloudProvider.GCP, credentials)
                self.cloud_manager.set_active_provider(CloudProvider.GCP)
            
            elif self.config.cloud_provider == CloudProvider.AZURE:
                credentials = CloudCredentials(
                    provider=CloudProvider.AZURE,
                    region=self.config.region,
                    subscription_id=self.config.custom_configs.get('azure_subscription_id')
                )
                self.cloud_manager.register_provider(CloudProvider.AZURE, credentials)
                self.cloud_manager.set_active_provider(CloudProvider.AZURE)
            
            return {
                'status': 'success',
                'provider': self.config.cloud_provider.value,
                'region': self.config.region
            }
            
        except Exception as e:
            logger.error(f"Failed to setup cloud provider: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _setup_networking(self) -> Dict[str, Any]:
        """Setup networking infrastructure"""
        try:
            logger.info("Setting up networking infrastructure")
            
            # Create VPC specification for IA Influencer platform
            vpc_spec = VPCSpec(
                name="ia-influencer-vpc",
                cidr_block="10.0.0.0/16",
                region=self.config.region,
                availability_zones=[f"{self.config.region}a", f"{self.config.region}b", f"{self.config.region}c"],
                enable_dns_hostnames=True,
                enable_dns_support=True,
                tags={
                    'Project': 'IA-Influencer-Agent',
                    'Environment': self.config.deployment_mode.value,
                    'Component': 'networking'
                }
            )
            
            # Setup networking
            result = await self.networking_manager.create_vpc_infrastructure(vpc_spec)
            
            return {
                'status': 'success',
                'vpc_id': result.get('vpc_id'),
                'subnets': result.get('subnets'),
                'security_groups': result.get('security_groups')
            }
            
        except Exception as e:
            logger.error(f"Failed to setup networking: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _setup_storage(self) -> Dict[str, Any]:
        """Setup storage infrastructure"""
        try:
            logger.info("Setting up storage infrastructure")
            
            # Object storage for content files (images, audio, video)
            object_storage_config = ObjectStorageConfig(
                bucket_name=f"ia-influencer-content-{self.config.region}",
                region=self.config.region,
                encryption_enabled=self.config.enable_encryption,
                versioning_enabled=True,
                lifecycle_policies=[
                    {
                        'id': 'transition_to_cold',
                        'days': 90,
                        'storage_class': 'GLACIER'
                    },
                    {
                        'id': 'delete_old_versions',
                        'days': 365,
                        'action': 'delete'
                    }
                ]
            )
            
            # Backup configuration
            backup_config = BackupConfig(
                enabled=self.config.enable_backup,
                retention_days=self.config.backup_retention_days,
                backup_schedule="0 2 * * *",  # Daily at 2 AM
                cross_region_backup=True,
                encryption_enabled=self.config.enable_encryption
            )
            
            # Storage configuration
            storage_config = StorageConfig(
                object_storage=object_storage_config,
                backup_config=backup_config,
                persistent_volumes=[
                    PersistentVolumeSpec(
                        name="ia-influencer-postgres-pv",
                        size="100Gi",
                        storage_class=self.config.storage_class,
                        access_modes=["ReadWriteOnce"]
                    ),
                    PersistentVolumeSpec(
                        name="ia-influencer-redis-pv",
                        size="20Gi",
                        storage_class=self.config.storage_class,
                        access_modes=["ReadWriteOnce"]
                    ),
                    PersistentVolumeSpec(
                        name="ia-influencer-vector-db-pv",
                        size="200Gi",
                        storage_class=self.config.storage_class,
                        access_modes=["ReadWriteOnce"]
                    )
                ]
            )
            
            result = await self.storage_manager.deploy_storage_infrastructure(storage_config)
            
            return {
                'status': 'success',
                'object_storage': result.get('object_storage'),
                'persistent_volumes': result.get('persistent_volumes'),
                'backup_config': result.get('backup_config')
            }
            
        except Exception as e:
            logger.error(f"Failed to setup storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _deploy_databases(self) -> Dict[str, Any]:
        """Deploy database infrastructure"""
        try:
            logger.info("Deploying database infrastructure")
            
            results = {}
            
            # PostgreSQL for primary application data
            postgres_config = DatabaseConfig(
                name="ia-influencer-postgres",
                database_type="postgresql",
                version="15",
                namespace=self.config.namespace,
                replicas=2 if self.config.deployment_mode == DeploymentMode.PRODUCTION else 1,
                resources={
                    'cpu': self.config.cpu_limit,
                    'memory': self.config.memory_limit,
                    'storage': '100Gi'
                },
                backup_enabled=self.config.enable_backup,
                monitoring_enabled=self.config.enable_monitoring
            )
            
            postgres_result = await self.database_provisioner.deploy_postgresql(postgres_config)
            results['postgresql'] = postgres_result
            
            # Redis for caching and session management
            redis_config = DatabaseConfig(
                name="ia-influencer-redis",
                database_type="redis",
                version="7",
                namespace=self.config.namespace,
                replicas=2 if self.config.deployment_mode == DeploymentMode.PRODUCTION else 1,
                resources={
                    'cpu': '500m',
                    'memory': '2Gi',
                    'storage': '20Gi'
                },
                backup_enabled=self.config.enable_backup,
                monitoring_enabled=self.config.enable_monitoring
            )
            
            redis_result = await self.database_provisioner.deploy_redis(redis_config)
            results['redis'] = redis_result
            
            # MongoDB for content metadata and documents
            mongodb_config = DatabaseConfig(
                name="ia-influencer-mongodb",
                database_type="mongodb",
                version="6.0",
                namespace=self.config.namespace,
                replicas=3 if self.config.deployment_mode == DeploymentMode.PRODUCTION else 1,
                resources={
                    'cpu': '1000m',
                    'memory': '4Gi',
                    'storage': '50Gi'
                },
                backup_enabled=self.config.enable_backup,
                monitoring_enabled=self.config.enable_monitoring
            )
            
            mongodb_result = await self.database_provisioner.deploy_mongodb(mongodb_config)
            results['mongodb'] = mongodb_result
            
            # Elasticsearch for search and analytics
            elasticsearch_config = DatabaseConfig(
                name="ia-influencer-elasticsearch",
                database_type="elasticsearch",
                version="8.11",
                namespace=self.config.namespace,
                replicas=3 if self.config.deployment_mode == DeploymentMode.PRODUCTION else 1,
                resources={
                    'cpu': '2000m',
                    'memory': '8Gi',
                    'storage': '100Gi'
                },
                backup_enabled=self.config.enable_backup,
                monitoring_enabled=self.config.enable_monitoring
            )
            
            elasticsearch_result = await self.database_provisioner.deploy_elasticsearch(elasticsearch_config)
            results['elasticsearch'] = elasticsearch_result
            
            return {
                'status': 'success',
                'databases': results
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy databases: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _deploy_vector_databases(self) -> Dict[str, Any]:
        """Deploy vector databases for AI content fingerprinting"""
        try:
            logger.info("Deploying vector databases for AI content fingerprinting")
            
            # Create comprehensive vector database setup for IA Influencer platform
            result = await self.vector_db_manager.create_ia_influencer_vector_db(
                namespace=self.config.namespace
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy vector databases: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _setup_container_orchestration(self) -> Dict[str, Any]:
        """Setup container orchestration with Kubernetes"""
        try:
            logger.info("Setting up container orchestration")
            
            # Deploy IA Influencer application services
            service_specs = [
                ServiceSpec(
                    name="ia-influencer-api",
                    image="ia-influencer/api:latest",
                    replicas=self.config.min_replicas,
                    ports=[8000, 9090],
                    environment_vars={
                        'POSTGRES_URL': 'postgresql://ia-influencer-postgres:5432/ia_influencer',
                        'REDIS_URL': 'redis://ia-influencer-redis:6379',
                        'MONGODB_URL': 'mongodb://ia-influencer-mongodb:27017/ia_influencer',
                        'ELASTICSEARCH_URL': 'http://ia-influencer-elasticsearch:9200',
                        'VECTOR_DB_URL': 'http://vector-db-api-service:8000',
                        'LOG_LEVEL': 'INFO'
                    }
                ),
                ServiceSpec(
                    name="ia-influencer-worker",
                    image="ia-influencer/worker:latest",
                    replicas=self.config.min_replicas,
                    ports=[],
                    environment_vars={
                        'CELERY_BROKER_URL': 'redis://ia-influencer-redis:6379',
                        'CELERY_RESULT_BACKEND': 'redis://ia-influencer-redis:6379',
                        'POSTGRES_URL': 'postgresql://ia-influencer-postgres:5432/ia_influencer'
                    }
                ),
                ServiceSpec(
                    name="ia-influencer-fingerprinting",
                    image="ia-influencer/fingerprinting:latest",
                    replicas=2,
                    ports=[8001],
                    environment_vars={
                        'VECTOR_DB_URL': 'http://vector-db-api-service:8000',
                        'GPU_ENABLED': 'true'
                    }
                )
            ]
            
            results = {}
            for spec in service_specs:
                result = await self.container_orchestrator.deploy_service(spec, self.config.namespace)
                results[spec.name] = result
            
            return {
                'status': 'success',
                'services': results
            }
            
        except Exception as e:
            logger.error(f"Failed to setup container orchestration: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _deploy_service_mesh(self) -> Dict[str, Any]:
        """Deploy service mesh for microservices communication"""
        try:
            logger.info("Deploying service mesh")
            
            # Configure Istio service mesh for IA Influencer platform
            service_mesh_config = ServiceMeshConfig(
                mesh_type=ServiceMeshType.ISTIO,
                namespace=self.config.namespace,
                mtls_enabled=True,
                observability_enabled=True,
                traffic_management_enabled=True
            )
            
            result = await self.service_mesh_manager.deploy_service_mesh(service_mesh_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy service mesh: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _setup_monitoring(self) -> Dict[str, Any]:
        """Setup monitoring and observability stack"""
        try:
            logger.info("Setting up monitoring and observability")
            
            # Configure comprehensive monitoring for IA Influencer platform
            monitoring_config = MonitoringConfig(
                namespace=self.config.namespace,
                prometheus_enabled=True,
                grafana_enabled=True,
                jaeger_enabled=True,
                alert_manager_enabled=True,
                retention_days=30
            )
            
            result = await self.monitoring_manager.deploy_complete_monitoring_stack(monitoring_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _deploy_load_balancer(self) -> Dict[str, Any]:
        """Deploy load balancer and ingress"""
        try:
            logger.info("Deploying load balancer")
            
            # Configure load balancer for IA Influencer platform
            load_balancer_config = LoadBalancerConfig(
                name="ia-influencer-alb",
                namespace=self.config.namespace,
                ssl_enabled=self.config.enable_ssl,
                domains=self.config.custom_configs.get('domains', []),
                ingress_controller="nginx"
            )
            
            result = await self.load_balancer_manager.deploy_load_balancer(load_balancer_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _setup_auto_scaling(self) -> Dict[str, Any]:
        """Setup auto-scaling for services"""
        try:
            logger.info("Setting up auto-scaling")
            
            # Configure auto-scaling for IA Influencer services
            hpa_specs = [
                HPASpec(
                    name="ia-influencer-api-hpa",
                    target_deployment="ia-influencer-api",
                    min_replicas=self.config.min_replicas,
                    max_replicas=self.config.max_replicas,
                    target_cpu_utilization=70
                ),
                HPASpec(
                    name="ia-influencer-worker-hpa",
                    target_deployment="ia-influencer-worker",
                    min_replicas=self.config.min_replicas,
                    max_replicas=self.config.max_replicas,
                    target_cpu_utilization=80
                )
            ]
            
            results = {}
            for hpa_spec in hpa_specs:
                result = await self.scaling_manager.create_horizontal_pod_autoscaler(
                    hpa_spec, self.config.namespace
                )
                results[hpa_spec.name] = result
            
            return {
                'status': 'success',
                'autoscalers': results
            }
            
        except Exception as e:
            logger.error(f"Failed to setup auto-scaling: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _get_deployment_endpoints(self) -> Dict[str, Any]:
        """Get deployment endpoints and access information"""
        try:
            endpoints = {
                'api_endpoint': f"https://api.ia-influencer.{self.config.region}.com",
                'grafana_dashboard': f"https://grafana.ia-influencer.{self.config.region}.com",
                'prometheus_metrics': f"https://prometheus.ia-influencer.{self.config.region}.com",
                'jaeger_tracing': f"https://jaeger.ia-influencer.{self.config.region}.com",
                'vector_db_api': f"http://vector-db-api-service.{self.config.namespace}:8000",
                'documentation': "https://docs.ia-influencer.com"
            }
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to get deployment endpoints: {e}")
            return {}
    
    async def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure status"""
        try:
            status = {
                'deployment_status': self.deployment_status,
                'config': {
                    'deployment_mode': self.config.deployment_mode.value,
                    'environment': self.config.environment.value,
                    'cloud_provider': self.config.cloud_provider.value,
                    'region': self.config.region,
                    'namespace': self.config.namespace
                },
                'cloud_provider_status': await self.cloud_manager.get_infrastructure_status('ia-influencer'),
                'vector_db_status': await self.vector_db_manager.get_vector_database_status(self.config.namespace),
                'monitoring_status': await self.monitoring_manager.get_monitoring_status(self.config.namespace)
            }
            
            return {
                'status': 'success',
                'infrastructure_status': status
            }
            
        except Exception as e:
            logger.error(f"Failed to get infrastructure status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def destroy_infrastructure(self) -> Dict[str, Any]:
        """Destroy complete infrastructure (use with caution)"""
        try:
            logger.warning("Starting infrastructure destruction - THIS WILL DELETE ALL RESOURCES")
            
            results = {}
            
            # Destroy in reverse order of deployment
            if self.deployment_status.get('auto_scaling'):
                scaling_result = await self.scaling_manager.delete_all_autoscalers(self.config.namespace)
                results['auto_scaling_destruction'] = scaling_result
            
            if self.deployment_status.get('load_balancer'):
                lb_result = await self.load_balancer_manager.delete_load_balancer(
                    f"ia-influencer-alb", self.config.namespace
                )
                results['load_balancer_destruction'] = lb_result
            
            if self.deployment_status.get('monitoring'):
                monitoring_result = await self.monitoring_manager.destroy_monitoring_stack(self.config.namespace)
                results['monitoring_destruction'] = monitoring_result
            
            if self.deployment_status.get('service_mesh'):
                service_mesh_result = await self.service_mesh_manager.destroy_service_mesh(self.config.namespace)
                results['service_mesh_destruction'] = service_mesh_result
            
            if self.deployment_status.get('container_orchestration'):
                container_result = await self.container_orchestrator.destroy_all_services(self.config.namespace)
                results['container_destruction'] = container_result
            
            if self.deployment_status.get('vector_databases'):
                vector_db_result = await self.vector_db_manager.destroy_vector_databases(self.config.namespace)
                results['vector_db_destruction'] = vector_db_result
            
            if self.deployment_status.get('databases'):
                database_result = await self.database_provisioner.destroy_all_databases(self.config.namespace)
                results['database_destruction'] = database_result
            
            if self.deployment_status.get('storage'):
                storage_result = await self.storage_manager.destroy_storage_infrastructure(self.config.namespace)
                results['storage_destruction'] = storage_result
            
            if self.deployment_status.get('networking'):
                networking_result = await self.networking_manager.destroy_vpc_infrastructure("ia-influencer-vpc")
                results['networking_destruction'] = networking_result
            
            if self.deployment_status.get('cloud_provider'):
                cloud_result = await self.cloud_manager.destroy_infrastructure("ia-influencer")
                results['cloud_destruction'] = cloud_result
            
            # Reset deployment status
            self.deployment_status = {key: False for key in self.deployment_status}
            
            logger.warning("Infrastructure destruction completed")
            return {
                'status': 'success',
                'destruction_results': results,
                'message': 'All infrastructure resources have been destroyed'
            }
            
        except Exception as e:
            logger.error(f"Failed to destroy infrastructure: {e}")
            return {'status': 'error', 'message': str(e)}

# Convenience functions for quick deployment
async def deploy_ia_influencer_production_infrastructure(
    cloud_provider: CloudProvider,
    region: str,
    custom_configs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Deploy production-ready IA Influencer infrastructure
    
    Args:
        cloud_provider: Cloud provider to use (AWS, GCP, Azure)
        region: Target region for deployment
        custom_configs: Additional custom configuration options
    
    Returns:
        Dict containing deployment results and status
    """
    config = IAInfluencerInfrastructureConfig(
        deployment_mode=DeploymentMode.PRODUCTION,
        environment=DeploymentEnvironment.CLOUD,
        cloud_provider=cloud_provider,
        region=region,
        namespace="ia-influencer-prod",
        enable_vector_database=True,
        enable_monitoring=True,
        enable_service_mesh=True,
        enable_auto_scaling=True,
        enable_backup=True,
        enable_ssl=True,
        enable_encryption=True,
        enable_audit_logging=True,
        enable_rbac=True,
        min_replicas=3,
        max_replicas=20,
        cpu_limit="4000m",
        memory_limit="8Gi",
        storage_class="fast-ssd",
        backup_retention_days=90,
        custom_configs=custom_configs or {}
    )
    
    manager = IAInfluencerInfrastructureManager(config)
    return await manager.deploy_complete_infrastructure()

async def deploy_ia_influencer_development_infrastructure(
    cloud_provider: CloudProvider,
    region: str
) -> Dict[str, Any]:
    """
    Deploy development IA Influencer infrastructure
    
    Args:
        cloud_provider: Cloud provider to use (AWS, GCP, Azure)
        region: Target region for deployment
    
    Returns:
        Dict containing deployment results and status
    """
    config = IAInfluencerInfrastructureConfig(
        deployment_mode=DeploymentMode.DEVELOPMENT,
        environment=DeploymentEnvironment.CLOUD,
        cloud_provider=cloud_provider,
        region=region,
        namespace="ia-influencer-dev",
        enable_vector_database=True,
        enable_monitoring=True,
        enable_service_mesh=False,
        enable_auto_scaling=False,
        enable_backup=False,
        enable_ssl=False,
        enable_encryption=False,
        enable_audit_logging=False,
        enable_rbac=False,
        min_replicas=1,
        max_replicas=3,
        cpu_limit="1000m",
        memory_limit="2Gi",
        storage_class="standard",
        backup_retention_days=7
    )
    
    manager = IAInfluencerInfrastructureManager(config)
    return await manager.deploy_complete_infrastructure()

# Export main classes and functions
__all__ = [
    'IAInfluencerInfrastructureManager',
    'IAInfluencerInfrastructureConfig', 
    'DeploymentMode',
    'DeploymentEnvironment',
    'deploy_ia_influencer_production_infrastructure',
    'deploy_ia_influencer_development_infrastructure',
    # Re-export infrastructure components
    'CloudProviderManager',
    'ContainerOrchestrator',
    'DatabaseProvisioner',
    'VectorDatabaseManager',
    'MonitoringStackManager',
    'StorageManager',
    'LoadBalancerManager',
    'NetworkingManager',
    'ServiceMeshManager',
    'ResourceScalingManager'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
