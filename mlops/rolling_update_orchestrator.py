"""
Enterprise Rolling Update Orchestrator for MLOps
DevOps + Lead Dev IA implementation with zero-downtime model updates
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import uuid
from pathlib import Path
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class UpdateStrategy(Enum):
    """Rolling update strategies"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    RECREATE = "recreate"
    CANARY_ROLLING = "canary_rolling"


class UpdatePhase(Enum):
    """Update phases"""
    PREPARATION = "preparation"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"
    COMPLETION = "completion"
    ROLLBACK = "rollback"


class PodStatus(Enum):
    """Pod/container status"""
    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    FAILED = "failed"


class UpdateStatus(Enum):
    """Update status"""
    PENDING = "pending"
    PREPARING = "preparing"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    PAUSED = "paused"


@dataclass
class PodInstance:
    """Pod/container instance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = ""
    status: PodStatus = PodStatus.PENDING
    node: Optional[str] = None
    
    # Resource allocation
    cpu_allocated: str = "100m"
    memory_allocated: str = "128Mi"
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Health and readiness
    health_check_passed: bool = False
    readiness_check_passed: bool = False
    last_health_check: Optional[datetime] = None
    
    # Networking
    ip_address: Optional[str] = None
    port: int = 8080
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class UpdateConfiguration:
    """Rolling update configuration"""
    strategy: UpdateStrategy = UpdateStrategy.ROLLING_UPDATE
    
    # Update parameters
    max_unavailable: Union[int, str] = 1  # Number or percentage
    max_surge: Union[int, str] = 1  # Number or percentage
    min_ready_seconds: int = 30
    progress_deadline_seconds: int = 600
    
    # Validation settings
    validation_enabled: bool = True
    validation_timeout_seconds: int = 300
    health_check_timeout_seconds: int = 60
    readiness_timeout_seconds: int = 120
    
    # Rollback settings
    auto_rollback_enabled: bool = True
    rollback_on_failure: bool = True
    rollback_timeout_seconds: int = 300
    
    # Advanced settings
    surge_strategy: str = "gradual"  # gradual, immediate
    termination_grace_period_seconds: int = 30
    pod_disruption_budget_enabled: bool = True
    
    # Custom hooks
    pre_update_hook: Optional[Callable] = None
    post_update_hook: Optional[Callable] = None
    pre_pod_creation_hook: Optional[Callable] = None
    post_pod_ready_hook: Optional[Callable] = None


@dataclass
class DeploymentSpec:
    """Deployment specification"""
    name: str
    namespace: str = "default"
    
    # Application details
    app_name: str = ""
    app_version: str = ""
    previous_version: str = ""
    
    # Replica configuration
    desired_replicas: int = 3
    current_replicas: int = 0
    ready_replicas: int = 0
    updated_replicas: int = 0
    
    # Container specification
    container_image: str = ""
    container_tag: str = ""
    container_port: int = 8080
    
    # Resource requirements
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    
    # Environment configuration
    environment_variables: Dict[str, str] = field(default_factory=dict)
    config_maps: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    
    # Service configuration
    service_type: str = "ClusterIP"
    service_port: int = 80
    target_port: int = 8080
    
    # Labels and selectors
    labels: Dict[str, str] = field(default_factory=dict)
    selector: Dict[str, str] = field(default_factory=dict)
    
    # Health checks
    liveness_probe: Dict[str, Any] = field(default_factory=dict)
    readiness_probe: Dict[str, Any] = field(default_factory=dict)
    startup_probe: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollingUpdateProgress:
    """Rolling update progress tracking"""
    update_id: str
    deployment_name: str
    start_time: datetime
    current_phase: UpdatePhase = UpdatePhase.PREPARATION
    status: UpdateStatus = UpdateStatus.PENDING
    
    # Progress metrics
    total_replicas: int = 0
    updated_replicas: int = 0
    ready_replicas: int = 0
    available_replicas: int = 0
    unavailable_replicas: int = 0
    
    # Timing
    phase_start_time: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None
    
    # Pod tracking
    old_pods: List[PodInstance] = field(default_factory=list)
    new_pods: List[PodInstance] = field(default_factory=list)
    terminating_pods: List[PodInstance] = field(default_factory=list)
    
    # Events and logs
    events: List[Dict[str, Any]] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    
    # Performance metrics
    update_duration_seconds: float = 0.0
    rollback_triggered: bool = False
    rollback_reason: Optional[str] = None


class PodManager:
    """Manages pod lifecycle during rolling updates"""
    
    def __init__(self) -> None:
        self.pods: Dict[str, PodInstance] = {}
        
    async def create_pod(
        self,
        spec: DeploymentSpec,
        version: str,
        pod_name: Optional[str] = None
    ) -> PodInstance:
        """Create a new pod"""
        try:
            if not pod_name:
                pod_name = f"{spec.name}-{version}-{uuid.uuid4().hex[:8]}"
            
            pod = PodInstance(
                name=pod_name,
                version=version,
                status=PodStatus.PENDING,
                port=spec.target_port,
                cpu_allocated=spec.cpu_request,
                memory_allocated=spec.memory_request,
                labels={
                    "app": spec.app_name,
                    "version": version,
                    "deployment": spec.name
                }
            )
            
            # Simulate pod creation
            logger.info(f"Creating pod {pod_name} with version {version}")
            await asyncio.sleep(1)  # Simulate creation time
            
            pod.status = PodStatus.RUNNING
            pod.started_at = datetime.utcnow()
            pod.ip_address = f"10.0.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}"
            
            self.pods[pod.id] = pod
            
            return pod
            
        except Exception as e:
            logger.error(f"Failed to create pod: {e}")
            raise

    async def wait_for_pod_ready(
        self,
        pod_id: str,
        timeout_seconds: int = 120
    ) -> bool:
        """Wait for pod to become ready"""
        try:
            if pod_id not in self.pods:
                return False
            
            pod = self.pods[pod_id]
            start_time = time.time()
            
            logger.info(f"Waiting for pod {pod.name} to become ready")
            
            while time.time() - start_time < timeout_seconds:
                # Simulate readiness check
                await asyncio.sleep(2)
                
                # Mock readiness progression
                elapsed = time.time() - start_time
                if elapsed > 10:  # After 10 seconds, consider ready
                    pod.health_check_passed = True
                    pod.readiness_check_passed = True
                    pod.status = PodStatus.READY
                    pod.ready_at = datetime.utcnow()
                    pod.last_health_check = datetime.utcnow()
                    
                    logger.info(f"Pod {pod.name} is ready")
                    return True
            
            logger.warning(f"Pod {pod.name} failed to become ready within {timeout_seconds}s")
            pod.status = PodStatus.FAILED
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for pod readiness: {e}")
            return False

    async def terminate_pod(
        self,
        pod_id: str,
        grace_period_seconds: int = 30
    ) -> bool:
        """Terminate a pod gracefully"""
        try:
            if pod_id not in self.pods:
                return False
            
            pod = self.pods[pod_id]
            logger.info(f"Terminating pod {pod.name}")
            
            # Mark as terminating
            pod.status = PodStatus.TERMINATING
            
            # Simulate graceful termination
            await asyncio.sleep(min(grace_period_seconds, 5))  # Simulate termination time
            
            pod.status = PodStatus.TERMINATED
            pod.terminated_at = datetime.utcnow()
            
            logger.info(f"Pod {pod.name} terminated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate pod: {e}")
            return False

    async def get_pod_health(self, pod_id: str) -> Dict[str, Any]:
        """Get pod health status"""
        try:
            if pod_id not in self.pods:
                return {"healthy": False, "error": "Pod not found"}
            
            pod = self.pods[pod_id]
            
            # Simulate health check
            if pod.status == PodStatus.READY:
                # Mock some resource usage
                pod.cpu_usage = np.random.uniform(10, 80)
                pod.memory_usage_mb = np.random.uniform(50, 200)
                
                return {
                    "healthy": True,
                    "status": pod.status.value,
                    "cpu_usage": pod.cpu_usage,
                    "memory_usage_mb": pod.memory_usage_mb,
                    "last_check": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "healthy": False,
                    "status": pod.status.value,
                    "message": f"Pod is in {pod.status.value} state"
                }
                
        except Exception as e:
            logger.error(f"Failed to get pod health: {e}")
            return {"healthy": False, "error": str(e)}

    def get_pods_by_version(self, version: str) -> List[PodInstance]:
        """Get all pods for a specific version"""
        return [pod for pod in self.pods.values() if pod.version == version]

    def get_ready_pods(self) -> List[PodInstance]:
        """Get all ready pods"""
        return [pod for pod in self.pods.values() if pod.status == PodStatus.READY]

    def cleanup_terminated_pods(self) -> None:
        """Clean up terminated pods"""
        terminated_pods = [
            pod_id for pod_id, pod in self.pods.items() 
            if pod.status == PodStatus.TERMINATED
        ]
        
        for pod_id in terminated_pods:
            del self.pods[pod_id]
        
        if terminated_pods:
            logger.info(f"Cleaned up {len(terminated_pods)} terminated pods")


class UpdateValidator:
    """Validates deployments during rolling updates"""
    
    def __init__(self) -> None:
        self.validation_cache: Dict[str, Dict[str, Any]] = {}
        
    async def validate_deployment_spec(self, spec: DeploymentSpec) -> Dict[str, Any]:
        """Validate deployment specification"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Basic validation
            if not spec.name:
                validation_result["errors"].append("Deployment name is required")
            
            if not spec.container_image:
                validation_result["errors"].append("Container image is required")
            
            if spec.desired_replicas <= 0:
                validation_result["errors"].append("Desired replicas must be greater than 0")
            
            # Resource validation
            if not self._validate_resource_spec(spec.cpu_request):
                validation_result["errors"].append("Invalid CPU request format")
            
            if not self._validate_resource_spec(spec.memory_request):
                validation_result["errors"].append("Invalid memory request format")
            
            # Health check validation
            if not spec.readiness_probe:
                validation_result["warnings"].append("No readiness probe configured")
            
            if not spec.liveness_probe:
                validation_result["warnings"].append("No liveness probe configured")
            
            # Set overall validity
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }

    def _validate_resource_spec(self, resource_spec: str) -> bool:
        """Validate Kubernetes resource specification"""
        try:
            # Simple validation for CPU/memory specs
            if resource_spec.endswith('m'):  # CPU millicores
                return int(resource_spec[:-1]) > 0
            elif resource_spec.endswith('Mi') or resource_spec.endswith('Gi'):  # Memory
                return int(resource_spec[:-2]) > 0
            else:
                return False
        except:
            return False

    async def validate_update_readiness(
        self,
        spec: DeploymentSpec,
        current_pods: List[PodInstance]
    ) -> Dict[str, Any]:
        """Validate if deployment is ready for update"""
        try:
            validation_result = {
                "ready": True,
                "issues": [],
                "recommendations": []
            }
            
            # Check current pod health
            healthy_pods = [pod for pod in current_pods if pod.status == PodStatus.READY]
            unhealthy_pods = [pod for pod in current_pods if pod.status != PodStatus.READY]
            
            if len(unhealthy_pods) > 0:
                validation_result["issues"].append(
                    f"{len(unhealthy_pods)} pods are not healthy"
                )
            
            # Check if minimum replicas are available
            if len(healthy_pods) < 1:
                validation_result["ready"] = False
                validation_result["issues"].append("No healthy pods available for update")
            
            # Resource utilization check
            avg_cpu = np.mean([pod.cpu_usage for pod in healthy_pods]) if healthy_pods else 0
            avg_memory = np.mean([pod.memory_usage_mb for pod in healthy_pods]) if healthy_pods else 0
            
            if avg_cpu > 80:
                validation_result["recommendations"].append(
                    f"High CPU utilization ({avg_cpu:.1f}%) - consider waiting for lower load"
                )
            
            if avg_memory > 400:  # Assuming 512Mi limit
                validation_result["recommendations"].append(
                    f"High memory utilization ({avg_memory:.0f}MB) - monitor memory usage"
                )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Update readiness validation failed: {e}")
            return {
                "ready": False,
                "issues": [str(e)],
                "recommendations": []
            }


class RollingUpdateOrchestrator:
    """
    Enterprise rolling update orchestrator for ML deployments
    """
    
    def __init__(self) -> None:
        self.pod_manager = PodManager()
        self.validator = UpdateValidator()
        self.active_updates: Dict[str, RollingUpdateProgress] = {}
        self.update_history: Dict[str, RollingUpdateProgress] = {}
        
    async def start_rolling_update(
        self,
        spec: DeploymentSpec,
        config: UpdateConfiguration
    ) -> RollingUpdateProgress:
        """Start a rolling update"""
        update_id = str(uuid.uuid4())
        
        progress = RollingUpdateProgress(
            update_id=update_id,
            deployment_name=spec.name,
            start_time=datetime.utcnow(),
            total_replicas=spec.desired_replicas
        )
        
        try:
            logger.info(f"Starting rolling update for {spec.name}")
            self.active_updates[update_id] = progress
            
            # Execute update phases
            await self._execute_update_phases(spec, config, progress)
            
            # Store in history
            self.update_history[update_id] = progress
            
            logger.info(f"Rolling update completed for {spec.name}: {progress.status.value}")
            return progress
            
        except Exception as e:
            progress.status = UpdateStatus.FAILED
            progress.error_messages.append(str(e))
            logger.error(f"Rolling update failed for {spec.name}: {e}")
            
            # Attempt rollback
            if config.auto_rollback_enabled:
                await self._rollback_update(spec, config, progress)
            
            return progress
        
        finally:
            progress.update_duration_seconds = (
                datetime.utcnow() - progress.start_time
            ).total_seconds()
            
            # Remove from active updates
            if update_id in self.active_updates:
                del self.active_updates[update_id]

    async def _execute_update_phases(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Execute all update phases"""
        try:
            # Phase 1: Preparation
            await self._phase_preparation(spec, config, progress)
            
            # Phase 2: Validation
            await self._phase_validation(spec, config, progress)
            
            # Phase 3: Deployment
            await self._phase_deployment(spec, config, progress)
            
            # Phase 4: Verification
            await self._phase_verification(spec, config, progress)
            
            # Phase 5: Completion
            await self._phase_completion(spec, config, progress)
            
        except Exception as e:
            logger.error(f"Update phase execution failed: {e}")
            raise

    async def _phase_preparation(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Preparation phase"""
        try:
            logger.info(f"Phase 1: Preparation for {spec.name}")
            progress.current_phase = UpdatePhase.PREPARATION
            progress.status = UpdateStatus.PREPARING
            progress.phase_start_time = datetime.utcnow()
            
            # Validate deployment spec
            validation_result = await self.validator.validate_deployment_spec(spec)
            if not validation_result["valid"]:
                raise Exception(f"Deployment validation failed: {validation_result['errors']}")
            
            # Get current pods
            current_pods = self.pod_manager.get_pods_by_version(spec.previous_version)
            progress.old_pods = current_pods
            progress.available_replicas = len([p for p in current_pods if p.status == PodStatus.READY])
            
            # Execute pre-update hook
            if config.pre_update_hook:
                logger.info("Executing pre-update hook")
                await config.pre_update_hook(spec, progress)
            
            self._add_event(progress, "Preparation phase completed")
            logger.info(f"Preparation phase completed for {spec.name}")
            
        except Exception as e:
            logger.error(f"Preparation phase failed: {e}")
            raise

    async def _phase_validation(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Validation phase"""
        try:
            logger.info(f"Phase 2: Validation for {spec.name}")
            progress.current_phase = UpdatePhase.VALIDATION
            progress.status = UpdateStatus.VALIDATING
            progress.phase_start_time = datetime.utcnow()
            
            # Validate update readiness
            current_pods = self.pod_manager.get_ready_pods()
            readiness_result = await self.validator.validate_update_readiness(spec, current_pods)
            
            if not readiness_result["ready"]:
                raise Exception(f"Update readiness validation failed: {readiness_result['issues']}")
            
            # Log recommendations
            for recommendation in readiness_result.get("recommendations", []):
                logger.warning(f"Recommendation: {recommendation}")
            
            self._add_event(progress, "Validation phase completed")
            logger.info(f"Validation phase completed for {spec.name}")
            
        except Exception as e:
            logger.error(f"Validation phase failed: {e}")
            raise

    async def _phase_deployment(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Deployment phase"""
        try:
            logger.info(f"Phase 3: Deployment for {spec.name}")
            progress.current_phase = UpdatePhase.DEPLOYMENT
            progress.status = UpdateStatus.DEPLOYING
            progress.phase_start_time = datetime.utcnow()
            
            # Calculate update parameters
            max_unavailable = self._calculate_max_unavailable(spec, config)
            max_surge = self._calculate_max_surge(spec, config)
            
            logger.info(f"Update parameters: max_unavailable={max_unavailable}, max_surge={max_surge}")
            
            # Execute rolling update strategy
            if config.strategy == UpdateStrategy.ROLLING_UPDATE:
                await self._execute_rolling_update(spec, config, progress, max_unavailable, max_surge)
            elif config.strategy == UpdateStrategy.BLUE_GREEN:
                await self._execute_blue_green_update(spec, config, progress)
            elif config.strategy == UpdateStrategy.RECREATE:
                await self._execute_recreate_update(spec, config, progress)
            else:
                await self._execute_rolling_update(spec, config, progress, max_unavailable, max_surge)
            
            self._add_event(progress, "Deployment phase completed")
            logger.info(f"Deployment phase completed for {spec.name}")
            
        except Exception as e:
            logger.error(f"Deployment phase failed: {e}")
            raise

    async def _execute_rolling_update(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress,
        max_unavailable -> None: int,
        max_surge -> None: int
    ) -> None:
        """Execute rolling update strategy"""
        try:
            target_replicas = spec.desired_replicas
            old_pods = progress.old_pods.copy()
            
            # Create new pods gradually
            pods_to_create = min(max_surge, target_replicas)
            
            for i in range(pods_to_create):
                # Create new pod
                new_pod = await self.pod_manager.create_pod(spec, spec.app_version)
                progress.new_pods.append(new_pod)
                
                # Execute pre-pod creation hook
                if config.pre_pod_creation_hook:
                    await config.pre_pod_creation_hook(new_pod, spec, progress)
                
                # Wait for pod to be ready
                pod_ready = await self.pod_manager.wait_for_pod_ready(
                    new_pod.id, config.readiness_timeout_seconds
                )
                
                if not pod_ready:
                    raise Exception(f"Pod {new_pod.name} failed to become ready")
                
                progress.ready_replicas += 1
                progress.updated_replicas += 1
                
                # Execute post-pod ready hook
                if config.post_pod_ready_hook:
                    await config.post_pod_ready_hook(new_pod, spec, progress)
                
                self._add_event(progress, f"New pod {new_pod.name} is ready")
                
                # Wait for minimum ready time
                await asyncio.sleep(config.min_ready_seconds)
                
                # Terminate old pod if we have enough new ones
                if len(progress.new_pods) > max_unavailable and old_pods:
                    old_pod = old_pods.pop(0)
                    progress.terminating_pods.append(old_pod)
                    
                    await self.pod_manager.terminate_pod(
                        old_pod.id, config.termination_grace_period_seconds
                    )
                    
                    progress.available_replicas = max(0, progress.available_replicas - 1)
                    self._add_event(progress, f"Old pod {old_pod.name} terminated")
            
            # Terminate remaining old pods
            for old_pod in old_pods:
                progress.terminating_pods.append(old_pod)
                await self.pod_manager.terminate_pod(
                    old_pod.id, config.termination_grace_period_seconds
                )
                self._add_event(progress, f"Old pod {old_pod.name} terminated")
            
            # Update final counts
            progress.available_replicas = len([p for p in progress.new_pods if p.status == PodStatus.READY])
            progress.unavailable_replicas = target_replicas - progress.available_replicas
            
        except Exception as e:
            logger.error(f"Rolling update execution failed: {e}")
            raise

    async def _execute_blue_green_update(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Execute blue-green update strategy"""
        try:
            # Create all new pods (green)
            for i in range(spec.desired_replicas):
                new_pod = await self.pod_manager.create_pod(spec, spec.app_version)
                progress.new_pods.append(new_pod)
                
                pod_ready = await self.pod_manager.wait_for_pod_ready(
                    new_pod.id, config.readiness_timeout_seconds
                )
                
                if not pod_ready:
                    raise Exception(f"Pod {new_pod.name} failed to become ready")
                
                progress.ready_replicas += 1
                progress.updated_replicas += 1
            
            # Switch traffic to new pods (would update service selector)
            await asyncio.sleep(2)  # Simulate traffic switch
            
            # Terminate all old pods (blue)
            for old_pod in progress.old_pods:
                progress.terminating_pods.append(old_pod)
                await self.pod_manager.terminate_pod(
                    old_pod.id, config.termination_grace_period_seconds
                )
            
            progress.available_replicas = len(progress.new_pods)
            progress.unavailable_replicas = 0
            
        except Exception as e:
            logger.error(f"Blue-green update execution failed: {e}")
            raise

    async def _execute_recreate_update(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Execute recreate update strategy"""
        try:
            # Terminate all old pods first
            for old_pod in progress.old_pods:
                progress.terminating_pods.append(old_pod)
                await self.pod_manager.terminate_pod(
                    old_pod.id, config.termination_grace_period_seconds
                )
            
            progress.available_replicas = 0
            progress.unavailable_replicas = spec.desired_replicas
            
            # Create all new pods
            for i in range(spec.desired_replicas):
                new_pod = await self.pod_manager.create_pod(spec, spec.app_version)
                progress.new_pods.append(new_pod)
                
                pod_ready = await self.pod_manager.wait_for_pod_ready(
                    new_pod.id, config.readiness_timeout_seconds
                )
                
                if not pod_ready:
                    raise Exception(f"Pod {new_pod.name} failed to become ready")
                
                progress.ready_replicas += 1
                progress.updated_replicas += 1
                progress.available_replicas += 1
                progress.unavailable_replicas -= 1
            
        except Exception as e:
            logger.error(f"Recreate update execution failed: {e}")
            raise

    async def _phase_verification(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Verification phase"""
        try:
            logger.info(f"Phase 4: Verification for {spec.name}")
            progress.current_phase = UpdatePhase.VERIFICATION
            progress.status = UpdateStatus.VERIFYING
            progress.phase_start_time = datetime.utcnow()
            
            # Verify all new pods are healthy
            for pod in progress.new_pods:
                health_status = await self.pod_manager.get_pod_health(pod.id)
                if not health_status.get("healthy", False):
                    raise Exception(f"Pod {pod.name} failed health verification")
            
            # Additional verification (could include functional tests)
            await asyncio.sleep(config.min_ready_seconds)
            
            self._add_event(progress, "Verification phase completed")
            logger.info(f"Verification phase completed for {spec.name}")
            
        except Exception as e:
            logger.error(f"Verification phase failed: {e}")
            raise

    async def _phase_completion(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Completion phase"""
        try:
            logger.info(f"Phase 5: Completion for {spec.name}")
            progress.current_phase = UpdatePhase.COMPLETION
            progress.status = UpdateStatus.COMPLETED
            progress.phase_start_time = datetime.utcnow()
            
            # Clean up terminated pods
            self.pod_manager.cleanup_terminated_pods()
            
            # Execute post-update hook
            if config.post_update_hook:
                logger.info("Executing post-update hook")
                await config.post_update_hook(spec, progress)
            
            # Update final status
            progress.total_replicas = spec.desired_replicas
            progress.updated_replicas = len(progress.new_pods)
            progress.ready_replicas = len([p for p in progress.new_pods if p.status == PodStatus.READY])
            progress.available_replicas = progress.ready_replicas
            progress.unavailable_replicas = progress.total_replicas - progress.available_replicas
            
            self._add_event(progress, "Rolling update completed successfully")
            logger.info(f"Completion phase finished for {spec.name}")
            
        except Exception as e:
            logger.error(f"Completion phase failed: {e}")
            raise

    def _calculate_max_unavailable(
        self, 
        spec: DeploymentSpec, 
        config: UpdateConfiguration
    ) -> int:
        """Calculate maximum unavailable pods"""
        if isinstance(config.max_unavailable, int):
            return config.max_unavailable
        elif isinstance(config.max_unavailable, str) and config.max_unavailable.endswith('%'):
            percentage = int(config.max_unavailable[:-1])
            return max(1, int(spec.desired_replicas * percentage / 100))
        else:
            return 1

    def _calculate_max_surge(
        self, 
        spec: DeploymentSpec, 
        config: UpdateConfiguration
    ) -> int:
        """Calculate maximum surge pods"""
        if isinstance(config.max_surge, int):
            return config.max_surge
        elif isinstance(config.max_surge, str) and config.max_surge.endswith('%'):
            percentage = int(config.max_surge[:-1])
            return max(1, int(spec.desired_replicas * percentage / 100))
        else:
            return 1

    def _add_event(self, progress -> None: RollingUpdateProgress, message -> None: str) -> None:
        """Add event to progress tracking"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "phase": progress.current_phase.value
        }
        progress.events.append(event)

    async def _rollback_update(
        self,
        spec -> None: DeploymentSpec,
        config -> None: UpdateConfiguration,
        progress -> None: RollingUpdateProgress
    ) -> None:
        """Rollback failed update"""
        try:
            logger.info(f"Starting rollback for {spec.name}")
            progress.current_phase = UpdatePhase.ROLLBACK
            progress.status = UpdateStatus.ROLLING_BACK
            progress.rollback_triggered = True
            
            # Terminate new pods
            for pod in progress.new_pods:
                await self.pod_manager.terminate_pod(
                    pod.id, config.termination_grace_period_seconds
                )
            
            # Recreate old pods if necessary
            if not progress.old_pods:
                for i in range(spec.desired_replicas):
                    old_pod = await self.pod_manager.create_pod(spec, spec.previous_version)
                    await self.pod_manager.wait_for_pod_ready(
                        old_pod.id, config.readiness_timeout_seconds
                    )
            
            progress.status = UpdateStatus.ROLLED_BACK
            self._add_event(progress, "Rollback completed")
            logger.info(f"Rollback completed for {spec.name}")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            progress.error_messages.append(f"Rollback failed: {e}")

    async def get_update_status(self, update_id: str) -> Optional[RollingUpdateProgress]:
        """Get update status"""
        if update_id in self.active_updates:
            return self.active_updates[update_id]
        elif update_id in self.update_history:
            return self.update_history[update_id]
        else:
            return None

    async def pause_update(self, update_id: str) -> bool:
        """Pause an active update"""
        try:
            if update_id in self.active_updates:
                progress = self.active_updates[update_id]
                progress.status = UpdateStatus.PAUSED
                self._add_event(progress, "Update paused")
                logger.info(f"Update {update_id} paused")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to pause update: {e}")
            return False

    async def resume_update(self, update_id: str) -> bool:
        """Resume a paused update"""
        try:
            if update_id in self.active_updates:
                progress = self.active_updates[update_id]
                if progress.status == UpdateStatus.PAUSED:
                    progress.status = UpdateStatus.DEPLOYING
                    self._add_event(progress, "Update resumed")
                    logger.info(f"Update {update_id} resumed")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume update: {e}")
            return False


# Factory functions
def create_rolling_update_orchestrator() -> RollingUpdateOrchestrator:
    """Create a new rolling update orchestrator instance"""
    return RollingUpdateOrchestrator()


def create_deployment_spec(
    name: str,
    app_name: str,
    app_version: str,
    replicas: int = 3
) -> DeploymentSpec:
    """Create a deployment specification"""
    return DeploymentSpec(
        name=name,
        app_name=app_name,
        app_version=app_version,
        desired_replicas=replicas,
        previous_version="previous"
    )


def create_update_configuration(
    strategy: UpdateStrategy = UpdateStrategy.ROLLING_UPDATE,
    max_unavailable: Union[int, str] = 1,
    max_surge: Union[int, str] = 1
) -> UpdateConfiguration:
    """Create update configuration"""
    return UpdateConfiguration(
        strategy=strategy,
        max_unavailable=max_unavailable,
        max_surge=max_surge
    )


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Create orchestrator
        orchestrator = create_rolling_update_orchestrator()
        
        # Create deployment spec
        spec = create_deployment_spec(
            name="ml-recommendation-engine",
            app_name="recommendation-engine",
            app_version="v2.1.0",
            replicas=5
        )
        
        # Set container details
        spec.container_image = "ml-models/recommendation-engine"
        spec.container_tag = "v2.1.0"
        spec.previous_version = "v2.0.0"
        
        # Create update configuration
        config = create_update_configuration(
            strategy=UpdateStrategy.ROLLING_UPDATE,
            max_unavailable="20%",
            max_surge="25%"
        )
        
        # Set timeouts
        config.readiness_timeout_seconds = 180
        config.min_ready_seconds = 30
        config.auto_rollback_enabled = True
        
        print(f"Starting rolling update for {spec.name}")
        print(f"Strategy: {config.strategy.value}")
        print(f"Updating from {spec.previous_version} to {spec.app_version}")
        print(f"Target replicas: {spec.desired_replicas}")
        
        # Start rolling update
        progress = await orchestrator.start_rolling_update(spec, config)
        
        print(f"\nRolling update completed:")
        print(f"- Status: {progress.status.value}")
        print(f"- Duration: {progress.update_duration_seconds:.1f} seconds")
        print(f"- Updated replicas: {progress.updated_replicas}/{progress.total_replicas}")
        print(f"- Ready replicas: {progress.ready_replicas}")
        print(f"- Available replicas: {progress.available_replicas}")
        
        if progress.rollback_triggered:
            print(f"- Rollback triggered: {progress.rollback_reason}")
        
        if progress.error_messages:
            print("\nErrors:")
            for error in progress.error_messages:
                print(f"- {error}")
        
        print(f"\nUpdate events ({len(progress.events)}):")
        for event in progress.events[-5:]:  # Show last 5 events
            print(f"- {event['timestamp']}: {event['message']}")
    
    asyncio.run(main())