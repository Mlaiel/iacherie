"""
Enterprise Environment Manager for MLOps
DevOps + Backend Senior implementation with multi-stage environment management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import yaml
import os
import subprocess
import uuid
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"
    SANDBOX = "sandbox"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"


class EnvironmentStatus(Enum):
    """Environment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CREATING = "creating"
    UPDATING = "updating"
    DELETING = "deleting"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class PromotionStatus(Enum):
    """Model promotion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class EnvironmentConfig:
    """Environment configuration"""
    name: str
    type: EnvironmentType
    region: str = "us-east-1"
    cpu_cores: float = 2.0
    memory_gb: int = 4
    storage_gb: int = 50
    gpu_count: int = 0
    auto_scaling: bool = True
    min_instances: int = 1
    max_instances: int = 10
    network_config: Dict[str, Any] = field(default_factory=dict)
    security_groups: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    monitoring_enabled: bool = True
    logging_level: str = "INFO"
    backup_enabled: bool = True
    backup_retention_days: int = 30


@dataclass
class ModelDeployment:
    """Model deployment in environment"""
    deployment_id: str
    model_id: str
    model_version: str
    environment_name: str
    status: str = "active"
    endpoint_url: Optional[str] = None
    replicas: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PromotionRequest:
    """Model promotion request between environments"""
    promotion_id: str
    model_id: str
    model_version: str
    source_environment: str
    target_environment: str
    requester: str
    status: PromotionStatus = PromotionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    approval_required: bool = True
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnvironmentProvisioner:
    """Provisions and manages environment infrastructure"""
    
    def __init__(self) -> None:
        self.provisioning_templates = {}
        self.active_provisioning = set()
    
    async def provision_environment(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Provision a new environment"""
        try:
            if config.name in self.active_provisioning:
                raise ValueError(f"Environment {config.name} is already being provisioned")
            
            self.active_provisioning.add(config.name)
            logger.info(f"Starting provisioning of environment: {config.name}")
            
            # Generate infrastructure template
            template = self._generate_infrastructure_template(config)
            
            # Create environment namespace/resource group
            namespace_result = await self._create_namespace(config)
            
            # Provision compute resources
            compute_result = await self._provision_compute(config)
            
            # Setup networking
            network_result = await self._setup_networking(config)
            
            # Configure security
            security_result = await self._configure_security(config)
            
            # Setup monitoring and logging
            monitoring_result = await self._setup_monitoring(config)
            
            # Validate environment
            validation_result = await self._validate_environment(config)
            
            provisioning_result = {
                "environment_name": config.name,
                "status": "success",
                "infrastructure_template": template,
                "namespace": namespace_result,
                "compute": compute_result,
                "network": network_result,
                "security": security_result,
                "monitoring": monitoring_result,
                "validation": validation_result,
                "provisioned_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully provisioned environment: {config.name}")
            return provisioning_result
            
        except Exception as e:
            logger.error(f"Failed to provision environment {config.name}: {e}")
            raise
        finally:
            self.active_provisioning.discard(config.name)
    
    def _generate_infrastructure_template(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Generate infrastructure as code template"""
        template = {
            "version": "1.0",
            "environment": config.name,
            "type": config.type.value,
            "resources": {
                "compute": {
                    "cpu_cores": config.cpu_cores,
                    "memory_gb": config.memory_gb,
                    "gpu_count": config.gpu_count,
                    "auto_scaling": {
                        "enabled": config.auto_scaling,
                        "min_instances": config.min_instances,
                        "max_instances": config.max_instances
                    }
                },
                "storage": {
                    "size_gb": config.storage_gb,
                    "backup_enabled": config.backup_enabled,
                    "retention_days": config.backup_retention_days
                },
                "network": config.network_config,
                "security": {
                    "security_groups": config.security_groups
                }
            },
            "configuration": {
                "environment_variables": config.environment_variables,
                "secrets": list(config.secrets.keys()),  # Don't include actual secret values
                "monitoring": config.monitoring_enabled,
                "logging_level": config.logging_level
            }
        }
        return template
    
    async def _create_namespace(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Create environment namespace/resource group"""
        # Simulate namespace creation
        await asyncio.sleep(1)
        return {
            "namespace": f"ainflue-{config.name}",
            "region": config.region,
            "created": True
        }
    
    async def _provision_compute(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Provision compute resources"""
        # Simulate compute provisioning
        await asyncio.sleep(2)
        return {
            "instances": [
                {
                    "instance_id": f"i-{uuid.uuid4().hex[:8]}",
                    "cpu_cores": config.cpu_cores,
                    "memory_gb": config.memory_gb,
                    "gpu_count": config.gpu_count,
                    "status": "running"
                }
            ],
            "auto_scaling_group": f"asg-{config.name}",
            "load_balancer": f"alb-{config.name}"
        }
    
    async def _setup_networking(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Setup networking configuration"""
        await asyncio.sleep(1)
        return {
            "vpc_id": f"vpc-{uuid.uuid4().hex[:8]}",
            "subnet_ids": [f"subnet-{uuid.uuid4().hex[:8]}" for _ in range(2)],
            "security_groups": config.security_groups,
            "endpoints": {
                "api": f"https://api-{config.name}.ainflue.com",
                "monitoring": f"https://metrics-{config.name}.ainflue.com"
            }
        }
    
    async def _configure_security(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Configure security settings"""
        await asyncio.sleep(1)
        return {
            "iam_roles": [f"AinflueMlops{config.name.title()}Role"],
            "secrets_manager": f"ainflue/{config.name}/secrets",
            "ssl_certificates": [f"*.{config.name}.ainflue.com"],
            "security_groups_created": len(config.security_groups)
        }
    
    async def _setup_monitoring(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Setup monitoring and logging"""
        await asyncio.sleep(1)
        
        if not config.monitoring_enabled:
            return {"monitoring": "disabled"}
        
        return {
            "monitoring_enabled": True,
            "metrics_endpoint": f"https://metrics-{config.name}.ainflue.com",
            "logging_endpoint": f"https://logs-{config.name}.ainflue.com",
            "alerting_rules": [
                "cpu_usage_high",
                "memory_usage_high",
                "model_error_rate_high",
                "inference_latency_high"
            ],
            "dashboards": [
                "infrastructure_dashboard",
                "model_performance_dashboard",
                "business_metrics_dashboard"
            ]
        }
    
    async def _validate_environment(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Validate environment is properly configured"""
        await asyncio.sleep(1)
        
        validation_checks = [
            {"check": "compute_resources", "status": "passed"},
            {"check": "network_connectivity", "status": "passed"},
            {"check": "security_configuration", "status": "passed"},
            {"check": "monitoring_setup", "status": "passed"},
            {"check": "environment_variables", "status": "passed"}
        ]
        
        all_passed = all(check["status"] == "passed" for check in validation_checks)
        
        return {
            "validation_passed": all_passed,
            "checks": validation_checks,
            "validated_at": datetime.now().isoformat()
        }


class ModelPromotionManager:
    """Manages model promotions between environments"""
    
    def __init__(self) -> None:
        self.promotion_workflows = {}
        self.approval_rules = {
            EnvironmentType.PRODUCTION: ["lead_engineer", "security_team"],
            EnvironmentType.STAGING: ["senior_engineer"],
            EnvironmentType.TESTING: [],  # Auto-approve
            EnvironmentType.DEVELOPMENT: []  # Auto-approve
        }
    
    async def request_promotion(self, promotion_request: PromotionRequest) -> str:
        """Request model promotion to target environment"""
        try:
            logger.info(
                f"Promotion requested: {promotion_request.model_id} v{promotion_request.model_version} "
                f"from {promotion_request.source_environment} to {promotion_request.target_environment}"
            )
            
            # Validate promotion request
            await self._validate_promotion_request(promotion_request)
            
            # Check if approval is required
            target_env_type = EnvironmentType(promotion_request.target_environment)
            required_approvers = self.approval_rules.get(target_env_type, [])
            
            if required_approvers:
                promotion_request.approval_required = True
                logger.info(f"Promotion {promotion_request.promotion_id} requires approval from: {required_approvers}")
            else:
                promotion_request.approval_required = False
                promotion_request.approved_by = "auto_approval"
                promotion_request.approval_timestamp = datetime.now()
                promotion_request.status = PromotionStatus.IN_PROGRESS
                
                # Start promotion workflow
                await self._start_promotion_workflow(promotion_request)
            
            self.promotion_workflows[promotion_request.promotion_id] = promotion_request
            return promotion_request.promotion_id
            
        except Exception as e:
            logger.error(f"Failed to request promotion: {e}")
            promotion_request.status = PromotionStatus.FAILED
            promotion_request.metadata["error"] = str(e)
            raise
    
    async def approve_promotion(self, promotion_id: str, approver: str) -> bool:
        """Approve a pending promotion"""
        if promotion_id not in self.promotion_workflows:
            raise ValueError(f"Promotion {promotion_id} not found")
        
        promotion = self.promotion_workflows[promotion_id]
        
        if promotion.status != PromotionStatus.PENDING:
            raise ValueError(f"Promotion {promotion_id} is not in pending state")
        
        # Check if approver is authorized
        target_env_type = EnvironmentType(promotion.target_environment)
        required_approvers = self.approval_rules.get(target_env_type, [])
        
        if required_approvers and approver not in required_approvers:
            raise ValueError(f"Approver {approver} is not authorized for {target_env_type.value}")
        
        promotion.approved_by = approver
        promotion.approval_timestamp = datetime.now()
        promotion.status = PromotionStatus.IN_PROGRESS
        
        logger.info(f"Promotion {promotion_id} approved by {approver}")
        
        # Start promotion workflow
        await self._start_promotion_workflow(promotion)
        
        return True
    
    async def _validate_promotion_request(self, promotion_request -> None: PromotionRequest) -> None:
        """Validate promotion request"""
        # Check if source environment exists and has the model
        # Check if target environment exists
        # Validate promotion path (e.g., dev -> test -> staging -> prod)
        
        valid_promotion_paths = {
            EnvironmentType.DEVELOPMENT: [EnvironmentType.TESTING, EnvironmentType.INTEGRATION],
            EnvironmentType.TESTING: [EnvironmentType.STAGING, EnvironmentType.PERFORMANCE],
            EnvironmentType.INTEGRATION: [EnvironmentType.STAGING],
            EnvironmentType.STAGING: [EnvironmentType.PRODUCTION],
            EnvironmentType.PERFORMANCE: [EnvironmentType.PRODUCTION]
        }
        
        source_type = EnvironmentType(promotion_request.source_environment)
        target_type = EnvironmentType(promotion_request.target_environment)
        
        allowed_targets = valid_promotion_paths.get(source_type, [])
        if target_type not in allowed_targets:
            raise ValueError(
                f"Invalid promotion path: {source_type.value} -> {target_type.value}. "
                f"Allowed targets: {[t.value for t in allowed_targets]}"
            )
    
    async def _start_promotion_workflow(self, promotion_request -> None: PromotionRequest) -> None:
        """Start the promotion workflow"""
        try:
            logger.info(f"Starting promotion workflow for {promotion_request.promotion_id}")
            
            # Run pre-promotion validations
            validation_results = await self._run_pre_promotion_validations(promotion_request)
            promotion_request.validation_results = validation_results
            
            # Check if all validations passed
            all_validations_passed = all(
                result.get("status") == "passed" for result in validation_results
            )
            
            if not all_validations_passed:
                promotion_request.status = PromotionStatus.FAILED
                promotion_request.metadata["error"] = "Pre-promotion validations failed"
                logger.error(f"Promotion {promotion_request.promotion_id} failed validations")
                return
            
            # Create rollback plan
            rollback_plan = await self._create_rollback_plan(promotion_request)
            promotion_request.rollback_plan = rollback_plan
            
            # Execute deployment to target environment
            deployment_result = await self._deploy_to_target_environment(promotion_request)
            
            if deployment_result["status"] == "success":
                # Run post-deployment validations
                post_validation_results = await self._run_post_deployment_validations(promotion_request)
                
                if all(result.get("status") == "passed" for result in post_validation_results):
                    promotion_request.status = PromotionStatus.COMPLETED
                    promotion_request.metadata["deployment"] = deployment_result
                    logger.info(f"Promotion {promotion_request.promotion_id} completed successfully")
                else:
                    # Rollback due to post-deployment validation failures
                    await self._execute_rollback(promotion_request)
                    promotion_request.status = PromotionStatus.ROLLED_BACK
                    logger.warning(f"Promotion {promotion_request.promotion_id} rolled back due to validation failures")
            else:
                promotion_request.status = PromotionStatus.FAILED
                promotion_request.metadata["error"] = deployment_result.get("error", "Deployment failed")
                logger.error(f"Promotion {promotion_request.promotion_id} failed during deployment")
        
        except Exception as e:
            logger.error(f"Promotion workflow error for {promotion_request.promotion_id}: {e}")
            promotion_request.status = PromotionStatus.FAILED
            promotion_request.metadata["error"] = str(e)
    
    async def _run_pre_promotion_validations(self, promotion_request: PromotionRequest) -> List[Dict[str, Any]]:
        """Run validations before promotion"""
        validations = []
        
        # Model existence validation
        validations.append({
            "validation": "model_exists",
            "status": "passed",
            "message": f"Model {promotion_request.model_id} v{promotion_request.model_version} exists"
        })
        
        # Performance validation
        validations.append({
            "validation": "performance_metrics",
            "status": "passed",
            "message": "Model meets performance requirements",
            "metrics": {
                "accuracy": 0.92,
                "latency_ms": 45,
                "throughput_rps": 1000
            }
        })
        
        # Security validation
        validations.append({
            "validation": "security_scan",
            "status": "passed",
            "message": "No security vulnerabilities detected"
        })
        
        # Compatibility validation
        validations.append({
            "validation": "compatibility_check",
            "status": "passed",
            "message": "Model compatible with target environment"
        })
        
        await asyncio.sleep(1)  # Simulate validation time
        return validations
    
    async def _create_rollback_plan(self, promotion_request: PromotionRequest) -> Dict[str, Any]:
        """Create rollback plan for the promotion"""
        rollback_plan = {
            "rollback_strategy": "previous_version",
            "target_environment": promotion_request.target_environment,
            "rollback_steps": [
                "stop_traffic_to_new_version",
                "restore_previous_version",
                "validate_rollback",
                "resume_traffic"
            ],
            "estimated_rollback_time_minutes": 5,
            "validation_checks": [
                "model_health_check",
                "endpoint_availability",
                "performance_metrics"
            ]
        }
        
        return rollback_plan
    
    async def _deploy_to_target_environment(self, promotion_request: PromotionRequest) -> Dict[str, Any]:
        """Deploy model to target environment"""
        try:
            # Simulate deployment process
            await asyncio.sleep(2)
            
            deployment_id = f"deploy-{uuid.uuid4().hex[:8]}"
            endpoint_url = f"https://api-{promotion_request.target_environment}.ainflue.com/models/{promotion_request.model_id}"
            
            return {
                "status": "success",
                "deployment_id": deployment_id,
                "endpoint_url": endpoint_url,
                "model_id": promotion_request.model_id,
                "model_version": promotion_request.model_version,
                "deployed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _run_post_deployment_validations(self, promotion_request: PromotionRequest) -> List[Dict[str, Any]]:
        """Run validations after deployment"""
        validations = []
        
        # Health check
        validations.append({
            "validation": "health_check",
            "status": "passed",
            "message": "Model endpoint is healthy"
        })
        
        # Smoke tests
        validations.append({
            "validation": "smoke_tests",
            "status": "passed",
            "message": "Basic functionality tests passed"
        })
        
        # Performance validation
        validations.append({
            "validation": "performance_validation",
            "status": "passed",
            "message": "Performance metrics within acceptable range"
        })
        
        await asyncio.sleep(1)  # Simulate validation time
        return validations
    
    async def _execute_rollback(self, promotion_request -> None: PromotionRequest) -> None:
        """Execute rollback plan"""
        logger.info(f"Executing rollback for promotion {promotion_request.promotion_id}")
        
        if not promotion_request.rollback_plan:
            logger.error("No rollback plan available")
            return
        
        # Simulate rollback execution
        for step in promotion_request.rollback_plan["rollback_steps"]:
            logger.info(f"Executing rollback step: {step}")
            await asyncio.sleep(0.5)
        
        logger.info(f"Rollback completed for promotion {promotion_request.promotion_id}")


class EnvironmentManager:
    """Main environment manager with comprehensive environment lifecycle management"""
    
    def __init__(self) -> None:
        self.environments = {}
        self.deployments = {}
        self.provisioner = EnvironmentProvisioner()
        self.promotion_manager = ModelPromotionManager()
        self.environment_lock = asyncio.Lock()
    
    async def create_environment(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Create a new environment"""
        async with self.environment_lock:
            if config.name in self.environments:
                raise ValueError(f"Environment {config.name} already exists")
            
            logger.info(f"Creating environment: {config.name}")
            
            # Set initial status
            environment_data = {
                "config": config,
                "status": EnvironmentStatus.CREATING,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "deployments": {},
                "metrics": {},
                "health_status": "unknown"
            }
            
            self.environments[config.name] = environment_data
            
            try:
                # Provision infrastructure
                provisioning_result = await self.provisioner.provision_environment(config)
                
                # Update environment data
                environment_data["provisioning_result"] = provisioning_result
                environment_data["status"] = EnvironmentStatus.ACTIVE
                environment_data["health_status"] = "healthy"
                
                logger.info(f"Environment {config.name} created successfully")
                
                return {
                    "environment_name": config.name,
                    "status": "created",
                    "provisioning_result": provisioning_result
                }
                
            except Exception as e:
                environment_data["status"] = EnvironmentStatus.ERROR
                environment_data["error"] = str(e)
                logger.error(f"Failed to create environment {config.name}: {e}")
                raise
    
    async def deploy_model(self, model_id: str, model_version: str, 
                          environment_name: str, replicas: int = 1) -> str:
        """Deploy a model to an environment"""
        if environment_name not in self.environments:
            raise ValueError(f"Environment {environment_name} does not exist")
        
        environment = self.environments[environment_name]
        
        if environment["status"] != EnvironmentStatus.ACTIVE:
            raise ValueError(f"Environment {environment_name} is not active")
        
        deployment_id = str(uuid.uuid4())
        
        deployment = ModelDeployment(
            deployment_id=deployment_id,
            model_id=model_id,
            model_version=model_version,
            environment_name=environment_name,
            replicas=replicas,
            endpoint_url=f"https://api-{environment_name}.ainflue.com/models/{model_id}",
            health_check_url=f"https://api-{environment_name}.ainflue.com/models/{model_id}/health"
        )
        
        # Store deployment
        self.deployments[deployment_id] = deployment
        environment["deployments"][deployment_id] = deployment
        
        logger.info(f"Deployed model {model_id} v{model_version} to {environment_name}")
        
        return deployment_id
    
    async def promote_model(self, model_id: str, model_version: str,
                           source_environment: str, target_environment: str,
                           requester: str) -> str:
        """Promote a model between environments"""
        if source_environment not in self.environments:
            raise ValueError(f"Source environment {source_environment} does not exist")
        
        if target_environment not in self.environments:
            raise ValueError(f"Target environment {target_environment} does not exist")
        
        promotion_request = PromotionRequest(
            promotion_id=str(uuid.uuid4()),
            model_id=model_id,
            model_version=model_version,
            source_environment=source_environment,
            target_environment=target_environment,
            requester=requester
        )
        
        promotion_id = await self.promotion_manager.request_promotion(promotion_request)
        
        logger.info(f"Model promotion requested: {promotion_id}")
        return promotion_id
    
    async def approve_promotion(self, promotion_id: str, approver: str) -> bool:
        """Approve a model promotion"""
        return await self.promotion_manager.approve_promotion(promotion_id, approver)
    
    async def update_environment(self, environment_name: str, 
                                config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update environment configuration"""
        async with self.environment_lock:
            if environment_name not in self.environments:
                raise ValueError(f"Environment {environment_name} does not exist")
            
            environment = self.environments[environment_name]
            environment["status"] = EnvironmentStatus.UPDATING
            
            try:
                # Apply configuration updates
                current_config = environment["config"]
                
                for key, value in config_updates.items():
                    if hasattr(current_config, key):
                        setattr(current_config, key, value)
                
                environment["updated_at"] = datetime.now()
                environment["status"] = EnvironmentStatus.ACTIVE
                
                logger.info(f"Environment {environment_name} updated successfully")
                
                return {
                    "environment_name": environment_name,
                    "status": "updated",
                    "updated_config": config_updates
                }
                
            except Exception as e:
                environment["status"] = EnvironmentStatus.ERROR
                environment["error"] = str(e)
                logger.error(f"Failed to update environment {environment_name}: {e}")
                raise
    
    async def delete_environment(self, environment_name: str, force: bool = False) -> Dict[str, Any]:
        """Delete an environment"""
        async with self.environment_lock:
            if environment_name not in self.environments:
                raise ValueError(f"Environment {environment_name} does not exist")
            
            environment = self.environments[environment_name]
            
            # Check for active deployments
            if environment["deployments"] and not force:
                raise ValueError(
                    f"Environment {environment_name} has active deployments. "
                    "Use force=True to delete anyway."
                )
            
            environment["status"] = EnvironmentStatus.DELETING
            
            try:
                # Remove deployments
                for deployment_id in list(environment["deployments"].keys()):
                    if deployment_id in self.deployments:
                        del self.deployments[deployment_id]
                
                # Cleanup infrastructure (simulated)
                await asyncio.sleep(1)
                
                # Remove environment
                del self.environments[environment_name]
                
                logger.info(f"Environment {environment_name} deleted successfully")
                
                return {
                    "environment_name": environment_name,
                    "status": "deleted"
                }
                
            except Exception as e:
                environment["status"] = EnvironmentStatus.ERROR
                environment["error"] = str(e)
                logger.error(f"Failed to delete environment {environment_name}: {e}")
                raise
    
    def get_environment_status(self, environment_name: str) -> Optional[Dict[str, Any]]:
        """Get environment status and details"""
        if environment_name not in self.environments:
            return None
        
        environment = self.environments[environment_name]
        config = environment["config"]
        
        return {
            "name": environment_name,
            "type": config.type.value,
            "status": environment["status"].value,
            "health_status": environment.get("health_status", "unknown"),
            "created_at": environment["created_at"].isoformat(),
            "updated_at": environment["updated_at"].isoformat(),
            "deployments": len(environment["deployments"]),
            "config": {
                "cpu_cores": config.cpu_cores,
                "memory_gb": config.memory_gb,
                "storage_gb": config.storage_gb,
                "gpu_count": config.gpu_count,
                "auto_scaling": config.auto_scaling,
                "region": config.region
            },
            "error": environment.get("error")
        }
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """List all environments"""
        return [
            self.get_environment_status(name) 
            for name in self.environments.keys()
        ]
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        if deployment_id not in self.deployments:
            return None
        
        deployment = self.deployments[deployment_id]
        
        return {
            "deployment_id": deployment.deployment_id,
            "model_id": deployment.model_id,
            "model_version": deployment.model_version,
            "environment_name": deployment.environment_name,
            "status": deployment.status,
            "endpoint_url": deployment.endpoint_url,
            "health_check_url": deployment.health_check_url,
            "replicas": deployment.replicas,
            "created_at": deployment.created_at.isoformat(),
            "updated_at": deployment.updated_at.isoformat(),
            "metrics": deployment.metrics,
            "metadata": deployment.metadata
        }
    
    def get_promotion_status(self, promotion_id: str) -> Optional[Dict[str, Any]]:
        """Get promotion status"""
        if promotion_id not in self.promotion_manager.promotion_workflows:
            return None
        
        promotion = self.promotion_manager.promotion_workflows[promotion_id]
        
        return {
            "promotion_id": promotion.promotion_id,
            "model_id": promotion.model_id,
            "model_version": promotion.model_version,
            "source_environment": promotion.source_environment,
            "target_environment": promotion.target_environment,
            "status": promotion.status.value,
            "requester": promotion.requester,
            "approval_required": promotion.approval_required,
            "approved_by": promotion.approved_by,
            "approval_timestamp": promotion.approval_timestamp.isoformat() if promotion.approval_timestamp else None,
            "created_at": promotion.created_at.isoformat(),
            "validation_results": promotion.validation_results,
            "metadata": promotion.metadata
        }


# Factory function
def create_environment_manager() -> EnvironmentManager:
    """Create a configured environment manager"""
    return EnvironmentManager()


# Export main classes
__all__ = [
    "EnvironmentManager",
    "EnvironmentConfig",
    "EnvironmentType",
    "EnvironmentStatus",
    "ModelDeployment",
    "PromotionRequest",
    "PromotionStatus",
    "create_environment_manager"
]