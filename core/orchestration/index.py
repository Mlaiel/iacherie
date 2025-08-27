"""
Orchestration Module Index - Enterprise Orchestration System Entry Point

Centralized initialization and configuration management for the IA Influencer Agent
orchestration core module, providing streamlined access to all orchestration
components and intelligent system bootstrap.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import os
from pathlib import Path

from backend.core.orchestration.orchestration_controller import (
    OrchestrationController, OrchestrationConfig, OrchestrationMode
)
from backend.core.orchestration.workflow_engine import WorkflowEngine
from backend.core.orchestration.pipeline_builder import PipelineBuilder
from backend.core.orchestration.pipeline_coordinator import PipelineCoordinator
from backend.core.orchestration.task_scheduler import TaskScheduler
from backend.core.orchestration.resource_manager import ResourceManager
from backend.core.orchestration.performance_optimizer import PerformanceOptimizer


@dataclass
class OrchestrationSystemConfig:
    """Complete orchestration system configuration."""
    # System Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    config_path: Optional[str] = None
    
    # Orchestration Configuration
    orchestration_config: Optional[OrchestrationConfig] = None
    
    # Component Configurations
    workflow_config: Dict[str, Any] = field(default_factory=dict)
    pipeline_config: Dict[str, Any] = field(default_factory=dict)
    scheduler_config: Dict[str, Any] = field(default_factory=dict)
    resource_config: Dict[str, Any] = field(default_factory=dict)
    
    # Performance Configuration
    performance_config: Dict[str, Any] = field(default_factory=lambda: {
        "optimization_interval": 300,  # 5 minutes
        "metrics_retention_days": 30,
        "auto_scaling_enabled": True,
        "performance_thresholds": {
            "cpu_threshold": 0.8,
            "memory_threshold": 0.8,
            "response_time_threshold": 30.0
        }
    })
    
    # Monitoring Configuration
    monitoring_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "metrics_interval": 30,
        "health_check_interval": 60,
        "alert_thresholds": {
            "error_rate": 0.05,
            "response_time": 30,
            "resource_usage": 0.8
        }
    })


class OrchestrationSystem:
    """
    Complete orchestration system manager for IA Influencer Agent platform.
    
    Features:
    - Centralized system initialization
    - Component lifecycle management
    - Configuration management
    - Health monitoring and diagnostics
    - Performance optimization
    - Graceful shutdown handling
    """

    def __init__(self, config: Optional[OrchestrationSystemConfig] = None):
        """Initialize the orchestration system."""
        self.config = config or OrchestrationSystemConfig()
        self.logger = self._setup_logging()
        
        # Core components
        self.controller: Optional[OrchestrationController] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.pipeline_builder: Optional[PipelineBuilder] = None
        self.pipeline_coordinator: Optional[PipelineCoordinator] = None
        self.task_scheduler: Optional[TaskScheduler] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        
        # System state
        self.initialized = False
        self.running = False
        self.startup_time: Optional[datetime] = None
        self.component_health: Dict[str, bool] = {}

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    f"orchestration_system_{datetime.now().strftime('%Y%m%d')}.log"
                )
            ]
        )
        return logging.getLogger(__name__)

    async def initialize(self) -> bool:
        """
        Initialize the complete orchestration system.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing IA Influencer Agent Orchestration System...")
            self.startup_time = datetime.utcnow()
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize core components
            await self._initialize_components()
            
            # Verify component health
            await self._verify_system_health()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.initialized = True
            self.running = True
            
            self.logger.info(
                f"Orchestration system initialized successfully in "
                f"{(datetime.utcnow() - self.startup_time).total_seconds():.2f} seconds"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration system: {str(e)}")
            await self._cleanup_partial_initialization()
            return False

    async def _load_configuration(self):
        """Load and validate system configuration."""
        if self.config.config_path:
            # Load configuration from file
            config_path = Path(self.config.config_path)
            if config_path.exists():
                # Implementation for loading configuration from file
                pass
        
        # Set up orchestration configuration
        if not self.config.orchestration_config:
            self.config.orchestration_config = OrchestrationConfig(
                mode=OrchestrationMode.NORMAL,
                max_concurrent_workflows=50,
                max_concurrent_tasks=200,
                monitoring_config=self.config.monitoring_config
            )

    async def _initialize_components(self):
        """Initialize all orchestration components."""
        try:
            # Initialize Resource Manager first (other components depend on it)
            self.logger.info("Initializing Resource Manager...")
            self.resource_manager = ResourceManager()
            await self.resource_manager.initialize()
            self.component_health["resource_manager"] = True
            
            # Initialize Task Scheduler
            self.logger.info("Initializing Task Scheduler...")
            self.task_scheduler = TaskScheduler()
            await self.task_scheduler.initialize()
            self.component_health["task_scheduler"] = True
            
            # Initialize Performance Optimizer
            self.logger.info("Initializing Performance Optimizer...")
            self.performance_optimizer = PerformanceOptimizer()
            await self.performance_optimizer.initialize()
            self.component_health["performance_optimizer"] = True
            
            # Initialize Workflow Engine
            self.logger.info("Initializing Workflow Engine...")
            self.workflow_engine = WorkflowEngine()
            self.component_health["workflow_engine"] = True
            
            # Initialize Pipeline Builder
            self.logger.info("Initializing Pipeline Builder...")
            self.pipeline_builder = PipelineBuilder()
            self.component_health["pipeline_builder"] = True
            
            # Initialize Pipeline Coordinator
            self.logger.info("Initializing Pipeline Coordinator...")
            self.pipeline_coordinator = PipelineCoordinator()
            self.component_health["pipeline_coordinator"] = True
            
            # Initialize Orchestration Controller (master controller)
            self.logger.info("Initializing Orchestration Controller...")
            self.controller = OrchestrationController(
                config=self.config.orchestration_config,
                logger=self.logger
            )
            self.component_health["orchestration_controller"] = True
            
            self.logger.info("All orchestration components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {str(e)}")
            raise

    async def _verify_system_health(self):
        """Verify the health of all system components."""
        unhealthy_components = []
        
        for component_name, is_healthy in self.component_health.items():
            if not is_healthy:
                unhealthy_components.append(component_name)
        
        if unhealthy_components:
            raise RuntimeError(
                f"Unhealthy components detected: {', '.join(unhealthy_components)}"
            )
        
        # Perform additional health checks
        if self.controller:
            health_status = await self.controller._check_system_health()
            if not health_status["healthy"]:
                self.logger.warning(f"System health issues: {health_status['issues']}")

    async def _start_monitoring(self):
        """Start system monitoring and health checks."""
        if self.config.monitoring_config.get("enabled", True):
            # Start background monitoring tasks
            asyncio.create_task(self._health_monitoring_loop())
            asyncio.create_task(self._performance_monitoring_loop())
            
            self.logger.info("System monitoring started")

    async def _health_monitoring_loop(self):
        """Background health monitoring loop."""
        interval = self.config.monitoring_config.get("health_check_interval", 60)
        
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                # Check component health
                for component_name in self.component_health:
                    # Implement specific health checks for each component
                    health_status = await self._check_component_health(component_name)
                    self.component_health[component_name] = health_status
                
                # Check overall system health
                if self.controller:
                    system_health = await self.controller._check_system_health()
                    if not system_health["healthy"]:
                        self.logger.warning(f"System health degraded: {system_health['issues']}")
                        
                        # Trigger automatic remediation if configured
                        if self.config.performance_config.get("auto_scaling_enabled", True):
                            await self._auto_remediate(system_health)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")

    async def _performance_monitoring_loop(self):
        """Background performance monitoring loop."""
        interval = self.config.performance_config.get("optimization_interval", 300)
        
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                # Trigger performance optimization
                if self.controller:
                    await self.controller.optimize_performance()
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {str(e)}")

    async def _check_component_health(self, component_name: str) -> bool:
        """Check the health of a specific component."""
        try:
            component = getattr(self, component_name, None)
            if component is None:
                return False
            
            # Implement component-specific health checks
            if hasattr(component, 'health_check'):
                return await component.health_check()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed for {component_name}: {str(e)}")
            return False

    async def _auto_remediate(self, health_status: Dict[str, Any]):
        """Attempt automatic remediation of health issues."""
        try:
            for issue in health_status.get("issues", []):
                if "High" in issue and "usage" in issue:
                    # Scale resources if high usage detected
                    if self.resource_manager:
                        await self.resource_manager.scale_resources()
                
                elif "error rate" in issue:
                    # Restart components if high error rate
                    await self._restart_unhealthy_components()
                
        except Exception as e:
            self.logger.error(f"Auto-remediation failed: {str(e)}")

    async def _restart_unhealthy_components(self):
        """Restart unhealthy components."""
        for component_name, is_healthy in self.component_health.items():
            if not is_healthy:
                self.logger.info(f"Restarting unhealthy component: {component_name}")
                # Implement component restart logic
                # This would depend on the specific component implementation

    async def submit_workflow(
        self,
        workflow_name: str,
        template_id: Optional[str] = None,
        workflow_definition: Optional[Any] = None,
        priority: str = "normal",
        parameters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """
        Submit a workflow for execution through the orchestration system.
        
        Args:
            workflow_name: Name of the workflow
            template_id: Template ID for pipeline creation
            workflow_definition: Direct workflow definition
            priority: Execution priority
            parameters: Workflow parameters
            user_id: User identifier
            tenant_id: Tenant identifier
            
        Returns:
            str: Execution ID for tracking
        """
        if not self.controller:
            raise RuntimeError("Orchestration system not initialized")
        
        # Import necessary classes for workflow request
        from backend.core.orchestration.orchestration_controller import WorkflowRequest, Priority
        
        # Map string priority to enum
        priority_mapping = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "normal": Priority.NORMAL,
            "low": Priority.LOW,
            "background": Priority.BACKGROUND
        }
        
        request = WorkflowRequest(
            request_id=str(uuid.uuid4()),
            workflow_name=workflow_name,
            template_id=template_id,
            workflow_definition=workflow_definition,
            priority=priority_mapping.get(priority, Priority.NORMAL),
            parameters=parameters or {},
            user_id=user_id,
            tenant_id=tenant_id
        )
        
        execution_id = await self.controller.submit_workflow(request)
        return execution_id

    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        if not self.controller:
            raise RuntimeError("Orchestration system not initialized")
        
        return await self.controller.get_workflow_status(execution_id)

    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow execution."""
        if not self.controller:
            raise RuntimeError("Orchestration system not initialized")
        
        return await self.controller.cancel_workflow(execution_id)

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        if not self.controller:
            raise RuntimeError("Orchestration system not initialized")
        
        metrics = await self.controller.get_system_metrics()
        
        # Add component health status
        metrics_dict = {
            "orchestration_metrics": metrics.__dict__,
            "component_health": self.component_health,
            "system_uptime": (datetime.utcnow() - self.startup_time).total_seconds() if self.startup_time else 0,
            "system_status": "healthy" if all(self.component_health.values()) else "degraded"
        }
        
        return metrics_dict

    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        if not self.controller:
            raise RuntimeError("Orchestration system not initialized")
        
        return await self.controller.list_active_workflows()

    async def create_dynamic_pipeline(
        self,
        content_type: str,
        requirements: Dict[str, Any],
        optimization_level: str = "balanced"
    ) -> str:
        """Create a dynamic pipeline based on content type and requirements."""
        if not self.pipeline_builder:
            raise RuntimeError("Pipeline builder not initialized")
        
        workflow = await self.pipeline_builder.build_dynamic_pipeline(
            content_type=content_type,
            requirements=requirements,
            optimization_level=optimization_level
        )
        
        # Submit the dynamically created workflow
        execution_id = await self.submit_workflow(
            workflow_name=workflow.name,
            workflow_definition=workflow,
            parameters=requirements
        )
        
        return execution_id

    async def shutdown(self):
        """Gracefully shutdown the orchestration system."""
        try:
            self.logger.info("Shutting down orchestration system...")
            self.running = False
            
            # Shutdown controller first
            if self.controller:
                await self.controller.shutdown()
            
            # Shutdown other components
            components = [
                self.performance_optimizer,
                self.resource_manager,
                self.task_scheduler,
                self.pipeline_coordinator
            ]
            
            for component in components:
                if component and hasattr(component, 'shutdown'):
                    try:
                        await component.shutdown()
                    except Exception as e:
                        self.logger.error(f"Error shutting down component: {str(e)}")
            
            self.initialized = False
            self.logger.info("Orchestration system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    async def _cleanup_partial_initialization(self):
        """Clean up after partial initialization failure."""
        components = [
            self.controller,
            self.performance_optimizer,
            self.resource_manager,
            self.task_scheduler,
            self.pipeline_coordinator
        ]
        
        for component in components:
            if component and hasattr(component, 'shutdown'):
                try:
                    await component.shutdown()
                except Exception:
                    pass  # Ignore errors during cleanup

    def is_healthy(self) -> bool:
        """Check if the orchestration system is healthy."""
        return self.initialized and self.running and all(self.component_health.values())

    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed status of all components."""
        return {
            "initialized": self.initialized,
            "running": self.running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "component_health": self.component_health,
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds() if self.startup_time else 0
        }


# Global orchestration system instance
_orchestration_system: Optional[OrchestrationSystem] = None


async def initialize_orchestration_system(
    config: Optional[OrchestrationSystemConfig] = None
) -> OrchestrationSystem:
    """
    Initialize the global orchestration system.
    
    Args:
        config: System configuration
        
    Returns:
        OrchestrationSystem: Initialized system instance
    """
    global _orchestration_system
    
    if _orchestration_system is not None:
        return _orchestration_system
    
    _orchestration_system = OrchestrationSystem(config)
    success = await _orchestration_system.initialize()
    
    if not success:
        _orchestration_system = None
        raise RuntimeError("Failed to initialize orchestration system")
    
    return _orchestration_system


def get_orchestration_system() -> Optional[OrchestrationSystem]:
    """Get the global orchestration system instance."""
    return _orchestration_system


async def shutdown_orchestration_system():
    """Shutdown the global orchestration system."""
    global _orchestration_system
    
    if _orchestration_system:
        await _orchestration_system.shutdown()
        _orchestration_system = None


# Convenience functions for common operations
async def submit_content_processing_workflow(
    content_data: Dict[str, Any],
    user_id: str,
    tenant_id: Optional[str] = None,
    priority: str = "normal"
) -> str:
    """Submit a content processing workflow."""
    system = get_orchestration_system()
    if not system:
        raise RuntimeError("Orchestration system not initialized")
    
    return await system.submit_workflow(
        workflow_name="Content Processing",
        template_id="content_processing",
        parameters=content_data,
        priority=priority,
        user_id=user_id,
        tenant_id=tenant_id
    )


async def submit_protection_workflow(
    content_data: Dict[str, Any],
    user_id: str,
    tenant_id: Optional[str] = None,
    priority: str = "high"
) -> str:
    """Submit a content protection workflow."""
    system = get_orchestration_system()
    if not system:
        raise RuntimeError("Orchestration system not initialized")
    
    return await system.submit_workflow(
        workflow_name="Content Protection",
        template_id="protection_workflow",
        parameters=content_data,
        priority=priority,
        user_id=user_id,
        tenant_id=tenant_id
    )


async def submit_monetization_workflow(
    content_data: Dict[str, Any],
    user_id: str,
    tenant_id: Optional[str] = None,
    priority: str = "normal"
) -> str:
    """Submit a monetization workflow."""
    system = get_orchestration_system()
    if not system:
        raise RuntimeError("Orchestration system not initialized")
    
    return await system.submit_workflow(
        workflow_name="Monetization",
        template_id="monetization_pipeline",
        parameters=content_data,
        priority=priority,
        user_id=user_id,
        tenant_id=tenant_id
    )
