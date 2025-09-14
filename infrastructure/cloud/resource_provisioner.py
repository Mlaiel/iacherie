"""
🏗️ Ainflue Infrastructure - Cloud Resource Provisioner
Automated cloud resource provisioning and lifecycle management.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import uuid
from enum import Enum
import yaml

from ..cloud.aws_provider import AWSProvider
from ..cloud.gcp_provider import GCPProvider
from ..cloud.azure_provider import AzureProvider


class ResourceState(Enum):
    """Resource lifecycle states."""
    REQUESTED = "requested"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    UPDATING = "updating"
    SCALING = "scaling"
    DEPROVISIONING = "deprovisioning"
    TERMINATED = "terminated"
    ERROR = "error"


class ProvisioningStrategy(Enum):
    """Resource provisioning strategies."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"


class ResourceCategory(Enum):
    """Categories of cloud resources."""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    AI_ML = "ai_ml"
    ANALYTICS = "analytics"
    CONTAINER = "container"


@dataclass
class ResourceTemplate:
    """Resource provisioning template."""
    template_id: str
    name: str
    description: str
    category: ResourceCategory
    cloud_provider: str
    resource_type: str
    configuration: Dict[str, Any]
    cost_estimate: float
    provisioning_time_minutes: int
    dependencies: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ResourceRequest:
    """Resource provisioning request."""
    request_id: str
    template_id: str
    requested_by: str
    environment: str  # dev, staging, production
    priority: str  # low, medium, high, critical
    strategy: ProvisioningStrategy
    scheduled_time: Optional[datetime] = None
    custom_configuration: Dict[str, Any] = field(default_factory=dict)
    approval_required: bool = True
    auto_terminate: Optional[datetime] = None


@dataclass
class ProvisionedResource:
    """Provisioned resource tracking."""
    resource_id: str
    request_id: str
    template_id: str
    cloud_provider: str
    resource_type: str
    state: ResourceState
    created_at: datetime
    configuration: Dict[str, Any]
    cloud_resource_id: Optional[str] = None
    endpoints: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    cost_actual: float = 0.0
    last_updated: Optional[datetime] = None


@dataclass
class ProvisioningJob:
    """Provisioning job execution tracking."""
    job_id: str
    request_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    progress_percentage: float
    steps_completed: int
    steps_total: int
    error_message: Optional[str] = None
    rollback_available: bool = True


class CloudResourceProvisioner:
    """
    Enterprise cloud resource provisioning system.
    
    Provides automated resource provisioning, lifecycle management,
    and cost optimization across multiple cloud providers.
    """

    def __init__(self) -> None:
        """Initialize cloud resource provisioner."""
        self.logger = logging.getLogger(__name__)
        
        # Cloud providers
        self.providers = {
            'aws': AWSProvider(),
            'gcp': GCPProvider(),
            'azure': AzureProvider()
        }
        
        # Resource management
        self.templates: Dict[str, ResourceTemplate] = {}
        self.requests: Dict[str, ResourceRequest] = {}
        self.provisioned_resources: Dict[str, ProvisionedResource] = {}
        self.active_jobs: Dict[str, ProvisioningJob] = {}
        
        # Approval and scheduling
        self.pending_approvals: List[str] = []
        self.scheduled_requests: List[Tuple[datetime, str]] = []
        
        # Resource usage tracking
        self.usage_metrics: Dict[str, Dict[str, Any]] = {}
        self.cost_tracking: Dict[str, float] = {}
        
        # Initialize default templates
        self._initialize_default_templates()
        
        self.logger.info("CloudResourceProvisioner initialized successfully")

    def _initialize_default_templates(self) -> None:
        """Initialize default resource templates."""
        try:
            default_templates = [
                # AWS Templates
                ResourceTemplate(
                    template_id="aws_ec2_web_server",
                    name="AWS EC2 Web Server",
                    description="Standard web server on AWS EC2",
                    category=ResourceCategory.COMPUTE,
                    cloud_provider="aws",
                    resource_type="ec2_instance",
                    configuration={
                        "instance_type": "t3.medium",
                        "ami_id": "ami-0abcdef1234567890",
                        "security_groups": ["web-server-sg"],
                        "key_pair": "ainflue-key",
                        "storage": {"size": 20, "type": "gp3"},
                        "monitoring": True
                    },
                    cost_estimate=50.0,
                    provisioning_time_minutes=10,
                    tags={"Environment": "{{environment}}", "Project": "ainflue"}
                ),
                ResourceTemplate(
                    template_id="aws_rds_postgresql",
                    name="AWS RDS PostgreSQL",
                    description="Managed PostgreSQL database on AWS RDS",
                    category=ResourceCategory.DATABASE,
                    cloud_provider="aws",
                    resource_type="rds_instance",
                    configuration={
                        "engine": "postgres",
                        "engine_version": "13.7",
                        "instance_class": "db.t3.micro",
                        "allocated_storage": 20,
                        "backup_retention": 7,
                        "multi_az": False,
                        "encryption": True
                    },
                    cost_estimate=25.0,
                    provisioning_time_minutes=15,
                    dependencies=["vpc", "security_group"]
                ),
                ResourceTemplate(
                    template_id="aws_s3_bucket",
                    name="AWS S3 Bucket",
                    description="S3 bucket for object storage",
                    category=ResourceCategory.STORAGE,
                    cloud_provider="aws",
                    resource_type="s3_bucket",
                    configuration={
                        "versioning": True,
                        "encryption": "AES256",
                        "public_access_block": True,
                        "lifecycle_rules": [
                            {
                                "id": "archive_old_objects",
                                "status": "Enabled",
                                "transitions": [
                                    {"days": 30, "storage_class": "STANDARD_IA"},
                                    {"days": 90, "storage_class": "GLACIER"}
                                ]
                            }
                        ]
                    },
                    cost_estimate=10.0,
                    provisioning_time_minutes=5
                ),
                
                # GCP Templates
                ResourceTemplate(
                    template_id="gcp_compute_instance",
                    name="GCP Compute Engine Instance",
                    description="Virtual machine on Google Compute Engine",
                    category=ResourceCategory.COMPUTE,
                    cloud_provider="gcp",
                    resource_type="compute_instance",
                    configuration={
                        "machine_type": "e2-medium",
                        "image": "ubuntu-2004-lts",
                        "disk_size": 20,
                        "disk_type": "pd-standard",
                        "network": "default",
                        "preemptible": False
                    },
                    cost_estimate=40.0,
                    provisioning_time_minutes=8
                ),
                ResourceTemplate(
                    template_id="gcp_cloud_sql",
                    name="GCP Cloud SQL PostgreSQL",
                    description="Managed PostgreSQL on Google Cloud SQL",
                    category=ResourceCategory.DATABASE,
                    cloud_provider="gcp",
                    resource_type="cloud_sql_instance",
                    configuration={
                        "database_version": "POSTGRES_13",
                        "tier": "db-f1-micro",
                        "disk_size": 10,
                        "disk_type": "PD_SSD",
                        "backup_enabled": True,
                        "binary_log_enabled": False
                    },
                    cost_estimate=20.0,
                    provisioning_time_minutes=20
                ),
                
                # Azure Templates
                ResourceTemplate(
                    template_id="azure_vm",
                    name="Azure Virtual Machine",
                    description="Virtual machine on Azure",
                    category=ResourceCategory.COMPUTE,
                    cloud_provider="azure",
                    resource_type="virtual_machine",
                    configuration={
                        "vm_size": "Standard_B2s",
                        "image": "Ubuntu18.04-LTS",
                        "disk_size": 30,
                        "disk_type": "Premium_LRS",
                        "network_security_group": "default-nsg"
                    },
                    cost_estimate=45.0,
                    provisioning_time_minutes=12
                ),
                ResourceTemplate(
                    template_id="azure_sql_database",
                    name="Azure SQL Database",
                    description="Managed SQL database on Azure",
                    category=ResourceCategory.DATABASE,
                    cloud_provider="azure",
                    resource_type="sql_database",
                    configuration={
                        "edition": "Basic",
                        "service_objective": "Basic",
                        "collation": "SQL_Latin1_General_CP1_CI_AS",
                        "max_size_bytes": 2147483648,
                        "backup_retention": 7
                    },
                    cost_estimate=30.0,
                    provisioning_time_minutes=10
                ),
                
                # Container Templates
                ResourceTemplate(
                    template_id="aws_eks_cluster",
                    name="AWS EKS Cluster",
                    description="Managed Kubernetes cluster on AWS EKS",
                    category=ResourceCategory.CONTAINER,
                    cloud_provider="aws",
                    resource_type="eks_cluster",
                    configuration={
                        "kubernetes_version": "1.21",
                        "node_group": {
                            "instance_types": ["t3.medium"],
                            "scaling_config": {
                                "desired_size": 2,
                                "max_size": 10,
                                "min_size": 1
                            }
                        },
                        "vpc_config": {
                            "subnet_ids": [],
                            "endpoint_private_access": True,
                            "endpoint_public_access": True
                        }
                    },
                    cost_estimate=150.0,
                    provisioning_time_minutes=30,
                    dependencies=["vpc", "subnets", "security_groups"]
                )
            ]
            
            for template in default_templates:
                self.templates[template.template_id] = template
            
            self.logger.info(f"Initialized {len(default_templates)} default resource templates")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default templates: {e}")

    async def request_resource(self, request_data: Dict[str, Any]) -> str:
        """Request provisioning of a new resource."""
        try:
            request_id = str(uuid.uuid4())
            self.logger.info(f"Creating resource request: {request_id}")
            
            # Validate template exists
            template_id = request_data['template_id']
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
            
            template = self.templates[template_id]
            
            # Create resource request
            request = ResourceRequest(
                request_id=request_id,
                template_id=template_id,
                requested_by=request_data['requested_by'],
                environment=request_data.get('environment', 'dev'),
                priority=request_data.get('priority', 'medium'),
                strategy=ProvisioningStrategy(request_data.get('strategy', 'immediate')),
                scheduled_time=request_data.get('scheduled_time'),
                custom_configuration=request_data.get('custom_configuration', {}),
                approval_required=request_data.get('approval_required', True),
                auto_terminate=request_data.get('auto_terminate')
            )
            
            # Store request
            self.requests[request_id] = request
            
            # Handle based on strategy and approval requirements
            if request.approval_required and request.environment == 'production':
                self.pending_approvals.append(request_id)
                self.logger.info(f"Request {request_id} added to approval queue")
            elif request.strategy == ProvisioningStrategy.SCHEDULED and request.scheduled_time:
                self.scheduled_requests.append((request.scheduled_time, request_id))
                self.scheduled_requests.sort(key=lambda x: x[0])
                self.logger.info(f"Request {request_id} scheduled for {request.scheduled_time}")
            elif request.strategy == ProvisioningStrategy.IMMEDIATE:
                # Start provisioning immediately
                await self._start_provisioning(request_id)
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Resource request failed: {e}")
            raise

    async def approve_request(self, request_id: str, approved_by: str) -> bool:
        """Approve a pending resource request."""
        try:
            if request_id not in self.pending_approvals:
                raise ValueError(f"Request {request_id} is not pending approval")
            
            if request_id not in self.requests:
                raise ValueError(f"Request {request_id} not found")
            
            # Remove from pending approvals
            self.pending_approvals.remove(request_id)
            
            self.logger.info(f"Request {request_id} approved by {approved_by}")
            
            # Start provisioning
            await self._start_provisioning(request_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Request approval failed: {e}")
            return False

    async def provision_resource(self, request_id: str) -> str:
        """Provision resource based on request."""
        try:
            if request_id not in self.requests:
                raise ValueError(f"Request {request_id} not found")
            
            request = self.requests[request_id]
            template = self.templates[request.template_id]
            
            # Create provisioning job
            job_id = str(uuid.uuid4())
            job = ProvisioningJob(
                job_id=job_id,
                request_id=request_id,
                status="running",
                start_time=datetime.utcnow(),
                end_time=None,
                progress_percentage=0.0,
                steps_completed=0,
                steps_total=self._calculate_provisioning_steps(template)
            )
            
            self.active_jobs[job_id] = job
            
            try:
                # Execute provisioning steps
                provisioned_resource = await self._execute_provisioning(job, request, template)
                
                # Update job status
                job.status = "completed"
                job.end_time = datetime.utcnow()
                job.progress_percentage = 100.0
                
                # Store provisioned resource
                self.provisioned_resources[provisioned_resource.resource_id] = provisioned_resource
                
                self.logger.info(f"Resource provisioned successfully: {provisioned_resource.resource_id}")
                return provisioned_resource.resource_id
                
            except Exception as e:
                # Update job with error
                job.status = "failed"
                job.error_message = str(e)
                job.end_time = datetime.utcnow()
                
                self.logger.error(f"Resource provisioning failed: {e}")
                raise
                
        except Exception as e:
            self.logger.error(f"Resource provisioning failed: {e}")
            raise

    async def scale_resource(self, resource_id: str, scaling_config: Dict[str, Any]) -> bool:
        """Scale an existing resource."""
        try:
            if resource_id not in self.provisioned_resources:
                raise ValueError(f"Resource {resource_id} not found")
            
            resource = self.provisioned_resources[resource_id]
            
            if resource.state not in [ResourceState.ACTIVE, ResourceState.SCALING]:
                raise ValueError(f"Resource {resource_id} is not in a scalable state")
            
            self.logger.info(f"Scaling resource: {resource_id}")
            
            # Update resource state
            resource.state = ResourceState.SCALING
            resource.last_updated = datetime.utcnow()
            
            # Execute scaling operation
            scaling_result = await self._execute_scaling(resource, scaling_config)
            
            if scaling_result['success']:
                # Update resource configuration
                resource.configuration.update(scaling_config)
                resource.state = ResourceState.ACTIVE
                resource.last_updated = datetime.utcnow()
                
                self.logger.info(f"Resource scaled successfully: {resource_id}")
                return True
            else:
                resource.state = ResourceState.ERROR
                self.logger.error(f"Resource scaling failed: {scaling_result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Resource scaling failed: {e}")
            return False

    async def terminate_resource(self, resource_id: str, force: bool = False) -> bool:
        """Terminate a provisioned resource."""
        try:
            if resource_id not in self.provisioned_resources:
                raise ValueError(f"Resource {resource_id} not found")
            
            resource = self.provisioned_resources[resource_id]
            
            if not force and resource.state == ResourceState.ACTIVE:
                # Check for dependencies
                dependencies = await self._check_resource_dependencies(resource_id)
                if dependencies:
                    raise ValueError(f"Resource has active dependencies: {dependencies}")
            
            self.logger.info(f"Terminating resource: {resource_id}")
            
            # Update resource state
            resource.state = ResourceState.DEPROVISIONING
            resource.last_updated = datetime.utcnow()
            
            # Execute termination
            termination_result = await self._execute_termination(resource)
            
            if termination_result['success']:
                resource.state = ResourceState.TERMINATED
                resource.last_updated = datetime.utcnow()
                
                # Record final costs
                final_cost = await self._calculate_final_cost(resource)
                resource.cost_actual = final_cost
                
                self.logger.info(f"Resource terminated successfully: {resource_id}")
                return True
            else:
                resource.state = ResourceState.ERROR
                self.logger.error(f"Resource termination failed: {termination_result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Resource termination failed: {e}")
            return False

    async def get_resource_status(self, resource_id: str) -> Dict[str, Any]:
        """Get detailed status of a provisioned resource."""
        try:
            if resource_id not in self.provisioned_resources:
                raise ValueError(f"Resource {resource_id} not found")
            
            resource = self.provisioned_resources[resource_id]
            
            # Get current metrics
            current_metrics = await self._get_resource_metrics(resource)
            
            # Get cost information
            cost_info = await self._get_resource_cost_info(resource)
            
            # Get health status
            health_status = await self._get_resource_health(resource)
            
            status = {
                'resource_id': resource.resource_id,
                'state': resource.state.value,
                'cloud_provider': resource.cloud_provider,
                'resource_type': resource.resource_type,
                'created_at': resource.created_at.isoformat(),
                'last_updated': resource.last_updated.isoformat() if resource.last_updated else None,
                'configuration': resource.configuration,
                'endpoints': resource.endpoints,
                'metrics': current_metrics,
                'cost_info': cost_info,
                'health_status': health_status,
                'cloud_resource_id': resource.cloud_resource_id
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get resource status: {e}")
            raise

    async def list_resources(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all provisioned resources with optional filters."""
        try:
            resources = []
            
            for resource in self.provisioned_resources.values():
                # Apply filters if provided
                if filters:
                    if 'cloud_provider' in filters and resource.cloud_provider != filters['cloud_provider']:
                        continue
                    if 'state' in filters and resource.state.value != filters['state']:
                        continue
                    if 'resource_type' in filters and resource.resource_type != filters['resource_type']:
                        continue
                
                resource_info = {
                    'resource_id': resource.resource_id,
                    'resource_type': resource.resource_type,
                    'cloud_provider': resource.cloud_provider,
                    'state': resource.state.value,
                    'created_at': resource.created_at.isoformat(),
                    'cost_actual': resource.cost_actual
                }
                resources.append(resource_info)
            
            # Sort by creation time (newest first)
            resources.sort(key=lambda x: x['created_at'], reverse=True)
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Failed to list resources: {e}")
            return []

    async def get_provisioning_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive provisioning dashboard."""
        try:
            # Get resource summary
            resource_summary = await self._calculate_resource_summary()
            
            # Get cost summary
            cost_summary = await self._calculate_cost_summary()
            
            # Get active jobs
            active_jobs = [
                {
                    'job_id': job.job_id,
                    'request_id': job.request_id,
                    'status': job.status,
                    'progress_percentage': job.progress_percentage,
                    'start_time': job.start_time.isoformat()
                }
                for job in self.active_jobs.values()
                if job.status == 'running'
            ]
            
            # Get pending requests
            pending_requests = [
                {
                    'request_id': req_id,
                    'template_id': self.requests[req_id].template_id,
                    'requested_by': self.requests[req_id].requested_by,
                    'priority': self.requests[req_id].priority
                }
                for req_id in self.pending_approvals
            ]
            
            # Get scheduled requests
            upcoming_scheduled = [
                {
                    'request_id': req_id,
                    'scheduled_time': scheduled_time.isoformat(),
                    'template_id': self.requests[req_id].template_id
                }
                for scheduled_time, req_id in self.scheduled_requests[:5]
            ]
            
            # Get performance metrics
            performance_metrics = await self._calculate_performance_metrics()
            
            dashboard = {
                'summary': {
                    'total_resources': len(self.provisioned_resources),
                    'active_resources': len([r for r in self.provisioned_resources.values() 
                                           if r.state == ResourceState.ACTIVE]),
                    'total_cost_monthly': cost_summary.get('monthly_total', 0),
                    'active_jobs': len(active_jobs),
                    'pending_approvals': len(pending_requests)
                },
                'resource_summary': resource_summary,
                'cost_summary': cost_summary,
                'active_jobs': active_jobs,
                'pending_requests': pending_requests,
                'scheduled_requests': upcoming_scheduled,
                'performance_metrics': performance_metrics,
                'templates_available': len(self.templates),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {e}")
            raise

    # Private helper methods

    async def _start_provisioning(self, request_id -> None: str) -> None:
        """Start the provisioning process for a request."""
        try:
            self.logger.info(f"Starting provisioning for request: {request_id}")
            
            # Start provisioning in background
            asyncio.create_task(self.provision_resource(request_id))
            
        except Exception as e:
            self.logger.error(f"Failed to start provisioning: {e}")

    def _calculate_provisioning_steps(self, template: ResourceTemplate) -> int:
        """Calculate number of provisioning steps."""
        base_steps = 5  # validation, preparation, creation, configuration, verification
        
        # Add steps based on complexity
        if template.dependencies:
            base_steps += len(template.dependencies)
        
        if template.category == ResourceCategory.DATABASE:
            base_steps += 2  # backup setup, security configuration
        elif template.category == ResourceCategory.CONTAINER:
            base_steps += 3  # cluster setup, node configuration, health checks
        
        return base_steps

    async def _execute_provisioning(self, job: ProvisioningJob, 
                                  request: ResourceRequest, 
                                  template: ResourceTemplate) -> ProvisionedResource:
        """Execute the actual provisioning process."""
        try:
            self.logger.info(f"Executing provisioning for job: {job.job_id}")
            
            # Step 1: Validate configuration
            await self._update_job_progress(job, "Validating configuration", 1)
            merged_config = {**template.configuration, **request.custom_configuration}
            
            # Step 2: Prepare environment
            await self._update_job_progress(job, "Preparing environment", 2)
            await asyncio.sleep(1)  # Simulate preparation
            
            # Step 3: Create cloud resource
            await self._update_job_progress(job, "Creating cloud resource", 3)
            cloud_resource_id = await self._create_cloud_resource(template, merged_config)
            
            # Step 4: Configure resource
            await self._update_job_progress(job, "Configuring resource", 4)
            endpoints = await self._configure_resource(template, cloud_resource_id, merged_config)
            
            # Step 5: Verify resource
            await self._update_job_progress(job, "Verifying resource", 5)
            await self._verify_resource(template, cloud_resource_id)
            
            # Create provisioned resource record
            resource = ProvisionedResource(
                resource_id=str(uuid.uuid4()),
                request_id=request.request_id,
                template_id=template.template_id,
                cloud_provider=template.cloud_provider,
                resource_type=template.resource_type,
                state=ResourceState.ACTIVE,
                created_at=datetime.utcnow(),
                configuration=merged_config,
                cloud_resource_id=cloud_resource_id,
                endpoints=endpoints
            )
            
            return resource
            
        except Exception as e:
            self.logger.error(f"Provisioning execution failed: {e}")
            raise

    async def _update_job_progress(self, job -> None: ProvisioningJob, step_description -> None: str, step_number -> None: int) -> None:
        """Update job progress."""
        job.steps_completed = step_number
        job.progress_percentage = (step_number / job.steps_total) * 100
        self.logger.info(f"Job {job.job_id}: {step_description} ({job.progress_percentage:.1f}%)")
        
        # Simulate step execution time
        await asyncio.sleep(0.5)

    async def _create_cloud_resource(self, template: ResourceTemplate, 
                                   configuration: Dict[str, Any]) -> str:
        """Create resource in cloud provider."""
        try:
            provider = self.providers[template.cloud_provider]
            
            # Simulate cloud resource creation
            # In production, this would call actual cloud provider APIs
            cloud_resource_id = f"{template.cloud_provider}_{template.resource_type}_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"Created cloud resource: {cloud_resource_id}")
            return cloud_resource_id
            
        except Exception as e:
            self.logger.error(f"Cloud resource creation failed: {e}")
            raise

    async def _configure_resource(self, template: ResourceTemplate, 
                                cloud_resource_id: str,
                                configuration: Dict[str, Any]) -> List[str]:
        """Configure the created resource."""
        try:
            # Simulate resource configuration
            endpoints = []
            
            if template.category == ResourceCategory.COMPUTE:
                endpoints.append(f"http://{cloud_resource_id}.{template.cloud_provider}.compute.internal")
            elif template.category == ResourceCategory.DATABASE:
                endpoints.append(f"{cloud_resource_id}.{template.cloud_provider}.rds.internal:5432")
            elif template.category == ResourceCategory.STORAGE:
                endpoints.append(f"https://{cloud_resource_id}.s3.{template.cloud_provider}.com")
            
            self.logger.info(f"Configured resource with endpoints: {endpoints}")
            return endpoints
            
        except Exception as e:
            self.logger.error(f"Resource configuration failed: {e}")
            raise

    async def _verify_resource(self, template -> None: ResourceTemplate, cloud_resource_id -> None: str) -> None:
        """Verify resource is working correctly."""
        try:
            # Simulate resource verification
            await asyncio.sleep(1)
            
            # Perform health checks based on resource type
            if template.category == ResourceCategory.COMPUTE:
                await self._verify_compute_instance(cloud_resource_id)
            elif template.category == ResourceCategory.DATABASE:
                await self._verify_database(cloud_resource_id)
            
            self.logger.info(f"Resource verification completed: {cloud_resource_id}")
            
        except Exception as e:
            self.logger.error(f"Resource verification failed: {e}")
            raise

    async def _verify_compute_instance(self, cloud_resource_id -> None: str) -> None:
        """Verify compute instance is running."""
        # Simulate compute instance verification
        await asyncio.sleep(0.5)

    async def _verify_database(self, cloud_resource_id -> None: str) -> None:
        """Verify database is accessible."""
        # Simulate database verification
        await asyncio.sleep(1)

    async def _execute_scaling(self, resource: ProvisionedResource, 
                             scaling_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute resource scaling operation."""
        try:
            # Simulate scaling operation
            await asyncio.sleep(2)
            
            return {
                'success': True,
                'previous_config': resource.configuration.copy(),
                'new_config': {**resource.configuration, **scaling_config}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _execute_termination(self, resource: ProvisionedResource) -> Dict[str, Any]:
        """Execute resource termination."""
        try:
            # Simulate termination
            await asyncio.sleep(1)
            
            return {'success': True, 'terminated_at': datetime.utcnow().isoformat()}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _check_resource_dependencies(self, resource_id: str) -> List[str]:
        """Check for resource dependencies."""
        # Simulate dependency checking
        dependencies = []
        
        # In production, this would check actual dependencies
        for other_resource in self.provisioned_resources.values():
            if (resource_id in str(other_resource.configuration) and 
                other_resource.state == ResourceState.ACTIVE):
                dependencies.append(other_resource.resource_id)
        
        return dependencies

    async def _calculate_final_cost(self, resource: ProvisionedResource) -> float:
        """Calculate final cost for terminated resource."""
        try:
            # Calculate based on usage duration
            usage_duration = datetime.utcnow() - resource.created_at
            hours_used = usage_duration.total_seconds() / 3600
            
            # Get template for cost estimation
            template = self.templates.get(resource.template_id)
            if template:
                hourly_rate = template.cost_estimate / (24 * 30)  # Convert monthly to hourly
                total_cost = hours_used * hourly_rate
            else:
                total_cost = 0.0
            
            return round(total_cost, 2)
            
        except Exception as e:
            self.logger.error(f"Final cost calculation failed: {e}")
            return 0.0

    async def _get_resource_metrics(self, resource: ProvisionedResource) -> Dict[str, Any]:
        """Get current resource metrics."""
        try:
            # Simulate metrics collection
            import random
            
            metrics = {
                'cpu_utilization': round(random.uniform(10, 80), 2),
                'memory_utilization': round(random.uniform(20, 70), 2),
                'disk_utilization': round(random.uniform(5, 50), 2),
                'network_in_mbps': round(random.uniform(1, 100), 2),
                'network_out_mbps': round(random.uniform(1, 100), 2),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return {}

    async def _get_resource_cost_info(self, resource: ProvisionedResource) -> Dict[str, Any]:
        """Get resource cost information."""
        try:
            # Calculate current costs
            usage_duration = datetime.utcnow() - resource.created_at
            hours_used = usage_duration.total_seconds() / 3600
            
            template = self.templates.get(resource.template_id)
            if template:
                hourly_rate = template.cost_estimate / (24 * 30)
                current_cost = hours_used * hourly_rate
                estimated_monthly = template.cost_estimate
            else:
                current_cost = 0.0
                estimated_monthly = 0.0
            
            return {
                'current_cost': round(current_cost, 2),
                'estimated_monthly': round(estimated_monthly, 2),
                'hours_running': round(hours_used, 2),
                'cost_per_hour': round(hourly_rate, 4) if template else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Cost info calculation failed: {e}")
            return {}

    async def _get_resource_health(self, resource: ProvisionedResource) -> Dict[str, str]:
        """Get resource health status."""
        try:
            # Simulate health checking
            import random
            
            if resource.state == ResourceState.ACTIVE:
                health_score = random.uniform(80, 100)
                if health_score > 95:
                    status = "excellent"
                elif health_score > 85:
                    status = "good"
                elif health_score > 70:
                    status = "fair"
                else:
                    status = "poor"
            else:
                status = "unavailable"
                health_score = 0
            
            return {
                'status': status,
                'score': round(health_score, 1),
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {'status': 'unknown', 'score': 0, 'last_check': datetime.utcnow().isoformat()}

    async def _calculate_resource_summary(self) -> Dict[str, Any]:
        """Calculate resource summary statistics."""
        try:
            summary = {
                'by_cloud': {},
                'by_type': {},
                'by_state': {}
            }
            
            for resource in self.provisioned_resources.values():
                # By cloud provider
                cloud = resource.cloud_provider
                if cloud not in summary['by_cloud']:
                    summary['by_cloud'][cloud] = 0
                summary['by_cloud'][cloud] += 1
                
                # By resource type
                res_type = resource.resource_type
                if res_type not in summary['by_type']:
                    summary['by_type'][res_type] = 0
                summary['by_type'][res_type] += 1
                
                # By state
                state = resource.state.value
                if state not in summary['by_state']:
                    summary['by_state'][state] = 0
                summary['by_state'][state] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Resource summary calculation failed: {e}")
            return {}

    async def _calculate_cost_summary(self) -> Dict[str, Any]:
        """Calculate cost summary statistics."""
        try:
            total_actual = sum(r.cost_actual for r in self.provisioned_resources.values())
            
            # Calculate estimated monthly costs for active resources
            estimated_monthly = 0
            for resource in self.provisioned_resources.values():
                if resource.state == ResourceState.ACTIVE:
                    template = self.templates.get(resource.template_id)
                    if template:
                        estimated_monthly += template.cost_estimate
            
            return {
                'total_actual': round(total_actual, 2),
                'monthly_total': round(estimated_monthly, 2),
                'average_per_resource': round(total_actual / max(len(self.provisioned_resources), 1), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Cost summary calculation failed: {e}")
            return {}

    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        try:
            # Calculate success rate
            total_jobs = len(self.active_jobs)
            successful_jobs = len([j for j in self.active_jobs.values() if j.status == 'completed'])
            success_rate = (successful_jobs / max(total_jobs, 1)) * 100
            
            # Calculate average provisioning time
            completed_jobs = [j for j in self.active_jobs.values() if j.end_time]
            if completed_jobs:
                avg_duration = sum(
                    (j.end_time - j.start_time).total_seconds() / 60 
                    for j in completed_jobs
                ) / len(completed_jobs)
            else:
                avg_duration = 0
            
            return {
                'success_rate': round(success_rate, 1),
                'average_provisioning_minutes': round(avg_duration, 1),
                'total_jobs': total_jobs,
                'active_jobs': len([j for j in self.active_jobs.values() if j.status == 'running'])
            }
            
        except Exception as e:
            self.logger.error(f"Performance metrics calculation failed: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    async def main() -> None:
        # Initialize provisioner
        provisioner = CloudResourceProvisioner()
        
        # Request a new resource
        request_data = {
            'template_id': 'aws_ec2_web_server',
            'requested_by': 'developer@ainflue.com',
            'environment': 'dev',
            'priority': 'medium',
            'strategy': 'immediate',
            'approval_required': False,
            'custom_configuration': {
                'instance_type': 't3.large'
            }
        }
        
        request_id = await provisioner.request_resource(request_data)
        print(f"Resource requested: {request_id}")
        
        # Wait for provisioning to complete
        await asyncio.sleep(3)
        
        # Get dashboard
        dashboard = await provisioner.get_provisioning_dashboard()
        print(f"\nProvisioning Dashboard:")
        print(f"Total Resources: {dashboard['summary']['total_resources']}")
        print(f"Active Resources: {dashboard['summary']['active_resources']}")
        print(f"Monthly Cost: ${dashboard['summary']['total_cost_monthly']:.2f}")

    asyncio.run(main())