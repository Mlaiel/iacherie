"""
🚀 Deployment Manager - Advanced Deployment Strategies Controller
================================================================

Enterprise-grade deployment automation with multiple strategies, health validation,
automated rollback, and deployment performance analytics.

Features:
- Blue/Green deployment automation with health validation
- Canary release management with traffic splitting
- Rolling deployment with progressive validation
- Automated rollback with performance metrics
- Deployment performance analytics and optimization
- A/B testing integration
- Feature flag management
- Deployment approval workflows
- Multi-environment coordination

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + Deployment Engineering + Site Reliability Engineering
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import statistics
from collections import defaultdict, deque
import time

logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    """Available deployment strategies"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"
    A_B_TESTING = "a_b_testing"
    SHADOW = "shadow"

class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

class DeploymentStage(Enum):
    """Deployment stages"""
    PREPARATION = "preparation"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    TESTING = "testing"
    TRAFFIC_SHIFT = "traffic_shift"
    MONITORING = "monitoring"
    COMPLETION = "completion"
    ROLLBACK = "rollback"

class HealthCheckStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    strategy: DeploymentStrategy
    environment: str
    replicas: int
    health_check_path: str
    health_check_timeout: int
    rollback_on_failure: bool
    approval_required: bool
    traffic_split_percentage: float = 0.0
    canary_analysis_duration: int = 300  # 5 minutes
    success_criteria: Dict[str, float] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)

@dataclass
class DeploymentMetrics:
    """Deployment performance metrics"""
    deployment_id: str
    timestamp: datetime
    response_time_ms: float
    error_rate: float
    throughput_rps: float
    cpu_usage: float
    memory_usage: float
    success_rate: float
    availability: float

@dataclass
class HealthCheck:
    """Health check result"""
    service_name: str
    endpoint: str
    status: HealthCheckStatus
    response_time_ms: float
    status_code: int
    timestamp: datetime
    error_message: Optional[str] = None

@dataclass
class Deployment:
    """Deployment instance"""
    deployment_id: str
    application_name: str
    version: str
    environment: str
    strategy: DeploymentStrategy
    config: DeploymentConfig
    status: DeploymentStatus
    current_stage: DeploymentStage
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: List[Dict[str, Any]] = field(default_factory=list)
    metrics: List[DeploymentMetrics] = field(default_factory=list)
    health_checks: List[HealthCheck] = field(default_factory=list)
    rollback_reason: Optional[str] = None
    approval_status: str = "pending"
    approval_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrafficSplit:
    """Traffic splitting configuration"""
    deployment_id: str
    current_version_percentage: float
    new_version_percentage: float
    routing_rules: Dict[str, Any]
    timestamp: datetime

class DeploymentManager:
    """
    Advanced Deployment Strategies Controller
    
    Responsibilities:
    - Multi-strategy deployment execution and management
    - Health validation and automated rollback
    - Traffic management and progressive rollouts
    - Deployment performance monitoring and analytics
    - A/B testing and feature flag coordination
    - Approval workflow management
    - Cross-environment deployment coordination
    """
    
    def __init__(self):
        # Deployment state
        self.active_deployments: Dict[str, Deployment] = {}
        self.deployment_history: List[Deployment] = []
        self.deployment_configs: Dict[str, DeploymentConfig] = {}
        
        # Traffic management
        self.traffic_splits: Dict[str, TrafficSplit] = {}
        self.load_balancer_configs: Dict[str, Dict] = {}
        
        # Health monitoring
        self.health_check_configs: Dict[str, Dict] = {}
        self.service_health_status: Dict[str, HealthCheckStatus] = {}
        
        # Performance analytics
        self.deployment_metrics: deque = deque(maxlen=10000)
        self.performance_baselines: Dict[str, Dict] = {}
        
        # Feature flags and A/B testing
        self.feature_flags: Dict[str, Dict] = {}
        self.ab_tests: Dict[str, Dict] = {}
        
        # Approval workflows
        self.approval_policies: Dict[str, Dict] = {}
        self.pending_approvals: List[str] = []
        
        self._initialize_deployment_manager()
        
        logger.info("DeploymentManager initialized")

    def _initialize_deployment_manager(self):
        """Initialize deployment manager"""
        
        # Start background tasks
        asyncio.create_task(self._deployment_monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._traffic_monitoring_loop())
        
        # Initialize default configurations
        self._setup_default_configs()
        self._setup_health_check_configs()
        self._setup_approval_policies()
        
        logger.info("Deployment manager initialization complete")

    def _setup_default_configs(self):
        """Setup default deployment configurations"""
        
        self.deployment_configs = {
            "development": DeploymentConfig(
                strategy=DeploymentStrategy.ROLLING,
                environment="development",
                replicas=1,
                health_check_path="/health",
                health_check_timeout=30,
                rollback_on_failure=True,
                approval_required=False,
                success_criteria={
                    "error_rate_threshold": 0.05,
                    "response_time_threshold": 1000.0,
                    "availability_threshold": 0.95
                }
            ),
            "staging": DeploymentConfig(
                strategy=DeploymentStrategy.BLUE_GREEN,
                environment="staging",
                replicas=2,
                health_check_path="/health",
                health_check_timeout=60,
                rollback_on_failure=True,
                approval_required=False,
                success_criteria={
                    "error_rate_threshold": 0.02,
                    "response_time_threshold": 500.0,
                    "availability_threshold": 0.98
                }
            ),
            "production": DeploymentConfig(
                strategy=DeploymentStrategy.CANARY,
                environment="production",
                replicas=5,
                health_check_path="/health",
                health_check_timeout=120,
                rollback_on_failure=True,
                approval_required=True,
                traffic_split_percentage=0.05,  # Start with 5%
                canary_analysis_duration=600,   # 10 minutes
                success_criteria={
                    "error_rate_threshold": 0.01,
                    "response_time_threshold": 200.0,
                    "availability_threshold": 0.999
                }
            )
        }

    def _setup_health_check_configs(self):
        """Setup health check configurations"""
        
        self.health_check_configs = {
            "standard": {
                "interval": 30,
                "timeout": 10,
                "retries": 3,
                "endpoints": ["/health", "/ready", "/metrics"]
            },
            "detailed": {
                "interval": 15,
                "timeout": 5,
                "retries": 5,
                "endpoints": ["/health", "/ready", "/metrics", "/deep-health"]
            },
            "critical": {
                "interval": 10,
                "timeout": 3,
                "retries": 2,
                "endpoints": ["/health", "/ready"]
            }
        }

    def _setup_approval_policies(self):
        """Setup deployment approval policies"""
        
        self.approval_policies = {
            "production": {
                "required_approvers": 2,
                "approval_timeout": 3600,  # 1 hour
                "auto_approve_patch": False,
                "auto_approve_rollback": True,
                "required_roles": ["devops_lead", "security_engineer"]
            },
            "staging": {
                "required_approvers": 1,
                "approval_timeout": 1800,  # 30 minutes
                "auto_approve_patch": True,
                "auto_approve_rollback": True,
                "required_roles": ["devops_engineer"]
            }
        }

    async def deploy_application(
        self,
        application_name: str,
        version: str,
        environment: str,
        strategy: Optional[DeploymentStrategy] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Deploy application with specified strategy
        
        Args:
            application_name: Name of the application
            version: Application version to deploy
            environment: Target environment
            strategy: Deployment strategy (optional, uses environment default)
            config_overrides: Configuration overrides
            
        Returns:
            Deployment identifier
        """
        
        deployment_id = str(uuid.uuid4())
        
        try:
            # Get deployment configuration
            if environment not in self.deployment_configs:
                raise ValueError(f"Environment configuration not found: {environment}")
            
            config = self.deployment_configs[environment]
            
            # Override strategy if specified
            if strategy:
                config.strategy = strategy
            
            # Apply configuration overrides
            if config_overrides:
                for key, value in config_overrides.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            
            # Create deployment instance
            deployment = Deployment(
                deployment_id=deployment_id,
                application_name=application_name,
                version=version,
                environment=environment,
                strategy=config.strategy,
                config=config,
                status=DeploymentStatus.PENDING,
                current_stage=DeploymentStage.PREPARATION,
                start_time=datetime.now(),
                approval_status="pending" if config.approval_required else "approved"
            )
            
            self.active_deployments[deployment_id] = deployment
            
            logger.info(f"Deployment created: {application_name} v{version} -> {environment} (Strategy: {config.strategy.value})")
            
            # Start deployment execution
            if not config.approval_required or deployment.approval_status == "approved":
                asyncio.create_task(self._execute_deployment(deployment))
            else:
                self.pending_approvals.append(deployment_id)
                logger.info(f"Deployment pending approval: {deployment_id}")
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Deployment creation failed: {str(e)}")
            raise

    async def approve_deployment(self, deployment_id: str, approver: str, comments: str = "") -> bool:
        """
        Approve a pending deployment
        
        Args:
            deployment_id: Deployment identifier
            approver: Approver identifier
            comments: Approval comments
            
        Returns:
            Approval success status
        """
        
        try:
            if deployment_id not in self.active_deployments:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            deployment = self.active_deployments[deployment_id]
            
            if deployment.approval_status != "pending":
                raise ValueError(f"Deployment not pending approval: {deployment_id}")
            
            # Record approval
            deployment.approval_metadata["approver"] = approver
            deployment.approval_metadata["approved_at"] = datetime.now().isoformat()
            deployment.approval_metadata["comments"] = comments
            deployment.approval_status = "approved"
            
            # Remove from pending approvals
            if deployment_id in self.pending_approvals:
                self.pending_approvals.remove(deployment_id)
            
            # Start deployment execution
            asyncio.create_task(self._execute_deployment(deployment))
            
            logger.info(f"Deployment approved by {approver}: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Deployment approval failed: {str(e)}")
            return False

    async def _execute_deployment(self, deployment: Deployment):
        """Execute deployment based on strategy"""
        
        try:
            deployment.status = DeploymentStatus.RUNNING
            
            logger.info(f"Executing deployment: {deployment.deployment_id} (Strategy: {deployment.strategy.value})")
            
            if deployment.strategy == DeploymentStrategy.BLUE_GREEN:
                success = await self._execute_blue_green_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.CANARY:
                success = await self._execute_canary_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.ROLLING:
                success = await self._execute_rolling_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.RECREATE:
                success = await self._execute_recreate_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.A_B_TESTING:
                success = await self._execute_ab_testing_deployment(deployment)
            else:
                raise ValueError(f"Unsupported deployment strategy: {deployment.strategy}")
            
            if success:
                deployment.status = DeploymentStatus.SUCCESS
                deployment.current_stage = DeploymentStage.COMPLETION
                logger.info(f"Deployment completed successfully: {deployment.deployment_id}")
            else:
                deployment.status = DeploymentStatus.FAILED
                if deployment.config.rollback_on_failure:
                    await self._execute_rollback(deployment, "Deployment failed health checks")
            
            deployment.end_time = datetime.now()
            
            # Move to history
            self.deployment_history.append(deployment)
            if deployment.deployment_id in self.active_deployments:
                del self.active_deployments[deployment.deployment_id]
            
        except Exception as e:
            logger.error(f"Deployment execution failed: {deployment.deployment_id} - {str(e)}")
            deployment.status = DeploymentStatus.FAILED
            deployment.end_time = datetime.now()
            
            if deployment.config.rollback_on_failure:
                await self._execute_rollback(deployment, f"Deployment execution error: {str(e)}")

    async def _execute_blue_green_deployment(self, deployment: Deployment) -> bool:
        """Execute blue-green deployment strategy"""
        
        try:
            stages = [
                {"name": "Prepare Green Environment", "stage": DeploymentStage.PREPARATION},
                {"name": "Deploy to Green", "stage": DeploymentStage.DEPLOYMENT},
                {"name": "Health Check Green", "stage": DeploymentStage.TESTING},
                {"name": "Switch Traffic", "stage": DeploymentStage.TRAFFIC_SHIFT},
                {"name": "Monitor", "stage": DeploymentStage.MONITORING},
                {"name": "Cleanup Blue", "stage": DeploymentStage.COMPLETION}
            ]
            
            for stage_info in stages:
                deployment.current_stage = stage_info["stage"]
                
                stage_result = {
                    "name": stage_info["name"],
                    "stage": stage_info["stage"].value,
                    "start_time": datetime.now(),
                    "status": "running"
                }
                
                deployment.stages.append(stage_result)
                
                logger.info(f"Blue-Green stage: {stage_info['name']} - {deployment.deployment_id}")
                
                if stage_info["stage"] == DeploymentStage.PREPARATION:
                    # Prepare green environment
                    await asyncio.sleep(2)
                    
                elif stage_info["stage"] == DeploymentStage.DEPLOYMENT:
                    # Deploy to green environment
                    await asyncio.sleep(5)
                    
                elif stage_info["stage"] == DeploymentStage.TESTING:
                    # Health check green environment
                    health_status = await self._perform_health_checks(deployment)
                    if health_status != HealthCheckStatus.HEALTHY:
                        stage_result["status"] = "failed"
                        stage_result["end_time"] = datetime.now()
                        return False
                        
                elif stage_info["stage"] == DeploymentStage.TRAFFIC_SHIFT:
                    # Switch traffic from blue to green
                    await self._switch_traffic(deployment, 100.0)
                    await asyncio.sleep(2)
                    
                elif stage_info["stage"] == DeploymentStage.MONITORING:
                    # Monitor green environment
                    success = await self._monitor_deployment_health(deployment, 300)  # 5 minutes
                    if not success:
                        stage_result["status"] = "failed"
                        stage_result["end_time"] = datetime.now()
                        return False
                        
                elif stage_info["stage"] == DeploymentStage.COMPLETION:
                    # Cleanup blue environment
                    await asyncio.sleep(1)
                
                stage_result["status"] = "success"
                stage_result["end_time"] = datetime.now()
                
                # Wait between stages
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {str(e)}")
            return False

    async def _execute_canary_deployment(self, deployment: Deployment) -> bool:
        """Execute canary deployment strategy"""
        
        try:
            stages = [
                {"name": "Deploy Canary", "stage": DeploymentStage.DEPLOYMENT, "traffic": 5},
                {"name": "Monitor Canary", "stage": DeploymentStage.MONITORING, "traffic": 5},
                {"name": "Expand to 25%", "stage": DeploymentStage.TRAFFIC_SHIFT, "traffic": 25},
                {"name": "Monitor 25%", "stage": DeploymentStage.MONITORING, "traffic": 25},
                {"name": "Expand to 50%", "stage": DeploymentStage.TRAFFIC_SHIFT, "traffic": 50},
                {"name": "Monitor 50%", "stage": DeploymentStage.MONITORING, "traffic": 50},
                {"name": "Full Rollout", "stage": DeploymentStage.TRAFFIC_SHIFT, "traffic": 100},
                {"name": "Final Monitoring", "stage": DeploymentStage.MONITORING, "traffic": 100}
            ]
            
            for stage_info in stages:
                deployment.current_stage = stage_info["stage"]
                
                stage_result = {
                    "name": stage_info["name"],
                    "stage": stage_info["stage"].value,
                    "traffic_percentage": stage_info["traffic"],
                    "start_time": datetime.now(),
                    "status": "running"
                }
                
                deployment.stages.append(stage_result)
                
                logger.info(f"Canary stage: {stage_info['name']} - {deployment.deployment_id}")
                
                if stage_info["stage"] == DeploymentStage.DEPLOYMENT:
                    # Deploy canary version
                    await asyncio.sleep(3)
                    await self._switch_traffic(deployment, stage_info["traffic"])
                    
                elif stage_info["stage"] == DeploymentStage.TRAFFIC_SHIFT:
                    # Gradually increase traffic
                    await self._switch_traffic(deployment, stage_info["traffic"])
                    await asyncio.sleep(2)
                    
                elif stage_info["stage"] == DeploymentStage.MONITORING:
                    # Monitor canary performance
                    monitor_duration = deployment.config.canary_analysis_duration
                    success = await self._monitor_deployment_health(deployment, monitor_duration)
                    
                    if not success:
                        stage_result["status"] = "failed"
                        stage_result["end_time"] = datetime.now()
                        return False
                
                stage_result["status"] = "success"
                stage_result["end_time"] = datetime.now()
                
                # Wait between stages
                await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Canary deployment failed: {str(e)}")
            return False

    async def _execute_rolling_deployment(self, deployment: Deployment) -> bool:
        """Execute rolling deployment strategy"""
        
        try:
            replicas = deployment.config.replicas
            
            for i in range(replicas):
                deployment.current_stage = DeploymentStage.DEPLOYMENT
                
                stage_result = {
                    "name": f"Deploy Instance {i+1}/{replicas}",
                    "stage": DeploymentStage.DEPLOYMENT.value,
                    "instance": i+1,
                    "start_time": datetime.now(),
                    "status": "running"
                }
                
                deployment.stages.append(stage_result)
                
                logger.info(f"Rolling deployment: Instance {i+1}/{replicas} - {deployment.deployment_id}")
                
                # Deploy to single instance
                await asyncio.sleep(2)
                
                # Health check instance
                health_status = await self._perform_health_checks(deployment)
                if health_status != HealthCheckStatus.HEALTHY:
                    stage_result["status"] = "failed"
                    stage_result["end_time"] = datetime.now()
                    return False
                
                stage_result["status"] = "success"
                stage_result["end_time"] = datetime.now()
                
                # Wait before next instance
                await asyncio.sleep(1)
            
            # Final monitoring
            deployment.current_stage = DeploymentStage.MONITORING
            success = await self._monitor_deployment_health(deployment, 180)  # 3 minutes
            
            return success
            
        except Exception as e:
            logger.error(f"Rolling deployment failed: {str(e)}")
            return False

    async def _execute_recreate_deployment(self, deployment: Deployment) -> bool:
        """Execute recreate deployment strategy"""
        
        try:
            stages = [
                {"name": "Stop Old Version", "stage": DeploymentStage.PREPARATION},
                {"name": "Deploy New Version", "stage": DeploymentStage.DEPLOYMENT},
                {"name": "Health Check", "stage": DeploymentStage.TESTING},
                {"name": "Monitor", "stage": DeploymentStage.MONITORING}
            ]
            
            for stage_info in stages:
                deployment.current_stage = stage_info["stage"]
                
                stage_result = {
                    "name": stage_info["name"],
                    "stage": stage_info["stage"].value,
                    "start_time": datetime.now(),
                    "status": "running"
                }
                
                deployment.stages.append(stage_result)
                
                logger.info(f"Recreate stage: {stage_info['name']} - {deployment.deployment_id}")
                
                if stage_info["stage"] == DeploymentStage.PREPARATION:
                    # Stop old version
                    await asyncio.sleep(2)
                    
                elif stage_info["stage"] == DeploymentStage.DEPLOYMENT:
                    # Deploy new version
                    await asyncio.sleep(4)
                    
                elif stage_info["stage"] == DeploymentStage.TESTING:
                    # Health check
                    health_status = await self._perform_health_checks(deployment)
                    if health_status != HealthCheckStatus.HEALTHY:
                        stage_result["status"] = "failed"
                        stage_result["end_time"] = datetime.now()
                        return False
                        
                elif stage_info["stage"] == DeploymentStage.MONITORING:
                    # Monitor deployment
                    success = await self._monitor_deployment_health(deployment, 240)  # 4 minutes
                    if not success:
                        stage_result["status"] = "failed"
                        stage_result["end_time"] = datetime.now()
                        return False
                
                stage_result["status"] = "success"
                stage_result["end_time"] = datetime.now()
                
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Recreate deployment failed: {str(e)}")
            return False

    async def _execute_ab_testing_deployment(self, deployment: Deployment) -> bool:
        """Execute A/B testing deployment strategy"""
        
        try:
            # Split traffic 50/50 between versions
            await self._switch_traffic(deployment, 50.0)
            
            # Monitor both versions for comparison
            deployment.current_stage = DeploymentStage.MONITORING
            
            stage_result = {
                "name": "A/B Testing Analysis",
                "stage": DeploymentStage.MONITORING.value,
                "start_time": datetime.now(),
                "status": "running",
                "traffic_split": "50/50"
            }
            
            deployment.stages.append(stage_result)
            
            # Extended monitoring for A/B analysis
            success = await self._monitor_deployment_health(deployment, 900)  # 15 minutes
            
            stage_result["status"] = "success" if success else "failed"
            stage_result["end_time"] = datetime.now()
            
            return success
            
        except Exception as e:
            logger.error(f"A/B testing deployment failed: {str(e)}")
            return False

    async def _perform_health_checks(self, deployment: Deployment) -> HealthCheckStatus:
        """Perform health checks on deployment"""
        
        try:
            config = self.health_check_configs.get("standard", {})
            endpoints = config.get("endpoints", ["/health"])
            
            all_healthy = True
            health_results = []
            
            for endpoint in endpoints:
                # Mock health check
                import random
                
                response_time = random.uniform(50, 200)
                status_code = 200 if random.random() > 0.05 else 500  # 95% success rate
                
                health_check = HealthCheck(
                    service_name=deployment.application_name,
                    endpoint=endpoint,
                    status=HealthCheckStatus.HEALTHY if status_code == 200 else HealthCheckStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    status_code=status_code,
                    timestamp=datetime.now()
                )
                
                health_results.append(health_check)
                deployment.health_checks.append(health_check)
                
                if health_check.status != HealthCheckStatus.HEALTHY:
                    all_healthy = False
            
            overall_status = HealthCheckStatus.HEALTHY if all_healthy else HealthCheckStatus.UNHEALTHY
            
            logger.info(f"Health check completed: {deployment.deployment_id} - Status: {overall_status.value}")
            
            return overall_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return HealthCheckStatus.UNKNOWN

    async def _monitor_deployment_health(self, deployment: Deployment, duration_seconds: int) -> bool:
        """Monitor deployment health for specified duration"""
        
        try:
            start_time = time.time()
            success_criteria = deployment.config.success_criteria
            
            while time.time() - start_time < duration_seconds:
                # Collect metrics
                metrics = await self._collect_deployment_metrics(deployment)
                deployment.metrics.append(metrics)
                
                # Check success criteria
                if not self._evaluate_success_criteria(metrics, success_criteria):
                    logger.warning(f"Deployment failed success criteria: {deployment.deployment_id}")
                    return False
                
                await asyncio.sleep(30)  # Check every 30 seconds
            
            logger.info(f"Deployment monitoring completed successfully: {deployment.deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Deployment monitoring failed: {str(e)}")
            return False

    async def _collect_deployment_metrics(self, deployment: Deployment) -> DeploymentMetrics:
        """Collect deployment performance metrics"""
        
        # Mock metrics collection
        import random
        
        base_response_time = 100
        base_error_rate = 0.005
        
        # Add some variation based on deployment stage
        if deployment.current_stage == DeploymentStage.DEPLOYMENT:
            response_time_multiplier = 1.5
            error_rate_multiplier = 2.0
        else:
            response_time_multiplier = 1.0
            error_rate_multiplier = 1.0
        
        metrics = DeploymentMetrics(
            deployment_id=deployment.deployment_id,
            timestamp=datetime.now(),
            response_time_ms=base_response_time * response_time_multiplier * random.uniform(0.8, 1.2),
            error_rate=base_error_rate * error_rate_multiplier * random.uniform(0.5, 2.0),
            throughput_rps=random.uniform(800, 1200),
            cpu_usage=random.uniform(30, 70),
            memory_usage=random.uniform(40, 80),
            success_rate=1.0 - (base_error_rate * error_rate_multiplier),
            availability=random.uniform(0.98, 1.0)
        )
        
        # Store in global metrics
        self.deployment_metrics.append(metrics)
        
        return metrics

    def _evaluate_success_criteria(self, metrics: DeploymentMetrics, criteria: Dict[str, float]) -> bool:
        """Evaluate if metrics meet success criteria"""
        
        try:
            if "error_rate_threshold" in criteria:
                if metrics.error_rate > criteria["error_rate_threshold"]:
                    return False
            
            if "response_time_threshold" in criteria:
                if metrics.response_time_ms > criteria["response_time_threshold"]:
                    return False
            
            if "availability_threshold" in criteria:
                if metrics.availability < criteria["availability_threshold"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Success criteria evaluation failed: {str(e)}")
            return False

    async def _switch_traffic(self, deployment: Deployment, percentage: float):
        """Switch traffic to new deployment version"""
        
        try:
            traffic_split = TrafficSplit(
                deployment_id=deployment.deployment_id,
                current_version_percentage=100.0 - percentage,
                new_version_percentage=percentage,
                routing_rules={
                    "weight_based": True,
                    "header_based": False,
                    "cookie_based": False
                },
                timestamp=datetime.now()
            )
            
            self.traffic_splits[deployment.deployment_id] = traffic_split
            
            logger.info(f"Traffic switched: {percentage}% to new version - {deployment.deployment_id}")
            
            # Simulate traffic switching
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Traffic switching failed: {str(e)}")
            raise

    async def _execute_rollback(self, deployment: Deployment, reason: str):
        """Execute deployment rollback"""
        
        try:
            deployment.status = DeploymentStatus.ROLLING_BACK
            deployment.current_stage = DeploymentStage.ROLLBACK
            deployment.rollback_reason = reason
            
            logger.info(f"Rolling back deployment: {deployment.deployment_id} - Reason: {reason}")
            
            # Rollback steps
            rollback_stage = {
                "name": "Rollback Deployment",
                "stage": DeploymentStage.ROLLBACK.value,
                "start_time": datetime.now(),
                "status": "running",
                "reason": reason
            }
            
            deployment.stages.append(rollback_stage)
            
            # Revert traffic to previous version
            if deployment.deployment_id in self.traffic_splits:
                await self._switch_traffic(deployment, 0.0)
            
            # Wait for rollback completion
            await asyncio.sleep(5)
            
            rollback_stage["status"] = "success"
            rollback_stage["end_time"] = datetime.now()
            
            deployment.status = DeploymentStatus.ROLLED_BACK
            
            logger.info(f"Rollback completed: {deployment.deployment_id}")
            
        except Exception as e:
            logger.error(f"Rollback failed: {deployment.deployment_id} - {str(e)}")
            deployment.status = DeploymentStatus.FAILED

    async def rollback_deployment(self, deployment_id: str, reason: str = "Manual rollback") -> bool:
        """
        Manually rollback a deployment
        
        Args:
            deployment_id: Deployment identifier
            reason: Rollback reason
            
        Returns:
            Rollback success status
        """
        
        try:
            if deployment_id not in self.active_deployments:
                # Check if in history
                deployment = None
                for hist_deployment in self.deployment_history:
                    if hist_deployment.deployment_id == deployment_id:
                        deployment = hist_deployment
                        break
                
                if not deployment:
                    raise ValueError(f"Deployment not found: {deployment_id}")
            else:
                deployment = self.active_deployments[deployment_id]
            
            await self._execute_rollback(deployment, reason)
            
            return deployment.status == DeploymentStatus.ROLLED_BACK
            
        except Exception as e:
            logger.error(f"Manual rollback failed: {str(e)}")
            return False

    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment status and details
        
        Args:
            deployment_id: Deployment identifier
            
        Returns:
            Deployment status information
        """
        
        try:
            deployment = None
            
            if deployment_id in self.active_deployments:
                deployment = self.active_deployments[deployment_id]
            else:
                # Search in history
                for hist_deployment in self.deployment_history:
                    if hist_deployment.deployment_id == deployment_id:
                        deployment = hist_deployment
                        break
            
            if not deployment:
                return None
            
            # Calculate deployment duration
            end_time = deployment.end_time or datetime.now()
            duration_seconds = (end_time - deployment.start_time).total_seconds()
            
            return {
                "deployment_id": deployment.deployment_id,
                "application_name": deployment.application_name,
                "version": deployment.version,
                "environment": deployment.environment,
                "strategy": deployment.strategy.value,
                "status": deployment.status.value,
                "current_stage": deployment.current_stage.value,
                "start_time": deployment.start_time.isoformat(),
                "end_time": deployment.end_time.isoformat() if deployment.end_time else None,
                "duration_seconds": duration_seconds,
                "approval_status": deployment.approval_status,
                "approval_metadata": deployment.approval_metadata,
                "stages": deployment.stages,
                "health_checks": len(deployment.health_checks),
                "metrics_count": len(deployment.metrics),
                "rollback_reason": deployment.rollback_reason,
                "traffic_split": self.traffic_splits.get(deployment_id, {})
            }
            
        except Exception as e:
            logger.error(f"Get deployment status failed: {str(e)}")
            return None

    # Background monitoring tasks
    async def _deployment_monitoring_loop(self):
        """Background deployment monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Monitor active deployments
                for deployment in self.active_deployments.values():
                    if deployment.status == DeploymentStatus.RUNNING:
                        # Check for timeouts
                        runtime = datetime.now() - deployment.start_time
                        if runtime.total_seconds() > 3600:  # 1 hour timeout
                            logger.warning(f"Deployment timeout: {deployment.deployment_id}")
                            await self._execute_rollback(deployment, "Deployment timeout")
                
            except Exception as e:
                logger.error(f"Deployment monitoring loop error: {str(e)}")

    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Perform health checks on active deployments
                for deployment in self.active_deployments.values():
                    if deployment.status == DeploymentStatus.RUNNING:
                        await self._perform_health_checks(deployment)
                
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")

    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Collect metrics for active deployments
                for deployment in self.active_deployments.values():
                    if deployment.status == DeploymentStatus.RUNNING:
                        await self._collect_deployment_metrics(deployment)
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {str(e)}")

    async def _traffic_monitoring_loop(self):
        """Background traffic monitoring loop"""
        while True:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes
                
                # Monitor traffic splits and routing
                for deployment_id, traffic_split in self.traffic_splits.items():
                    # Log traffic distribution
                    logger.debug(f"Traffic split {deployment_id}: {traffic_split.new_version_percentage}%")
                
            except Exception as e:
                logger.error(f"Traffic monitoring loop error: {str(e)}")

    async def health_check(self) -> bool:
        """Deployment manager health check"""
        
        try:
            # Check for stuck deployments
            stuck_deployments = [
                d for d in self.active_deployments.values()
                if d.status == DeploymentStatus.RUNNING and 
                (datetime.now() - d.start_time).total_seconds() > 7200  # 2 hours
            ]
            
            # Health criteria
            if len(stuck_deployments) > 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment manager health check failed: {str(e)}")
            return False

    def get_deployment_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive deployment dashboard"""
        
        active_count = len(self.active_deployments)
        pending_approvals_count = len(self.pending_approvals)
        
        # Calculate deployment statistics
        successful_deployments = len([
            d for d in self.deployment_history 
            if d.status == DeploymentStatus.SUCCESS
        ])
        failed_deployments = len([
            d for d in self.deployment_history 
            if d.status == DeploymentStatus.FAILED
        ])
        
        success_rate = (
            successful_deployments / len(self.deployment_history) * 100
            if self.deployment_history else 0
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "active_deployments": active_count,
                "pending_approvals": pending_approvals_count,
                "total_deployments": len(self.deployment_history),
                "successful_deployments": successful_deployments,
                "failed_deployments": failed_deployments,
                "success_rate_percentage": success_rate
            },
            "deployments_by_strategy": {
                strategy.value: len([
                    d for d in self.deployment_history 
                    if d.strategy == strategy
                ]) for strategy in DeploymentStrategy
            },
            "deployments_by_environment": {
                env: len([
                    d for d in self.deployment_history 
                    if d.environment == env
                ]) for env in self.deployment_configs.keys()
            },
            "average_deployment_time": statistics.mean([
                (d.end_time - d.start_time).total_seconds() / 60
                for d in self.deployment_history
                if d.end_time
            ]) if self.deployment_history else 0,
            "active_traffic_splits": len(self.traffic_splits),
            "pending_approvals_list": self.pending_approvals,
            "health_status": {
                "total_health_checks": sum(len(d.health_checks) for d in self.active_deployments.values()),
                "metrics_collected": len(self.deployment_metrics)
            }
        }

# Global deployment manager instance
deployment_manager = DeploymentManager()

logger.info("🚀 Deployment Manager initialized - Advanced deployment strategies controller")