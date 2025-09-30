#!/usr/bin/env python3
"""
🌐 Cloud Deployment Orchestrator - Multi-Cloud ML Infrastructure

Enterprise multi-cloud deployment orchestration for AWS, Azure, and GCP with 
intelligent resource allocation, cost optimization, and geo-distributed inference.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Architecture Integration:
- Integrates with DeploymentManager for multi-cloud strategies
- Supports AWS SageMaker, Azure ML, and GCP AI Platform
- Intelligent cost optimization across cloud providers
- Geo-distributed deployment for global creator audience
- Data residency compliance for GDPR and regional requirements
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path

import numpy as np


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi"


class DeploymentRegion(Enum):
    """Deployment regions for global coverage."""
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"
    EU_CENTRAL = "eu-central-1"
    ASIA_PACIFIC = "ap-southeast-1"
    ASIA_NORTHEAST = "ap-northeast-1"


class InstanceType(Enum):
    """Instance types across cloud providers."""
    CPU_SMALL = "cpu_small"
    CPU_MEDIUM = "cpu_medium"
    CPU_LARGE = "cpu_large"
    GPU_SMALL = "gpu_small"
    GPU_MEDIUM = "gpu_medium"
    GPU_LARGE = "gpu_large"
    TPU_V4 = "tpu_v4"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    SCALING = "scaling"
    UPDATING = "updating"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class CloudConfiguration:
    """Cloud provider configuration."""
    provider: CloudProvider
    region: DeploymentRegion
    instance_type: InstanceType
    min_instances: int = 1
    max_instances: int = 10
    auto_scaling: bool = True
    spot_instances: bool = False  # Cost optimization
    
    # Provider-specific configs
    aws_config: Optional[Dict[str, Any]] = None
    azure_config: Optional[Dict[str, Any]] = None
    gcp_config: Optional[Dict[str, Any]] = None
    
    # Cost and performance constraints
    max_cost_per_hour: float = 10.0
    target_latency_ms: float = 100.0
    availability_target: float = 99.9


@dataclass
class DeploymentSpec:
    """Deployment specification."""
    deployment_id: str
    model_id: str
    model_version: str
    cloud_configs: List[CloudConfiguration]
    
    # Traffic distribution
    traffic_split: Dict[CloudProvider, float] = field(default_factory=dict)
    
    # Creator-specific optimization
    creator_types: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    
    # Compliance requirements
    data_residency_regions: List[str] = field(default_factory=list)
    gdpr_compliant: bool = True
    
    # Performance requirements
    sla_requirements: Dict[str, float] = field(default_factory=dict)


@dataclass
class DeploymentInstance:
    """Represents a deployed instance."""
    instance_id: str
    provider: CloudProvider
    region: DeploymentRegion
    instance_type: InstanceType
    status: DeploymentStatus
    created_at: float
    
    # Performance metrics
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    gpu_utilization: float = 0.0
    requests_per_second: float = 0.0
    avg_latency_ms: float = 0.0
    
    # Cost tracking
    cost_per_hour: float = 0.0
    total_cost: float = 0.0
    
    # Health status
    last_health_check: float = field(default_factory=time.time)
    health_score: float = 1.0


class CloudDeploymentOrchestrator:
    """
    Enterprise multi-cloud deployment orchestrator for ML models.
    
    Features:
    - Multi-cloud deployment (AWS, Azure, GCP)
    - Intelligent cost optimization
    - Geo-distributed inference for global performance
    - Auto-scaling based on demand and performance
    - Data residency compliance
    - Creator-specific optimizations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the cloud deployment orchestrator."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Deployment tracking
        self.deployments: Dict[str, DeploymentSpec] = {}
        self.instances: Dict[str, DeploymentInstance] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        # Performance and cost tracking
        self.performance_metrics: Dict[str, List[float]] = {
            "latency": [],
            "throughput": [],
            "cost_per_request": [],
            "availability": [],
            "error_rate": []
        }
        
        # Provider-specific pricing (simulated)
        self.pricing_models = self._initialize_pricing_models()
        
        # Regional performance data
        self.regional_performance: Dict[str, Dict[str, float]] = {}
        
        self.logger.info("Cloud Deployment Orchestrator initialized")
    
    def _initialize_pricing_models(self) -> Dict[CloudProvider, Dict[str, float]]:
        """Initialize pricing models for different cloud providers."""
        return {
            CloudProvider.AWS: {
                "cpu_small": 0.05,   # $/hour
                "cpu_medium": 0.10,
                "cpu_large": 0.20,
                "gpu_small": 0.50,
                "gpu_medium": 1.00,
                "gpu_large": 2.50
            },
            CloudProvider.AZURE: {
                "cpu_small": 0.048,  # Slightly cheaper
                "cpu_medium": 0.096,
                "cpu_large": 0.192,
                "gpu_small": 0.48,
                "gpu_medium": 0.96,
                "gpu_large": 2.40
            },
            CloudProvider.GCP: {
                "cpu_small": 0.047,  # Most competitive
                "cpu_medium": 0.094,
                "cpu_large": 0.188,
                "gpu_small": 0.47,
                "gpu_medium": 0.94,
                "gpu_large": 2.35,
                "tpu_v4": 1.50     # TPU advantage
            }
        }
    
    async def create_deployment(self, 
                              deployment_spec: DeploymentSpec) -> str:
        """Create a new multi-cloud deployment."""
        try:
            deployment_id = deployment_spec.deployment_id
            
            # Validate deployment specification
            if not await self._validate_deployment_spec(deployment_spec):
                raise ValueError("Invalid deployment specification")
            
            # Optimize cloud configuration
            optimized_spec = await self._optimize_deployment_configuration(deployment_spec)
            
            # Store deployment
            self.deployments[deployment_id] = optimized_spec
            
            # Start deployment process
            asyncio.create_task(self._execute_deployment(optimized_spec))
            
            self.logger.info(f"Deployment {deployment_id} created for model {deployment_spec.model_id}")
            
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to create deployment: {e}")
            raise
    
    async def _validate_deployment_spec(self, spec: DeploymentSpec) -> bool:
        """Validate deployment specification."""
        try:
            # Check required fields
            if not spec.model_id or not spec.cloud_configs:
                return False
            
            # Validate traffic split
            if spec.traffic_split:
                total_traffic = sum(spec.traffic_split.values())
                if abs(total_traffic - 1.0) > 0.001:
                    self.logger.error(f"Traffic split must sum to 1.0, got {total_traffic}")
                    return False
            
            # Validate cloud configurations
            for cloud_config in spec.cloud_configs:
                if cloud_config.min_instances < 1:
                    return False
                if cloud_config.max_instances < cloud_config.min_instances:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment validation failed: {e}")
            return False
    
    async def _optimize_deployment_configuration(self, 
                                               spec: DeploymentSpec) -> DeploymentSpec:
        """Optimize deployment configuration for cost and performance."""
        try:
            optimized_spec = spec
            
            # Cost optimization
            if not spec.traffic_split:
                optimized_spec.traffic_split = await self._optimize_traffic_split(spec)
            
            # Regional optimization for creator types
            if spec.creator_types:
                optimized_spec = await self._optimize_for_creator_types(optimized_spec)
            
            # Data residency compliance
            if spec.data_residency_regions:
                optimized_spec = await self._ensure_data_residency_compliance(optimized_spec)
            
            return optimized_spec
            
        except Exception as e:
            self.logger.error(f"Failed to optimize deployment configuration: {e}")
            return spec
    
    async def _optimize_traffic_split(self, spec: DeploymentSpec) -> Dict[CloudProvider, float]:
        """Optimize traffic split across cloud providers."""
        try:
            providers = [config.provider for config in spec.cloud_configs]
            
            # Cost-based optimization
            provider_costs = {}
            for config in spec.cloud_configs:
                instance_cost = self.pricing_models[config.provider].get(
                    config.instance_type.value, 1.0
                )
                provider_costs[config.provider] = instance_cost
            
            # Performance-based weights (simulated)
            provider_performance = {
                CloudProvider.AWS: 1.0,
                CloudProvider.AZURE: 0.95,
                CloudProvider.GCP: 1.05
            }
            
            # Calculate optimal split
            total_score = 0
            provider_scores = {}
            
            for provider in providers:
                # Score = Performance / Cost
                cost = provider_costs.get(provider, 1.0)
                performance = provider_performance.get(provider, 1.0)
                score = performance / cost
                provider_scores[provider] = score
                total_score += score
            
            # Normalize to traffic split
            traffic_split = {
                provider: score / total_score 
                for provider, score in provider_scores.items()
            }
            
            self.logger.info(f"Optimized traffic split: {traffic_split}")
            
            return traffic_split
            
        except Exception as e:
            self.logger.error(f"Failed to optimize traffic split: {e}")
            return {CloudProvider.AWS: 1.0}  # Fallback
    
    async def _optimize_for_creator_types(self, spec: DeploymentSpec) -> DeploymentSpec:
        """Optimize deployment for specific creator types."""
        try:
            # Creator-specific optimizations
            creator_optimizations = {
                "musician": {
                    "preferred_regions": [DeploymentRegion.US_WEST, DeploymentRegion.EU_WEST],
                    "instance_preference": InstanceType.GPU_MEDIUM,  # Audio processing
                    "latency_requirement": 50.0  # Real-time audio
                },
                "photographer": {
                    "preferred_regions": [DeploymentRegion.US_EAST, DeploymentRegion.EU_CENTRAL],
                    "instance_preference": InstanceType.GPU_LARGE,  # Image processing
                    "latency_requirement": 200.0  # Batch image processing
                },
                "blogger": {
                    "preferred_regions": [DeploymentRegion.US_EAST, DeploymentRegion.EU_WEST],
                    "instance_preference": InstanceType.CPU_MEDIUM,  # Text processing
                    "latency_requirement": 100.0  # Interactive text
                },
                "influencer": {
                    "preferred_regions": [DeploymentRegion.US_WEST, DeploymentRegion.ASIA_PACIFIC],
                    "instance_preference": InstanceType.GPU_MEDIUM,  # Multi-modal
                    "latency_requirement": 75.0  # Social media speed
                }
            }
            
            # Apply optimizations
            for creator_type in spec.creator_types:
                if creator_type in creator_optimizations:
                    opt = creator_optimizations[creator_type]
                    
                    # Update SLA requirements
                    spec.sla_requirements[f"{creator_type}_latency"] = opt["latency_requirement"]
                    
                    # Prefer optimal instance types
                    for config in spec.cloud_configs:
                        if config.instance_type.value.startswith("cpu") and opt["instance_preference"].value.startswith("gpu"):
                            config.instance_type = opt["instance_preference"]
            
            return spec
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for creator types: {e}")
            return spec
    
    async def _ensure_data_residency_compliance(self, spec: DeploymentSpec) -> DeploymentSpec:
        """Ensure data residency compliance."""
        try:
            # GDPR compliance for EU regions
            if "EU" in spec.data_residency_regions or spec.gdpr_compliant:
                eu_regions = [DeploymentRegion.EU_WEST, DeploymentRegion.EU_CENTRAL]
                
                # Ensure EU deployment exists
                has_eu_deployment = any(
                    config.region in eu_regions 
                    for config in spec.cloud_configs
                )
                
                if not has_eu_deployment:
                    # Add EU deployment
                    eu_config = CloudConfiguration(
                        provider=CloudProvider.AWS,  # Default
                        region=DeploymentRegion.EU_WEST,
                        instance_type=InstanceType.CPU_MEDIUM
                    )
                    spec.cloud_configs.append(eu_config)
            
            return spec
            
        except Exception as e:
            self.logger.error(f"Failed to ensure data residency compliance: {e}")
            return spec
    
    async def _execute_deployment(self, spec: DeploymentSpec):
        """Execute the deployment across cloud providers."""
        deployment_id = spec.deployment_id
        
        try:
            self.logger.info(f"Starting deployment {deployment_id}")
            
            # Deploy to each cloud configuration
            deployment_tasks = []
            for cloud_config in spec.cloud_configs:
                task = asyncio.create_task(
                    self._deploy_to_cloud(deployment_id, cloud_config)
                )
                deployment_tasks.append(task)
            
            # Wait for all deployments
            deployment_results = await asyncio.gather(*deployment_tasks, return_exceptions=True)
            
            # Check deployment results
            successful_deployments = 0
            for i, result in enumerate(deployment_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Deployment failed for config {i}: {result}")
                else:
                    successful_deployments += 1
            
            if successful_deployments == 0:
                raise Exception("All cloud deployments failed")
            
            # Start traffic routing
            await self._configure_traffic_routing(deployment_id)
            
            # Start monitoring
            asyncio.create_task(self._monitor_deployment(deployment_id))
            
            self.logger.info(f"Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Deployment {deployment_id} failed: {e}")
            await self._handle_deployment_failure(deployment_id, str(e))
    
    async def _deploy_to_cloud(self, 
                             deployment_id: str, 
                             cloud_config: CloudConfiguration) -> bool:
        """Deploy to specific cloud provider."""
        try:
            provider = cloud_config.provider
            region = cloud_config.region
            
            self.logger.info(f"Deploying to {provider.value} in {region.value}")
            
            # Create instances based on configuration
            for i in range(cloud_config.min_instances):
                instance_id = f"{deployment_id}_{provider.value}_{region.value}_{i}"
                
                instance = DeploymentInstance(
                    instance_id=instance_id,
                    provider=provider,
                    region=region,
                    instance_type=cloud_config.instance_type,
                    status=DeploymentStatus.DEPLOYING,
                    created_at=time.time(),
                    cost_per_hour=self.pricing_models[provider].get(
                        cloud_config.instance_type.value, 1.0
                    )
                )
                
                # Simulate deployment time
                deployment_time = np.random.uniform(30, 120)  # 30-120 seconds
                await asyncio.sleep(deployment_time / 60)  # Scale down for demo
                
                # Update instance status
                instance.status = DeploymentStatus.ACTIVE
                instance.health_score = np.random.uniform(0.95, 1.0)
                
                self.instances[instance_id] = instance
                
                self.logger.info(f"Instance {instance_id} deployed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy to {cloud_config.provider.value}: {e}")
            return False
    
    async def _configure_traffic_routing(self, deployment_id: str):
        """Configure traffic routing across cloud providers."""
        try:
            spec = self.deployments.get(deployment_id)
            if not spec:
                return
            
            # Get deployment instances
            deployment_instances = [
                instance for instance in self.instances.values()
                if instance.instance_id.startswith(deployment_id)
            ]
            
            if not deployment_instances:
                return
            
            # Configure load balancing based on traffic split
            traffic_split = spec.traffic_split
            
            for provider, traffic_percentage in traffic_split.items():
                provider_instances = [
                    instance for instance in deployment_instances
                    if instance.provider == provider
                ]
                
                for instance in provider_instances:
                    # Simulate traffic configuration
                    expected_rps = traffic_percentage * 100  # Assuming 100 RPS total
                    instance.requests_per_second = expected_rps
                    
                    self.logger.debug(f"Configured {instance.instance_id} for {expected_rps} RPS")
            
            self.logger.info(f"Traffic routing configured for deployment {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to configure traffic routing: {e}")
    
    async def _monitor_deployment(self, deployment_id: str):
        """Monitor deployment performance and health."""
        try:
            while deployment_id in self.deployments:
                # Get deployment instances
                deployment_instances = [
                    instance for instance in self.instances.values()
                    if instance.instance_id.startswith(deployment_id)
                ]
                
                if not deployment_instances:
                    break
                
                # Update instance metrics
                for instance in deployment_instances:
                    await self._update_instance_metrics(instance)
                
                # Check for scaling needs
                await self._check_auto_scaling(deployment_id, deployment_instances)
                
                # Update cost tracking
                await self._update_cost_tracking(deployment_instances)
                
                # Health checks
                await self._perform_health_checks(deployment_instances)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Monitoring failed for deployment {deployment_id}: {e}")
    
    async def _update_instance_metrics(self, instance: DeploymentInstance):
        """Update performance metrics for instance."""
        try:
            # Simulate realistic metrics
            base_cpu = 0.3 + np.random.normal(0, 0.1)
            instance.cpu_utilization = max(0.0, min(1.0, base_cpu))
            
            base_memory = 0.4 + np.random.normal(0, 0.05)
            instance.memory_utilization = max(0.0, min(1.0, base_memory))
            
            if "gpu" in instance.instance_type.value:
                base_gpu = 0.6 + np.random.normal(0, 0.15)
                instance.gpu_utilization = max(0.0, min(1.0, base_gpu))
            
            # Latency based on instance type and load
            base_latency = {
                InstanceType.CPU_SMALL: 150,
                InstanceType.CPU_MEDIUM: 100,
                InstanceType.CPU_LARGE: 75,
                InstanceType.GPU_SMALL: 80,
                InstanceType.GPU_MEDIUM: 50,
                InstanceType.GPU_LARGE: 30,
                InstanceType.TPU_V4: 25
            }.get(instance.instance_type, 100)
            
            load_factor = 1 + (instance.cpu_utilization * 0.5)
            instance.avg_latency_ms = base_latency * load_factor + np.random.normal(0, 5)
            
            # Update health score based on performance
            if instance.avg_latency_ms > 200:
                instance.health_score *= 0.95
            elif instance.avg_latency_ms < 100:
                instance.health_score = min(1.0, instance.health_score * 1.01)
            
            instance.last_health_check = time.time()
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics for {instance.instance_id}: {e}")
    
    async def _check_auto_scaling(self, 
                                deployment_id: str, 
                                instances: List[DeploymentInstance]):
        """Check if auto-scaling is needed."""
        try:
            spec = self.deployments.get(deployment_id)
            if not spec:
                return
            
            # Group instances by cloud configuration
            provider_instances = {}
            for instance in instances:
                provider = instance.provider
                if provider not in provider_instances:
                    provider_instances[provider] = []
                provider_instances[provider].append(instance)
            
            # Check scaling for each provider
            for provider, provider_instances_list in provider_instances.items():
                config = next(
                    (config for config in spec.cloud_configs if config.provider == provider), 
                    None
                )
                
                if not config or not config.auto_scaling:
                    continue
                
                # Calculate average CPU utilization
                avg_cpu = np.mean([inst.cpu_utilization for inst in provider_instances_list])
                
                current_count = len(provider_instances_list)
                
                # Scale up if high utilization
                if avg_cpu > 0.8 and current_count < config.max_instances:
                    await self._scale_up(deployment_id, provider, config)
                
                # Scale down if low utilization
                elif avg_cpu < 0.3 and current_count > config.min_instances:
                    await self._scale_down(deployment_id, provider, provider_instances_list)
                
        except Exception as e:
            self.logger.error(f"Auto-scaling check failed: {e}")
    
    async def _scale_up(self, 
                      deployment_id: str, 
                      provider: CloudProvider, 
                      config: CloudConfiguration):
        """Scale up instances for provider."""
        try:
            instance_id = f"{deployment_id}_{provider.value}_{config.region.value}_{uuid.uuid4().hex[:8]}"
            
            instance = DeploymentInstance(
                instance_id=instance_id,
                provider=provider,
                region=config.region,
                instance_type=config.instance_type,
                status=DeploymentStatus.DEPLOYING,
                created_at=time.time(),
                cost_per_hour=self.pricing_models[provider].get(
                    config.instance_type.value, 1.0
                )
            )
            
            # Simulate deployment
            await asyncio.sleep(np.random.uniform(1, 3))  # Quick scale-up
            instance.status = DeploymentStatus.ACTIVE
            
            self.instances[instance_id] = instance
            
            self.logger.info(f"Scaled up: Added instance {instance_id}")
            
        except Exception as e:
            self.logger.error(f"Scale up failed: {e}")
    
    async def _scale_down(self, 
                        deployment_id: str, 
                        provider: CloudProvider, 
                        instances: List[DeploymentInstance]):
        """Scale down instances for provider."""
        try:
            # Remove instance with lowest health score
            instance_to_remove = min(instances, key=lambda x: x.health_score)
            
            instance_to_remove.status = DeploymentStatus.TERMINATED
            
            # Remove from tracking after grace period
            await asyncio.sleep(5)  # Grace period
            del self.instances[instance_to_remove.instance_id]
            
            self.logger.info(f"Scaled down: Removed instance {instance_to_remove.instance_id}")
            
        except Exception as e:
            self.logger.error(f"Scale down failed: {e}")
    
    async def _update_cost_tracking(self, instances: List[DeploymentInstance]):
        """Update cost tracking for instances."""
        try:
            current_time = time.time()
            
            for instance in instances:
                if instance.status == DeploymentStatus.ACTIVE:
                    # Calculate cost since last update
                    time_diff_hours = (current_time - instance.created_at) / 3600
                    instance.total_cost = instance.cost_per_hour * time_diff_hours
                    
                    # Add to metrics
                    if instance.requests_per_second > 0:
                        cost_per_request = instance.cost_per_hour / (instance.requests_per_second * 3600)
                        self.performance_metrics["cost_per_request"].append(cost_per_request)
            
        except Exception as e:
            self.logger.error(f"Cost tracking update failed: {e}")
    
    async def _perform_health_checks(self, instances: List[DeploymentInstance]):
        """Perform health checks on instances."""
        try:
            for instance in instances:
                # Simulate health check
                health_ok = np.random.random() > 0.05  # 95% success rate
                
                if not health_ok:
                    instance.health_score *= 0.9
                    if instance.health_score < 0.5:
                        instance.status = DeploymentStatus.FAILED
                        self.logger.warning(f"Instance {instance.instance_id} failed health check")
                
        except Exception as e:
            self.logger.error(f"Health checks failed: {e}")
    
    async def _handle_deployment_failure(self, deployment_id: str, error: str):
        """Handle deployment failure."""
        try:
            spec = self.deployments.get(deployment_id)
            if spec:
                # Mark all instances as failed
                deployment_instances = [
                    instance for instance in self.instances.values()
                    if instance.instance_id.startswith(deployment_id)
                ]
                
                for instance in deployment_instances:
                    instance.status = DeploymentStatus.FAILED
                
                # Log failure
                failure_record = {
                    "deployment_id": deployment_id,
                    "error": error,
                    "timestamp": time.time(),
                    "affected_instances": len(deployment_instances)
                }
                
                self.deployment_history.append(failure_record)
                
                self.logger.error(f"Deployment {deployment_id} marked as failed: {error}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle deployment failure: {e}")
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive deployment status."""
        try:
            if deployment_id not in self.deployments:
                return None
            
            spec = self.deployments[deployment_id]
            
            # Get deployment instances
            deployment_instances = [
                instance for instance in self.instances.values()
                if instance.instance_id.startswith(deployment_id)
            ]
            
            # Calculate aggregate metrics
            total_instances = len(deployment_instances)
            active_instances = len([i for i in deployment_instances if i.status == DeploymentStatus.ACTIVE])
            
            if deployment_instances:
                avg_latency = np.mean([i.avg_latency_ms for i in deployment_instances])
                total_rps = sum(i.requests_per_second for i in deployment_instances)
                total_cost = sum(i.total_cost for i in deployment_instances)
                avg_health = np.mean([i.health_score for i in deployment_instances])
            else:
                avg_latency = total_rps = total_cost = avg_health = 0
            
            return {
                "deployment_id": deployment_id,
                "model_id": spec.model_id,
                "status": "active" if active_instances > 0 else "failed",
                "total_instances": total_instances,
                "active_instances": active_instances,
                "performance_metrics": {
                    "avg_latency_ms": avg_latency,
                    "total_rps": total_rps,
                    "avg_health_score": avg_health
                },
                "cost_metrics": {
                    "total_cost": total_cost,
                    "cost_per_hour": sum(i.cost_per_hour for i in deployment_instances)
                },
                "provider_distribution": {
                    provider.value: len([i for i in deployment_instances if i.provider == provider])
                    for provider in CloudProvider
                    if any(i.provider == provider for i in deployment_instances)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get deployment status: {e}")
            return None
    
    async def terminate_deployment(self, deployment_id: str) -> bool:
        """Terminate a deployment."""
        try:
            if deployment_id not in self.deployments:
                return False
            
            # Get deployment instances
            deployment_instances = [
                instance for instance in self.instances.values()
                if instance.instance_id.startswith(deployment_id)
            ]
            
            # Terminate all instances
            for instance in deployment_instances:
                instance.status = DeploymentStatus.TERMINATED
                
                # Remove from tracking after grace period
                asyncio.create_task(self._cleanup_instance(instance.instance_id))
            
            # Remove deployment
            del self.deployments[deployment_id]
            
            self.logger.info(f"Deployment {deployment_id} terminated")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate deployment {deployment_id}: {e}")
            return False
    
    async def _cleanup_instance(self, instance_id: str):
        """Cleanup terminated instance after grace period."""
        await asyncio.sleep(30)  # Grace period
        
        if instance_id in self.instances:
            del self.instances[instance_id]
    
    async def get_cost_analysis(self, 
                              deployment_id: Optional[str] = None,
                              time_range_hours: int = 24) -> Dict[str, Any]:
        """Get cost analysis for deployments."""
        try:
            if deployment_id:
                instances = [
                    instance for instance in self.instances.values()
                    if instance.instance_id.startswith(deployment_id)
                ]
            else:
                instances = list(self.instances.values())
            
            # Calculate costs by provider
            provider_costs = {}
            instance_type_costs = {}
            
            total_cost = 0
            
            for instance in instances:
                provider = instance.provider.value
                instance_type = instance.instance_type.value
                
                if provider not in provider_costs:
                    provider_costs[provider] = 0
                if instance_type not in instance_type_costs:
                    instance_type_costs[instance_type] = 0
                
                provider_costs[provider] += instance.total_cost
                instance_type_costs[instance_type] += instance.total_cost
                total_cost += instance.total_cost
            
            # Calculate cost efficiency
            if total_cost > 0:
                avg_cost_per_request = np.mean(self.performance_metrics["cost_per_request"][-100:]) if self.performance_metrics["cost_per_request"] else 0
            else:
                avg_cost_per_request = 0
            
            return {
                "total_cost": total_cost,
                "provider_breakdown": provider_costs,
                "instance_type_breakdown": instance_type_costs,
                "cost_efficiency": {
                    "cost_per_request": avg_cost_per_request,
                    "cost_per_hour": total_cost / max(time_range_hours, 1)
                },
                "recommendations": await self._generate_cost_recommendations(instances)
            }
            
        except Exception as e:
            self.logger.error(f"Cost analysis failed: {e}")
            return {}
    
    async def _generate_cost_recommendations(self, 
                                           instances: List[DeploymentInstance]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        try:
            if not instances:
                return recommendations
            
            # Check for underutilized instances
            underutilized = [
                instance for instance in instances 
                if instance.cpu_utilization < 0.3 and instance.status == DeploymentStatus.ACTIVE
            ]
            
            if underutilized:
                recommendations.append(
                    f"Consider scaling down {len(underutilized)} underutilized instances to save ~${sum(i.cost_per_hour for i in underutilized):.2f}/hour"
                )
            
            # Check for expensive instance types
            expensive_instances = [
                instance for instance in instances
                if instance.cost_per_hour > 1.0 and instance.cpu_utilization < 0.6
            ]
            
            if expensive_instances:
                recommendations.append(
                    f"Consider downgrading {len(expensive_instances)} expensive instances to smaller instance types"
                )
            
            # Provider cost comparison
            provider_avg_costs = {}
            for instance in instances:
                provider = instance.provider
                if provider not in provider_avg_costs:
                    provider_avg_costs[provider] = []
                provider_avg_costs[provider].append(instance.cost_per_hour)
            
            if len(provider_avg_costs) > 1:
                cheapest_provider = min(
                    provider_avg_costs.keys(),
                    key=lambda p: np.mean(provider_avg_costs[p])
                )
                recommendations.append(
                    f"Consider migrating more workload to {cheapest_provider.value} for cost savings"
                )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate cost recommendations: {e}")
            return recommendations