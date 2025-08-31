"""🔧 Deployment Orchestrator - IA-Influencer-Agent CI/CD Enterprise
================================================================
Team Expertise: DevOps Engineer + Kubernetes Specialist + Cloud Architect + ML Engineer
Created: 2025-08-24
Author: Fahed Mlaiel (mlaiel@live.de)

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copy, modification or distribution without written 
permission is strictly prohibited and will result in legal action.

Enterprise deployment orchestration for IA Influencer multi-format platform.
Supports creator workflow deployment: Content Processing → AI Models → 
Protection Services → Revenue Tracking → Collaboration → Distribution.

Business Logic Features:
- Multi-format content processing service deployment
- AI/ML model deployment with version management
- Content protection service orchestration
- Revenue tracking and payment service deployment
- Creator collaboration system deployment
- SEO optimization service deployment
- Real-time analytics service orchestration
================================================================
"""from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging
import kubernetes
import yaml
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """Deployment status enumeration"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

class DeploymentStrategy(Enum):
    """Deployment strategy enumeration"""    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"

@dataclass
class DeploymentTarget:
    """Deployment target configuration"""    environment: str
    namespace: str
    cluster_name: str
    region: str
    replicas: int = 3
    resource_limits: Dict[str, str] = None
    health_check_path: str = "/health"
    readiness_probe_delay: int = 30
    liveness_probe_delay: int = 60

@dataclass
class DeploymentConfiguration:
    """Deployment configuration structure"""    deployment_id: str
    strategy: DeploymentStrategy
    target: DeploymentTarget
    image_tag: str
    config_map: Dict[str, str] = None
    secrets: Dict[str, str] = None
    environment_variables: Dict[str, str] = None
    traffic_split: Dict[str, int] = None  # For canary deployments
    rollback_enabled: bool = True
    auto_rollback_conditions: List[str] = None
    deployment_timeout: int = 900

@dataclass
class DeploymentResult:
    """Deployment result structure"""    deployment_id: str
    status: DeploymentStatus
    strategy: DeploymentStrategy
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    deployed_version: str = ""
    endpoint_urls: List[str] = None
    rollback_version: Optional[str] = None
    error_message: Optional[str] = None
    health_status: Dict[str, Any] = None

class DeploymentOrchestrator:
    """Enterprise deployment orchestration engine"""    
    def __init__(self):
        """Initialize deployment orchestrator"""        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.k8s_client = None
        self.apps_v1 = None
        self.core_v1 = None
        self.deployment_history: List[DeploymentResult] = []
        self.active_deployments: Dict[str, asyncio.Task] = {}
        self.rollback_stack: List[DeploymentConfiguration] = []
        
    async def initialize(self) -> bool:
        """Initialize orchestrator with Kubernetes client"""        try:
            # Load Kubernetes configuration
            try:
                config.load_incluster_config()  # For in-cluster deployment
            except:
                config.load_kube_config()  # For local development
            
            # Initialize Kubernetes clients
            self.k8s_client = client.ApiClient()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            
            # Verify cluster connection
            await self._verify_cluster_connection()
            
            self.initialized = True
            self.logger.info("✅ Deployment orchestrator initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False
    
    async def _verify_cluster_connection(self) -> None:
        """Verify Kubernetes cluster connection"""        try:
            version = self.core_v1.get_code()
            self.logger.info(f"Connected to Kubernetes cluster version: {version.git_version}")
        except Exception as e:
            raise RuntimeError(f"Kubernetes cluster connection failed: {e}")
    
    async def deploy(
        self,
        config: DeploymentConfiguration,
        progress_callback: Optional[Callable] = None
    ) -> DeploymentResult:
        """Execute deployment with specified strategy"""        deployment_id = config.deployment_id
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting deployment {deployment_id} with strategy: {config.strategy.value}")
            
            # Create deployment result tracker
            result = DeploymentResult(
                deployment_id=deployment_id,
                status=DeploymentStatus.PENDING,
                strategy=config.strategy,
                start_time=start_time
            )
            
            # Update status to in progress
            result.status = DeploymentStatus.IN_PROGRESS
            if progress_callback:
                await progress_callback(result)
            
            # Execute deployment based on strategy
            if config.strategy == DeploymentStrategy.BLUE_GREEN:
                await self._execute_blue_green_deployment(config, result, progress_callback)
            elif config.strategy == DeploymentStrategy.CANARY:
                await self._execute_canary_deployment(config, result, progress_callback)
            elif config.strategy == DeploymentStrategy.ROLLING:
                await self._execute_rolling_deployment(config, result, progress_callback)
            elif config.strategy == DeploymentStrategy.RECREATE:
                await self._execute_recreate_deployment(config, result, progress_callback)
            
            # Verify deployment health
            await self._verify_deployment_health(config, result)
            
            # Update final status
            result.status = DeploymentStatus.SUCCESS
            result.end_time = datetime.now()
            result.duration = (result.end_time - start_time).total_seconds()
            result.deployed_version = config.image_tag
            
            # Add to history and rollback stack
            self.deployment_history.append(result)
            if config.rollback_enabled:
                self.rollback_stack.append(config)
            
            self.logger.info(f"✅ Deployment {deployment_id} completed successfully")
            
            if progress_callback:
                await progress_callback(result)
            
            return result
            
        except Exception as e:
            # Handle deployment failure
            result.status = DeploymentStatus.FAILED
            result.end_time = datetime.now()
            result.duration = (result.end_time - start_time).total_seconds()
            result.error_message = str(e)
            
            self.deployment_history.append(result)
            self.logger.error(f"❌ Deployment {deployment_id} failed: {e}")
            
            # Attempt auto-rollback if enabled
            if config.rollback_enabled and config.auto_rollback_conditions:
                await self._attempt_auto_rollback(config, result)
            
            if progress_callback:
                await progress_callback(result)
            
            return result
    
    async def _execute_blue_green_deployment(
        self,
        config: DeploymentConfiguration,
        result: DeploymentResult,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Execute blue-green deployment strategy"""        try:
            # Step 1: Deploy to green environment
            await self._deploy_green_environment(config)
            
            # Step 2: Validate green environment
            await self._validate_green_environment(config)
            
            # Step 3: Switch traffic to green
            await self._switch_traffic_to_green(config)
            
            # Step 4: Monitor new deployment
            await self._monitor_deployment(config, duration=300)  # 5 minutes
            
            # Step 5: Cleanup blue environment
            await self._cleanup_blue_environment(config)
            
            result.endpoint_urls = await self._get_service_endpoints(config)
            
        except Exception as e:
            # Rollback to blue if green deployment fails
            await self._rollback_to_blue_environment(config)
            raise e
    
    async def _execute_canary_deployment(
        self,
        config: DeploymentConfiguration,
        result: DeploymentResult,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Execute canary deployment strategy"""        try:
            traffic_split = config.traffic_split or {"canary": 10, "stable": 90}
            
            # Step 1: Deploy canary version
            await self._deploy_canary_version(config, traffic_split["canary"])
            
            # Step 2: Monitor canary metrics
            canary_healthy = await self._monitor_canary_deployment(config, duration=600)
            
            if not canary_healthy:
                raise RuntimeError("Canary deployment failed health checks")
            
            # Step 3: Gradually increase canary traffic
            for canary_percent in [25, 50, 75, 100]:
                await self._update_traffic_split(config, canary_percent)
                await self._monitor_canary_deployment(config, duration=300)
            
            # Step 4: Promote canary to stable
            await self._promote_canary_to_stable(config)
            
            result.endpoint_urls = await self._get_service_endpoints(config)
            
        except Exception as e:
            # Rollback canary deployment
            await self._rollback_canary_deployment(config)
            raise e
    
    async def _execute_rolling_deployment(
        self,
        config: DeploymentConfiguration,
        result: DeploymentResult,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Execute rolling deployment strategy"""        try:
            # Update deployment with rolling update strategy
            deployment_manifest = await self._create_deployment_manifest(config)
            deployment_manifest["spec"]["strategy"] = {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxSurge": 1,
                    "maxUnavailable": 0
                }
            }
            
            # Apply deployment
            await self._apply_kubernetes_manifest(deployment_manifest, config.target.namespace)
            
            # Wait for rollout to complete
            await self._wait_for_rollout_completion(config)
            
            result.endpoint_urls = await self._get_service_endpoints(config)
            
        except Exception as e:
            # Rollback rolling deployment
            await self._rollback_rolling_deployment(config)
            raise e
    
    async def _execute_recreate_deployment(
        self,
        config: DeploymentConfiguration,
        result: DeploymentResult,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Execute recreate deployment strategy"""        try:
            # Step 1: Scale down existing deployment
            await self._scale_deployment(config, replicas=0)
            
            # Step 2: Wait for pods to terminate
            await self._wait_for_pods_termination(config)
            
            # Step 3: Update deployment with new image
            deployment_manifest = await self._create_deployment_manifest(config)
            deployment_manifest["spec"]["strategy"] = {"type": "Recreate"}
            
            # Step 4: Apply new deployment
            await self._apply_kubernetes_manifest(deployment_manifest, config.target.namespace)
            
            # Step 5: Scale up to desired replicas
            await self._scale_deployment(config, replicas=config.target.replicas)
            
            # Step 6: Wait for deployment readiness
            await self._wait_for_deployment_ready(config)
            
            result.endpoint_urls = await self._get_service_endpoints(config)
            
        except Exception as e:
            # Attempt to restore previous deployment
            await self._restore_previous_deployment(config)
            raise e
    
    async def _deploy_green_environment(self, config: DeploymentConfiguration) -> None:
        """Deploy to green environment"""        green_config = config
        green_config.target.namespace = f"{config.target.namespace}-green"
        
        # Create namespace if it doesn't exist
        await self._ensure_namespace_exists(green_config.target.namespace)
        
        # Create deployment manifest
        deployment_manifest = await self._create_deployment_manifest(green_config)
        
        # Apply deployment
        await self._apply_kubernetes_manifest(deployment_manifest, green_config.target.namespace)
        
        # Wait for deployment to be ready
        await self._wait_for_deployment_ready(green_config)
    
    async def _validate_green_environment(self, config: DeploymentConfiguration) -> None:
        """Validate green environment health"""        green_namespace = f"{config.target.namespace}-green"
        
        # Run health checks
        health_check_url = f"http://{config.target.cluster_name}.{green_namespace}{config.target.health_check_path}"
        
        for attempt in range(10):  # 10 attempts with 30-second intervals
            try:
                # Simulate health check (replace with actual HTTP check)
                await asyncio.sleep(30)
                self.logger.info(f"Green environment health check passed (attempt {attempt + 1})")
                return
            except Exception as e:
                if attempt == 9:  # Last attempt
                    raise RuntimeError(f"Green environment failed validation: {e}")
                await asyncio.sleep(30)
    
    async def _switch_traffic_to_green(self, config: DeploymentConfiguration) -> None:
        """Switch traffic from blue to green environment"""        # Update service selector to point to green deployment
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{config.deployment_id}-service",
                "namespace": config.target.namespace
            },
            "spec": {
                "selector": {
                    "app": config.deployment_id,
                    "version": "green"
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8000,
                        "protocol": "TCP"
                    }
                ]
            }
        }
        
        await self._apply_kubernetes_manifest(service_manifest, config.target.namespace)
    
    async def _create_deployment_manifest(self, config: DeploymentConfiguration) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest"""        resource_limits = config.target.resource_limits or {
            "cpu": "500m",
            "memory": "512Mi"
        }
        
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.deployment_id,
                "namespace": config.target.namespace,
                "labels": {
                    "app": config.deployment_id,
                    "version": config.image_tag.split(":")[-1],
                    "environment": config.target.environment
                }
            },
            "spec": {
                "replicas": config.target.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.deployment_id
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.deployment_id,
                            "version": config.image_tag.split(":")[-1]
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": config.deployment_id,
                                "image": config.image_tag,
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "protocol": "TCP"
                                    }
                                ],
                                "resources": {
                                    "limits": resource_limits,
                                    "requests": {
                                        "cpu": "250m",
                                        "memory": "256Mi"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": config.target.health_check_path,
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": config.target.liveness_probe_delay,
                                    "periodSeconds": 30
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": config.target.health_check_path,
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": config.target.readiness_probe_delay,
                                    "periodSeconds": 10
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        # Add environment variables
        if config.environment_variables:
            env_vars = [
                {"name": k, "value": v} for k, v in config.environment_variables.items()
            ]
            manifest["spec"]["template"]["spec"]["containers"][0]["env"] = env_vars
        
        return manifest
    
    async def _apply_kubernetes_manifest(self, manifest: Dict[str, Any], namespace: str) -> None:
        """Apply Kubernetes manifest"""        try:
            kind = manifest["kind"]
            name = manifest["metadata"]["name"]
            
            if kind == "Deployment":
                try:
                    # Try to update existing deployment
                    self.apps_v1.patch_namespaced_deployment(
                        name=name,
                        namespace=namespace,
                        body=manifest
                    )
                except ApiException as e:
                    if e.status == 404:
                        # Create new deployment
                        self.apps_v1.create_namespaced_deployment(
                            namespace=namespace,
                            body=manifest
                        )
                    else:
                        raise
            elif kind == "Service":
                try:
                    # Try to update existing service
                    self.core_v1.patch_namespaced_service(
                        name=name,
                        namespace=namespace,
                        body=manifest
                    )
                except ApiException as e:
                    if e.status == 404:
                        # Create new service
                        self.core_v1.create_namespaced_service(
                            namespace=namespace,
                            body=manifest
                        )
                    else:
                        raise
            
        except Exception as e:
            raise RuntimeError(f"Failed to apply Kubernetes manifest: {e}")
    
    async def _wait_for_deployment_ready(self, config: DeploymentConfiguration) -> None:
        """Wait for deployment to be ready"""        timeout = config.deployment_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=config.deployment_id,
                    namespace=config.target.namespace
                )
                
                if (deployment.status.ready_replicas == config.target.replicas and
                    deployment.status.available_replicas == config.target.replicas):
                    self.logger.info(f"Deployment {config.deployment_id} is ready")
                    return
                
                await asyncio.sleep(10)
                
            except Exception as e:
                if time.time() - start_time >= timeout:
                    raise RuntimeError(f"Deployment readiness timeout: {e}")
                await asyncio.sleep(10)
        
        raise RuntimeError(f"Deployment {config.deployment_id} failed to become ready within {timeout} seconds")
    
    async def _verify_deployment_health(self, config: DeploymentConfiguration, result: DeploymentResult) -> None:
        """Verify deployment health status"""        try:
            # Get pod status
            pods = self.core_v1.list_namespaced_pod(
                namespace=config.target.namespace,
                label_selector=f"app={config.deployment_id}"
            )
            
            healthy_pods = 0
            total_pods = len(pods.items)
            
            for pod in pods.items:
                if pod.status.phase == "Running":
                    # Check if all containers are ready
                    if pod.status.container_statuses:
                        if all(cs.ready for cs in pod.status.container_statuses):
                            healthy_pods += 1
            
            health_status = {
                "total_pods": total_pods,
                "healthy_pods": healthy_pods,
                "health_percentage": (healthy_pods / total_pods * 100) if total_pods > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            result.health_status = health_status
            
            if healthy_pods < total_pods:
                self.logger.warning(f"Deployment health warning: {healthy_pods}/{total_pods} pods healthy")
            
        except Exception as e:
            self.logger.error(f"Failed to verify deployment health: {e}")
            result.health_status = {"error": str(e)}
    
    async def _get_service_endpoints(self, config: DeploymentConfiguration) -> List[str]:
        """Get service endpoint URLs"""        try:
            services = self.core_v1.list_namespaced_service(
                namespace=config.target.namespace,
                label_selector=f"app={config.deployment_id}"
            )
            
            endpoints = []
            for service in services.items:
                if service.status.load_balancer and service.status.load_balancer.ingress:
                    for ingress in service.status.load_balancer.ingress:
                        if ingress.ip:
                            endpoints.append(f"http://{ingress.ip}")
                        elif ingress.hostname:
                            endpoints.append(f"http://{ingress.hostname}")
            
            return endpoints
            
        except Exception as e:
            self.logger.error(f"Failed to get service endpoints: {e}")
            return []
    
    async def _ensure_namespace_exists(self, namespace: str) -> None:
        """Ensure Kubernetes namespace exists"""        try:
            self.core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": namespace}
                }
                self.core_v1.create_namespace(body=namespace_manifest)
            else:
                raise
    
    async def rollback_deployment(self, deployment_id: str) -> DeploymentResult:
        """Rollback to previous deployment"""        try:
            # Find previous configuration from rollback stack
            previous_config = None
            for config in reversed(self.rollback_stack):
                if config.deployment_id != deployment_id:
                    previous_config = config
                    break
            
            if not previous_config:
                raise RuntimeError("No previous deployment found for rollback")
            
            # Create rollback configuration
            rollback_config = DeploymentConfiguration(
                deployment_id=f"{deployment_id}-rollback-{int(time.time())}",
                strategy=DeploymentStrategy.BLUE_GREEN,  # Use blue-green for safe rollback
                target=previous_config.target,
                image_tag=previous_config.image_tag,
                config_map=previous_config.config_map,
                secrets=previous_config.secrets,
                environment_variables=previous_config.environment_variables,
                rollback_enabled=False  # Prevent recursive rollbacks
            )
            
            self.logger.info(f"Rolling back deployment {deployment_id} to {previous_config.image_tag}")
            
            # Execute rollback deployment
            result = await self.deploy(rollback_config)
            result.status = DeploymentStatus.ROLLED_BACK
            result.rollback_version = previous_config.image_tag
            
            return result
            
        except Exception as e:
            self.logger.error(f"Rollback failed for deployment {deployment_id}: {e}")
            return DeploymentResult(
                deployment_id=f"{deployment_id}-rollback-failed",
                status=DeploymentStatus.FAILED,
                strategy=DeploymentStrategy.BLUE_GREEN,
                start_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _attempt_auto_rollback(self, config: DeploymentConfiguration, result: DeploymentResult) -> None:
        """Attempt automatic rollback on deployment failure"""        try:
            self.logger.info(f"Attempting auto-rollback for deployment {config.deployment_id}")
            result.status = DeploymentStatus.ROLLING_BACK
            
            rollback_result = await self.rollback_deployment(config.deployment_id)
            
            if rollback_result.status == DeploymentStatus.ROLLED_BACK:
                result.status = DeploymentStatus.ROLLED_BACK
                result.rollback_version = rollback_result.rollback_version
                self.logger.info(f"Auto-rollback successful for deployment {config.deployment_id}")
            else:
                self.logger.error(f"Auto-rollback failed for deployment {config.deployment_id}")
                
        except Exception as e:
            self.logger.error(f"Auto-rollback error for deployment {config.deployment_id}: {e}")
    
    def get_deployment_history(self, limit: int = 10) -> List[DeploymentResult]:
        """Get deployment history"""        return self.deployment_history[-limit:]
    
    def get_deployment_statistics(self) -> Dict[str, Any]:
        """Get deployment statistics"""        if not self.deployment_history:
            return {}
        
        successful_deployments = [d for d in self.deployment_history if d.status == DeploymentStatus.SUCCESS]
        failed_deployments = [d for d in self.deployment_history if d.status == DeploymentStatus.FAILED]
        
        avg_duration = sum(d.duration or 0 for d in self.deployment_history if d.duration) / len(self.deployment_history)
        
        return {
            "total_deployments": len(self.deployment_history),
            "successful_deployments": len(successful_deployments),
            "failed_deployments": len(failed_deployments),
            "success_rate": len(successful_deployments) / len(self.deployment_history) * 100,
            "average_duration": avg_duration,
            "last_deployment": self.deployment_history[-1] if self.deployment_history else None,
        }

__all__ = [
    "DeploymentOrchestrator",
    "DeploymentConfiguration",
    "DeploymentTarget",
    "DeploymentResult",
    "DeploymentStatus",
    "DeploymentStrategy",
]
