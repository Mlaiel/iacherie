"""
Enterprise Blue-Green Deployer for MLOps
DevOps + Backend Senior implementation with advanced rollback and zero-downtime deployment
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Deployment environment colors"""
    BLUE = "blue"
    GREEN = "green"


class DeploymentPhase(Enum):
    """Deployment phases"""
    PREPARATION = "preparation"
    DEPLOYMENT = "deployment"
    HEALTH_CHECK = "health_check"
    TRAFFIC_SWITCH = "traffic_switch"
    VALIDATION = "validation"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    ROLLBACK = "rollback"


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class HealthCheckStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ModelEndpoint:
    """Model endpoint configuration"""
    endpoint_id: str
    model_id: str
    model_version: str
    environment: DeploymentEnvironment
    url: str
    port: int = 8080
    replicas: int = 1
    cpu_limit: str = "1000m"
    memory_limit: str = "1Gi"
    health_check_path: str = "/health"
    ready_check_path: str = "/ready"
    metrics_path: str = "/metrics"
    environment_variables: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "inactive"


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    initial_delay_seconds: int = 30
    period_seconds: int = 10
    timeout_seconds: int = 5
    failure_threshold: int = 3
    success_threshold: int = 1
    custom_checks: List[str] = field(default_factory=list)


@dataclass
class TrafficSplitConfig:
    """Traffic splitting configuration"""
    blue_percentage: int = 100
    green_percentage: int = 0
    ramp_up_duration_minutes: int = 10
    ramp_up_steps: int = 5
    enable_canary: bool = False
    canary_percentage: int = 5
    canary_duration_minutes: int = 5


@dataclass
class RollbackConfig:
    """Rollback configuration"""
    auto_rollback_enabled: bool = True
    rollback_on_health_failure: bool = True
    rollback_on_performance_degradation: bool = True
    rollback_threshold_error_rate: float = 0.05  # 5%
    rollback_threshold_latency_ms: float = 1000.0
    rollback_timeout_minutes: int = 5
    preserve_failed_deployment: bool = True


@dataclass
class DeploymentRequest:
    """Blue-green deployment request"""
    deployment_id: str
    model_id: str
    model_version: str
    source_image: str
    target_environment: DeploymentEnvironment
    replicas: int = 3
    resource_requirements: Dict[str, str] = field(default_factory=lambda: {
        "cpu": "500m", "memory": "512Mi"
    })
    environment_variables: Dict[str, str] = field(default_factory=dict)
    health_check_config: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    traffic_split_config: TrafficSplitConfig = field(default_factory=TrafficSplitConfig)
    rollback_config: RollbackConfig = field(default_factory=RollbackConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class DeploymentResult:
    """Deployment operation result"""
    deployment_id: str
    status: DeploymentStatus
    current_phase: DeploymentPhase
    blue_endpoint: Optional[ModelEndpoint] = None
    green_endpoint: Optional[ModelEndpoint] = None
    active_environment: Optional[DeploymentEnvironment] = None
    traffic_split: TrafficSplitConfig = field(default_factory=TrafficSplitConfig)
    health_status: Dict[str, HealthCheckStatus] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    deployment_log: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None


class HealthChecker:
    """Health check system for deployed models"""
    
    def __init__(self) -> None:
        self.health_cache = {}
        self.check_history = {}
    
    async def check_endpoint_health(self, endpoint: ModelEndpoint,
                                  config: HealthCheckConfig) -> HealthCheckStatus:
        """Perform comprehensive health check on endpoint"""
        try:
            logger.info(f"Checking health for endpoint {endpoint.endpoint_id}")
            
            # Simulate health check (in production, would make actual HTTP requests)
            await asyncio.sleep(0.1)
            
            # Basic connectivity check
            connectivity_ok = await self._check_connectivity(endpoint)
            if not connectivity_ok:
                return HealthCheckStatus.UNHEALTHY
            
            # Health endpoint check
            health_ok = await self._check_health_endpoint(endpoint, config)
            if not health_ok:
                return HealthCheckStatus.UNHEALTHY
            
            # Ready endpoint check
            ready_ok = await self._check_ready_endpoint(endpoint, config)
            if not ready_ok:
                return HealthCheckStatus.DEGRADED
            
            # Performance check
            performance_ok = await self._check_performance(endpoint, config)
            if not performance_ok:
                return HealthCheckStatus.DEGRADED
            
            # Custom checks
            custom_checks_ok = await self._run_custom_checks(endpoint, config)
            if not custom_checks_ok:
                return HealthCheckStatus.DEGRADED
            
            return HealthCheckStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Health check failed for {endpoint.endpoint_id}: {e}")
            return HealthCheckStatus.UNHEALTHY
    
    async def _check_connectivity(self, endpoint: ModelEndpoint) -> bool:
        """Check basic connectivity to endpoint"""
        # Simulate connectivity check
        await asyncio.sleep(0.05)
        return True  # Simulate success
    
    async def _check_health_endpoint(self, endpoint: ModelEndpoint,
                                   config: HealthCheckConfig) -> bool:
        """Check /health endpoint"""
        # Simulate health endpoint check
        await asyncio.sleep(0.05)
        return True  # Simulate healthy
    
    async def _check_ready_endpoint(self, endpoint: ModelEndpoint,
                                  config: HealthCheckConfig) -> bool:
        """Check /ready endpoint"""
        # Simulate readiness check
        await asyncio.sleep(0.05)
        return True  # Simulate ready
    
    async def _check_performance(self, endpoint: ModelEndpoint,
                               config: HealthCheckConfig) -> bool:
        """Check endpoint performance metrics"""
        # Simulate performance check
        await asyncio.sleep(0.1)
        
        # Check response time, throughput, error rate
        response_time_ms = 50.0  # Simulate good response time
        error_rate = 0.01  # Simulate low error rate
        
        return response_time_ms < 1000 and error_rate < 0.05
    
    async def _run_custom_checks(self, endpoint: ModelEndpoint,
                               config: HealthCheckConfig) -> bool:
        """Run custom health checks"""
        if not config.custom_checks:
            return True
        
        # Simulate custom checks
        await asyncio.sleep(0.1)
        return True  # Simulate success
    
    async def monitor_endpoint_health(self, endpoint: ModelEndpoint,
                                    config: HealthCheckConfig,
                                    duration_minutes: int = 5) -> List[Dict[str, Any]]:
        """Monitor endpoint health over time"""
        health_history = []
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            health_status = await self.check_endpoint_health(endpoint, config)
            
            health_record = {
                "timestamp": datetime.now().isoformat(),
                "endpoint_id": endpoint.endpoint_id,
                "status": health_status.value,
                "response_time_ms": 50.0 + (10 * len(health_history) % 5),  # Simulate varying response time
                "memory_usage_mb": 128 + (5 * len(health_history) % 10),  # Simulate memory usage
                "cpu_usage_percent": 15 + (3 * len(health_history) % 8)   # Simulate CPU usage
            }
            
            health_history.append(health_record)
            
            await asyncio.sleep(config.period_seconds)
        
        return health_history


class TrafficManager:
    """Manages traffic splitting between blue and green environments"""
    
    def __init__(self) -> None:
        self.traffic_rules = {}
        self.traffic_history = []
    
    async def configure_traffic_split(self, deployment_id: str,
                                    config: TrafficSplitConfig) -> Dict[str, Any]:
        """Configure traffic splitting rules"""
        try:
            logger.info(f"Configuring traffic split for deployment {deployment_id}")
            
            # Validate percentages
            if config.blue_percentage + config.green_percentage != 100:
                raise ValueError("Blue and green percentages must sum to 100")
            
            # Store traffic configuration
            self.traffic_rules[deployment_id] = config
            
            # Simulate load balancer configuration
            await asyncio.sleep(0.5)
            
            result = {
                "deployment_id": deployment_id,
                "blue_percentage": config.blue_percentage,
                "green_percentage": config.green_percentage,
                "canary_enabled": config.enable_canary,
                "configured_at": datetime.now().isoformat()
            }
            
            self.traffic_history.append(result)
            
            logger.info(f"Traffic split configured: {config.blue_percentage}% blue, {config.green_percentage}% green")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to configure traffic split: {e}")
            raise
    
    async def gradual_traffic_switch(self, deployment_id: str,
                                   from_env: DeploymentEnvironment,
                                   to_env: DeploymentEnvironment,
                                   duration_minutes: int = 10,
                                   steps: int = 5) -> List[Dict[str, Any]]:
        """Gradually switch traffic from one environment to another"""
        try:
            logger.info(f"Starting gradual traffic switch from {from_env.value} to {to_env.value}")
            
            switch_history = []
            step_duration = duration_minutes / steps
            
            for step in range(steps + 1):
                # Calculate traffic percentages
                progress = step / steps
                
                if to_env == DeploymentEnvironment.GREEN:
                    green_percentage = int(progress * 100)
                    blue_percentage = 100 - green_percentage
                else:
                    blue_percentage = int(progress * 100)
                    green_percentage = 100 - blue_percentage
                
                # Update traffic split
                config = TrafficSplitConfig(
                    blue_percentage=blue_percentage,
                    green_percentage=green_percentage
                )
                
                await self.configure_traffic_split(deployment_id, config)
                
                switch_record = {
                    "step": step,
                    "progress_percent": progress * 100,
                    "blue_percentage": blue_percentage,
                    "green_percentage": green_percentage,
                    "timestamp": datetime.now().isoformat()
                }
                
                switch_history.append(switch_record)
                
                # Wait before next step (except for last step)
                if step < steps:
                    await asyncio.sleep(step_duration * 60)  # Convert to seconds
            
            logger.info(f"Traffic switch completed: 100% to {to_env.value}")
            
            return switch_history
            
        except Exception as e:
            logger.error(f"Traffic switch failed: {e}")
            raise
    
    async def immediate_traffic_switch(self, deployment_id: str,
                                     to_env: DeploymentEnvironment) -> Dict[str, Any]:
        """Immediately switch all traffic to specified environment"""
        if to_env == DeploymentEnvironment.BLUE:
            config = TrafficSplitConfig(blue_percentage=100, green_percentage=0)
        else:
            config = TrafficSplitConfig(blue_percentage=0, green_percentage=100)
        
        return await self.configure_traffic_split(deployment_id, config)
    
    def get_current_traffic_split(self, deployment_id: str) -> Optional[TrafficSplitConfig]:
        """Get current traffic split configuration"""
        return self.traffic_rules.get(deployment_id)


class ModelDeployer:
    """Handles model deployment to specific environments"""
    
    def __init__(self) -> None:
        self.deployed_models = {}
        self.deployment_history = []
    
    async def deploy_model(self, request: DeploymentRequest,
                         environment: DeploymentEnvironment) -> ModelEndpoint:
        """Deploy model to specified environment"""
        try:
            endpoint_id = f"{request.model_id}-{environment.value}-{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Deploying model {request.model_id} v{request.model_version} to {environment.value}")
            
            # Create endpoint configuration
            endpoint = ModelEndpoint(
                endpoint_id=endpoint_id,
                model_id=request.model_id,
                model_version=request.model_version,
                environment=environment,
                url=f"https://{environment.value}.ainflue.com/models/{request.model_id}",
                replicas=request.replicas,
                cpu_limit=request.resource_requirements.get("cpu", "500m"),
                memory_limit=request.resource_requirements.get("memory", "512Mi"),
                environment_variables=request.environment_variables.copy()
            )
            
            # Simulate deployment process
            await self._prepare_deployment(endpoint, request)
            await self._deploy_containers(endpoint, request)
            await self._configure_networking(endpoint, request)
            await self._setup_monitoring(endpoint, request)
            
            endpoint.status = "active"
            
            # Store deployed endpoint
            self.deployed_models[endpoint_id] = endpoint
            
            self.deployment_history.append({
                "endpoint_id": endpoint_id,
                "model_id": request.model_id,
                "model_version": request.model_version,
                "environment": environment.value,
                "deployed_at": datetime.now().isoformat(),
                "deployment_id": request.deployment_id
            })
            
            logger.info(f"Model deployed successfully to {environment.value}: {endpoint_id}")
            
            return endpoint
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            raise
    
    async def _prepare_deployment(self, endpoint -> None: ModelEndpoint, request -> None: DeploymentRequest) -> None:
        """Prepare deployment environment"""
        logger.info(f"Preparing deployment for {endpoint.endpoint_id}")
        await asyncio.sleep(1)  # Simulate preparation time
    
    async def _deploy_containers(self, endpoint -> None: ModelEndpoint, request -> None: DeploymentRequest) -> None:
        """Deploy model containers"""
        logger.info(f"Deploying containers for {endpoint.endpoint_id}")
        await asyncio.sleep(2)  # Simulate container deployment
    
    async def _configure_networking(self, endpoint -> None: ModelEndpoint, request -> None: DeploymentRequest) -> None:
        """Configure networking for endpoint"""
        logger.info(f"Configuring networking for {endpoint.endpoint_id}")
        await asyncio.sleep(0.5)  # Simulate network configuration
    
    async def _setup_monitoring(self, endpoint -> None: ModelEndpoint, request -> None: DeploymentRequest) -> None:
        """Setup monitoring for endpoint"""
        logger.info(f"Setting up monitoring for {endpoint.endpoint_id}")
        await asyncio.sleep(0.5)  # Simulate monitoring setup
    
    async def undeploy_model(self, endpoint_id: str) -> bool:
        """Undeploy model from environment"""
        try:
            if endpoint_id not in self.deployed_models:
                logger.warning(f"Endpoint {endpoint_id} not found")
                return False
            
            endpoint = self.deployed_models[endpoint_id]
            
            logger.info(f"Undeploying model from {endpoint.environment.value}: {endpoint_id}")
            
            # Simulate undeployment process
            await asyncio.sleep(1)
            
            # Remove from deployed models
            del self.deployed_models[endpoint_id]
            
            logger.info(f"Model undeployed successfully: {endpoint_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Model undeployment failed: {e}")
            return False
    
    def get_endpoint(self, endpoint_id: str) -> Optional[ModelEndpoint]:
        """Get endpoint by ID"""
        return self.deployed_models.get(endpoint_id)
    
    def list_endpoints(self, environment: Optional[DeploymentEnvironment] = None) -> List[ModelEndpoint]:
        """List all endpoints, optionally filtered by environment"""
        endpoints = list(self.deployed_models.values())
        
        if environment:
            endpoints = [ep for ep in endpoints if ep.environment == environment]
        
        return endpoints


class BlueGreenDeployer:
    """Main Blue-Green deployment orchestrator"""
    
    def __init__(self) -> None:
        self.health_checker = HealthChecker()
        self.traffic_manager = TrafficManager()
        self.model_deployer = ModelDeployer()
        self.active_deployments = {}
        self.deployment_history = []
    
    async def deploy(self, request: DeploymentRequest) -> str:
        """Execute blue-green deployment"""
        try:
            logger.info(f"Starting blue-green deployment: {request.deployment_id}")
            
            # Initialize deployment result
            result = DeploymentResult(
                deployment_id=request.deployment_id,
                status=DeploymentStatus.IN_PROGRESS,
                current_phase=DeploymentPhase.PREPARATION
            )
            
            self.active_deployments[request.deployment_id] = result
            
            try:
                # Phase 1: Preparation
                await self._prepare_deployment(request, result)
                
                # Phase 2: Deploy to target environment
                result.current_phase = DeploymentPhase.DEPLOYMENT
                await self._deploy_to_target_environment(request, result)
                
                # Phase 3: Health checks
                result.current_phase = DeploymentPhase.HEALTH_CHECK
                await self._perform_health_checks(request, result)
                
                # Phase 4: Traffic switching
                result.current_phase = DeploymentPhase.TRAFFIC_SWITCH
                await self._switch_traffic(request, result)
                
                # Phase 5: Validation
                result.current_phase = DeploymentPhase.VALIDATION
                await self._validate_deployment(request, result)
                
                # Phase 6: Cleanup
                result.current_phase = DeploymentPhase.CLEANUP
                await self._cleanup_old_deployment(request, result)
                
                # Deployment completed
                result.status = DeploymentStatus.COMPLETED
                result.current_phase = DeploymentPhase.COMPLETED
                result.completed_at = datetime.now()
                result.deployment_log.append("Blue-green deployment completed successfully")
                
                logger.info(f"Blue-green deployment completed: {request.deployment_id}")
                
                return request.deployment_id
                
            except Exception as e:
                # Handle deployment failure
                await self._handle_deployment_failure(request, result, str(e))
                raise
            
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            raise
    
    async def _prepare_deployment(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Prepare for deployment"""
        result.deployment_log.append("Preparing blue-green deployment")
        
        # Determine current active environment
        current_endpoints = self.model_deployer.list_endpoints()
        current_active = None
        
        for endpoint in current_endpoints:
            if endpoint.model_id == request.model_id and endpoint.status == "active":
                current_active = endpoint.environment
                break
        
        # Determine target environment (opposite of current or specified)
        if current_active:
            if current_active == DeploymentEnvironment.BLUE:
                target_env = DeploymentEnvironment.GREEN
            else:
                target_env = DeploymentEnvironment.BLUE
        else:
            target_env = request.target_environment
        
        result.deployment_log.append(f"Target environment: {target_env.value}")
        result.metadata["target_environment"] = target_env.value
        result.metadata["current_active"] = current_active.value if current_active else None
        
        await asyncio.sleep(0.5)  # Simulate preparation
    
    async def _deploy_to_target_environment(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Deploy model to target environment"""
        target_env = DeploymentEnvironment(result.metadata["target_environment"])
        
        result.deployment_log.append(f"Deploying to {target_env.value} environment")
        
        # Deploy model
        endpoint = await self.model_deployer.deploy_model(request, target_env)
        
        if target_env == DeploymentEnvironment.BLUE:
            result.blue_endpoint = endpoint
        else:
            result.green_endpoint = endpoint
        
        result.deployment_log.append(f"Model deployed to {target_env.value}: {endpoint.endpoint_id}")
    
    async def _perform_health_checks(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Perform comprehensive health checks"""
        target_env = DeploymentEnvironment(result.metadata["target_environment"])
        target_endpoint = result.blue_endpoint if target_env == DeploymentEnvironment.BLUE else result.green_endpoint
        
        result.deployment_log.append("Performing health checks on new deployment")
        
        # Wait for initial startup
        await asyncio.sleep(request.health_check_config.initial_delay_seconds)
        
        # Perform health checks
        health_status = await self.health_checker.check_endpoint_health(
            target_endpoint, request.health_check_config
        )
        
        result.health_status[target_endpoint.endpoint_id] = health_status
        
        if health_status != HealthCheckStatus.HEALTHY:
            raise Exception(f"Health check failed: {health_status.value}")
        
        result.deployment_log.append("Health checks passed")
    
    async def _switch_traffic(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Switch traffic to new deployment"""
        target_env = DeploymentEnvironment(result.metadata["target_environment"])
        
        result.deployment_log.append(f"Switching traffic to {target_env.value} environment")
        
        if request.traffic_split_config.ramp_up_duration_minutes > 0:
            # Gradual traffic switch
            current_env = DeploymentEnvironment.BLUE if target_env == DeploymentEnvironment.GREEN else DeploymentEnvironment.GREEN
            
            switch_history = await self.traffic_manager.gradual_traffic_switch(
                request.deployment_id,
                current_env,
                target_env,
                request.traffic_split_config.ramp_up_duration_minutes,
                request.traffic_split_config.ramp_up_steps
            )
            
            result.metadata["traffic_switch_history"] = switch_history
        else:
            # Immediate traffic switch
            await self.traffic_manager.immediate_traffic_switch(request.deployment_id, target_env)
        
        result.active_environment = target_env
        result.traffic_split = TrafficSplitConfig(
            blue_percentage=100 if target_env == DeploymentEnvironment.BLUE else 0,
            green_percentage=100 if target_env == DeploymentEnvironment.GREEN else 0
        )
        
        result.deployment_log.append("Traffic switched successfully")
    
    async def _validate_deployment(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Validate deployment after traffic switch"""
        result.deployment_log.append("Validating deployment")
        
        target_env = DeploymentEnvironment(result.metadata["target_environment"])
        target_endpoint = result.blue_endpoint if target_env == DeploymentEnvironment.BLUE else result.green_endpoint
        
        # Monitor health for validation period
        health_history = await self.health_checker.monitor_endpoint_health(
            target_endpoint, request.health_check_config, duration_minutes=2
        )
        
        # Check for any health issues
        unhealthy_checks = [h for h in health_history if h["status"] != HealthCheckStatus.HEALTHY.value]
        
        if unhealthy_checks:
            failure_rate = len(unhealthy_checks) / len(health_history)
            if failure_rate > 0.1:  # 10% failure threshold
                raise Exception(f"Validation failed: {failure_rate:.1%} health check failures")
        
        result.metadata["validation_health_history"] = health_history
        result.deployment_log.append("Deployment validation passed")
    
    async def _cleanup_old_deployment(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Clean up old deployment"""
        current_active = result.metadata.get("current_active")
        
        if current_active:
            old_env = DeploymentEnvironment(current_active)
            result.deployment_log.append(f"Cleaning up old {old_env.value} deployment")
            
            # Find and undeploy old endpoint
            old_endpoints = self.model_deployer.list_endpoints(old_env)
            for endpoint in old_endpoints:
                if endpoint.model_id == request.model_id:
                    await self.model_deployer.undeploy_model(endpoint.endpoint_id)
                    result.deployment_log.append(f"Cleaned up old endpoint: {endpoint.endpoint_id}")
                    break
        
        result.deployment_log.append("Cleanup completed")
    
    async def _handle_deployment_failure(self, request -> None: DeploymentRequest, 
                                       result -> None: DeploymentResult, error_message -> None: str) -> None:
        """Handle deployment failure and rollback if needed"""
        result.status = DeploymentStatus.FAILED
        result.error_message = error_message
        result.deployment_log.append(f"Deployment failed: {error_message}")
        
        if request.rollback_config.auto_rollback_enabled:
            result.current_phase = DeploymentPhase.ROLLBACK
            result.status = DeploymentStatus.ROLLING_BACK
            result.deployment_log.append("Initiating automatic rollback")
            
            try:
                await self._perform_rollback(request, result)
                result.status = DeploymentStatus.ROLLED_BACK
                result.rollback_reason = error_message
                result.deployment_log.append("Automatic rollback completed")
                
            except Exception as rollback_error:
                result.deployment_log.append(f"Rollback failed: {rollback_error}")
    
    async def _perform_rollback(self, request -> None: DeploymentRequest, result -> None: DeploymentResult) -> None:
        """Perform rollback to previous deployment"""
        target_env = DeploymentEnvironment(result.metadata["target_environment"])
        current_active = result.metadata.get("current_active")
        
        if current_active:
            # Switch traffic back to previous environment
            old_env = DeploymentEnvironment(current_active)
            await self.traffic_manager.immediate_traffic_switch(request.deployment_id, old_env)
            result.active_environment = old_env
            
            # Clean up failed deployment if configured
            if not request.rollback_config.preserve_failed_deployment:
                target_endpoint = result.blue_endpoint if target_env == DeploymentEnvironment.BLUE else result.green_endpoint
                if target_endpoint:
                    await self.model_deployer.undeploy_model(target_endpoint.endpoint_id)
    
    async def rollback_deployment(self, deployment_id: str, reason: str = "") -> bool:
        """Manually rollback a deployment"""
        try:
            if deployment_id not in self.active_deployments:
                logger.warning(f"Deployment {deployment_id} not found")
                return False
            
            result = self.active_deployments[deployment_id]
            
            if result.status != DeploymentStatus.COMPLETED:
                logger.warning(f"Cannot rollback deployment {deployment_id}: status is {result.status}")
                return False
            
            logger.info(f"Rolling back deployment {deployment_id}: {reason}")
            
            result.status = DeploymentStatus.ROLLING_BACK
            result.current_phase = DeploymentPhase.ROLLBACK
            result.rollback_reason = reason
            result.deployment_log.append(f"Manual rollback initiated: {reason}")
            
            # Create a dummy request for rollback
            request = DeploymentRequest(
                deployment_id=deployment_id,
                model_id="",  # Will be filled from result metadata
                model_version="",
                source_image="",
                target_environment=result.active_environment,
                rollback_config=RollbackConfig()
            )
            
            await self._perform_rollback(request, result)
            
            result.status = DeploymentStatus.ROLLED_BACK
            result.deployment_log.append("Manual rollback completed")
            
            logger.info(f"Deployment {deployment_id} rolled back successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for deployment {deployment_id}: {e}")
            return False
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        if deployment_id not in self.active_deployments:
            return None
        
        result = self.active_deployments[deployment_id]
        
        return {
            "deployment_id": result.deployment_id,
            "status": result.status.value,
            "current_phase": result.current_phase.value,
            "active_environment": result.active_environment.value if result.active_environment else None,
            "blue_endpoint": {
                "endpoint_id": result.blue_endpoint.endpoint_id,
                "url": result.blue_endpoint.url,
                "status": result.blue_endpoint.status
            } if result.blue_endpoint else None,
            "green_endpoint": {
                "endpoint_id": result.green_endpoint.endpoint_id,
                "url": result.green_endpoint.url,
                "status": result.green_endpoint.status
            } if result.green_endpoint else None,
            "traffic_split": {
                "blue_percentage": result.traffic_split.blue_percentage,
                "green_percentage": result.traffic_split.green_percentage
            },
            "health_status": {k: v.value for k, v in result.health_status.items()},
            "performance_metrics": result.performance_metrics,
            "started_at": result.started_at.isoformat(),
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "error_message": result.error_message,
            "rollback_reason": result.rollback_reason,
            "deployment_log": result.deployment_log,
            "metadata": result.metadata
        }
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        return [
            self.get_deployment_status(deployment_id)
            for deployment_id in self.active_deployments.keys()
        ]


# Factory function
def create_blue_green_deployer() -> BlueGreenDeployer:
    """Create a configured blue-green deployer"""
    return BlueGreenDeployer()


# Export main classes
__all__ = [
    "BlueGreenDeployer",
    "DeploymentRequest",
    "DeploymentResult",
    "ModelEndpoint",
    "DeploymentEnvironment",
    "DeploymentStatus",
    "DeploymentPhase",
    "HealthCheckConfig",
    "TrafficSplitConfig",
    "RollbackConfig",
    "HealthCheckStatus",
    "create_blue_green_deployer"
]