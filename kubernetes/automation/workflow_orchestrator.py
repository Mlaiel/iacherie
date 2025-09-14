"""Workflow Orchestrator - Deployment Automation

Main orchestration engine for managing complex deployment workflows across
the IA Influencer Agent platform including content protection, AI processing,
and monetization services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import uuid

from ..core.base import BaseComponent
from ..monitoring.metrics_collector import MetricsCollector
from ..infrastructure.cluster_manager import ClusterManager
from .service_deployer import ServiceDeployer
from .environment_provisioner import EnvironmentProvisioner
from .configuration_manager import ConfigurationManager
from .health_validator import HealthValidator
from .rollback_manager import RollbackManager
from .notification_handler import NotificationHandler
from .deployment_recorder import DeploymentRecorder


class DeploymentStrategy(Enum):
    """
Deployment strategy types"""

    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    RECREATE = "recreate"


class DeploymentPhase(Enum):
    """Deployment phase status"""

    PENDING = "pending"
    PREPARING = "preparing"
    DEPLOYING = "deploying"
    VALIDATING = "validating"
    PROMOTING = "promoting"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class WorkflowStep:
    """Individual workflow step configuration"""
    name: str
    action: Callable
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 3
    critical: bool = False
    parallel: bool = False
    rollback_action: Optional[Callable] = None
    validation: Optional[Callable] = None


@dataclass
class DeploymentWorkflow:
    """
Complete deployment workflow definition"""
    workflow_id: str
    name: str
    strategy: DeploymentStrategy
    environment: str
    services: List[str]
    steps: List[WorkflowStep]
    pre_hooks: List[Callable] = field(default_factory=list)
    post_hooks: List[Callable] = field(default_factory=list)
    rollback_hooks: List[Callable] = field(default_factory=list)
    max_duration: int = 3600
    auto_rollback: bool = True
    notification_channels: List[str] = field(default_factory=list)


class WorkflowOrchestrator(BaseComponent):
    """
    Enterprise-grade workflow orchestrator for deployment automation.
    
    Manages complex deployment workflows with support for multiple strategies,
    parallel execution, dependency management, and automated rollbacks.
    """
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.service_deployer = ServiceDeployer(config.get('service_deployer', {}))
        self.environment_provisioner = EnvironmentProvisioner(config.get('environment', {}))
        self.configuration_manager = ConfigurationManager(config.get('configuration', {}))
        self.health_validator = HealthValidator(config.get('health_validation', {}))
        self.rollback_manager = RollbackManager(config.get('rollback', {}))
        self.notification_handler = NotificationHandler(config.get('notifications', {}))
        self.deployment_recorder = DeploymentRecorder(config.get('recording', {}))
        
        # Infrastructure
        self.cluster_manager = ClusterManager(config.get('cluster', {}))
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        
        # Workflow state
        self.active_workflows: Dict[str, DeploymentWorkflow] = {}
        self.workflow_states: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        
        # Strategy handlers
        self.strategy_handlers = {
            DeploymentStrategy.BLUE_GREEN: self._handle_blue_green_deployment,
            DeploymentStrategy.ROLLING: self._handle_rolling_deployment,
            DeploymentStrategy.CANARY: self._handle_canary_deployment,
            DeploymentStrategy.RECREATE: self._handle_recreate_deployment
        }

    async def execute_workflow(
        self, 
        workflow: DeploymentWorkflow,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete deployment workflow.
        
        Args:
            workflow: Deployment workflow definition
            context: Additional execution context
            
        Returns:
            Workflow execution results
        """
        workflow_id = workflow.workflow_id
        self.active_workflows[workflow_id] = workflow
        
        execution_context = {
            'workflow_id': workflow_id,
            'start_time': datetime.utcnow(),
            'environment': workflow.environment,
            'strategy': workflow.strategy.value,
            'services': workflow.services,
            'phase': DeploymentPhase.PENDING,
            'steps_completed': [],
            'current_step': None,
            'errors': [],
            'metrics': {},
            **(context or {})
        }
        
        self.workflow_states[workflow_id] = execution_context
        
        try:
            self.logger.info(f"Starting workflow execution: {workflow.name} ({workflow_id})")
            
            # Record workflow start
            await self.deployment_recorder.record_workflow_start(workflow, execution_context)
            
            # Send start notifications
            await self.notification_handler.notify_workflow_start(workflow, execution_context)
            
            # Execute pre-hooks
            await self._execute_hooks(workflow.pre_hooks, execution_context, "pre-hook")
            
            # Prepare environment
            execution_context['phase'] = DeploymentPhase.PREPARING
            await self._prepare_environment(workflow, execution_context)
            
            # Execute main deployment strategy
            execution_context['phase'] = DeploymentPhase.DEPLOYING
            deployment_result = await self._execute_deployment_strategy(workflow, execution_context)
            
            # Validate deployment
            execution_context['phase'] = DeploymentPhase.VALIDATING
            validation_result = await self._validate_deployment(workflow, execution_context)
            
            if validation_result['success']:
                # Promote deployment
                execution_context['phase'] = DeploymentPhase.PROMOTING
                await self._promote_deployment(workflow, execution_context)
                
                # Execute post-hooks
                await self._execute_hooks(workflow.post_hooks, execution_context, "post-hook")
                
                execution_context['phase'] = DeploymentPhase.COMPLETED
                execution_context['end_time'] = datetime.utcnow()
                execution_context['success'] = True
                
                self.logger.info(f"Workflow completed successfully: {workflow_id}")
                
            else:
                # Validation failed, trigger rollback if enabled
                if workflow.auto_rollback:
                    await self._trigger_rollback(workflow, execution_context, "Validation failed")
                else:
                    execution_context['phase'] = DeploymentPhase.FAILED
                    execution_context['success'] = False
                    
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow_id}", exc_info=True)
            execution_context['errors'].append(str(e))
            execution_context['success'] = False
            
            # Trigger rollback if enabled
            if workflow.auto_rollback:
                await self._trigger_rollback(workflow, execution_context, f"Execution error: {str(e)}")
            else:
                execution_context['phase'] = DeploymentPhase.FAILED
                
        finally:
            # Record workflow completion
            await self.deployment_recorder.record_workflow_completion(workflow, execution_context)
            
            # Send completion notifications
            await self.notification_handler.notify_workflow_completion(workflow, execution_context)
            
            # Cleanup
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
                
        return execution_context

    async def _prepare_environment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> None:
        """Prepare deployment environment"""
        self.logger.info(f"Preparing environment for workflow: {workflow.workflow_id}")
        
        # Provision infrastructure resources
        provisioning_result = await self.environment_provisioner.provision_environment(
            workflow.environment,
            workflow.services,
            context
        )
        
        context['provisioning_result'] = provisioning_result
        
        # Prepare configurations
        config_result = await self.configuration_manager.prepare_configurations(
            workflow.environment,
            workflow.services,
            context
        )
        
        context['configuration_result'] = config_result
        
        # Validate environment readiness
        readiness_check = await self.health_validator.validate_environment_readiness(
            workflow.environment,
            context
        )
        
        if not readiness_check['ready']:
            raise Exception(f"Environment not ready: {readiness_check['errors']}")

    async def _execute_deployment_strategy(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute deployment using specified strategy"""
        strategy_handler = self.strategy_handlers.get(workflow.strategy)
        
        if not strategy_handler:
            raise ValueError(f"Unsupported deployment strategy: {workflow.strategy}")
            
        self.logger.info(f"Executing {workflow.strategy.value} deployment for workflow: {workflow.workflow_id}")
        
        return await strategy_handler(workflow, context)

    async def _handle_blue_green_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle blue-green deployment strategy"""
        results = {}
        
        # Deploy to green environment
        green_deployment = await self.service_deployer.deploy_services(
            workflow.services,
            f"{workflow.environment}-green",
            context
        )
        
        results['green_deployment'] = green_deployment
        
        # Validate green environment
        green_validation = await self.health_validator.validate_services(
            workflow.services,
            f"{workflow.environment}-green",
            context
        )
        
        if green_validation['healthy']:
            # Switch traffic to green
            traffic_switch = await self.cluster_manager.switch_traffic(
                workflow.environment,
                f"{workflow.environment}-green",
                context
            )
            
            results['traffic_switch'] = traffic_switch
            
            # Prepare rollback snapshot
            await self.rollback_manager.create_rollback_point(
                workflow.workflow_id,
                f"{workflow.environment}-blue",
                context
            )
            
        else:
            raise Exception(f"Green environment validation failed: {green_validation['errors']}")
            
        return results

    async def _handle_rolling_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle rolling deployment strategy"""
        results = {}
        
        # Get current service instances
        instances = await self.cluster_manager.get_service_instances(
            workflow.services,
            workflow.environment
        )
        
        # Calculate rolling update batches
        batch_size = context.get('rolling_batch_size', 1)
        batches = [instances[i:i + batch_size] for i in range(0, len(instances), batch_size)]
        
        # Deploy in rolling fashion
        for batch_index, batch in enumerate(batches):
            batch_result = await self.service_deployer.deploy_service_batch(
                batch,
                workflow.environment,
                context
            )
            
            # Validate batch health
            batch_validation = await self.health_validator.validate_service_batch(
                batch,
                workflow.environment,
                context
            )
            
            if not batch_validation['healthy']:
                raise Exception(f"Batch {batch_index} validation failed: {batch_validation['errors']}")
                
            results[f'batch_{batch_index}'] = batch_result
            
            # Wait for stabilization
            await asyncio.sleep(context.get('rolling_wait_time', 30))
            
        return results

    async def _handle_canary_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle canary deployment strategy"""
        results = {}
        
        # Deploy canary version
        canary_deployment = await self.service_deployer.deploy_canary_services(
            workflow.services,
            workflow.environment,
            context.get('canary_percentage', 10),
            context
        )
        
        results['canary_deployment'] = canary_deployment
        
        # Monitor canary metrics
        canary_metrics = await self.metrics_collector.collect_canary_metrics(
            workflow.services,
            workflow.environment,
            context.get('canary_monitoring_duration', 300)
        )
        
        results['canary_metrics'] = canary_metrics
        
        # Analyze canary performance
        canary_analysis = await self._analyze_canary_performance(canary_metrics, context)
        
        if canary_analysis['successful']:
            # Promote canary to full deployment
            full_deployment = await self.service_deployer.promote_canary_to_full(
                workflow.services,
                workflow.environment,
                context
            )
            
            results['full_deployment'] = full_deployment
            
        else:
            raise Exception(f"Canary analysis failed: {canary_analysis['issues']}")
            
        return results

    async def _handle_recreate_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle recreate deployment strategy"""
        results = {}
        
        # Create rollback point before destruction
        await self.rollback_manager.create_rollback_point(
            workflow.workflow_id,
            workflow.environment,
            context
        )
        
        # Stop existing services
        stop_result = await self.service_deployer.stop_services(
            workflow.services,
            workflow.environment,
            context
        )
        
        results['stop_result'] = stop_result
        
        # Deploy new services
        deploy_result = await self.service_deployer.deploy_services(
            workflow.services,
            workflow.environment,
            context
        )
        
        results['deploy_result'] = deploy_result
        
        return results

    async def _validate_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Validate deployment success"""
        validation_results = {}
        
        # Health validation
        health_validation = await self.health_validator.validate_services(
            workflow.services,
            workflow.environment,
            context
        )
        
        validation_results['health'] = health_validation
        
        # Performance validation
        performance_validation = await self.health_validator.validate_performance(
            workflow.services,
            workflow.environment,
            context
        )
        
        validation_results['performance'] = performance_validation
        
        # Security validation
        security_validation = await self.health_validator.validate_security(
            workflow.services,
            workflow.environment,
            context
        )
        
        validation_results['security'] = security_validation
        
        # Overall validation result
        validation_results['success'] = (
            health_validation['healthy'] and
            performance_validation['acceptable'] and
            security_validation['secure']
        )
        
        return validation_results

    async def _promote_deployment(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any]
    ) -> None:
        """
Promote deployment to production traffic"""
        if workflow.strategy == DeploymentStrategy.BLUE_GREEN:
            # Update load balancer configuration
            await self.cluster_manager.update_load_balancer(
                workflow.environment,
                workflow.services,
                context
            )
            
            # Update DNS records if needed
            await self.cluster_manager.update_dns_records(
                workflow.environment,
                workflow.services,
                context
            )

    async def _trigger_rollback(
        self, 
        workflow: DeploymentWorkflow, 
        context: Dict[str, Any],
        reason: str
    ) -> None:
        """
Trigger automated rollback"""
        self.logger.warning(f"Triggering rollback for workflow {workflow.workflow_id}: {reason}")
        
        context['phase'] = DeploymentPhase.ROLLED_BACK
        context['rollback_reason'] = reason
        context['rollback_time'] = datetime.utcnow()
        
        try:
            # Execute rollback hooks
            await self._execute_hooks(workflow.rollback_hooks, context, "rollback-hook")
            
            # Perform rollback
            rollback_result = await self.rollback_manager.execute_rollback(
                workflow.workflow_id,
                workflow.environment,
                context
            )
            
            context['rollback_result'] = rollback_result
            context['rollback_success'] = rollback_result.get('success', False)
            
        except Exception as e:
            self.logger.error(f"Rollback failed for workflow {workflow.workflow_id}", exc_info=True)
            context['rollback_error'] = str(e)
            context['rollback_success'] = False

    async def _execute_hooks(
        self, 
        hooks: List[Callable], 
        context: Dict[str, Any],
        hook_type: str
    ) -> None:
        """Execute workflow hooks"""
        if not hooks:
            return
            
        self.logger.info(f"Executing {len(hooks)} {hook_type}s")
        
        for i, hook in enumerate(hooks):
            try:
                await hook(context)
                self.logger.debug(f"Executed {hook_type} {i + 1}/{len(hooks)}")
            except Exception as e:
                self.logger.error(f"Failed to execute {hook_type} {i + 1}: {str(e)}")
                raise

    async def _analyze_canary_performance(
        self, 
        metrics: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze canary deployment performance"""
        analysis = {
            'successful': True,
            'issues': []
        }
        
        # Check error rate
        error_rate = metrics.get('error_rate', 0)
        if error_rate > context.get('canary_max_error_rate', 0.05):
            analysis['successful'] = False
            analysis['issues'].append(f"High error rate: {error_rate}")
        
        # Check response time
        response_time = metrics.get('avg_response_time', 0)
        if response_time > context.get('canary_max_response_time', 500):
            analysis['successful'] = False
            analysis['issues'].append(f"High response time: {response_time}ms")
        
        # Check resource usage
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > context.get('canary_max_cpu_usage', 0.8):
            analysis['successful'] = False
            analysis['issues'].append(f"High CPU usage: {cpu_usage}")
        
        return analysis

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        return self.workflow_states.get(workflow_id)

    async def cancel_workflow(self, workflow_id: str, reason: str = "") -> bool:
        """Cancel active workflow"""
        if workflow_id not in self.active_workflows:
            return False
            
        workflow = self.active_workflows[workflow_id]
        context = self.workflow_states.get(workflow_id, {})
        
        self.logger.info(f"Cancelling workflow: {workflow_id} - {reason}")
        
        # Trigger rollback if deployment is in progress
        if context.get('phase') in [DeploymentPhase.DEPLOYING, DeploymentPhase.VALIDATING]:
            await self._trigger_rollback(workflow, context, f"Cancelled: {reason}")
        
        # Update state
        context['phase'] = DeploymentPhase.FAILED
        context['cancelled'] = True
        context['cancel_reason'] = reason
        context['end_time'] = datetime.utcnow()
        
        # Cleanup
        del self.active_workflows[workflow_id]
        
        return True

    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        return [
            {
                'workflow_id': workflow.workflow_id,
                'name': workflow.name,
                'strategy': workflow.strategy.value,
                'environment': workflow.environment,
                'phase': self.workflow_states.get(workflow.workflow_id, {}).get('phase'),
                'start_time': self.workflow_states.get(workflow.workflow_id, {}).get('start_time')
            }
            for workflow in self.active_workflows.values()
        ]

    async def create_creator_onboarding_workflow(
        self,
        creator_type: str,
        environment: str,
        creator_tier: str = "standard"
    ) -> str:
        """
        Create specialized workflow for creator onboarding.
        
        This workflow orchestrates the deployment of all services needed
        for a specific type of creator (musician, video creator, photographer, etc.)
        """
        workflow_id = f"creator_onboarding_{creator_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Define services based on creator type
        creator_services = self._get_creator_services(creator_type, creator_tier)
        
        # Build specialized workflow steps
        workflow_steps = [
            WorkflowStep(
                name="provision_creator_infrastructure",
                action=self._provision_creator_infrastructure,
                timeout=900,
                critical=True
            ),
            WorkflowStep(
                name="deploy_ai_processing_stack",
                action=self._deploy_ai_processing_stack,
                dependencies=["provision_creator_infrastructure"],
                timeout=1200,
                critical=True,
                parallel=True
            ),
            WorkflowStep(
                name="setup_content_protection",
                action=self._setup_content_protection,
                dependencies=["deploy_ai_processing_stack"],
                timeout=1800,
                critical=True
            ),
            WorkflowStep(
                name="initialize_monetization_pipeline",
                action=self._initialize_monetization_pipeline,
                dependencies=["setup_content_protection"],
                timeout=600,
                critical=False
            ),
            WorkflowStep(
                name="configure_creator_workspace",
                action=self._configure_creator_workspace,
                dependencies=["initialize_monetization_pipeline"],
                timeout=300,
                critical=True
            ),
            WorkflowStep(
                name="validate_creator_workflow",
                action=self._validate_creator_workflow,
                dependencies=["configure_creator_workspace"],
                timeout=900,
                critical=True,
                validation=self._validate_end_to_end_creator_flow
            )
        ]
        
        # Add creator-type specific steps
        if creator_type in ["musician", "composer"]:
            workflow_steps.append(WorkflowStep(
                name="setup_audio_processing",
                action=self._setup_audio_processing,
                dependencies=["deploy_ai_processing_stack"],
                timeout=1500,
                critical=True
            ))
        
        if creator_type in ["video_creator", "filmmaker"]:
            workflow_steps.append(WorkflowStep(
                name="setup_video_processing",
                action=self._setup_video_processing,
                dependencies=["deploy_ai_processing_stack"],
                timeout=2100,
                critical=True
            ))
        
        workflow = DeploymentWorkflow(
            workflow_id=workflow_id,
            name=f"Creator Onboarding - {creator_type.title()}",
            strategy=DeploymentStrategy.ROLLING,
            environment=environment,
            services=creator_services,
            steps=workflow_steps,
            pre_hooks=[self._validate_creator_requirements],
            post_hooks=[self._notify_creator_onboarding_complete],
            max_duration=5400,  # 1.5 hours
            auto_rollback=True,
            notification_channels=["creator_support", "admin"]
        )
        
        return await self.execute_workflow(workflow)

    def _get_creator_services(self, creator_type: str, creator_tier: str) -> List[str]:
        """Get required services for specific creator type"""
        base_services = [
            "api_gateway",
            "ai_agent", 
            "content_protection",
            "fingerprinting",
            "seo_optimization"
        ]
        
        creator_type_services = {
            "musician": ["audio_processing", "music_generation", "audio_fingerprinting"],
            "composer": ["audio_processing", "music_generation", "collaboration_matching"],
            "video_creator": ["video_processing", "video_fingerprinting", "content_protection"],
            "photographer": ["image_processing", "image_fingerprinting", "licensing_engine"],
            "writer": ["text_processing", "plagiarism_detection", "seo_optimization"],
            "influencer": ["multi_media_processing", "cross_platform_integration", "analytics"],
            "comedian": ["audio_processing", "video_processing", "content_protection"]
        }
        
        tier_services = {
            "basic": ["monetization"],
            "standard": ["monetization", "revenue_analytics"],
            "premium": ["monetization", "revenue_analytics", "collaboration_matching", "priority_support"],
            "enterprise": ["monetization", "revenue_analytics", "collaboration_matching", "custom_integration", "dedicated_support"]
        }
        
        services = base_services.copy()
        services.extend(creator_type_services.get(creator_type, []))
        services.extend(tier_services.get(creator_tier, []))
        
        return list(set(services))  # Remove duplicates

    async def create_content_protection_workflow(
        self,
        content_types: List[str],
        environment: str,
        urgency: str = "normal"
    ) -> str:
        """
        Create workflow for deploying content protection systems.
        
        Optimized for rapid deployment when copyright infringement is detected.
        """
        workflow_id = f"content_protection_{urgency}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Adjust timeouts based on urgency
        timeouts = {
            "urgent": {"base": 300, "multiplier": 0.5},
            "normal": {"base": 600, "multiplier": 1.0}, 
            "planned": {"base": 900, "multiplier": 1.5}
        }
        
        timeout_config = timeouts.get(urgency, timeouts["normal"])
        
        workflow_steps = [
            WorkflowStep(
                name="provision_vector_database",
                action=self._provision_vector_database,
                timeout=int(timeout_config["base"] * timeout_config["multiplier"]),
                critical=True
            ),
            WorkflowStep(
                name="deploy_fingerprinting_engines",
                action=self._deploy_fingerprinting_engines,
                dependencies=["provision_vector_database"],
                timeout=int(1200 * timeout_config["multiplier"]),
                critical=True,
                parallel=True
            ),
            WorkflowStep(
                name="setup_content_crawlers",
                action=self._setup_content_crawlers,
                dependencies=["deploy_fingerprinting_engines"],
                timeout=int(900 * timeout_config["multiplier"]),
                critical=True
            ),
            WorkflowStep(
                name="initialize_protection_monitoring",
                action=self._initialize_protection_monitoring,
                dependencies=["setup_content_crawlers"],
                timeout=int(300 * timeout_config["multiplier"]),
                critical=True
            )
        ]
        
        workflow = DeploymentWorkflow(
            workflow_id=workflow_id,
            name=f"Content Protection Deployment - {urgency.title()}",
            strategy=DeploymentStrategy.ROLLING if urgency != "urgent" else DeploymentStrategy.BLUE_GREEN,
            environment=environment,
            services=["content_protection", "fingerprinting", "crawler", "vector_database"],
            steps=workflow_steps,
            max_duration=3600 if urgency != "urgent" else 1800,
            auto_rollback=True
        )
        
        return await self.execute_workflow(workflow)

    async def create_monetization_workflow(
        self,
        platforms: List[str],
        environment: str,
        payment_providers: List[str] = None
    ) -> str:
        """
        Create workflow for deploying monetization and revenue tracking systems.
        """
        workflow_id = f"monetization_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        payment_providers = payment_providers or ["stripe", "wise", "paypal"]
        
        workflow_steps = [
            WorkflowStep(
                name="setup_payment_infrastructure",
                action=self._setup_payment_infrastructure,
                timeout=900,
                critical=True
            ),
            WorkflowStep(
                name="configure_platform_integrations",
                action=self._configure_platform_integrations,
                dependencies=["setup_payment_infrastructure"],
                timeout=1200,
                critical=True
            ),
            WorkflowStep(
                name="deploy_revenue_tracking",
                action=self._deploy_revenue_tracking,
                dependencies=["configure_platform_integrations"],
                timeout=600,
                critical=True
            ),
            WorkflowStep(
                name="initialize_analytics_engine",
                action=self._initialize_analytics_engine,
                dependencies=["deploy_revenue_tracking"],
                timeout=900,
                critical=False
            ),
            WorkflowStep(
                name="setup_automated_payouts",
                action=self._setup_automated_payouts,
                dependencies=["initialize_analytics_engine"],
                timeout=600,
                critical=True
            )
        ]
        
        workflow = DeploymentWorkflow(
            workflow_id=workflow_id,
            name="Monetization System Deployment",
            strategy=DeploymentStrategy.ROLLING,
            environment=environment,
            services=["monetization", "revenue_analytics", "payment_processing"],
            steps=workflow_steps,
            max_duration=4200,
            auto_rollback=True
        )
        
        return await self.execute_workflow(workflow)

    async def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """Cleanup old completed workflow states"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        workflows_to_remove = []
        for workflow_id, state in self.workflow_states.items():
            if (state.get('phase') in [DeploymentPhase.COMPLETED, DeploymentPhase.FAILED, DeploymentPhase.ROLLED_BACK] and
                state.get('end_time', datetime.utcnow()) < cutoff_time):
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.workflow_states[workflow_id]
            cleaned_count += 1
            
        return cleaned_count
