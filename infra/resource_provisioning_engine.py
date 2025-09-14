"""
Resource Provisioning Engine module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Resource Provisioning Engine

Advanced resource provisioning system for enterprise infrastructure.
Handles automated resource allocation, scaling, and optimization across cloud providers.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Resource type options."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"
    DNS = "dns"
    SECURITY = "security"
    MONITORING = "monitoring"

class ResourceStatus(Enum):
    """Resource status options."""
    PENDING = "pending"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SCALING = "scaling"
    UPDATING = "updating"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    TERMINATING = "terminating"
    TERMINATED = "terminated"

class ProvisioningStrategy(Enum):
    """Provisioning strategy options."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    PREDICTIVE = "predictive"

@dataclass
class ResourceSpec:
    """Resource specification."""
    type: ResourceType
    name: str
    provider: str
    region: str
    size: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    cost_budget: Optional[float] = None
    lifecycle_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceInstance:
    """Resource instance representation."""
    id: str
    spec: ResourceSpec
    status: ResourceStatus
    provider_id: str
    endpoint: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProvisioningRequest:
    """Resource provisioning request."""
    id: str
    specs: List[ResourceSpec]
    strategy: ProvisioningStrategy
    priority: int = 5
    schedule: Optional[datetime] = None
    deadline: Optional[datetime] = None
    auto_scaling: bool = True
    cost_optimization: bool = True
    environment: str = "dev"
    requester: str = "system"

@dataclass
class ScalingPolicy:
    """Auto-scaling policy definition."""
    resource_id: str
    min_instances: int = 1
    max_instances: int = 10
    target_cpu: float = 70.0
    target_memory: float = 80.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    metrics_window: int = 300  # seconds
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

class ResourceProvisioningEngine:
    """
    Enterprise resource provisioning engine.
    
    Provides automated resource provisioning, scaling, optimization, and lifecycle
    management across multiple cloud providers with cost optimization.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize resource provisioning engine."""
        self.config = config or {}
        self.resources: Dict[str, ResourceInstance] = {}
        self.provisioning_requests: Dict[str, ProvisioningRequest] = {}
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.provider_clients: Dict[str, Any] = {}
        
        # Configuration
        self.max_concurrent_provisions = self.config.get("max_concurrent_provisions", 10)
        self.enable_cost_optimization = self.config.get("enable_cost_optimization", True)
        self.enable_auto_scaling = self.config.get("enable_auto_scaling", True)
        self.enable_predictive_scaling = self.config.get("enable_predictive_scaling", False)
        self.cost_budget_alerts = self.config.get("cost_budget_alerts", True)
        
        # Metrics and monitoring
        self.metrics_enabled = self.config.get("metrics_enabled", True)
        self.monitoring_interval = self.config.get("monitoring_interval", 60)
        
        # Initialize provider integrations
        self._initialize_providers()
        
        # Start background tasks
        if self.enable_auto_scaling:
            asyncio.create_task(self._auto_scaling_loop())
        if self.metrics_enabled:
            asyncio.create_task(self._metrics_collection_loop())
        
        logger.info("ResourceProvisioningEngine initialized")
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS provider
            aws_config = self.config.get("aws", {})
            if aws_config.get("enabled", True):
                from .aws_infrastructure_provider import AWSInfrastructureProvider
                self.provider_clients["aws"] = AWSInfrastructureProvider(aws_config)
            
            # Azure provider
            azure_config = self.config.get("azure", {})
            if azure_config.get("enabled", True):
                from .azure_infrastructure_provider import AzureInfrastructureProvider
                self.provider_clients["azure"] = AzureInfrastructureProvider(azure_config)
            
            # GCP provider
            gcp_config = self.config.get("gcp", {})
            if gcp_config.get("enabled", True):
                from .gcp_infrastructure_provider import GCPInfrastructureProvider
                self.provider_clients["gcp"] = GCPInfrastructureProvider(gcp_config)
            
            logger.info(f"Initialized {len(self.provider_clients)} cloud providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {str(e)}")
    
    async def provision_resources(self, request_config: Dict[str, Any]) -> str:
        """Provision resources based on request."""
        try:
            # Create provisioning request
            request_id = str(uuid.uuid4())
            
            specs = []
            for spec_config in request_config.get("specs", []):
                spec = ResourceSpec(
                    type=ResourceType(spec_config["type"]),
                    name=spec_config["name"],
                    provider=spec_config["provider"],
                    region=spec_config["region"],
                    size=spec_config["size"],
                    configuration=spec_config.get("configuration", {}),
                    tags=spec_config.get("tags", {}),
                    dependencies=spec_config.get("dependencies", []),
                    cost_budget=spec_config.get("cost_budget"),
                    lifecycle_policy=spec_config.get("lifecycle_policy", {})
                )
                specs.append(spec)
            
            request = ProvisioningRequest(
                id=request_id,
                specs=specs,
                strategy=ProvisioningStrategy(request_config.get("strategy", "immediate")),
                priority=request_config.get("priority", 5),
                schedule=request_config.get("schedule"),
                deadline=request_config.get("deadline"),
                auto_scaling=request_config.get("auto_scaling", True),
                cost_optimization=request_config.get("cost_optimization", True),
                environment=request_config.get("environment", "dev"),
                requester=request_config.get("requester", "system")
            )
            
            self.provisioning_requests[request_id] = request
            
            # Execute provisioning based on strategy
            if request.strategy == ProvisioningStrategy.IMMEDIATE:
                asyncio.create_task(self._execute_provisioning(request))
            elif request.strategy == ProvisioningStrategy.SCHEDULED:
                asyncio.create_task(self._schedule_provisioning(request))
            elif request.strategy == ProvisioningStrategy.ON_DEMAND:
                # Store for later execution
                pass
            elif request.strategy == ProvisioningStrategy.PREDICTIVE:
                asyncio.create_task(self._predictive_provisioning(request))
            
            logger.info(f"Created provisioning request: {request_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to provision resources: {str(e)}")
            raise
    
    async def _execute_provisioning(self, request -> None: ProvisioningRequest) -> None:
        """Execute resource provisioning."""
        try:
            logger.info(f"Executing provisioning request: {request.id}")
            
            # Sort specs by dependencies
            sorted_specs = await self._sort_specs_by_dependencies(request.specs)
            
            # Provision resources in dependency order
            provisioned_resources = []
            
            for spec in sorted_specs:
                try:
                    # Check provider availability
                    if spec.provider not in self.provider_clients:
                        raise ValueError(f"Provider not available: {spec.provider}")
                    
                    provider = self.provider_clients[spec.provider]
                    
                    # Optimize resource configuration if enabled
                    if request.cost_optimization and self.enable_cost_optimization:
                        spec = await self._optimize_resource_spec(spec)
                    
                    # Provision resource
                    resource_instance = await self._provision_single_resource(provider, spec, request)
                    
                    if resource_instance:
                        provisioned_resources.append(resource_instance)
                        self.resources[resource_instance.id] = resource_instance
                        
                        # Setup auto-scaling if enabled
                        if request.auto_scaling and self.enable_auto_scaling:
                            await self._setup_auto_scaling(resource_instance)
                        
                        logger.info(f"Provisioned resource: {resource_instance.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to provision resource {spec.name}: {str(e)}")
                    
                    # Cleanup already provisioned resources on failure
                    await self._cleanup_resources(provisioned_resources)
                    raise
            
            logger.info(f"Provisioning request {request.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Provisioning request {request.id} failed: {str(e)}")
            raise
    
    async def _provision_single_resource(self, provider: Any, spec: ResourceSpec, request: ProvisioningRequest) -> Optional[ResourceInstance]:
        """Provision a single resource."""
        try:
            # Generate resource ID
            resource_id = f"{spec.type.value}-{spec.name}-{uuid.uuid4().hex[:8]}"
            
            # Create resource instance
            resource = ResourceInstance(
                id=resource_id,
                spec=spec,
                status=ResourceStatus.PROVISIONING,
                provider_id="",
                created_at=datetime.now()
            )
            
            # Add resource metadata
            resource.metadata.update({
                "request_id": request.id,
                "environment": request.environment,
                "requester": request.requester,
                "provisioned_by": "ResourceProvisioningEngine"
            })
            
            # Provision based on resource type
            if spec.type == ResourceType.COMPUTE:
                provider_resource = await provider.create_compute_instance(
                    name=spec.name,
                    size=spec.size,
                    region=spec.region,
                    configuration=spec.configuration,
                    tags=spec.tags
                )
            elif spec.type == ResourceType.STORAGE:
                provider_resource = await provider.create_storage_volume(
                    name=spec.name,
                    size=spec.size,
                    region=spec.region,
                    configuration=spec.configuration,
                    tags=spec.tags
                )
            elif spec.type == ResourceType.DATABASE:
                provider_resource = await provider.create_database_instance(
                    name=spec.name,
                    size=spec.size,
                    region=spec.region,
                    configuration=spec.configuration,
                    tags=spec.tags
                )
            elif spec.type == ResourceType.LOAD_BALANCER:
                provider_resource = await provider.create_load_balancer(
                    name=spec.name,
                    region=spec.region,
                    configuration=spec.configuration,
                    tags=spec.tags
                )
            else:
                # Generic resource creation
                provider_resource = await provider.create_resource(
                    resource_type=spec.type.value,
                    name=spec.name,
                    size=spec.size,
                    region=spec.region,
                    configuration=spec.configuration,
                    tags=spec.tags
                )
            
            # Update resource with provider information
            resource.provider_id = provider_resource.get("id", "")
            resource.endpoint = provider_resource.get("endpoint")
            resource.status = ResourceStatus.ACTIVE
            resource.updated_at = datetime.now()
            
            # Initialize cost tracking
            resource.cost = await self._calculate_initial_cost(resource)
            
            return resource
            
        except Exception as e:
            logger.error(f"Failed to provision single resource {spec.name}: {str(e)}")
            if 'resource' in locals():
                resource.status = ResourceStatus.FAILED
            return None
    
    async def _sort_specs_by_dependencies(self, specs: List[ResourceSpec]) -> List[ResourceSpec]:
        """Sort resource specs by dependencies."""
        sorted_specs = []
        remaining_specs = specs.copy()
        
        while remaining_specs:
            # Find specs with no unresolved dependencies
            ready_specs = []
            for spec in remaining_specs:
                dependencies_met = True
                for dep in spec.dependencies:
                    if not any(s.name == dep for s in sorted_specs):
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    ready_specs.append(spec)
            
            if not ready_specs:
                # Circular dependency or missing dependency
                logger.warning("Circular dependency detected or missing dependencies")
                ready_specs = remaining_specs  # Force proceed
            
            sorted_specs.extend(ready_specs)
            for spec in ready_specs:
                remaining_specs.remove(spec)
        
        return sorted_specs
    
    async def _optimize_resource_spec(self, spec: ResourceSpec) -> ResourceSpec:
        """Optimize resource specification for cost and performance."""
        try:
            optimized_spec = spec
            
            # Optimize based on resource type
            if spec.type == ResourceType.COMPUTE:
                # Suggest optimal instance size based on usage patterns
                optimal_size = await self._suggest_optimal_compute_size(spec)
                if optimal_size != spec.size:
                    optimized_spec.size = optimal_size
                    logger.info(f"Optimized compute size for {spec.name}: {spec.size} -> {optimal_size}")
            
            elif spec.type == ResourceType.STORAGE:
                # Optimize storage type and size
                optimal_config = await self._optimize_storage_config(spec)
                optimized_spec.configuration.update(optimal_config)
            
            elif spec.type == ResourceType.DATABASE:
                # Optimize database configuration
                optimal_config = await self._optimize_database_config(spec)
                optimized_spec.configuration.update(optimal_config)
            
            # Add cost optimization tags
            optimized_spec.tags["cost_optimized"] = "true"
            optimized_spec.tags["optimization_engine"] = "ResourceProvisioningEngine"
            
            return optimized_spec
            
        except Exception as e:
            logger.error(f"Failed to optimize resource spec {spec.name}: {str(e)}")
            return spec
    
    async def _suggest_optimal_compute_size(self, spec: ResourceSpec) -> str:
        """Suggest optimal compute instance size."""
        # This would analyze historical usage patterns and workload requirements
        # For now, provide basic optimization logic
        
        size_mapping = {
            "small": ["t3.micro", "t3.small"],
            "medium": ["t3.medium", "t3.large"],
            "large": ["t3.xlarge", "t3.2xlarge"],
            "xlarge": ["t3.4xlarge", "t3.8xlarge"]
        }
        
        # Basic optimization based on configuration
        cpu_requirement = spec.configuration.get("cpu", 1)
        memory_requirement = spec.configuration.get("memory", 1)  # GB
        
        if cpu_requirement <= 1 and memory_requirement <= 2:
            return "t3.micro"
        elif cpu_requirement <= 2 and memory_requirement <= 4:
            return "t3.small"
        elif cpu_requirement <= 4 and memory_requirement <= 8:
            return "t3.medium"
        elif cpu_requirement <= 8 and memory_requirement <= 16:
            return "t3.large"
        else:
            return "t3.xlarge"
    
    async def _optimize_storage_config(self, spec: ResourceSpec) -> Dict[str, Any]:
        """Optimize storage configuration."""
        optimizations = {}
        
        # Optimize storage type based on performance requirements
        iops_requirement = spec.configuration.get("iops", 0)
        if iops_requirement > 3000:
            optimizations["storage_type"] = "gp3"
        elif iops_requirement > 0:
            optimizations["storage_type"] = "gp2"
        else:
            optimizations["storage_type"] = "standard"
        
        # Optimize encryption
        if spec.configuration.get("sensitive_data", False):
            optimizations["encryption"] = True
        
        return optimizations
    
    async def _optimize_database_config(self, spec: ResourceSpec) -> Dict[str, Any]:
        """Optimize database configuration."""
        optimizations = {}
        
        # Optimize based on workload type
        workload_type = spec.configuration.get("workload_type", "general")
        
        if workload_type == "read_heavy":
            optimizations["read_replicas"] = max(1, spec.configuration.get("read_replicas", 0))
        elif workload_type == "write_heavy":
            optimizations["connection_pooling"] = True
            optimizations["wal_level"] = "replica"
        
        # Enable automated backups
        optimizations["automated_backup"] = True
        optimizations["backup_retention_period"] = 7
        
        return optimizations
    
    async def _setup_auto_scaling(self, resource -> None: ResourceInstance) -> None:
        """Setup auto-scaling for a resource."""
        try:
            if resource.spec.type not in [ResourceType.COMPUTE, ResourceType.DATABASE]:
                return  # Auto-scaling not applicable
            
            # Create default scaling policy
            policy = ScalingPolicy(
                resource_id=resource.id,
                min_instances=resource.spec.configuration.get("min_instances", 1),
                max_instances=resource.spec.configuration.get("max_instances", 5),
                target_cpu=resource.spec.configuration.get("target_cpu", 70.0),
                target_memory=resource.spec.configuration.get("target_memory", 80.0)
            )
            
            self.scaling_policies[resource.id] = policy
            logger.info(f"Setup auto-scaling for resource: {resource.id}")
            
        except Exception as e:
            logger.error(f"Failed to setup auto-scaling for {resource.id}: {str(e)}")
    
    async def _auto_scaling_loop(self) -> None:
        """Auto-scaling monitoring and execution loop."""
        while True:
            try:
                if not self.enable_auto_scaling:
                    await asyncio.sleep(self.monitoring_interval)
                    continue
                
                # Check each resource with auto-scaling policy
                for resource_id, policy in self.scaling_policies.items():
                    if resource_id not in self.resources:
                        continue
                    
                    resource = self.resources[resource_id]
                    if resource.status != ResourceStatus.ACTIVE:
                        continue
                    
                    # Get current metrics
                    metrics = await self._get_resource_metrics(resource)
                    
                    # Determine if scaling is needed
                    scaling_decision = await self._evaluate_scaling_decision(resource, policy, metrics)
                    
                    if scaling_decision["action"] != "none":
                        await self._execute_scaling(resource, scaling_decision)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Auto-scaling loop error: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _evaluate_scaling_decision(self, resource: ResourceInstance, policy: ScalingPolicy, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if scaling is needed."""
        try:
            current_instances = metrics.get("instance_count", 1)
            cpu_utilization = metrics.get("cpu_utilization", 0.0)
            memory_utilization = metrics.get("memory_utilization", 0.0)
            
            # Check scale up conditions
            if (cpu_utilization > policy.target_cpu or memory_utilization > policy.target_memory) and current_instances < policy.max_instances:
                return {
                    "action": "scale_up",
                    "target_instances": min(current_instances + 1, policy.max_instances),
                    "reason": f"CPU: {cpu_utilization}%, Memory: {memory_utilization}%"
                }
            
            # Check scale down conditions
            elif (cpu_utilization < policy.target_cpu * 0.5 and memory_utilization < policy.target_memory * 0.5) and current_instances > policy.min_instances:
                return {
                    "action": "scale_down",
                    "target_instances": max(current_instances - 1, policy.min_instances),
                    "reason": f"CPU: {cpu_utilization}%, Memory: {memory_utilization}%"
                }
            
            return {"action": "none"}
            
        except Exception as e:
            logger.error(f"Failed to evaluate scaling decision: {str(e)}")
            return {"action": "none"}
    
    async def _execute_scaling(self, resource -> None: ResourceInstance, scaling_decision -> None: Dict[str, Any]) -> None:
        """Execute scaling action."""
        try:
            resource.status = ResourceStatus.SCALING
            
            provider = self.provider_clients[resource.spec.provider]
            
            if scaling_decision["action"] == "scale_up":
                await provider.scale_resource(
                    resource_id=resource.provider_id,
                    target_instances=scaling_decision["target_instances"]
                )
            elif scaling_decision["action"] == "scale_down":
                await provider.scale_resource(
                    resource_id=resource.provider_id,
                    target_instances=scaling_decision["target_instances"]
                )
            
            resource.status = ResourceStatus.ACTIVE
            resource.updated_at = datetime.now()
            
            logger.info(f"Executed {scaling_decision['action']} for resource {resource.id}: {scaling_decision['reason']}")
            
        except Exception as e:
            logger.error(f"Failed to execute scaling for {resource.id}: {str(e)}")
            resource.status = ResourceStatus.ACTIVE  # Reset status
    
    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop."""
        while True:
            try:
                if not self.metrics_enabled:
                    await asyncio.sleep(self.monitoring_interval)
                    continue
                
                # Collect metrics for all active resources
                for resource in self.resources.values():
                    if resource.status == ResourceStatus.ACTIVE:
                        metrics = await self._get_resource_metrics(resource)
                        resource.metrics.update(metrics)
                        resource.cost = await self._calculate_current_cost(resource)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _get_resource_metrics(self, resource: ResourceInstance) -> Dict[str, Any]:
        """Get metrics for a resource."""
        try:
            provider = self.provider_clients[resource.spec.provider]
            metrics = await provider.get_resource_metrics(resource.provider_id)
            
            # Add timestamp
            metrics["timestamp"] = datetime.now().isoformat()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for resource {resource.id}: {str(e)}")
            return {"timestamp": datetime.now().isoformat()}
    
    async def _calculate_initial_cost(self, resource: ResourceInstance) -> float:
        """Calculate initial cost for resource."""
        # This would integrate with cloud provider billing APIs
        # For now, provide estimated costs based on resource type and size
        
        base_costs = {
            ResourceType.COMPUTE: {"t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416},
            ResourceType.STORAGE: {"gp2": 0.10, "gp3": 0.08, "standard": 0.05},  # per GB per month
            ResourceType.DATABASE: {"db.t3.micro": 0.017, "db.t3.small": 0.034}
        }
        
        hourly_cost = base_costs.get(resource.spec.type, {}).get(resource.spec.size, 0.05)
        return hourly_cost
    
    async def _calculate_current_cost(self, resource: ResourceInstance) -> float:
        """Calculate current cost for resource."""
        try:
            # Calculate based on uptime and resource usage
            uptime_hours = (datetime.now() - resource.created_at).total_seconds() / 3600
            hourly_cost = await self._calculate_initial_cost(resource)
            
            return uptime_hours * hourly_cost
            
        except Exception as e:
            logger.error(f"Failed to calculate cost for resource {resource.id}: {str(e)}")
            return resource.cost
    
    async def _cleanup_resources(self, resources -> None: List[ResourceInstance]) -> None:
        """Cleanup resources on failure."""
        try:
            for resource in resources:
                await self.terminate_resource(resource.id)
            
        except Exception as e:
            logger.error(f"Failed to cleanup resources: {str(e)}")
    
    async def _schedule_provisioning(self, request -> None: ProvisioningRequest) -> None:
        """Schedule provisioning for later execution."""
        try:
            if not request.schedule:
                return
            
            # Wait until scheduled time
            wait_time = (request.schedule - datetime.now()).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Execute provisioning
            await self._execute_provisioning(request)
            
        except Exception as e:
            logger.error(f"Scheduled provisioning failed: {str(e)}")
    
    async def _predictive_provisioning(self, request -> None: ProvisioningRequest) -> None:
        """Execute predictive provisioning based on ML models."""
        try:
            # This would use ML models to predict optimal provisioning time and resources
            # For now, execute immediately
            await self._execute_provisioning(request)
            
        except Exception as e:
            logger.error(f"Predictive provisioning failed: {str(e)}")
    
    # Public API methods
    async def scale_resource(self, resource_id: str, target_instances: int) -> bool:
        """Manually scale a resource."""
        try:
            if resource_id not in self.resources:
                return False
            
            resource = self.resources[resource_id]
            provider = self.provider_clients[resource.spec.provider]
            
            resource.status = ResourceStatus.SCALING
            
            await provider.scale_resource(
                resource_id=resource.provider_id,
                target_instances=target_instances
            )
            
            resource.status = ResourceStatus.ACTIVE
            resource.updated_at = datetime.now()
            
            logger.info(f"Manually scaled resource {resource_id} to {target_instances} instances")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale resource {resource_id}: {str(e)}")
            return False
    
    async def terminate_resource(self, resource_id: str) -> bool:
        """Terminate a resource."""
        try:
            if resource_id not in self.resources:
                return False
            
            resource = self.resources[resource_id]
            provider = self.provider_clients[resource.spec.provider]
            
            resource.status = ResourceStatus.TERMINATING
            
            await provider.terminate_resource(resource.provider_id)
            
            resource.status = ResourceStatus.TERMINATED
            resource.updated_at = datetime.now()
            
            # Remove from active tracking
            del self.resources[resource_id]
            if resource_id in self.scaling_policies:
                del self.scaling_policies[resource_id]
            
            logger.info(f"Terminated resource: {resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate resource {resource_id}: {str(e)}")
            return False
    
    def get_resource_status(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a resource."""
        if resource_id not in self.resources:
            return None
        
        resource = self.resources[resource_id]
        return {
            "id": resource.id,
            "name": resource.spec.name,
            "type": resource.spec.type.value,
            "provider": resource.spec.provider,
            "region": resource.spec.region,
            "status": resource.status.value,
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat(),
            "cost": resource.cost,
            "metrics": resource.metrics
        }
    
    def list_resources(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all resources with optional filtering."""
        resources = []
        
        for resource in self.resources.values():
            # Apply filters
            if filter_by:
                if "type" in filter_by and resource.spec.type.value != filter_by["type"]:
                    continue
                if "provider" in filter_by and resource.spec.provider != filter_by["provider"]:
                    continue
                if "status" in filter_by and resource.status.value != filter_by["status"]:
                    continue
                if "environment" in filter_by and resource.metadata.get("environment") != filter_by["environment"]:
                    continue
            
            resources.append({
                "id": resource.id,
                "name": resource.spec.name,
                "type": resource.spec.type.value,
                "provider": resource.spec.provider,
                "region": resource.spec.region,
                "status": resource.status.value,
                "cost": resource.cost,
                "created_at": resource.created_at.isoformat()
            })
        
        return resources
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for all resources."""
        total_cost = sum(resource.cost for resource in self.resources.values())
        
        cost_by_provider = {}
        cost_by_type = {}
        cost_by_environment = {}
        
        for resource in self.resources.values():
            # By provider
            provider = resource.spec.provider
            cost_by_provider[provider] = cost_by_provider.get(provider, 0) + resource.cost
            
            # By type
            resource_type = resource.spec.type.value
            cost_by_type[resource_type] = cost_by_type.get(resource_type, 0) + resource.cost
            
            # By environment
            environment = resource.metadata.get("environment", "unknown")
            cost_by_environment[environment] = cost_by_environment.get(environment, 0) + resource.cost
        
        return {
            "total_cost": total_cost,
            "cost_by_provider": cost_by_provider,
            "cost_by_type": cost_by_type,
            "cost_by_environment": cost_by_environment,
            "currency": "USD",
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on provisioning engine."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "resources_count": len(self.resources),
            "active_resources": len([r for r in self.resources.values() if r.status == ResourceStatus.ACTIVE]),
            "pending_requests": len([r for r in self.provisioning_requests.values()]),
            "auto_scaling_enabled": self.enable_auto_scaling,
            "cost_optimization_enabled": self.enable_cost_optimization,
            "providers": list(self.provider_clients.keys()),
            "issues": []
        }
        
        # Check for issues
        failed_resources = [r for r in self.resources.values() if r.status == ResourceStatus.FAILED]
        if failed_resources:
            health["status"] = "degraded"
            health["issues"].append(f"{len(failed_resources)} resources in failed state")
        
        # Check provider connectivity
        for provider_name, provider in self.provider_clients.items():
            try:
                provider_health = await provider.health_check()
                if not provider_health.get("healthy", False):
                    health["status"] = "degraded"
                    health["issues"].append(f"Provider {provider_name} is unhealthy")
            except Exception as e:
                health["status"] = "degraded"
                health["issues"].append(f"Provider {provider_name} health check failed: {str(e)}")
        
        return health


# Export the main class
__all__ = ["ResourceProvisioningEngine", "ResourceType", "ResourceStatus", "ProvisioningStrategy",
           "ResourceSpec", "ResourceInstance", "ProvisioningRequest", "ScalingPolicy"]