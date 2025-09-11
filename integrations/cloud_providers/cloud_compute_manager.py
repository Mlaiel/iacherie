"""Multi-Cloud Compute Manager
==============================

Enterprise-grade multi-cloud compute management system supporting
AWS EC2, Azure VMs, GCP Compute Engine, DigitalOcean Droplets, and more.

This module provides unified compute resource management, intelligent
workload placement, auto-scaling, and cost optimization across multiple
cloud providers for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import math

import boto3
import httpx
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from google.cloud import compute_v1
from botocore.exceptions import ClientError


class CloudProvider(Enum):
    """Supported cloud providers for compute resources."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    HEROKU = "heroku"
    VERCEL = "vercel"


class InstanceState(Enum):
    """Instance states across providers."""
    PENDING = "pending"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    ERROR = "error"


class InstanceType(Enum):
    """Standardized instance types."""
    MICRO = "micro"      # 1 vCPU, 1GB RAM
    SMALL = "small"      # 1 vCPU, 2GB RAM
    MEDIUM = "medium"    # 2 vCPU, 4GB RAM
    LARGE = "large"      # 4 vCPU, 8GB RAM
    XLARGE = "xlarge"    # 8 vCPU, 16GB RAM
    XXLARGE = "xxlarge"  # 16 vCPU, 32GB RAM


class WorkloadType(Enum):
    """Workload types for intelligent placement."""
    WEB_SERVER = "web_server"
    API_SERVER = "api_server"
    DATABASE = "database"
    CACHE = "cache"
    AI_INFERENCE = "ai_inference"
    AI_TRAINING = "ai_training"
    BATCH_PROCESSING = "batch_processing"
    STREAM_PROCESSING = "stream_processing"
    CDN_EDGE = "cdn_edge"
    MONITORING = "monitoring"


@dataclass
class ComputeInstance:
    """Unified compute instance representation."""
    id: str
    name: str
    provider: CloudProvider
    instance_type: InstanceType
    state: InstanceState
    region: str
    zone: Optional[str] = None
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    vcpus: int = 1
    memory_gb: int = 1
    storage_gb: int = 10
    cost_per_hour: Decimal = field(default_factory=lambda: Decimal('0.00'))
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    workload_type: Optional[WorkloadType] = None
    auto_scaling_group: Optional[str] = None


@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration."""
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    enable_predictive_scaling: bool = True


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    name: str
    provider: CloudProvider
    algorithm: str = "round_robin"  # round_robin, least_connections, ip_hash
    health_check_path: str = "/health"
    health_check_interval: int = 30
    enable_ssl_termination: bool = True
    ssl_certificate_arn: Optional[str] = None


class MultiCloudComputeManager:
    """Enterprise multi-cloud compute resource manager."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize multi-cloud compute manager.
        
        Args:
            config: Configuration dict with provider credentials and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Provider clients
        self.aws_ec2 = None
        self.azure_compute = None
        self.gcp_compute = None
        self.digitalocean_client = None
        
        # Internal state
        self.instances: Dict[str, ComputeInstance] = {}
        self.auto_scaling_groups: Dict[str, AutoScalingConfig] = {}
        self.load_balancers: Dict[str, LoadBalancerConfig] = {}
        
        # Performance metrics
        self.metrics = {
            'total_instances': 0,
            'total_vcpus': 0,
            'total_memory_gb': 0,
            'total_cost_per_hour': Decimal('0.00'),
            'instances_by_provider': {},
            'instances_by_region': {},
            'instances_by_workload': {}
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS EC2
            if 'aws' in self.config:
                aws_config = self.config['aws']
                self.aws_ec2 = boto3.client(
                    'ec2',
                    aws_access_key_id=aws_config.get('access_key_id'),
                    aws_secret_access_key=aws_config.get('secret_access_key'),
                    region_name=aws_config.get('region', 'us-east-1')
                )
                self.logger.info("AWS EC2 client initialized")
            
            # Azure Compute
            if 'azure' in self.config:
                azure_config = self.config['azure']
                credential = DefaultAzureCredential()
                self.azure_compute = ComputeManagementClient(
                    credential,
                    azure_config.get('subscription_id')
                )
                self.logger.info("Azure Compute client initialized")
            
            # GCP Compute Engine
            if 'gcp' in self.config:
                gcp_config = self.config['gcp']
                if 'credentials_path' in gcp_config:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_config['credentials_path']
                self.gcp_compute = compute_v1.InstancesClient()
                self.logger.info("GCP Compute Engine client initialized")
            
            # DigitalOcean
            if 'digitalocean' in self.config:
                do_config = self.config['digitalocean']
                self.digitalocean_client = httpx.AsyncClient(
                    headers={'Authorization': f'Bearer {do_config.get("api_token")}'},
                    base_url='https://api.digitalocean.com/v2'
                )
                self.logger.info("DigitalOcean client initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing cloud providers: {e}")
            raise
    
    async def list_instances(self, provider: Optional[CloudProvider] = None) -> List[ComputeInstance]:
        """List compute instances across providers.
        
        Args:
            provider: Optional specific provider to query
            
        Returns:
            List of compute instances
        """
        instances = []
        
        try:
            if provider is None or provider == CloudProvider.AWS:
                instances.extend(await self._list_aws_instances())
            
            if provider is None or provider == CloudProvider.AZURE:
                instances.extend(await self._list_azure_instances())
            
            if provider is None or provider == CloudProvider.GCP:
                instances.extend(await self._list_gcp_instances())
            
            if provider is None or provider == CloudProvider.DIGITALOCEAN:
                instances.extend(await self._list_digitalocean_instances())
            
            # Update internal state
            for instance in instances:
                self.instances[instance.id] = instance
            
            self._update_metrics()
            return instances
            
        except Exception as e:
            self.logger.error(f"Error listing instances: {e}")
            raise
    
    async def _list_aws_instances(self) -> List[ComputeInstance]:
        """List AWS EC2 instances."""
        if not self.aws_ec2:
            return []
        
        instances = []
        try:
            response = self.aws_ec2.describe_instances()
            
            for reservation in response['Reservations']:
                for instance_data in reservation['Instances']:
                    instance = ComputeInstance(
                        id=instance_data['InstanceId'],
                        name=self._get_instance_name(instance_data.get('Tags', [])),
                        provider=CloudProvider.AWS,
                        instance_type=self._map_aws_instance_type(instance_data['InstanceType']),
                        state=self._map_aws_instance_state(instance_data['State']['Name']),
                        region=instance_data['Placement']['AvailabilityZone'][:-1],
                        zone=instance_data['Placement']['AvailabilityZone'],
                        public_ip=instance_data.get('PublicIpAddress'),
                        private_ip=instance_data.get('PrivateIpAddress'),
                        created_at=instance_data['LaunchTime'],
                        tags=self._format_aws_tags(instance_data.get('Tags', []))
                    )
                    
                    # Get instance specs
                    instance.vcpus, instance.memory_gb = self._get_aws_instance_specs(
                        instance_data['InstanceType']
                    )
                    
                    # Calculate cost
                    instance.cost_per_hour = self._calculate_aws_cost(
                        instance_data['InstanceType'],
                        instance.region
                    )
                    
                    instances.append(instance)
                    
        except ClientError as e:
            self.logger.error(f"AWS EC2 API error: {e}")
        except Exception as e:
            self.logger.error(f"Error listing AWS instances: {e}")
        
        return instances
    
    async def _list_azure_instances(self) -> List[ComputeInstance]:
        """List Azure virtual machines."""
        if not self.azure_compute:
            return []
        
        instances = []
        try:
            resource_groups = self.azure_compute.resource_groups.list()
            
            for rg in resource_groups:
                vms = self.azure_compute.virtual_machines.list(rg.name)
                
                for vm in vms:
                    instance = ComputeInstance(
                        id=vm.name,
                        name=vm.name,
                        provider=CloudProvider.AZURE,
                        instance_type=self._map_azure_instance_type(vm.hardware_profile.vm_size),
                        state=self._map_azure_instance_state(vm.provisioning_state),
                        region=vm.location,
                        tags=vm.tags or {}
                    )
                    
                    # Get instance specs
                    instance.vcpus, instance.memory_gb = self._get_azure_instance_specs(
                        vm.hardware_profile.vm_size
                    )
                    
                    # Calculate cost
                    instance.cost_per_hour = self._calculate_azure_cost(
                        vm.hardware_profile.vm_size,
                        vm.location
                    )
                    
                    instances.append(instance)
                    
        except Exception as e:
            self.logger.error(f"Error listing Azure instances: {e}")
        
        return instances
    
    async def _list_gcp_instances(self) -> List[ComputeInstance]:
        """List GCP Compute Engine instances."""
        if not self.gcp_compute:
            return []
        
        instances = []
        try:
            project = self.config['gcp']['project_id']
            zones = self.config['gcp'].get('zones', ['us-central1-a'])
            
            for zone in zones:
                request = compute_v1.ListInstancesRequest(
                    project=project,
                    zone=zone
                )
                
                page_result = self.gcp_compute.list(request=request)
                
                for instance_data in page_result:
                    instance = ComputeInstance(
                        id=str(instance_data.id),
                        name=instance_data.name,
                        provider=CloudProvider.GCP,
                        instance_type=self._map_gcp_instance_type(instance_data.machine_type),
                        state=self._map_gcp_instance_state(instance_data.status),
                        region=zone[:-2],  # Remove zone suffix
                        zone=zone,
                        created_at=datetime.fromisoformat(
                            instance_data.creation_timestamp.replace('Z', '+00:00')
                        )
                    )
                    
                    # Get network interfaces
                    if instance_data.network_interfaces:
                        network_interface = instance_data.network_interfaces[0]
                        instance.private_ip = network_interface.network_i_p
                        
                        if network_interface.access_configs:
                            instance.public_ip = network_interface.access_configs[0].nat_i_p
                    
                    # Get instance specs
                    instance.vcpus, instance.memory_gb = self._get_gcp_instance_specs(
                        instance_data.machine_type
                    )
                    
                    # Calculate cost
                    instance.cost_per_hour = self._calculate_gcp_cost(
                        instance_data.machine_type,
                        zone
                    )
                    
                    instances.append(instance)
                    
        except Exception as e:
            self.logger.error(f"Error listing GCP instances: {e}")
        
        return instances
    
    async def _list_digitalocean_instances(self) -> List[ComputeInstance]:
        """List DigitalOcean droplets."""
        if not self.digitalocean_client:
            return []
        
        instances = []
        try:
            response = await self.digitalocean_client.get('/droplets')
            response.raise_for_status()
            data = response.json()
            
            for droplet in data.get('droplets', []):
                instance = ComputeInstance(
                    id=str(droplet['id']),
                    name=droplet['name'],
                    provider=CloudProvider.DIGITALOCEAN,
                    instance_type=self._map_do_instance_type(droplet['size']['slug']),
                    state=self._map_do_instance_state(droplet['status']),
                    region=droplet['region']['slug'],
                    created_at=datetime.fromisoformat(
                        droplet['created_at'].replace('Z', '+00:00')
                    ),
                    tags=droplet.get('tags', [])
                )
                
                # Get network info
                if droplet['networks']['v4']:
                    for network in droplet['networks']['v4']:
                        if network['type'] == 'public':
                            instance.public_ip = network['ip_address']
                        elif network['type'] == 'private':
                            instance.private_ip = network['ip_address']
                
                # Get instance specs
                instance.vcpus = droplet['vcpus']
                instance.memory_gb = droplet['memory'] // 1024  # Convert MB to GB
                instance.storage_gb = droplet['disk']
                
                # Calculate cost
                instance.cost_per_hour = Decimal(str(droplet['size']['price_hourly']))
                
                instances.append(instance)
                
        except Exception as e:
            self.logger.error(f"Error listing DigitalOcean instances: {e}")
        
        return instances
    
    async def create_instance(
        self,
        name: str,
        instance_type: InstanceType,
        provider: CloudProvider,
        region: str,
        workload_type: WorkloadType,
        **kwargs
    ) -> ComputeInstance:
        """Create a new compute instance.
        
        Args:
            name: Instance name
            instance_type: Standardized instance type
            provider: Cloud provider
            region: Target region
            workload_type: Workload type for optimization
            **kwargs: Provider-specific options
            
        Returns:
            Created compute instance
        """
        try:
            if provider == CloudProvider.AWS:
                return await self._create_aws_instance(
                    name, instance_type, region, workload_type, **kwargs
                )
            elif provider == CloudProvider.AZURE:
                return await self._create_azure_instance(
                    name, instance_type, region, workload_type, **kwargs
                )
            elif provider == CloudProvider.GCP:
                return await self._create_gcp_instance(
                    name, instance_type, region, workload_type, **kwargs
                )
            elif provider == CloudProvider.DIGITALOCEAN:
                return await self._create_digitalocean_instance(
                    name, instance_type, region, workload_type, **kwargs
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Error creating instance: {e}")
            raise
    
    async def _create_aws_instance(
        self,
        name: str,
        instance_type: InstanceType,
        region: str,
        workload_type: WorkloadType,
        **kwargs
    ) -> ComputeInstance:
        """Create AWS EC2 instance."""
        if not self.aws_ec2:
            raise ValueError("AWS EC2 client not initialized")
        
        # Map to AWS instance type
        aws_instance_type = self._map_to_aws_instance_type(instance_type)
        
        # Get optimized AMI for workload
        ami_id = self._get_optimized_ami(workload_type, region)
        
        # Security group
        security_group_id = kwargs.get('security_group_id', 'default')
        
        # Subnet
        subnet_id = kwargs.get('subnet_id')
        
        # User data script
        user_data = self._generate_user_data_script(workload_type)
        
        try:
            response = self.aws_ec2.run_instances(
                ImageId=ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType=aws_instance_type,
                SecurityGroupIds=[security_group_id] if security_group_id != 'default' else [],
                SubnetId=subnet_id,
                UserData=user_data,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': name},
                        {'Key': 'WorkloadType', 'Value': workload_type.value},
                        {'Key': 'CreatedBy', 'Value': 'AinfluePlatform'},
                        {'Key': 'Environment', 'Value': kwargs.get('environment', 'production')}
                    ]
                }],
                **kwargs.get('aws_specific', {})
            )
            
            instance_data = response['Instances'][0]
            
            instance = ComputeInstance(
                id=instance_data['InstanceId'],
                name=name,
                provider=CloudProvider.AWS,
                instance_type=instance_type,
                state=InstanceState.PENDING,
                region=region,
                zone=instance_data['Placement']['AvailabilityZone'],
                workload_type=workload_type,
                tags={
                    'Name': name,
                    'WorkloadType': workload_type.value,
                    'CreatedBy': 'AinfluePlatform'
                }
            )
            
            # Get instance specs
            instance.vcpus, instance.memory_gb = self._get_aws_instance_specs(aws_instance_type)
            instance.cost_per_hour = self._calculate_aws_cost(aws_instance_type, region)
            
            self.instances[instance.id] = instance
            self.logger.info(f"Created AWS instance {instance.id} ({name})")
            
            return instance
            
        except ClientError as e:
            self.logger.error(f"AWS instance creation failed: {e}")
            raise
    
    async def intelligent_workload_placement(
        self,
        workload_type: WorkloadType,
        requirements: Dict[str, Any]
    ) -> Tuple[CloudProvider, str, InstanceType]:
        """Intelligently place workload based on requirements and costs.
        
        Args:
            workload_type: Type of workload
            requirements: Resource and location requirements
            
        Returns:
            Tuple of (provider, region, instance_type)
        """
        try:
            # Analyze requirements
            min_vcpus = requirements.get('min_vcpus', 1)
            min_memory_gb = requirements.get('min_memory_gb', 1)
            preferred_regions = requirements.get('preferred_regions', [])
            max_cost_per_hour = requirements.get('max_cost_per_hour', float('inf'))
            latency_requirements = requirements.get('latency_requirements', {})
            
            # Get pricing data for all providers
            placement_options = []
            
            for provider in CloudProvider:
                if provider.value not in self.config:
                    continue
                
                regions = self._get_provider_regions(provider)
                
                for region in regions:
                    if preferred_regions and region not in preferred_regions:
                        continue
                    
                    for instance_type in InstanceType:
                        vcpus, memory_gb = self._get_instance_specs(provider, instance_type)
                        
                        if vcpus < min_vcpus or memory_gb < min_memory_gb:
                            continue
                        
                        cost = self._calculate_cost(provider, instance_type, region)
                        
                        if cost > max_cost_per_hour:
                            continue
                        
                        # Calculate score based on workload optimization
                        score = self._calculate_placement_score(
                            provider, region, instance_type, workload_type,
                            requirements, cost
                        )
                        
                        placement_options.append({
                            'provider': provider,
                            'region': region,
                            'instance_type': instance_type,
                            'cost': cost,
                            'score': score,
                            'vcpus': vcpus,
                            'memory_gb': memory_gb
                        })
            
            # Sort by score (higher is better)
            placement_options.sort(key=lambda x: x['score'], reverse=True)
            
            if not placement_options:
                raise ValueError("No suitable placement options found")
            
            best_option = placement_options[0]
            
            self.logger.info(
                f"Intelligent placement selected: {best_option['provider'].value} "
                f"{best_option['region']} {best_option['instance_type'].value} "
                f"(score: {best_option['score']:.2f}, cost: ${best_option['cost']:.4f}/hour)"
            )
            
            return (
                best_option['provider'],
                best_option['region'],
                best_option['instance_type']
            )
            
        except Exception as e:
            self.logger.error(f"Error in intelligent placement: {e}")
            raise
    
    async def setup_auto_scaling(
        self,
        group_name: str,
        config: AutoScalingConfig,
        template_instance_id: str
    ) -> str:
        """Setup auto-scaling group for instances.
        
        Args:
            group_name: Auto-scaling group name
            config: Auto-scaling configuration
            template_instance_id: Template instance for scaling
            
        Returns:
            Auto-scaling group ID
        """
        try:
            template_instance = self.instances.get(template_instance_id)
            if not template_instance:
                raise ValueError(f"Template instance {template_instance_id} not found")
            
            # Create auto-scaling group based on provider
            if template_instance.provider == CloudProvider.AWS:
                asg_id = await self._setup_aws_auto_scaling(
                    group_name, config, template_instance
                )
            elif template_instance.provider == CloudProvider.AZURE:
                asg_id = await self._setup_azure_auto_scaling(
                    group_name, config, template_instance
                )
            elif template_instance.provider == CloudProvider.GCP:
                asg_id = await self._setup_gcp_auto_scaling(
                    group_name, config, template_instance
                )
            else:
                raise ValueError(f"Auto-scaling not supported for {template_instance.provider}")
            
            self.auto_scaling_groups[asg_id] = config
            
            self.logger.info(f"Auto-scaling group {asg_id} created successfully")
            return asg_id
            
        except Exception as e:
            self.logger.error(f"Error setting up auto-scaling: {e}")
            raise
    
    async def optimize_costs(self) -> Dict[str, Any]:
        """Optimize compute costs across all providers.
        
        Returns:
            Cost optimization report
        """
        try:
            current_instances = await self.list_instances()
            
            optimization_report = {
                'current_cost_per_hour': Decimal('0.00'),
                'optimized_cost_per_hour': Decimal('0.00'),
                'potential_savings_per_hour': Decimal('0.00'),
                'potential_savings_per_month': Decimal('0.00'),
                'recommendations': []
            }
            
            for instance in current_instances:
                optimization_report['current_cost_per_hour'] += instance.cost_per_hour
                
                # Analyze instance utilization (would need monitoring data)
                recommendations = await self._analyze_instance_optimization(instance)
                optimization_report['recommendations'].extend(recommendations)
            
            # Calculate potential savings
            for rec in optimization_report['recommendations']:
                if rec['type'] == 'rightsize':
                    savings = rec['current_cost'] - rec['recommended_cost']
                    optimization_report['potential_savings_per_hour'] += savings
                elif rec['type'] == 'terminate':
                    optimization_report['potential_savings_per_hour'] += rec['current_cost']
            
            optimization_report['optimized_cost_per_hour'] = (
                optimization_report['current_cost_per_hour'] -
                optimization_report['potential_savings_per_hour']
            )
            
            optimization_report['potential_savings_per_month'] = (
                optimization_report['potential_savings_per_hour'] * 24 * 30
            )
            
            self.logger.info(
                f"Cost optimization analysis complete. "
                f"Potential savings: ${optimization_report['potential_savings_per_month']}/month"
            )
            
            return optimization_report
            
        except Exception as e:
            self.logger.error(f"Error optimizing costs: {e}")
            raise
    
    def _calculate_placement_score(
        self,
        provider: CloudProvider,
        region: str,
        instance_type: InstanceType,
        workload_type: WorkloadType,
        requirements: Dict[str, Any],
        cost: float
    ) -> float:
        """Calculate placement score for intelligent workload placement."""
        score = 100.0  # Base score
        
        # Cost factor (lower cost = higher score)
        max_cost = requirements.get('max_cost_per_hour', 1.0)
        cost_factor = (max_cost - cost) / max_cost * 20
        score += cost_factor
        
        # Provider optimization for workload type
        provider_scores = {
            WorkloadType.AI_TRAINING: {
                CloudProvider.AWS: 15,      # Strong GPU instances
                CloudProvider.GCP: 20,      # TPUs and optimized ML
                CloudProvider.AZURE: 10,    # Good but limited
                CloudProvider.DIGITALOCEAN: 0  # Limited GPU support
            },
            WorkloadType.AI_INFERENCE: {
                CloudProvider.AWS: 15,
                CloudProvider.GCP: 18,
                CloudProvider.AZURE: 12,
                CloudProvider.DIGITALOCEAN: 5
            },
            WorkloadType.WEB_SERVER: {
                CloudProvider.AWS: 12,
                CloudProvider.GCP: 10,
                CloudProvider.AZURE: 10,
                CloudProvider.DIGITALOCEAN: 15  # Cost-effective
            },
            WorkloadType.DATABASE: {
                CloudProvider.AWS: 18,      # RDS optimizations
                CloudProvider.GCP: 15,      # Cloud SQL
                CloudProvider.AZURE: 15,    # Azure SQL
                CloudProvider.DIGITALOCEAN: 8
            }
        }
        
        if workload_type in provider_scores:
            score += provider_scores[workload_type].get(provider, 0)
        
        # Region preference
        preferred_regions = requirements.get('preferred_regions', [])
        if preferred_regions and region in preferred_regions:
            score += 10
        
        # Latency requirements
        latency_requirements = requirements.get('latency_requirements', {})
        if latency_requirements:
            region_latency = self._get_estimated_latency(provider, region, latency_requirements)
            if region_latency <= latency_requirements.get('max_latency_ms', 100):
                score += 15
        
        return score
    
    def _get_estimated_latency(
        self,
        provider: CloudProvider,
        region: str,
        latency_requirements: Dict[str, Any]
    ) -> float:
        """Estimate latency for provider/region combination."""
        # Simplified latency estimation based on common patterns
        # In production, this would use real latency measurements
        
        target_location = latency_requirements.get('target_location', 'us-east')
        
        latency_map = {
            ('aws', 'us-east-1', 'us-east'): 10,
            ('aws', 'us-west-2', 'us-west'): 10,
            ('aws', 'eu-west-1', 'europe'): 15,
            ('gcp', 'us-central1', 'us-central'): 12,
            ('azure', 'eastus', 'us-east'): 15,
            ('digitalocean', 'nyc3', 'us-east'): 20,
        }
        
        key = (provider.value, region, target_location)
        return latency_map.get(key, 50)  # Default higher latency
    
    def _update_metrics(self) -> None:
        """Update internal metrics."""
        self.metrics = {
            'total_instances': len(self.instances),
            'total_vcpus': sum(i.vcpus for i in self.instances.values()),
            'total_memory_gb': sum(i.memory_gb for i in self.instances.values()),
            'total_cost_per_hour': sum(i.cost_per_hour for i in self.instances.values()),
            'instances_by_provider': {},
            'instances_by_region': {},
            'instances_by_workload': {}
        }
        
        for instance in self.instances.values():
            # By provider
            provider = instance.provider.value
            if provider not in self.metrics['instances_by_provider']:
                self.metrics['instances_by_provider'][provider] = 0
            self.metrics['instances_by_provider'][provider] += 1
            
            # By region
            region = instance.region
            if region not in self.metrics['instances_by_region']:
                self.metrics['instances_by_region'][region] = 0
            self.metrics['instances_by_region'][region] += 1
            
            # By workload
            if instance.workload_type:
                workload = instance.workload_type.value
                if workload not in self.metrics['instances_by_workload']:
                    self.metrics['instances_by_workload'][workload] = 0
                self.metrics['instances_by_workload'][workload] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current compute metrics."""
        return self.metrics.copy()
    
    # Helper methods for provider-specific mappings and calculations
    def _map_aws_instance_type(self, aws_type: str) -> InstanceType:
        """Map AWS instance type to standardized type."""
        aws_mapping = {
            't2.nano': InstanceType.MICRO,
            't2.micro': InstanceType.MICRO,
            't2.small': InstanceType.SMALL,
            't2.medium': InstanceType.MEDIUM,
            't2.large': InstanceType.LARGE,
            't2.xlarge': InstanceType.XLARGE,
            't2.2xlarge': InstanceType.XXLARGE,
            'm5.large': InstanceType.LARGE,
            'm5.xlarge': InstanceType.XLARGE,
            'm5.2xlarge': InstanceType.XXLARGE,
            'c5.large': InstanceType.LARGE,
            'c5.xlarge': InstanceType.XLARGE,
        }
        return aws_mapping.get(aws_type, InstanceType.MEDIUM)
    
    def _map_to_aws_instance_type(self, instance_type: InstanceType) -> str:
        """Map standardized type to AWS instance type."""
        type_mapping = {
            InstanceType.MICRO: 't3.micro',
            InstanceType.SMALL: 't3.small',
            InstanceType.MEDIUM: 't3.medium',
            InstanceType.LARGE: 't3.large',
            InstanceType.XLARGE: 't3.xlarge',
            InstanceType.XXLARGE: 't3.2xlarge',
        }
        return type_mapping.get(instance_type, 't3.medium')
    
    def _get_aws_instance_specs(self, instance_type: str) -> Tuple[int, int]:
        """Get vCPUs and memory for AWS instance type."""
        specs = {
            't3.micro': (2, 1),
            't3.small': (2, 2),
            't3.medium': (2, 4),
            't3.large': (2, 8),
            't3.xlarge': (4, 16),
            't3.2xlarge': (8, 32),
            'm5.large': (2, 8),
            'm5.xlarge': (4, 16),
            'c5.large': (2, 4),
        }
        return specs.get(instance_type, (2, 4))
    
    def _calculate_aws_cost(self, instance_type: str, region: str) -> Decimal:
        """Calculate AWS instance cost per hour."""
        # Simplified pricing - would use AWS Pricing API in production
        base_costs = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            't3.xlarge': 0.1664,
            't3.2xlarge': 0.3328,
        }
        
        # Regional multipliers
        region_multipliers = {
            'us-east-1': 1.0,
            'us-west-2': 1.05,
            'eu-west-1': 1.1,
            'ap-southeast-1': 1.15,
        }
        
        base_cost = base_costs.get(instance_type, 0.05)
        multiplier = region_multipliers.get(region, 1.0)
        
        return Decimal(str(base_cost * multiplier))
    
    async def close(self) -> None:
        """Close all client connections."""
        try:
            if self.digitalocean_client:
                await self.digitalocean_client.aclose()
            
            self.logger.info("Multi-cloud compute manager closed")
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")


# Example usage
async def example_usage():
    """Example usage of MultiCloudComputeManager."""
    
    config = {
        'aws': {
            'access_key_id': 'your-aws-key',
            'secret_access_key': 'your-aws-secret',
            'region': 'us-east-1'
        },
        'gcp': {
            'project_id': 'your-gcp-project',
            'credentials_path': '/path/to/credentials.json',
            'zones': ['us-central1-a', 'us-central1-b']
        },
        'digitalocean': {
            'api_token': 'your-do-token'
        }
    }
    
    manager = MultiCloudComputeManager(config)
    
    try:
        # List all instances
        instances = await manager.list_instances()
        print(f"Found {len(instances)} instances")
        
        # Intelligent workload placement
        placement = await manager.intelligent_workload_placement(
            WorkloadType.AI_INFERENCE,
            {
                'min_vcpus': 4,
                'min_memory_gb': 8,
                'max_cost_per_hour': 0.50,
                'preferred_regions': ['us-east-1', 'us-west-2']
            }
        )
        
        provider, region, instance_type = placement
        print(f"Recommended placement: {provider.value} {region} {instance_type.value}")
        
        # Create optimized instance
        instance = await manager.create_instance(
            name="ainflue-ai-inference-001",
            instance_type=instance_type,
            provider=provider,
            region=region,
            workload_type=WorkloadType.AI_INFERENCE,
            environment="production"
        )
        
        print(f"Created instance: {instance.id}")
        
        # Cost optimization analysis
        optimization = await manager.optimize_costs()
        print(f"Potential monthly savings: ${optimization['potential_savings_per_month']}")
        
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(example_usage())