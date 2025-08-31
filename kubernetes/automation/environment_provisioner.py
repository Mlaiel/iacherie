"""Environment Provisioner - Deployment Automation

Automated environment provisioning and infrastructure management for the 
IA Influencer Agent platform across multiple cloud environments and 
deployment targets.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path

from ..core.base import BaseComponent
from ..infrastructure.resource_manager import ResourceManager
from ..infrastructure.network_manager import NetworkManager
from ..cloud.provider_factory import CloudProviderFactory
from ..kubernetes.cluster_provisioner import KubernetesProvisioner
from ..database.schema_manager import SchemaManager
from ..storage.volume_manager import VolumeManager


class EnvironmentType(Enum):
    """Environment types supported"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    SANDBOX = "sandbox"


class ProvisioningStatus(Enum):
    """Provisioning status types"""    PENDING = "pending"
    PROVISIONING = "provisioning"
    CONFIGURING = "configuring"
    VALIDATING = "validating"
    READY = "ready"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


@dataclass
class ResourceRequirements:
    """Resource requirements specification"""    cpu: str = "1000m"
    memory: str = "2Gi"
    storage: str = "10Gi"
    gpu: Optional[str] = None
    network_bandwidth: Optional[str] = None
    replicas: int = 1
    min_replicas: int = 1
    max_replicas: int = 10


@dataclass
class DatabaseRequirements:
    """Database requirements specification"""    engine: str = "postgresql"
    version: str = "14"
    size: str = "db.t3.medium"
    storage: str = "100Gi"
    backup_retention: int = 7
    high_availability: bool = False
    encryption: bool = True


@dataclass
class NetworkRequirements:
    """Network requirements specification"""    vpc_cidr: str = "10.0.0.0/16"
    public_subnets: List[str] = field(default_factory=lambda: ["10.0.1.0/24", "10.0.2.0/24"])
    private_subnets: List[str] = field(default_factory=lambda: ["10.0.10.0/24", "10.0.20.0/24"])
    load_balancer: bool = True
    ssl_termination: bool = True
    cdn: bool = False


@dataclass
class EnvironmentSpec:
    """Complete environment specification"""    name: str
    environment_type: EnvironmentType
    cloud_provider: str
    region: str
    resource_requirements: ResourceRequirements
    database_requirements: Optional[DatabaseRequirements] = None
    network_requirements: Optional[NetworkRequirements] = None
    kubernetes_config: Optional[Dict[str, Any]] = None
    security_config: Optional[Dict[str, Any]] = None
    monitoring_config: Optional[Dict[str, Any]] = None
    backup_config: Optional[Dict[str, Any]] = None
    tags: Dict[str, str] = field(default_factory=dict)


class EnvironmentProvisioner(BaseComponent):
    """    Enterprise-grade environment provisioner for multi-cloud deployment.
    
    Handles automated provisioning of infrastructure, networking, databases,
    and Kubernetes clusters across multiple cloud providers.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.resource_manager = ResourceManager(config.get('resource_manager', {}))
        self.network_manager = NetworkManager(config.get('network_manager', {}))
        self.cloud_provider_factory = CloudProviderFactory(config.get('cloud_providers', {}))
        self.k8s_provisioner = KubernetesProvisioner(config.get('kubernetes', {}))
        self.schema_manager = SchemaManager(config.get('database', {}))
        self.volume_manager = VolumeManager(config.get('storage', {}))
        
        # Environment state tracking
        self.provisioned_environments: Dict[str, Dict[str, Any]] = {}
        self.provisioning_tasks: Dict[str, asyncio.Task] = {}
        
        # Template configurations
        self.environment_templates = self._load_environment_templates()
        
        # Validation rules
        self.validation_rules = config.get('validation_rules', {})

    def _load_environment_templates(self) -> Dict[str, EnvironmentSpec]:
        """Load environment templates from configuration"""        templates = {}
        
        # Default templates for each environment type
        templates['development'] = EnvironmentSpec(
            name="development",
            environment_type=EnvironmentType.DEVELOPMENT,
            cloud_provider="aws",
            region="us-west-2",
            resource_requirements=ResourceRequirements(
                cpu="500m",
                memory="1Gi",
                storage="5Gi",
                replicas=1,
                min_replicas=1,
                max_replicas=3
            ),
            database_requirements=DatabaseRequirements(
                engine="postgresql",
                version="14",
                size="db.t3.micro",
                storage="20Gi",
                backup_retention=3,
                high_availability=False
            ),
            network_requirements=NetworkRequirements(
                vpc_cidr="10.1.0.0/16",
                public_subnets=["10.1.1.0/24"],
                private_subnets=["10.1.10.0/24"],
                load_balancer=False,
                ssl_termination=False
            )
        )
        
        templates['staging'] = EnvironmentSpec(
            name="staging",
            environment_type=EnvironmentType.STAGING,
            cloud_provider="aws",
            region="us-west-2",
            resource_requirements=ResourceRequirements(
                cpu="1000m",
                memory="2Gi",
                storage="10Gi",
                replicas=2,
                min_replicas=1,
                max_replicas=5
            ),
            database_requirements=DatabaseRequirements(
                engine="postgresql",
                version="14",
                size="db.t3.small",
                storage="50Gi",
                backup_retention=7,
                high_availability=False
            ),
            network_requirements=NetworkRequirements(
                vpc_cidr="10.2.0.0/16",
                public_subnets=["10.2.1.0/24", "10.2.2.0/24"],
                private_subnets=["10.2.10.0/24", "10.2.20.0/24"],
                load_balancer=True,
                ssl_termination=True
            )
        )
        
        templates['production'] = EnvironmentSpec(
            name="production",
            environment_type=EnvironmentType.PRODUCTION,
            cloud_provider="aws",
            region="us-west-2",
            resource_requirements=ResourceRequirements(
                cpu="2000m",
                memory="4Gi",
                storage="20Gi",
                replicas=3,
                min_replicas=2,
                max_replicas=20
            ),
            database_requirements=DatabaseRequirements(
                engine="postgresql",
                version="14",
                size="db.r5.large",
                storage="200Gi",
                backup_retention=30,
                high_availability=True,
                encryption=True
            ),
            network_requirements=NetworkRequirements(
                vpc_cidr="10.0.0.0/16",
                public_subnets=["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
                private_subnets=["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"],
                load_balancer=True,
                ssl_termination=True,
                cdn=True
            )
        )
        
        return templates

    async def provision_environment(
        self,
        environment_name: str,
        services: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Provision a complete environment with all required infrastructure.
        
        Args:
            environment_name: Name of the environment to provision
            services: List of services to be deployed
            context: Additional provisioning context
            
        Returns:
            Provisioning results and environment details
        """        self.logger.info(f"Starting environment provisioning: {environment_name}")
        
        # Get or create environment specification
        env_spec = await self._get_environment_spec(environment_name, context)
        
        # Initialize provisioning state
        provisioning_state = {
            'environment_name': environment_name,
            'status': ProvisioningStatus.PENDING,
            'start_time': datetime.utcnow(),
            'services': services,
            'context': context,
            'spec': env_spec,
            'resources': {},
            'phases': {},
            'errors': []
        }
        
        self.provisioned_environments[environment_name] = provisioning_state
        
        try:
            # Phase 1: Validate requirements
            provisioning_state['status'] = ProvisioningStatus.PROVISIONING
            await self._validate_provisioning_requirements(env_spec, context)
            provisioning_state['phases']['validation'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 2: Provision network infrastructure
            network_result = await self._provision_network_infrastructure(env_spec, context)
            provisioning_state['resources']['network'] = network_result
            provisioning_state['phases']['network'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 3: Provision compute resources
            compute_result = await self._provision_compute_resources(env_spec, services, context)
            provisioning_state['resources']['compute'] = compute_result
            provisioning_state['phases']['compute'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 4: Provision database resources
            if env_spec.database_requirements:
                database_result = await self._provision_database_resources(env_spec, context)
                provisioning_state['resources']['database'] = database_result
                provisioning_state['phases']['database'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 5: Provision storage resources
            storage_result = await self._provision_storage_resources(env_spec, services, context)
            provisioning_state['resources']['storage'] = storage_result
            provisioning_state['phases']['storage'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 6: Provision Kubernetes cluster
            if env_spec.kubernetes_config:
                k8s_result = await self._provision_kubernetes_cluster(env_spec, context)
                provisioning_state['resources']['kubernetes'] = k8s_result
                provisioning_state['phases']['kubernetes'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 7: Configure monitoring and logging
            monitoring_result = await self._configure_monitoring(env_spec, context)
            provisioning_state['resources']['monitoring'] = monitoring_result
            provisioning_state['phases']['monitoring'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 8: Configure security
            security_result = await self._configure_security(env_spec, context)
            provisioning_state['resources']['security'] = security_result
            provisioning_state['phases']['security'] = {'status': 'completed', 'timestamp': datetime.utcnow()}
            
            # Phase 9: Final validation
            provisioning_state['status'] = ProvisioningStatus.VALIDATING
            validation_result = await self._validate_environment(env_spec, provisioning_state)
            
            if validation_result['valid']:
                provisioning_state['status'] = ProvisioningStatus.READY
                provisioning_state['end_time'] = datetime.utcnow()
                
                self.logger.info(f"Environment provisioning completed: {environment_name}")
                
            else:
                raise Exception(f"Environment validation failed: {validation_result['errors']}")
                
        except Exception as e:
            self.logger.error(f"Environment provisioning failed: {environment_name}", exc_info=True)
            provisioning_state['status'] = ProvisioningStatus.FAILED
            provisioning_state['errors'].append(str(e))
            provisioning_state['end_time'] = datetime.utcnow()
            
            # Attempt cleanup on failure
            await self._cleanup_failed_provisioning(environment_name, provisioning_state)
            
            raise
        
        return provisioning_state

    async def _get_environment_spec(
        self, 
        environment_name: str, 
        context: Dict[str, Any]
    ) -> EnvironmentSpec:
        """Get environment specification from template or context"""        
        # Check if custom spec provided in context
        if 'environment_spec' in context:
            return EnvironmentSpec(**context['environment_spec'])
        
        # Use template based on environment name
        template_name = environment_name.split('-')[0]  # Extract base environment type
        
        if template_name in self.environment_templates:
            template = self.environment_templates[template_name]
            
            # Override template values with context
            if 'resource_overrides' in context:
                for key, value in context['resource_overrides'].items():
                    setattr(template.resource_requirements, key, value)
            
            if 'database_overrides' in context and template.database_requirements:
                for key, value in context['database_overrides'].items():
                    setattr(template.database_requirements, key, value)
            
            # Set environment-specific name
            template.name = environment_name
            
            return template
        
        # Fallback to development template
        template = self.environment_templates['development']
        template.name = environment_name
        return template

    async def _validate_provisioning_requirements(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> None:
        """Validate provisioning requirements and quotas"""        
        # Validate cloud provider credentials
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        await cloud_provider.validate_credentials()
        
        # Check resource quotas
        quota_check = await cloud_provider.check_resource_quotas(env_spec.resource_requirements)
        if not quota_check['sufficient']:
            raise Exception(f"Insufficient resource quotas: {quota_check['missing']}")
        
        # Validate region availability
        region_check = await cloud_provider.validate_region(env_spec.region)
        if not region_check['available']:
            raise Exception(f"Region not available: {env_spec.region}")
        
        # Validate network configuration
        if env_spec.network_requirements:
            network_validation = await self.network_manager.validate_network_config(
                env_spec.network_requirements
            )
            if not network_validation['valid']:
                raise Exception(f"Invalid network configuration: {network_validation['errors']}")

    async def _provision_network_infrastructure(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provision network infrastructure"""        
        if not env_spec.network_requirements:
            return {'message': 'No network requirements specified'}
        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        
        # Create VPC
        vpc_result = await cloud_provider.create_vpc(
            cidr_block=env_spec.network_requirements.vpc_cidr,
            name=f"{env_spec.name}-vpc",
            tags=env_spec.tags
        )
        
        # Create subnets
        public_subnets = []
        for i, subnet_cidr in enumerate(env_spec.network_requirements.public_subnets):
            subnet = await cloud_provider.create_subnet(
                vpc_id=vpc_result['vpc_id'],
                cidr_block=subnet_cidr,
                availability_zone=f"{env_spec.region}{chr(97 + i)}",  # a, b, c...
                public=True,
                name=f"{env_spec.name}-public-subnet-{i + 1}",
                tags=env_spec.tags
            )
            public_subnets.append(subnet)
        
        private_subnets = []
        for i, subnet_cidr in enumerate(env_spec.network_requirements.private_subnets):
            subnet = await cloud_provider.create_subnet(
                vpc_id=vpc_result['vpc_id'],
                cidr_block=subnet_cidr,
                availability_zone=f"{env_spec.region}{chr(97 + i)}",
                public=False,
                name=f"{env_spec.name}-private-subnet-{i + 1}",
                tags=env_spec.tags
            )
            private_subnets.append(subnet)
        
        # Create Internet Gateway
        igw_result = await cloud_provider.create_internet_gateway(
            vpc_id=vpc_result['vpc_id'],
            name=f"{env_spec.name}-igw",
            tags=env_spec.tags
        )
        
        # Create NAT Gateways for private subnets
        nat_gateways = []
        for i, public_subnet in enumerate(public_subnets):
            nat_gw = await cloud_provider.create_nat_gateway(
                subnet_id=public_subnet['subnet_id'],
                name=f"{env_spec.name}-nat-gw-{i + 1}",
                tags=env_spec.tags
            )
            nat_gateways.append(nat_gw)
        
        # Create security groups
        security_groups = await self._create_security_groups(
            cloud_provider, vpc_result['vpc_id'], env_spec
        )
        
        # Create load balancer if required
        load_balancer = None
        if env_spec.network_requirements.load_balancer:
            load_balancer = await cloud_provider.create_load_balancer(
                vpc_id=vpc_result['vpc_id'],
                subnet_ids=[subnet['subnet_id'] for subnet in public_subnets],
                security_group_ids=[sg['group_id'] for sg in security_groups],
                name=f"{env_spec.name}-alb",
                tags=env_spec.tags
            )
        
        return {
            'vpc': vpc_result,
            'public_subnets': public_subnets,
            'private_subnets': private_subnets,
            'internet_gateway': igw_result,
            'nat_gateways': nat_gateways,
            'security_groups': security_groups,
            'load_balancer': load_balancer
        }

    async def _provision_compute_resources(
        self, 
        env_spec: EnvironmentSpec, 
        services: List[str], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provision compute resources for services"""        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        
        # Calculate total resource requirements
        total_cpu = env_spec.resource_requirements.cpu
        total_memory = env_spec.resource_requirements.memory
        total_replicas = env_spec.resource_requirements.replicas * len(services)
        
        # Provision worker nodes
        worker_nodes = await cloud_provider.create_worker_nodes(
            count=max(2, (total_replicas + 2) // 3),  # Ensure adequate capacity
            instance_type=self._determine_instance_type(env_spec.resource_requirements),
            subnet_ids=context.get('private_subnet_ids', []),
            security_group_ids=context.get('security_group_ids', []),
            name_prefix=f"{env_spec.name}-worker",
            tags=env_spec.tags
        )
        
        # Provision auto-scaling groups
        asg_result = await cloud_provider.create_auto_scaling_group(
            min_size=env_spec.resource_requirements.min_replicas,
            max_size=env_spec.resource_requirements.max_replicas,
            desired_capacity=env_spec.resource_requirements.replicas,
            instance_type=self._determine_instance_type(env_spec.resource_requirements),
            subnet_ids=context.get('private_subnet_ids', []),
            name=f"{env_spec.name}-asg",
            tags=env_spec.tags
        )
        
        return {
            'worker_nodes': worker_nodes,
            'auto_scaling_group': asg_result,
            'total_capacity': {
                'cpu': total_cpu,
                'memory': total_memory,
                'replicas': total_replicas
            }
        }

    async def _provision_database_resources(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provision database resources"""        
        if not env_spec.database_requirements:
            return {'message': 'No database requirements specified'}
        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        db_req = env_spec.database_requirements
        
        # Create database subnet group
        db_subnet_group = await cloud_provider.create_db_subnet_group(
            name=f"{env_spec.name}-db-subnet-group",
            subnet_ids=context.get('private_subnet_ids', []),
            description=f"Database subnet group for {env_spec.name}",
            tags=env_spec.tags
        )
        
        # Create database instance
        db_instance = await cloud_provider.create_database_instance(
            db_instance_identifier=f"{env_spec.name}-db",
            engine=db_req.engine,
            engine_version=db_req.version,
            instance_class=db_req.size,
            allocated_storage=int(db_req.storage.replace('Gi', '')),
            master_username="admin",
            master_password=context.get('db_password', self._generate_password()),
            db_subnet_group_name=db_subnet_group['name'],
            vpc_security_group_ids=context.get('db_security_group_ids', []),
            backup_retention_period=db_req.backup_retention,
            multi_az=db_req.high_availability,
            storage_encrypted=db_req.encryption,
            tags=env_spec.tags
        )
        
        # Create read replicas if high availability is required
        read_replicas = []
        if db_req.high_availability:
            for i in range(2):  # Create 2 read replicas
                replica = await cloud_provider.create_read_replica(
                    source_db_identifier=db_instance['db_instance_identifier'],
                    db_instance_identifier=f"{env_spec.name}-db-replica-{i + 1}",
                    instance_class=db_req.size,
                    tags=env_spec.tags
                )
                read_replicas.append(replica)
        
        # Initialize database schemas
        schema_results = await self.schema_manager.initialize_schemas(
            db_instance['endpoint'],
            db_instance['port'],
            "admin",
            context.get('db_password'),
            context.get('required_schemas', ['ia_influencer_agent'])
        )
        
        return {
            'subnet_group': db_subnet_group,
            'primary_instance': db_instance,
            'read_replicas': read_replicas,
            'schema_initialization': schema_results
        }

    async def _provision_storage_resources(
        self, 
        env_spec: EnvironmentSpec, 
        services: List[str], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provision storage resources"""        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        
        # Create persistent volumes for each service
        volumes = {}
        for service in services:
            volume = await cloud_provider.create_persistent_volume(
                size=env_spec.resource_requirements.storage,
                volume_type="gp3",
                availability_zone=f"{env_spec.region}a",
                name=f"{env_spec.name}-{service}-volume",
                tags={**env_spec.tags, 'Service': service}
            )
            volumes[service] = volume
        
        # Create shared storage for content processing
        shared_storage = await cloud_provider.create_file_system(
            performance_mode="generalPurpose",
            throughput_mode="provisioned",
            provisioned_throughput=100,  # MB/s
            name=f"{env_spec.name}-shared-storage",
            tags=env_spec.tags
        )
        
        # Create backup storage
        backup_storage = await cloud_provider.create_s3_bucket(
            bucket_name=f"{env_spec.name}-backup-{datetime.utcnow().strftime('%Y%m%d')}",
            versioning=True,
            encryption=True,
            lifecycle_rules={
                'transition_to_ia': 30,
                'transition_to_glacier': 90,
                'expiration': 365
            },
            tags=env_spec.tags
        )
        
        return {
            'service_volumes': volumes,
            'shared_storage': shared_storage,
            'backup_storage': backup_storage
        }

    async def _provision_kubernetes_cluster(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provision Kubernetes cluster"""        
        if not env_spec.kubernetes_config:
            # Use default Kubernetes configuration
            k8s_config = {
                'version': '1.28',
                'node_groups': [{
                    'name': 'workers',
                    'instance_types': [self._determine_instance_type(env_spec.resource_requirements)],
                    'min_size': env_spec.resource_requirements.min_replicas,
                    'max_size': env_spec.resource_requirements.max_replicas,
                    'desired_size': env_spec.resource_requirements.replicas
                }]
            }
        else:
            k8s_config = env_spec.kubernetes_config
        
        # Provision EKS/GKE/AKS cluster
        cluster_result = await self.k8s_provisioner.provision_cluster(
            cluster_name=f"{env_spec.name}-cluster",
            version=k8s_config.get('version', '1.28'),
            vpc_id=context.get('vpc_id'),
            subnet_ids=context.get('private_subnet_ids', []),
            security_group_ids=context.get('security_group_ids', []),
            node_groups=k8s_config.get('node_groups', []),
            addons=k8s_config.get('addons', ['aws-load-balancer-controller', 'cluster-autoscaler']),
            tags=env_spec.tags
        )
        
        # Configure cluster networking
        networking_result = await self.k8s_provisioner.configure_cluster_networking(
            cluster_name=cluster_result['cluster_name'],
            vpc_cni_config=k8s_config.get('vpc_cni', {}),
            service_mesh=k8s_config.get('service_mesh', 'istio')
        )
        
        # Install essential operators
        operators_result = await self.k8s_provisioner.install_operators(
            cluster_name=cluster_result['cluster_name'],
            operators=['cert-manager', 'external-dns', 'prometheus-operator', 'istio-operator']
        )
        
        return {
            'cluster': cluster_result,
            'networking': networking_result,
            'operators': operators_result
        }

    async def _configure_monitoring(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure monitoring and observability"""        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        
        # Create CloudWatch/Stackdriver log groups
        log_groups = await cloud_provider.create_log_groups([
            f"/aws/lambda/{env_spec.name}",
            f"/aws/ecs/{env_spec.name}",
            f"/aws/apigateway/{env_spec.name}",
            f"/aws/rds/{env_spec.name}"
        ])
        
        # Create monitoring dashboards
        dashboards = await cloud_provider.create_monitoring_dashboards(
            dashboard_configs=[
                {
                    'name': f"{env_spec.name}-infrastructure",
                    'widgets': ['cpu_utilization', 'memory_utilization', 'network_io', 'disk_io']
                },
                {
                    'name': f"{env_spec.name}-applications",
                    'widgets': ['request_rate', 'error_rate', 'response_time', 'active_users']
                },
                {
                    'name': f"{env_spec.name}-ai-services",
                    'widgets': ['model_inference_time', 'gpu_utilization', 'queue_depth', 'processing_rate']
                }
            ]
        )
        
        # Configure alerting
        alerts = await cloud_provider.create_alerts([
            {
                'name': f"{env_spec.name}-high-cpu",
                'metric': 'cpu_utilization',
                'threshold': 80,
                'comparison': 'greater_than',
                'notification_targets': context.get('alert_channels', [])
            },
            {
                'name': f"{env_spec.name}-high-memory",
                'metric': 'memory_utilization',
                'threshold': 90,
                'comparison': 'greater_than',
                'notification_targets': context.get('alert_channels', [])
            },
            {
                'name': f"{env_spec.name}-high-error-rate",
                'metric': 'error_rate',
                'threshold': 5,
                'comparison': 'greater_than',
                'notification_targets': context.get('alert_channels', [])
            }
        ])
        
        return {
            'log_groups': log_groups,
            'dashboards': dashboards,
            'alerts': alerts
        }

    async def _configure_security(
        self, 
        env_spec: EnvironmentSpec, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure security settings"""        
        cloud_provider = self.cloud_provider_factory.get_provider(env_spec.cloud_provider)
        
        # Create IAM roles and policies
        iam_result = await cloud_provider.create_iam_resources(
            roles=[
                {
                    'name': f"{env_spec.name}-execution-role",
                    'trust_policy': 'ecs-tasks.amazonaws.com',
                    'policies': ['AmazonECSTaskExecutionRolePolicy']
                },
                {
                    'name': f"{env_spec.name}-task-role",
                    'trust_policy': 'ecs-tasks.amazonaws.com',
                    'policies': ['CloudWatchLogsFullAccess', 'AmazonS3ReadOnlyAccess']
                }
            ]
        )
        
        # Configure encryption keys
        encryption_keys = await cloud_provider.create_encryption_keys([
            {
                'alias': f"{env_spec.name}-database-key",
                'description': f"Encryption key for {env_spec.name} database",
                'usage': 'ENCRYPT_DECRYPT'
            },
            {
                'alias': f"{env_spec.name}-storage-key",
                'description': f"Encryption key for {env_spec.name} storage",
                'usage': 'ENCRYPT_DECRYPT'
            }
        ])
        
        # Configure secrets management
        secrets = await cloud_provider.create_secrets([
            {
                'name': f"{env_spec.name}/database/password",
                'value': context.get('db_password', self._generate_password()),
                'description': f"Database password for {env_spec.name}"
            },
            {
                'name': f"{env_spec.name}/api/jwt-secret",
                'value': self._generate_jwt_secret(),
                'description': f"JWT secret for {env_spec.name}"
            }
        ])
        
        return {
            'iam_resources': iam_result,
            'encryption_keys': encryption_keys,
            'secrets': secrets
        }

    async def _create_security_groups(
        self, 
        cloud_provider, 
        vpc_id: str, 
        env_spec: EnvironmentSpec
    ) -> List[Dict[str, Any]]:
        """Create security groups for the environment"""        
        security_groups = []
        
        # Web tier security group
        web_sg = await cloud_provider.create_security_group(
            name=f"{env_spec.name}-web-sg",
            description="Security group for web tier",
            vpc_id=vpc_id,
            ingress_rules=[
                {'protocol': 'tcp', 'port': 80, 'source': '0.0.0.0/0'},
                {'protocol': 'tcp', 'port': 443, 'source': '0.0.0.0/0'}
            ],
            egress_rules=[
                {'protocol': 'all', 'port': 'all', 'destination': '0.0.0.0/0'}
            ],
            tags=env_spec.tags
        )
        security_groups.append(web_sg)
        
        # Application tier security group
        app_sg = await cloud_provider.create_security_group(
            name=f"{env_spec.name}-app-sg",
            description="Security group for application tier",
            vpc_id=vpc_id,
            ingress_rules=[
                {'protocol': 'tcp', 'port': 8000, 'source': web_sg['group_id']},
                {'protocol': 'tcp', 'port': 8080, 'source': web_sg['group_id']}
            ],
            egress_rules=[
                {'protocol': 'all', 'port': 'all', 'destination': '0.0.0.0/0'}
            ],
            tags=env_spec.tags
        )
        security_groups.append(app_sg)
        
        # Database tier security group
        db_sg = await cloud_provider.create_security_group(
            name=f"{env_spec.name}-db-sg",
            description="Security group for database tier",
            vpc_id=vpc_id,
            ingress_rules=[
                {'protocol': 'tcp', 'port': 5432, 'source': app_sg['group_id']},
                {'protocol': 'tcp', 'port': 6379, 'source': app_sg['group_id']}
            ],
            egress_rules=[],
            tags=env_spec.tags
        )
        security_groups.append(db_sg)
        
        return security_groups

    async def _validate_environment(
        self, 
        env_spec: EnvironmentSpec, 
        provisioning_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate provisioned environment"""        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate network connectivity
        network_validation = await self.network_manager.validate_network_connectivity(
            provisioning_state['resources'].get('network', {})
        )
        
        if not network_validation['connected']:
            validation_results['valid'] = False
            validation_results['errors'].extend(network_validation['errors'])
        
        # Validate compute resources
        compute_validation = await self._validate_compute_resources(
            provisioning_state['resources'].get('compute', {})
        )
        
        if not compute_validation['healthy']:
            validation_results['valid'] = False
            validation_results['errors'].extend(compute_validation['errors'])
        
        # Validate database connectivity
        if 'database' in provisioning_state['resources']:
            db_validation = await self.schema_manager.validate_database_connectivity(
                provisioning_state['resources']['database']
            )
            
            if not db_validation['connected']:
                validation_results['valid'] = False
                validation_results['errors'].extend(db_validation['errors'])
        
        # Validate Kubernetes cluster
        if 'kubernetes' in provisioning_state['resources']:
            k8s_validation = await self.k8s_provisioner.validate_cluster_health(
                provisioning_state['resources']['kubernetes']['cluster']['cluster_name']
            )
            
            if not k8s_validation['healthy']:
                validation_results['valid'] = False
                validation_results['errors'].extend(k8s_validation['errors'])
        
        return validation_results

    async def _cleanup_failed_provisioning(
        self, 
        environment_name: str, 
        provisioning_state: Dict[str, Any]
    ) -> None:
        """Cleanup resources from failed provisioning"""        
        self.logger.info(f"Cleaning up failed provisioning for environment: {environment_name}")
        
        try:
            # Cleanup in reverse order of creation
            cloud_provider = self.cloud_provider_factory.get_provider(
                provisioning_state['spec'].cloud_provider
            )
            
            # Cleanup Kubernetes cluster
            if 'kubernetes' in provisioning_state['resources']:
                await self.k8s_provisioner.delete_cluster(
                    provisioning_state['resources']['kubernetes']['cluster']['cluster_name']
                )
            
            # Cleanup database resources
            if 'database' in provisioning_state['resources']:
                await cloud_provider.delete_database_resources(
                    provisioning_state['resources']['database']
                )
            
            # Cleanup compute resources
            if 'compute' in provisioning_state['resources']:
                await cloud_provider.delete_compute_resources(
                    provisioning_state['resources']['compute']
                )
            
            # Cleanup network resources
            if 'network' in provisioning_state['resources']:
                await cloud_provider.delete_network_resources(
                    provisioning_state['resources']['network']
                )
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup resources for {environment_name}: {str(e)}")

    def _determine_instance_type(self, resource_req: ResourceRequirements) -> str:
        """Determine appropriate instance type based on resource requirements"""        
        # Parse CPU and memory requirements
        cpu_millicores = int(resource_req.cpu.replace('m', ''))
        memory_gb = int(resource_req.memory.replace('Gi', ''))
        
        # AWS instance type mapping
        if cpu_millicores <= 1000 and memory_gb <= 2:
            return "t3.small"
        elif cpu_millicores <= 2000 and memory_gb <= 4:
            return "t3.medium"
        elif cpu_millicores <= 4000 and memory_gb <= 8:
            return "t3.large"
        elif cpu_millicores <= 8000 and memory_gb <= 16:
            return "m5.xlarge"
        else:
            return "m5.2xlarge"

    def _generate_password(self, length: int = 20) -> str:
        """Generate secure random password"""        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_jwt_secret(self, length: int = 64) -> str:
        """Generate JWT secret"""        import secrets
        return secrets.token_urlsafe(length)

    async def destroy_environment(self, environment_name: str) -> Dict[str, Any]:
        """Destroy a provisioned environment"""        
        if environment_name not in self.provisioned_environments:
            raise ValueError(f"Environment not found: {environment_name}")
        
        provisioning_state = self.provisioned_environments[environment_name]
        provisioning_state['status'] = ProvisioningStatus.DESTROYING
        
        try:
            await self._cleanup_failed_provisioning(environment_name, provisioning_state)
            
            provisioning_state['status'] = ProvisioningStatus.DESTROYED
            provisioning_state['destroy_time'] = datetime.utcnow()
            
            # Remove from active environments
            del self.provisioned_environments[environment_name]
            
            return {'success': True, 'message': f'Environment {environment_name} destroyed successfully'}
            
        except Exception as e:
            provisioning_state['status'] = ProvisioningStatus.FAILED
            provisioning_state['destroy_error'] = str(e)
            raise

    async def get_environment_status(self, environment_name: str) -> Optional[Dict[str, Any]]:
        """Get environment provisioning status"""        return self.provisioned_environments.get(environment_name)

    async def list_environments(self) -> List[Dict[str, Any]]:
        """List all provisioned environments"""        return [
            {
                'name': name,
                'status': state['status'].value,
                'start_time': state.get('start_time'),
                'environment_type': state['spec'].environment_type.value,
                'cloud_provider': state['spec'].cloud_provider,
                'region': state['spec'].region
            }
            for name, state in self.provisioned_environments.items()
        ]
