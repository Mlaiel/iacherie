"""
Tenant Provisioning Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Tenant Provisioning Engine - Enterprise Core Component
Automated tenant onboarding and provisioning system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive tenant provisioning capabilities including:
- Automated tenant onboarding
- Resource provisioning automation
- Configuration template management
- Tenant-specific customizations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProvisioningStatus(Enum):
    """Provisioning status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"
    CANCELLED = "cancelled"


class TenantTier(Enum):
    """Tenant tier enumeration"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Resource type enumeration"""
    DATABASE = "database"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"
    SECURITY = "security"
    MONITORING = "monitoring"
    BACKUP = "backup"


@dataclass
class ResourceQuota:
    """Resource quota configuration"""
    resource_type: ResourceType
    max_value: float
    unit: str
    warning_threshold: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvisioningTemplate:
    """Provisioning template definition"""
    template_id: str
    name: str
    tier: TenantTier
    description: str
    resources: List[ResourceQuota]
    configuration: Dict[str, Any]
    customizations: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


@dataclass
class TenantRequest:
    """Tenant provisioning request"""
    request_id: str
    tenant_name: str
    tenant_id: str
    tier: TenantTier
    template_id: Optional[str] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)
    requested_by: str = ""
    priority: int = 5  # 1-10, higher is more urgent
    estimated_completion: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvisioningStep:
    """Individual provisioning step"""
    step_id: str
    name: str
    description: str
    resource_type: Optional[ResourceType] = None
    dependencies: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: int = 30
    retry_count: int = 3
    rollback_steps: List[str] = field(default_factory=list)


@dataclass
class ProvisioningExecution:
    """Provisioning execution tracking"""
    execution_id: str
    request_id: str
    tenant_id: str
    status: ProvisioningStatus
    current_step: int = 0
    total_steps: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    logs: List[str] = field(default_factory=list)
    provisioned_resources: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None


class TenantProvisioningEngine:
    """
    Enterprise Tenant Provisioning Engine
    
    Manages automated tenant onboarding with configurable templates,
    resource provisioning, and comprehensive tracking capabilities.
    """
    
    def __init__(self) -> None:
        self.templates: Dict[str, ProvisioningTemplate] = {}
        self.pending_requests: Dict[str, TenantRequest] = {}
        self.active_executions: Dict[str, ProvisioningExecution] = {}
        self.completed_executions: List[ProvisioningExecution] = []
        self.provisioning_tasks: Dict[str, asyncio.Task] = {}
        
        # Resource providers
        self.resource_providers: Dict[ResourceType, Any] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[callable]] = {
            "provisioning_started": [],
            "provisioning_completed": [],
            "provisioning_failed": [],
            "step_completed": [],
            "resource_provisioned": [],
            "tenant_ready": []
        }
        
        # Configuration
        self.max_concurrent_provisions = 5
        self.default_timeout = timedelta(hours=2)
        self.auto_cleanup_failed = True
        self.notification_enabled = True
        
        # Load default templates
        self._load_default_templates()
        
        logger.info("Tenant Provisioning Engine initialized")
    
    async def create_template(self, template: ProvisioningTemplate) -> bool:
        """Create provisioning template"""
        try:
            # Validate template
            validation_result = await self._validate_template(template)
            if not validation_result["valid"]:
                logger.error(f"Template validation failed: {validation_result['errors']}")
                return False
            
            self.templates[template.template_id] = template
            
            logger.info(f"Provisioning template created: {template.template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template {template.template_id}: {e}")
            return False
    
    async def submit_provisioning_request(self, request: TenantRequest) -> str:
        """Submit tenant provisioning request"""
        try:
            # Validate request
            if not await self._validate_request(request):
                raise ValueError("Invalid provisioning request")
            
            # Estimate completion time
            template = self.templates.get(request.template_id)
            if template:
                request.estimated_completion = datetime.utcnow() + timedelta(hours=1)
            
            self.pending_requests[request.request_id] = request
            
            # Start provisioning if capacity allows
            if len(self.active_executions) < self.max_concurrent_provisions:
                await self._start_provisioning(request.request_id)
            
            logger.info(f"Provisioning request submitted: {request.request_id}")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Failed to submit provisioning request: {e}")
            raise
    
    async def get_provisioning_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get provisioning status"""
        # Check active executions
        execution = self.active_executions.get(request_id)
        if execution:
            return self._format_execution_status(execution)
        
        # Check completed executions
        for completed_execution in self.completed_executions:
            if completed_execution.request_id == request_id:
                return self._format_execution_status(completed_execution)
        
        # Check pending requests
        request = self.pending_requests.get(request_id)
        if request:
            return {
                "request_id": request_id,
                "status": "queued",
                "tenant_id": request.tenant_id,
                "tenant_name": request.tenant_name,
                "tier": request.tier.value,
                "estimated_completion": request.estimated_completion.isoformat() if request.estimated_completion else None,
                "queue_position": list(self.pending_requests.keys()).index(request_id) + 1
            }
        
        return None
    
    async def cancel_provisioning(self, request_id: str) -> bool:
        """Cancel provisioning request"""
        try:
            # Cancel if pending
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
                logger.info(f"Pending provisioning request cancelled: {request_id}")
                return True
            
            # Cancel if active
            execution = self.active_executions.get(request_id)
            if execution:
                execution.status = ProvisioningStatus.CANCELLED
                
                # Cancel task
                if request_id in self.provisioning_tasks:
                    self.provisioning_tasks[request_id].cancel()
                
                # Cleanup provisioned resources
                await self._cleanup_provisioned_resources(execution)
                
                logger.info(f"Active provisioning cancelled: {request_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel provisioning {request_id}: {e}")
            return False
    
    async def rollback_provisioning(self, request_id: str) -> bool:
        """Rollback completed provisioning"""
        try:
            # Find completed execution
            execution = None
            for completed_execution in self.completed_executions:
                if completed_execution.request_id == request_id:
                    execution = completed_execution
                    break
            
            if not execution or execution.status != ProvisioningStatus.COMPLETED:
                logger.error(f"Cannot rollback: execution not found or not completed: {request_id}")
                return False
            
            execution.status = ProvisioningStatus.ROLLBACK
            
            # Perform rollback
            success = await self._perform_rollback(execution)
            
            if success:
                logger.info(f"Provisioning rollback completed: {request_id}")
            else:
                logger.error(f"Provisioning rollback failed: {request_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rollback provisioning {request_id}: {e}")
            return False
    
    async def list_templates(self, tier: Optional[TenantTier] = None) -> List[Dict[str, Any]]:
        """List available templates"""
        templates = []
        
        for template in self.templates.values():
            if tier and template.tier != tier:
                continue
            
            templates.append({
                "template_id": template.template_id,
                "name": template.name,
                "tier": template.tier.value,
                "description": template.description,
                "resource_count": len(template.resources),
                "version": template.version,
                "created_at": template.created_at.isoformat()
            })
        
        return templates
    
    async def get_provisioning_metrics(self) -> Dict[str, Any]:
        """Get provisioning metrics"""
        total_requests = len(self.pending_requests) + len(self.active_executions) + len(self.completed_executions)
        
        completed_count = len([e for e in self.completed_executions if e.status == ProvisioningStatus.COMPLETED])
        failed_count = len([e for e in self.completed_executions if e.status == ProvisioningStatus.FAILED])
        
        return {
            "total_requests": total_requests,
            "pending_requests": len(self.pending_requests),
            "active_provisions": len(self.active_executions),
            "completed_provisions": completed_count,
            "failed_provisions": failed_count,
            "success_rate": (completed_count / max(len(self.completed_executions), 1)) * 100,
            "average_provisioning_time": self._calculate_average_provisioning_time(),
            "queue_depth": len(self.pending_requests),
            "concurrent_capacity": self.max_concurrent_provisions
        }
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update provisioning template"""
        try:
            template = self.templates.get(template_id)
            if not template:
                logger.error(f"Template not found: {template_id}")
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            # Increment version
            version_parts = template.version.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            template.version = '.'.join(version_parts)
            
            # Validate updated template
            validation_result = await self._validate_template(template)
            if not validation_result["valid"]:
                logger.error(f"Updated template validation failed: {validation_result['errors']}")
                return False
            
            logger.info(f"Template updated: {template_id} (version {template.version})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return False
    
    async def export_template(self, template_id: str, format_type: str = "yaml") -> Optional[str]:
        """Export template configuration"""
        template = self.templates.get(template_id)
        if not template:
            return None
        
        template_data = {
            "template_id": template.template_id,
            "name": template.name,
            "tier": template.tier.value,
            "description": template.description,
            "version": template.version,
            "resources": [
                {
                    "resource_type": quota.resource_type.value,
                    "max_value": quota.max_value,
                    "unit": quota.unit,
                    "warning_threshold": quota.warning_threshold,
                    "metadata": quota.metadata
                }
                for quota in template.resources
            ],
            "configuration": template.configuration,
            "customizations": template.customizations,
            "dependencies": template.dependencies
        }
        
        if format_type.lower() == "yaml":
            return yaml.dump(template_data, default_flow_style=False)
        elif format_type.lower() == "json":
            return json.dumps(template_data, indent=2)
        else:
            return str(template_data)
    
    # Private methods
    
    async def _start_provisioning(self, request_id -> None: str) -> None:
        """Start provisioning process"""
        request = self.pending_requests.get(request_id)
        if not request:
            return
        
        # Move from pending to active
        del self.pending_requests[request_id]
        
        execution = ProvisioningExecution(
            execution_id=str(uuid.uuid4()),
            request_id=request_id,
            tenant_id=request.tenant_id,
            status=ProvisioningStatus.IN_PROGRESS
        )
        
        self.active_executions[request_id] = execution
        
        # Start provisioning task
        task = asyncio.create_task(self._execute_provisioning(execution, request))
        self.provisioning_tasks[request_id] = task
        
        await self._trigger_event("provisioning_started", request_id)
    
    async def _execute_provisioning(self, execution -> None: ProvisioningExecution, request -> None: TenantRequest) -> None:
        """Execute provisioning process"""
        try:
            # Get template
            template = self.templates.get(request.template_id) if request.template_id else None
            if not template:
                raise ValueError(f"Template not found: {request.template_id}")
            
            # Generate provisioning steps
            steps = await self._generate_provisioning_steps(template, request)
            execution.total_steps = len(steps)
            
            execution.logs.append(f"Starting provisioning for tenant {request.tenant_name}")
            execution.logs.append(f"Total steps: {len(steps)}")
            
            # Execute steps
            for i, step in enumerate(steps):
                execution.current_step = i + 1
                execution.progress_percentage = (i / len(steps)) * 100
                
                execution.logs.append(f"Executing step {i + 1}: {step.name}")
                
                success = await self._execute_provisioning_step(step, execution, request)
                
                if not success:
                    execution.status = ProvisioningStatus.FAILED
                    execution.error_details = f"Step {i + 1} failed: {step.name}"
                    break
                
                await self._trigger_event("step_completed", f"{request.tenant_id}:{step.step_id}")
            
            if execution.status == ProvisioningStatus.IN_PROGRESS:
                execution.status = ProvisioningStatus.COMPLETED
                execution.progress_percentage = 100.0
                execution.logs.append("Provisioning completed successfully")
                
                await self._trigger_event("provisioning_completed", request.tenant_id)
                await self._trigger_event("tenant_ready", request.tenant_id)
            else:
                await self._trigger_event("provisioning_failed", request.tenant_id)
                
                # Auto-cleanup if enabled
                if self.auto_cleanup_failed:
                    await self._cleanup_provisioned_resources(execution)
            
            execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            execution.status = ProvisioningStatus.FAILED
            execution.error_details = str(e)
            execution.completed_at = datetime.utcnow()
            execution.logs.append(f"Provisioning failed: {e}")
            
            await self._trigger_event("provisioning_failed", request.tenant_id)
            logger.error(f"Provisioning failed for {request.tenant_id}: {e}")
        
        finally:
            # Move to completed
            if request.request_id in self.active_executions:
                self.completed_executions.append(self.active_executions[request.request_id])
                del self.active_executions[request.request_id]
            
            # Cleanup task
            if request.request_id in self.provisioning_tasks:
                del self.provisioning_tasks[request.request_id]
            
            # Start next queued request
            if self.pending_requests:
                next_request_id = next(iter(self.pending_requests))
                await self._start_provisioning(next_request_id)
    
    async def _generate_provisioning_steps(
        self,
        template: ProvisioningTemplate,
        request: TenantRequest
    ) -> List[ProvisioningStep]:
        """Generate provisioning steps from template"""
        steps = []
        
        # Step 1: Initialize tenant
        steps.append(ProvisioningStep(
            step_id="init_tenant",
            name="Initialize Tenant",
            description=f"Initialize tenant {request.tenant_name}",
            configuration={"tenant_id": request.tenant_id, "tenant_name": request.tenant_name}
        ))
        
        # Step 2: Provision resources
        for i, resource_quota in enumerate(template.resources):
            steps.append(ProvisioningStep(
                step_id=f"provision_{resource_quota.resource_type.value}_{i}",
                name=f"Provision {resource_quota.resource_type.value.title()}",
                description=f"Provision {resource_quota.resource_type.value} resources",
                resource_type=resource_quota.resource_type,
                configuration={
                    "resource_type": resource_quota.resource_type.value,
                    "max_value": resource_quota.max_value,
                    "unit": resource_quota.unit,
                    "tenant_id": request.tenant_id
                },
                dependencies=["init_tenant"] if i == 0 else [f"provision_{template.resources[i-1].resource_type.value}_{i-1}"]
            ))
        
        # Step 3: Apply configuration
        steps.append(ProvisioningStep(
            step_id="apply_config",
            name="Apply Configuration",
            description="Apply tenant-specific configuration",
            configuration={**template.configuration, **request.custom_config},
            dependencies=[f"provision_{resource.resource_type.value}_{i}" for i, resource in enumerate(template.resources)]
        ))
        
        # Step 4: Validate setup
        steps.append(ProvisioningStep(
            step_id="validate_setup",
            name="Validate Setup",
            description="Validate tenant setup",
            dependencies=["apply_config"]
        ))
        
        return steps
    
    async def _execute_provisioning_step(
        self,
        step: ProvisioningStep,
        execution: ProvisioningExecution,
        request: TenantRequest
    ) -> bool:
        """Execute individual provisioning step"""
        try:
            # Simulate step execution based on type
            if step.step_id == "init_tenant":
                success = await self._initialize_tenant(step, execution, request)
            elif step.step_id.startswith("provision_"):
                success = await self._provision_resource(step, execution, request)
            elif step.step_id == "apply_config":
                success = await self._apply_configuration(step, execution, request)
            elif step.step_id == "validate_setup":
                success = await self._validate_setup(step, execution, request)
            else:
                # Generic step execution
                success = await self._execute_generic_step(step, execution, request)
            
            if success:
                execution.logs.append(f"Step completed: {step.name}")
            else:
                execution.logs.append(f"Step failed: {step.name}")
            
            return success
            
        except Exception as e:
            execution.logs.append(f"Step error: {step.name} - {e}")
            logger.error(f"Step execution failed: {step.name} - {e}")
            return False
    
    async def _initialize_tenant(self, step: ProvisioningStep, execution: ProvisioningExecution, request: TenantRequest) -> bool:
        """Initialize tenant"""
        # Simulate tenant initialization
        execution.logs.append(f"Creating tenant namespace: {request.tenant_id}")
        await asyncio.sleep(1)  # Simulate work
        
        execution.provisioned_resources["tenant_namespace"] = request.tenant_id
        execution.logs.append("Tenant namespace created successfully")
        return True
    
    async def _provision_resource(self, step: ProvisioningStep, execution: ProvisioningExecution, request: TenantRequest) -> bool:
        """Provision resource"""
        resource_type = step.resource_type
        if not resource_type:
            return False
        
        execution.logs.append(f"Provisioning {resource_type.value} resources")
        
        # Simulate resource provisioning
        await asyncio.sleep(2)  # Simulate work
        
        resource_id = f"{request.tenant_id}_{resource_type.value}_{uuid.uuid4().hex[:8]}"
        
        execution.provisioned_resources[resource_type.value] = {
            "resource_id": resource_id,
            "type": resource_type.value,
            "configuration": step.configuration
        }
        
        await self._trigger_event("resource_provisioned", f"{request.tenant_id}:{resource_type.value}")
        execution.logs.append(f"{resource_type.value.title()} resources provisioned: {resource_id}")
        return True
    
    async def _apply_configuration(self, step: ProvisioningStep, execution: ProvisioningExecution, request: TenantRequest) -> bool:
        """Apply configuration"""
        execution.logs.append("Applying tenant configuration")
        
        # Simulate configuration application
        await asyncio.sleep(1)
        
        execution.provisioned_resources["configuration"] = step.configuration
        execution.logs.append("Configuration applied successfully")
        return True
    
    async def _validate_setup(self, step: ProvisioningStep, execution: ProvisioningExecution, request: TenantRequest) -> bool:
        """Validate setup"""
        execution.logs.append("Validating tenant setup")
        
        # Simulate validation
        await asyncio.sleep(1)
        
        # Check if all required resources are provisioned
        required_resources = ["tenant_namespace"]
        for resource_name in required_resources:
            if resource_name not in execution.provisioned_resources:
                execution.logs.append(f"Validation failed: missing {resource_name}")
                return False
        
        execution.logs.append("Setup validation completed successfully")
        return True
    
    async def _execute_generic_step(self, step: ProvisioningStep, execution: ProvisioningExecution, request: TenantRequest) -> bool:
        """Execute generic step"""
        execution.logs.append(f"Executing generic step: {step.description}")
        
        # Simulate generic step
        await asyncio.sleep(0.5)
        
        return True
    
    async def _cleanup_provisioned_resources(self, execution -> None: ProvisioningExecution) -> None:
        """Cleanup provisioned resources"""
        execution.logs.append("Starting resource cleanup")
        
        for resource_name, resource_info in execution.provisioned_resources.items():
            try:
                # Simulate resource cleanup
                await asyncio.sleep(0.5)
                execution.logs.append(f"Cleaned up {resource_name}")
            except Exception as e:
                execution.logs.append(f"Failed to cleanup {resource_name}: {e}")
        
        execution.logs.append("Resource cleanup completed")
    
    async def _perform_rollback(self, execution: ProvisioningExecution) -> bool:
        """Perform rollback of completed provisioning"""
        try:
            execution.logs.append("Starting rollback process")
            
            # Cleanup all provisioned resources
            await self._cleanup_provisioned_resources(execution)
            
            execution.logs.append("Rollback completed successfully")
            return True
            
        except Exception as e:
            execution.logs.append(f"Rollback failed: {e}")
            logger.error(f"Rollback failed for {execution.tenant_id}: {e}")
            return False
    
    async def _validate_template(self, template: ProvisioningTemplate) -> Dict[str, Any]:
        """Validate provisioning template"""
        errors = []
        
        # Basic validation
        if not template.template_id or not template.name:
            errors.append("Template ID and name are required")
        
        if not template.resources:
            errors.append("Template must have at least one resource")
        
        # Resource validation
        for resource in template.resources:
            if resource.max_value <= 0:
                errors.append(f"Invalid max_value for {resource.resource_type.value}")
            
            if not resource.unit:
                errors.append(f"Unit is required for {resource.resource_type.value}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _validate_request(self, request: TenantRequest) -> bool:
        """Validate provisioning request"""
        if not request.tenant_id or not request.tenant_name:
            return False
        
        if request.template_id and request.template_id not in self.templates:
            return False
        
        return True
    
    def _load_default_templates(self) -> None:
        """Load default provisioning templates"""
        # Basic tier template
        basic_template = ProvisioningTemplate(
            template_id="basic_tier",
            name="Basic Tier",
            tier=TenantTier.BASIC,
            description="Basic tenant with minimal resources",
            resources=[
                ResourceQuota(ResourceType.DATABASE, 1.0, "instance"),
                ResourceQuota(ResourceType.STORAGE, 10.0, "GB"),
                ResourceQuota(ResourceType.COMPUTE, 2.0, "CPU cores")
            ],
            configuration={
                "max_users": 10,
                "max_projects": 5,
                "backup_retention_days": 7
            }
        )
        
        # Standard tier template
        standard_template = ProvisioningTemplate(
            template_id="standard_tier",
            name="Standard Tier",
            tier=TenantTier.STANDARD,
            description="Standard tenant with moderate resources",
            resources=[
                ResourceQuota(ResourceType.DATABASE, 2.0, "instance"),
                ResourceQuota(ResourceType.STORAGE, 100.0, "GB"),
                ResourceQuota(ResourceType.COMPUTE, 8.0, "CPU cores"),
                ResourceQuota(ResourceType.MONITORING, 1.0, "instance")
            ],
            configuration={
                "max_users": 100,
                "max_projects": 50,
                "backup_retention_days": 30
            }
        )
        
        # Premium tier template
        premium_template = ProvisioningTemplate(
            template_id="premium_tier",
            name="Premium Tier",
            tier=TenantTier.PREMIUM,
            description="Premium tenant with extensive resources",
            resources=[
                ResourceQuota(ResourceType.DATABASE, 5.0, "instance"),
                ResourceQuota(ResourceType.STORAGE, 1000.0, "GB"),
                ResourceQuota(ResourceType.COMPUTE, 32.0, "CPU cores"),
                ResourceQuota(ResourceType.MONITORING, 1.0, "instance"),
                ResourceQuota(ResourceType.BACKUP, 1.0, "instance"),
                ResourceQuota(ResourceType.SECURITY, 1.0, "instance")
            ],
            configuration={
                "max_users": 1000,
                "max_projects": 500,
                "backup_retention_days": 90,
                "advanced_security": True,
                "dedicated_support": True
            }
        )
        
        self.templates = {
            basic_template.template_id: basic_template,
            standard_template.template_id: standard_template,
            premium_template.template_id: premium_template
        }
    
    def _format_execution_status(self, execution: ProvisioningExecution) -> Dict[str, Any]:
        """Format execution status for API response"""
        return {
            "execution_id": execution.execution_id,
            "request_id": execution.request_id,
            "tenant_id": execution.tenant_id,
            "status": execution.status.value,
            "progress_percentage": execution.progress_percentage,
            "current_step": execution.current_step,
            "total_steps": execution.total_steps,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "provisioned_resources": list(execution.provisioned_resources.keys()),
            "recent_logs": execution.logs[-5:],  # Last 5 log entries
            "error_details": execution.error_details
        }
    
    def _calculate_average_provisioning_time(self) -> float:
        """Calculate average provisioning time in minutes"""
        completed_executions = [
            e for e in self.completed_executions 
            if e.status == ProvisioningStatus.COMPLETED and e.completed_at
        ]
        
        if not completed_executions:
            return 0.0
        
        total_time = sum(
            (e.completed_at - e.started_at).total_seconds()
            for e in completed_executions
        )
        
        return (total_time / len(completed_executions)) / 60  # Convert to minutes
    
    async def _trigger_event(self, event_type -> None: str, event_data -> None: str) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
tenant_provisioning_engine = TenantProvisioningEngine()


# Convenience functions
async def create_tenant_request(
    tenant_name: str,
    tier: TenantTier,
    requested_by: str,
    template_id: Optional[str] = None,
    custom_config: Optional[Dict[str, Any]] = None
) -> str:
    """Create tenant provisioning request"""
    request_id = str(uuid.uuid4())
    tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
    
    # Use default template if not specified
    if not template_id:
        template_map = {
            TenantTier.BASIC: "basic_tier",
            TenantTier.STANDARD: "standard_tier",
            TenantTier.PREMIUM: "premium_tier"
        }
        template_id = template_map.get(tier, "basic_tier")
    
    request = TenantRequest(
        request_id=request_id,
        tenant_name=tenant_name,
        tenant_id=tenant_id,
        tier=tier,
        template_id=template_id,
        custom_config=custom_config or {},
        requested_by=requested_by
    )
    
    await tenant_provisioning_engine.submit_provisioning_request(request)
    return request_id


async def get_provisioning_status(request_id: str) -> Optional[Dict[str, Any]]:
    """Get provisioning status"""
    return await tenant_provisioning_engine.get_provisioning_status(request_id)


async def list_available_templates() -> List[Dict[str, Any]]:
    """List available provisioning templates"""
    return await tenant_provisioning_engine.list_templates()


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Create tenant provisioning request
        request_id = await create_tenant_request(
            tenant_name="Acme Corporation",
            tier=TenantTier.STANDARD,
            requested_by="admin@acme.com"
        )
        
        print(f"Provisioning request created: {request_id}")
        
        # Wait for provisioning to complete
        while True:
            status = await get_provisioning_status(request_id)
            if status:
                print(f"Status: {status['status']} - Progress: {status.get('progress_percentage', 0):.1f}%")
                
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            
            await asyncio.sleep(2)
        
        # Get final status
        final_status = await get_provisioning_status(request_id)
        print(f"Final status: {final_status}")
        
        # Get metrics
        metrics = await tenant_provisioning_engine.get_provisioning_metrics()
        print(f"Provisioning metrics: {metrics}")
    
    asyncio.run(main())