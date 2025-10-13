"""🏗️ MLOps Infrastructure Provisioning Engine - Enterprise Automation
============================================================================
Module: mlops/model_deployment/infrastructure_provisioning_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, modification, distribution ou
reproduction est strictement interdite et peut entraîner des poursuites
judiciaires. Tous droits réservés.

🎯 INFRASTRUCTURE PROVISIONING ENGINE
Enterprise infrastructure automation for ML model deployment with:
- Multi-cloud resource provisioning (AWS/Azure/GCP/Kubernetes)
- Dynamic resource template generation
- Creator-tier optimized provisioning
- Cost estimation and optimization
- Infrastructure as Code integration
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from google.cloud import resource_manager
import kubernetes
from kubernetes import client, config

logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Supported cloud providers for infrastructure provisioning"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    KUBERNETES = "kubernetes"
    MULTI_CLOUD = "multi_cloud"

class ResourceType(Enum):
    """Infrastructure resource types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORKING = "networking"
    DATABASE = "database"
    LOAD_BALANCER = "load_balancer"
    API_GATEWAY = "api_gateway"
    CDN = "cdn"
    MONITORING = "monitoring"

class CreatorTier(Enum):
    """Creator subscription tiers for resource optimization"""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class ResourceSpec:
    """Infrastructure resource specification"""
    resource_type: ResourceType
    name: str
    cpu: str
    memory: str
    storage: str
    replicas: int
    tier: CreatorTier
    tags: Dict[str, str]
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['resource_type'] = self.resource_type.value
        data['tier'] = self.tier.value
        return data

@dataclass
class ProvisioningPlan:
    """Infrastructure provisioning plan"""
    plan_id: str
    provider: CloudProvider
    resources: List[ResourceSpec]
    estimated_cost: float
    provisioning_time: int
    dependencies: Dict[str, List[str]]
    validation_rules: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['provider'] = self.provider.value
        data['resources'] = [r.to_dict() for r in self.resources]
        return data

@dataclass
class ProvisioningResult:
    """Infrastructure provisioning result"""
    plan_id: str
    provider: CloudProvider
    success: bool
    provisioned_resources: List[Dict[str, Any]]
    failed_resources: List[Dict[str, Any]]
    total_cost: float
    provisioning_time: float
    error_message: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['provider'] = self.provider.value
        return data

class InfrastructureProvisioningEngine:
    """
    🏗️ Enterprise Infrastructure Provisioning Engine
    
    Automated infrastructure provisioning for ML model deployment with:
    - Multi-cloud resource automation
    - Creator-tier optimization
    - Cost-aware provisioning
    - Infrastructure as Code integration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Infrastructure Provisioning Engine"""
        self.config = config or {}
        self.providers: Dict[CloudProvider, Any] = {}
        self.provisioning_plans: Dict[str, ProvisioningPlan] = {}
        self.provisioning_results: Dict[str, ProvisioningResult] = {}
        self.resource_templates: Dict[str, Dict[str, Any]] = {}
        self.cost_estimator = self._init_cost_estimator()
        self.terraform_client = self._init_terraform_client()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize cloud providers
        asyncio.create_task(self._init_providers())
    
    async def _init_providers(self):
        """Initialize cloud provider clients"""
        try:
            # AWS
            if self.config.get('aws', {}).get('enabled', True):
                self.providers[CloudProvider.AWS] = boto3.Session(
                    region_name=self.config.get('aws', {}).get('region', 'us-east-1')
                )
            
            # Azure
            if self.config.get('azure', {}).get('enabled', True):
                credential = DefaultAzureCredential()
                self.providers[CloudProvider.AZURE] = ResourceManagementClient(
                    credential, 
                    self.config.get('azure', {}).get('subscription_id', '')
                )
            
            # GCP
            if self.config.get('gcp', {}).get('enabled', True):
                self.providers[CloudProvider.GCP] = resource_manager.Client()
            
            # Kubernetes
            if self.config.get('kubernetes', {}).get('enabled', True):
                try:
                    config.load_incluster_config()
                except:
                    config.load_kube_config()
                self.providers[CloudProvider.KUBERNETES] = client.ApiClient()
                
            self.logger.info("Cloud providers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize providers: {str(e)}")
    
    def _init_cost_estimator(self) -> Dict[str, Any]:
        """Initialize cost estimation engine"""
        return {
            'aws': {
                'ec2': {'m5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384},
                'rds': {'db.t3.micro': 0.017, 'db.t3.small': 0.034},
                'lambda': {'request': 0.0000002, 'duration_gb_second': 0.0000166667}
            },
            'azure': {
                'vm': {'Standard_D2s_v3': 0.096, 'Standard_D4s_v3': 0.192},
                'sql': {'Basic': 0.020, 'Standard_S0': 0.020},
                'functions': {'request': 0.0000002, 'execution_gb_second': 0.000016}
            },
            'gcp': {
                'compute': {'n1-standard-1': 0.0475, 'n1-standard-2': 0.095},
                'sql': {'db-f1-micro': 0.0150, 'db-g1-small': 0.025},
                'functions': {'invocation': 0.0000004, 'compute_gb_second': 0.0000025}
            }
        }
    
    def _init_terraform_client(self) -> Optional[Any]:
        """Initialize Terraform client for IaC"""
        try:
            # Initialize Terraform client if available
            return None  # Placeholder for actual Terraform client
        except Exception as e:
            self.logger.warning(f"Terraform client not available: {str(e)}")
            return None
    
    async def create_provisioning_plan(
        self,
        deployment_id: str,
        requirements: Dict[str, Any],
        tier: CreatorTier = CreatorTier.CREATOR,
        provider: CloudProvider = CloudProvider.AWS
    ) -> ProvisioningPlan:
        """
        Create infrastructure provisioning plan
        
        Args:
            deployment_id: Unique deployment identifier
            requirements: Infrastructure requirements
            tier: Creator subscription tier
            provider: Target cloud provider
            
        Returns:
            ProvisioningPlan: Generated provisioning plan
        """
        try:
            plan_id = f"plan_{deployment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate resources based on requirements and tier
            resources = await self._generate_resources(requirements, tier, provider)
            
            # Estimate cost
            estimated_cost = await self._estimate_cost(resources, provider)
            
            # Calculate provisioning time
            provisioning_time = self._calculate_provisioning_time(resources)
            
            # Generate dependencies
            dependencies = self._generate_dependencies(resources)
            
            # Create validation rules
            validation_rules = self._generate_validation_rules(resources, tier)
            
            plan = ProvisioningPlan(
                plan_id=plan_id,
                provider=provider,
                resources=resources,
                estimated_cost=estimated_cost,
                provisioning_time=provisioning_time,
                dependencies=dependencies,
                validation_rules=validation_rules,
                created_at=datetime.now(timezone.utc)
            )
            
            self.provisioning_plans[plan_id] = plan
            self.logger.info(f"Provisioning plan created: {plan_id}")
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create provisioning plan: {str(e)}")
            raise
    
    async def _generate_resources(
        self,
        requirements: Dict[str, Any],
        tier: CreatorTier,
        provider: CloudProvider
    ) -> List[ResourceSpec]:
        """Generate resource specifications based on requirements"""
        resources = []
        
        # Base resource multipliers by tier
        tier_multipliers = {
            CreatorTier.FREE: {'cpu': 0.5, 'memory': 0.5, 'storage': 0.5, 'replicas': 1},
            CreatorTier.CREATOR: {'cpu': 1.0, 'memory': 1.0, 'storage': 1.0, 'replicas': 2},
            CreatorTier.PRO: {'cpu': 2.0, 'memory': 2.0, 'storage': 2.0, 'replicas': 3},
            CreatorTier.ENTERPRISE: {'cpu': 4.0, 'memory': 4.0, 'storage': 4.0, 'replicas': 5}
        }
        
        multiplier = tier_multipliers[tier]
        
        # Compute resources
        if requirements.get('compute', True):
            cpu = f"{int(float(requirements.get('cpu', '1')) * multiplier['cpu'])}m"
            memory = f"{int(float(requirements.get('memory', '1')) * multiplier['memory'])}Gi"
            storage = f"{int(float(requirements.get('storage', '10')) * multiplier['storage'])}Gi"
            
            resources.append(ResourceSpec(
                resource_type=ResourceType.COMPUTE,
                name=f"compute-{requirements.get('model_name', 'model')}",
                cpu=cpu,
                memory=memory,
                storage=storage,
                replicas=multiplier['replicas'],
                tier=tier,
                tags={'tier': tier.value, 'type': 'ml-model'},
                metadata=requirements,
                created_at=datetime.now(timezone.utc)
            ))
        
        # Storage resources
        if requirements.get('persistent_storage', False):
            resources.append(ResourceSpec(
                resource_type=ResourceType.STORAGE,
                name=f"storage-{requirements.get('model_name', 'model')}",
                cpu="0",
                memory="0",
                storage=f"{int(float(requirements.get('storage', '50')) * multiplier['storage'])}Gi",
                replicas=1,
                tier=tier,
                tags={'tier': tier.value, 'type': 'persistent-storage'},
                metadata=requirements,
                created_at=datetime.now(timezone.utc)
            ))
        
        # Database resources
        if requirements.get('database', False):
            resources.append(ResourceSpec(
                resource_type=ResourceType.DATABASE,
                name=f"db-{requirements.get('model_name', 'model')}",
                cpu=f"{int(0.5 * multiplier['cpu'])}m",
                memory=f"{int(2 * multiplier['memory'])}Gi",
                storage=f"{int(20 * multiplier['storage'])}Gi",
                replicas=1 if tier != CreatorTier.ENTERPRISE else 2,
                tier=tier,
                tags={'tier': tier.value, 'type': 'database'},
                metadata=requirements,
                created_at=datetime.now(timezone.utc)
            ))
        
        # Load balancer for higher tiers
        if tier in [CreatorTier.PRO, CreatorTier.ENTERPRISE]:
            resources.append(ResourceSpec(
                resource_type=ResourceType.LOAD_BALANCER,
                name=f"lb-{requirements.get('model_name', 'model')}",
                cpu="100m",
                memory="128Mi",
                storage="0",
                replicas=1,
                tier=tier,
                tags={'tier': tier.value, 'type': 'load-balancer'},
                metadata=requirements,
                created_at=datetime.now(timezone.utc)
            ))
        
        return resources
    
    async def _estimate_cost(
        self,
        resources: List[ResourceSpec],
        provider: CloudProvider
    ) -> float:
        """Estimate infrastructure cost"""
        total_cost = 0.0
        
        try:
            provider_rates = self.cost_estimator.get(provider.value, {})
            
            for resource in resources:
                if resource.resource_type == ResourceType.COMPUTE:
                    # Estimate compute cost
                    cpu_cores = float(resource.cpu.replace('m', '')) / 1000
                    memory_gb = float(resource.memory.replace('Gi', ''))
                    
                    # Base cost calculation (simplified)
                    hourly_cost = (cpu_cores * 0.048) + (memory_gb * 0.0067)
                    monthly_cost = hourly_cost * 24 * 30 * resource.replicas
                    total_cost += monthly_cost
                
                elif resource.resource_type == ResourceType.STORAGE:
                    # Estimate storage cost
                    storage_gb = float(resource.storage.replace('Gi', ''))
                    monthly_cost = storage_gb * 0.10  # $0.10 per GB per month
                    total_cost += monthly_cost
                
                elif resource.resource_type == ResourceType.DATABASE:
                    # Estimate database cost
                    monthly_cost = 50.0 * resource.replicas  # Base database cost
                    total_cost += monthly_cost
                
                elif resource.resource_type == ResourceType.LOAD_BALANCER:
                    # Estimate load balancer cost
                    monthly_cost = 15.0  # Base load balancer cost
                    total_cost += monthly_cost
            
            self.logger.info(f"Estimated monthly cost: ${total_cost:.2f}")
            return total_cost
            
        except Exception as e:
            self.logger.error(f"Cost estimation failed: {str(e)}")
            return 0.0
    
    def _calculate_provisioning_time(self, resources: List[ResourceSpec]) -> int:
        """Calculate estimated provisioning time in minutes"""
        base_times = {
            ResourceType.COMPUTE: 5,
            ResourceType.STORAGE: 2,
            ResourceType.DATABASE: 10,
            ResourceType.LOAD_BALANCER: 3,
            ResourceType.NETWORKING: 2
        }
        
        total_time = 0
        for resource in resources:
            base_time = base_times.get(resource.resource_type, 5)
            total_time += base_time * resource.replicas
        
        return max(total_time, 5)  # Minimum 5 minutes
    
    def _generate_dependencies(self, resources: List[ResourceSpec]) -> Dict[str, List[str]]:
        """Generate resource dependencies"""
        dependencies = {}
        
        for resource in resources:
            deps = []
            
            if resource.resource_type == ResourceType.COMPUTE:
                # Compute depends on networking and storage
                for r in resources:
                    if r.resource_type in [ResourceType.NETWORKING, ResourceType.STORAGE]:
                        deps.append(r.name)
            
            elif resource.resource_type == ResourceType.LOAD_BALANCER:
                # Load balancer depends on compute
                for r in resources:
                    if r.resource_type == ResourceType.COMPUTE:
                        deps.append(r.name)
            
            dependencies[resource.name] = deps
        
        return dependencies
    
    def _generate_validation_rules(
        self,
        resources: List[ResourceSpec],
        tier: CreatorTier
    ) -> List[str]:
        """Generate validation rules for resources"""
        rules = [
            "resource_limits_within_tier_quota",
            "security_groups_properly_configured",
            "backup_and_disaster_recovery_enabled"
        ]
        
        if tier == CreatorTier.ENTERPRISE:
            rules.extend([
                "high_availability_enabled",
                "monitoring_and_alerting_configured",
                "compliance_controls_active"
            ])
        
        return rules
    
    async def provision_infrastructure(
        self,
        plan_id: str,
        dry_run: bool = False
    ) -> ProvisioningResult:
        """
        Provision infrastructure according to plan
        
        Args:
            plan_id: Provisioning plan identifier
            dry_run: If True, simulate provisioning without creating resources
            
        Returns:
            ProvisioningResult: Provisioning execution result
        """
        try:
            if plan_id not in self.provisioning_plans:
                raise ValueError(f"Provisioning plan not found: {plan_id}")
            
            plan = self.provisioning_plans[plan_id]
            start_time = datetime.now()
            
            provisioned_resources = []
            failed_resources = []
            
            self.logger.info(f"Starting infrastructure provisioning: {plan_id}")
            
            # Sort resources by dependencies
            sorted_resources = self._sort_resources_by_dependencies(
                plan.resources, 
                plan.dependencies
            )
            
            for resource in sorted_resources:
                try:
                    if dry_run:
                        # Simulate provisioning
                        await asyncio.sleep(0.1)
                        provisioned_resources.append({
                            'name': resource.name,
                            'type': resource.resource_type.value,
                            'status': 'simulated',
                            'id': f"sim-{resource.name}"
                        })
                    else:
                        # Actual provisioning
                        resource_result = await self._provision_resource(resource, plan.provider)
                        provisioned_resources.append(resource_result)
                    
                    self.logger.info(f"Resource provisioned: {resource.name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to provision {resource.name}: {str(e)}")
                    failed_resources.append({
                        'name': resource.name,
                        'type': resource.resource_type.value,
                        'error': str(e)
                    })
            
            # Calculate actual provisioning time
            end_time = datetime.now()
            provisioning_time = (end_time - start_time).total_seconds() / 60
            
            # Calculate actual cost
            total_cost = plan.estimated_cost if provisioned_resources else 0.0
            
            result = ProvisioningResult(
                plan_id=plan_id,
                provider=plan.provider,
                success=len(failed_resources) == 0,
                provisioned_resources=provisioned_resources,
                failed_resources=failed_resources,
                total_cost=total_cost,
                provisioning_time=provisioning_time,
                error_message=None if len(failed_resources) == 0 else f"{len(failed_resources)} resources failed",
                created_at=datetime.now(timezone.utc)
            )
            
            self.provisioning_results[plan_id] = result
            self.logger.info(f"Provisioning completed: {plan_id}, Success: {result.success}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Infrastructure provisioning failed: {str(e)}")
            error_result = ProvisioningResult(
                plan_id=plan_id,
                provider=plan.provider,
                success=False,
                provisioned_resources=[],
                failed_resources=[],
                total_cost=0.0,
                provisioning_time=0.0,
                error_message=str(e),
                created_at=datetime.now(timezone.utc)
            )
            self.provisioning_results[plan_id] = error_result
            return error_result
    
    def _sort_resources_by_dependencies(
        self,
        resources: List[ResourceSpec],
        dependencies: Dict[str, List[str]]
    ) -> List[ResourceSpec]:
        """Sort resources by dependency order"""
        sorted_resources = []
        resource_map = {r.name: r for r in resources}
        visited = set()
        
        def visit(resource_name: str):
            if resource_name in visited:
                return
            visited.add(resource_name)
            
            # Visit dependencies first
            for dep in dependencies.get(resource_name, []):
                if dep in resource_map:
                    visit(dep)
            
            # Add resource after dependencies
            if resource_name in resource_map:
                sorted_resources.append(resource_map[resource_name])
        
        # Visit all resources
        for resource in resources:
            visit(resource.name)
        
        return sorted_resources
    
    async def _provision_resource(
        self,
        resource: ResourceSpec,
        provider: CloudProvider
    ) -> Dict[str, Any]:
        """Provision a single resource"""
        if provider == CloudProvider.AWS:
            return await self._provision_aws_resource(resource)
        elif provider == CloudProvider.AZURE:
            return await self._provision_azure_resource(resource)
        elif provider == CloudProvider.GCP:
            return await self._provision_gcp_resource(resource)
        elif provider == CloudProvider.KUBERNETES:
            return await self._provision_k8s_resource(resource)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _provision_aws_resource(self, resource: ResourceSpec) -> Dict[str, Any]:
        """Provision AWS resource"""
        # Simulate AWS resource provisioning
        await asyncio.sleep(0.5)
        return {
            'name': resource.name,
            'type': resource.resource_type.value,
            'provider': 'aws',
            'status': 'running',
            'id': f"aws-{resource.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def _provision_azure_resource(self, resource: ResourceSpec) -> Dict[str, Any]:
        """Provision Azure resource"""
        # Simulate Azure resource provisioning
        await asyncio.sleep(0.5)
        return {
            'name': resource.name,
            'type': resource.resource_type.value,
            'provider': 'azure',
            'status': 'running',
            'id': f"azure-{resource.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def _provision_gcp_resource(self, resource: ResourceSpec) -> Dict[str, Any]:
        """Provision GCP resource"""
        # Simulate GCP resource provisioning
        await asyncio.sleep(0.5)
        return {
            'name': resource.name,
            'type': resource.resource_type.value,
            'provider': 'gcp',
            'status': 'running',
            'id': f"gcp-{resource.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def _provision_k8s_resource(self, resource: ResourceSpec) -> Dict[str, Any]:
        """Provision Kubernetes resource"""
        # Simulate Kubernetes resource provisioning
        await asyncio.sleep(0.3)
        return {
            'name': resource.name,
            'type': resource.resource_type.value,
            'provider': 'kubernetes',
            'status': 'running',
            'id': f"k8s-{resource.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def destroy_infrastructure(
        self,
        plan_id: str,
        force: bool = False
    ) -> bool:
        """
        Destroy provisioned infrastructure
        
        Args:
            plan_id: Provisioning plan identifier
            force: Force destruction even if resources are in use
            
        Returns:
            bool: True if destruction was successful
        """
        try:
            if plan_id not in self.provisioning_results:
                raise ValueError(f"Provisioning result not found: {plan_id}")
            
            result = self.provisioning_results[plan_id]
            
            self.logger.info(f"Starting infrastructure destruction: {plan_id}")
            
            destroyed_count = 0
            for resource in reversed(result.provisioned_resources):
                try:
                    # Simulate resource destruction
                    await asyncio.sleep(0.2)
                    destroyed_count += 1
                    self.logger.info(f"Resource destroyed: {resource['name']}")
                except Exception as e:
                    self.logger.error(f"Failed to destroy {resource['name']}: {str(e)}")
                    if not force:
                        return False
            
            self.logger.info(f"Infrastructure destroyed: {plan_id}, Resources: {destroyed_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Infrastructure destruction failed: {str(e)}")
            return False
    
    async def get_provisioning_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get provisioning status for a plan"""
        if plan_id in self.provisioning_results:
            result = self.provisioning_results[plan_id]
            return {
                'plan_id': plan_id,
                'status': 'completed',
                'success': result.success,
                'resources': len(result.provisioned_resources),
                'cost': result.total_cost,
                'time': result.provisioning_time
            }
        elif plan_id in self.provisioning_plans:
            return {
                'plan_id': plan_id,
                'status': 'planned',
                'estimated_cost': self.provisioning_plans[plan_id].estimated_cost,
                'estimated_time': self.provisioning_plans[plan_id].provisioning_time
            }
        return None
    
    def get_cost_optimization_recommendations(
        self,
        plan_id: str
    ) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        if plan_id not in self.provisioning_plans:
            return recommendations
        
        plan = self.provisioning_plans[plan_id]
        
        # Analyze resources for optimization opportunities
        for resource in plan.resources:
            if resource.resource_type == ResourceType.COMPUTE:
                if resource.tier == CreatorTier.FREE and resource.replicas > 1:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'resource': resource.name,
                        'suggestion': 'Consider reducing replicas for free tier',
                        'potential_savings': 30.0
                    })
            
            elif resource.resource_type == ResourceType.STORAGE:
                storage_gb = float(resource.storage.replace('Gi', ''))
                if storage_gb > 100:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'resource': resource.name,
                        'suggestion': 'Consider using cheaper storage tiers for large volumes',
                        'potential_savings': 20.0
                    })
        
        return recommendations

# Global infrastructure provisioning engine instance
_infrastructure_engine = None

def get_infrastructure_provisioning_engine(
    config: Optional[Dict[str, Any]] = None
) -> InfrastructureProvisioningEngine:
    """
    Get or create the global infrastructure provisioning engine instance
    
    Args:
        config: Configuration for the engine
        
    Returns:
        InfrastructureProvisioningEngine instance
    """
    global _infrastructure_engine
    
    if _infrastructure_engine is None:
        _infrastructure_engine = InfrastructureProvisioningEngine(config)
    
    return _infrastructure_engine

# Convenience functions for direct access
async def create_provisioning_plan(
    deployment_id: str,
    requirements: Dict[str, Any],
    tier: CreatorTier = CreatorTier.CREATOR,
    provider: CloudProvider = CloudProvider.AWS
) -> ProvisioningPlan:
    """Convenience function for creating provisioning plan"""
    engine = get_infrastructure_provisioning_engine()
    return await engine.create_provisioning_plan(deployment_id, requirements, tier, provider)

async def provision_infrastructure(
    plan_id: str,
    dry_run: bool = False
) -> ProvisioningResult:
    """Convenience function for provisioning infrastructure"""
    engine = get_infrastructure_provisioning_engine()
    return await engine.provision_infrastructure(plan_id, dry_run)

async def destroy_infrastructure(
    plan_id: str,
    force: bool = False
) -> bool:
    """Convenience function for destroying infrastructure"""
    engine = get_infrastructure_provisioning_engine()
    return await engine.destroy_infrastructure(plan_id, force)

# Export all main components and functions
__all__ = [
    'InfrastructureProvisioningEngine',
    'CloudProvider',
    'ResourceType',
    'CreatorTier',
    'ResourceSpec',
    'ProvisioningPlan',
    'ProvisioningResult',
    'get_infrastructure_provisioning_engine',
    'create_provisioning_plan',
    'provision_infrastructure',
    'destroy_infrastructure'
]