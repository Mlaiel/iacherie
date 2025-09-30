"""AI Processing Deployment Module - Enterprise Index
=================================================

Comprehensive entry point for enterprise-grade AI processing deployment system
supporting multi-format content analysis, protection, and monetization.

This module provides unified access to all deployment components including:
- High-performance AI model deployment and scaling
- Multi-format content fingerprinting engines  
- Vector database management and similarity search
- Kubernetes-native orchestration and scheduling
- Enterprise monitoring and security features

Features:
- Production-ready AI model serving infrastructure
- Auto-scaling with Kubernetes HPA integration  
- Multi-tenant processing with data isolation
- Real-time performance monitoring and alerting
- Advanced security with encryption and audit logging
- Support for GPU acceleration and distributed processing

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Core deployment infrastructure
from .core import (
    AIProcessingDeployment,
    ProcessingConfig, 
    ProcessingTask,
    ProcessingStatus,
    AIModelType
)

# Orchestration and coordination
from .orchestrator import (
    ProcessingOrchestrator,
    OrchestratorMode,
    WorkerNode,
    ProcessingPlan
)

# Processing pipeline management
from .pipeline import (
    ProcessingPipeline,
    PipelineConfig,
    PipelineStage,
    ContentFormat,
    StageResult,
    PipelineResult
)

# Advanced scheduling system
from .scheduler import (
    AIProcessingScheduler,
    SchedulingConfig,
    SchedulingStrategy,
    TaskPriority,
    ResourceRequirement,
    ScheduledTask,
    ResourcePool
)

# Deployment management
from .manager import (
    DeploymentManager,
    DeploymentConfig,
    DeploymentStatus,
    ScalingPolicy,
    MonitoringConfig
)

logger = logging.getLogger(__name__)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export all public components
__all__ = [
    # Core components
    "AIProcessingDeployment",
    "ProcessingConfig", 
    "ProcessingTask",
    "ProcessingStatus",
    "AIModelType",
    
    # Orchestration
    "ProcessingOrchestrator",
    "OrchestratorMode",
    "WorkerNode",
    "ProcessingPlan",
    
    # Pipeline processing
    "ProcessingPipeline",
    "PipelineConfig",
    "PipelineStage",
    "ContentFormat",
    "StageResult",
    "PipelineResult",
    
    # Scheduling
    "AIProcessingScheduler",
    "SchedulingConfig",
    "SchedulingStrategy",
    "TaskPriority",
    "ResourceRequirement",
    "ScheduledTask",
    "ResourcePool",
    
    # Management
    "DeploymentManager",
    "DeploymentConfig",
    "DeploymentStatus",
    "ScalingPolicy",
    "MonitoringConfig",
    
    # Factory functions
    "create_deployment_config",
    "create_orchestrator",
    "create_pipeline",
    "create_scheduler",
    "create_deployment_manager",
    "create_enterprise_deployment"
]


def create_deployment_config(
    max_workers: int = 10,
    gpu_enabled: bool = True,
    memory_limit: str = "16Gi",
    cpu_limit: str = "8",
    scaling_enabled: bool = True,
    monitoring_enabled: bool = True,
    security_enabled: bool = True,
    tenant_isolation: bool = True
) -> ProcessingConfig:
    """
    Create optimized processing configuration for deployment.
    
    Args:
        max_workers: Maximum number of processing workers
        gpu_enabled: Enable GPU acceleration
        memory_limit: Memory limit per worker (Kubernetes format)
        cpu_limit: CPU limit per worker
        scaling_enabled: Enable auto-scaling
        monitoring_enabled: Enable monitoring and metrics
        security_enabled: Enable security features
        tenant_isolation: Enable multi-tenant isolation
        
    Returns:
        ProcessingConfig: Configured processing settings
    """
    return ProcessingConfig(
        max_workers=max_workers,
        gpu_enabled=gpu_enabled,
        memory_limit=memory_limit,
        cpu_limit=cpu_limit,
        scaling_enabled=scaling_enabled,
        monitoring_enabled=monitoring_enabled,
        security_enabled=security_enabled,
        tenant_isolation=tenant_isolation
    )


async def create_orchestrator(
    mode: OrchestratorMode = OrchestratorMode.PRODUCTION,
    redis_url: str = "redis://localhost:6379",
    kubernetes_enabled: bool = True,
    monitoring_enabled: bool = True
) -> ProcessingOrchestrator:
    """
    Create and initialize processing orchestrator.
    
    Args:
        mode: Orchestrator operation mode
        redis_url: Redis connection URL for coordination
        kubernetes_enabled: Enable Kubernetes integration
        monitoring_enabled: Enable metrics and monitoring
        
    Returns:
        ProcessingOrchestrator: Initialized orchestrator instance
    """
    orchestrator = ProcessingOrchestrator(
        mode=mode,
        redis_url=redis_url,
        kubernetes_enabled=kubernetes_enabled,
        monitoring_enabled=monitoring_enabled
    )
    
    await orchestrator.initialize()
    return orchestrator


def create_pipeline(
    content_formats: List[ContentFormat],
    enable_gpu: bool = True,
    batch_size: int = 32,
    quality_checks: bool = True,
    monitoring: bool = True
) -> ProcessingPipeline:
    """
    Create content processing pipeline with specified formats.
    
    Args:
        content_formats: List of content formats to support
        enable_gpu: Enable GPU acceleration for processing
        batch_size: Processing batch size for optimization
        quality_checks: Enable quality assurance checks
        monitoring: Enable pipeline monitoring
        
    Returns:
        ProcessingPipeline: Configured processing pipeline
    """
    config = PipelineConfig(
        supported_formats=content_formats,
        gpu_enabled=enable_gpu,
        batch_size=batch_size,
        quality_checks_enabled=quality_checks,
        monitoring_enabled=monitoring
    )
    
    return ProcessingPipeline(config)


def create_scheduler(
    strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY_BASED,
    max_concurrent_tasks: int = 100,
    resource_optimization: bool = True
) -> AIProcessingScheduler:
    """
    Create AI processing scheduler with specified strategy.
    
    Args:
        strategy: Task scheduling strategy
        max_concurrent_tasks: Maximum concurrent processing tasks
        resource_optimization: Enable resource optimization
        
    Returns:
        AIProcessingScheduler: Configured scheduler instance
    """
    config = SchedulingConfig(
        strategy=strategy,
        max_concurrent_tasks=max_concurrent_tasks,
        resource_optimization_enabled=resource_optimization,
        metrics_enabled=True,
        health_checks_enabled=True
    )
    
    return AIProcessingScheduler(config)


def create_deployment_manager(
    environment: str = "production",
    auto_scaling: bool = True,
    monitoring: bool = True,
    security: bool = True
) -> DeploymentManager:
    """
    Create deployment manager for infrastructure management.
    
    Args:
        environment: Deployment environment (production/staging/development)
        auto_scaling: Enable auto-scaling capabilities
        monitoring: Enable comprehensive monitoring
        security: Enable security features
        
    Returns:
        DeploymentManager: Configured deployment manager
    """
    config = DeploymentConfig(
        environment=environment,
        auto_scaling_enabled=auto_scaling,
        monitoring_enabled=monitoring,
        security_enabled=security,
        multi_tenant=True,
        compliance_mode=True
    )
    
    return DeploymentManager(config)


async def create_enterprise_deployment(
    tenant_id: str,
    config: Optional[ProcessingConfig] = None,
    orchestrator_mode: OrchestratorMode = OrchestratorMode.PRODUCTION
) -> Dict[str, Any]:
    """
    Create complete enterprise deployment stack.
    
    This factory function creates and configures all necessary components
    for a production-ready AI processing deployment including:
    - Core processing deployment
    - Orchestrator for task coordination  
    - Processing pipeline for content analysis
    - Scheduler for resource management
    - Deployment manager for infrastructure
    
    Args:
        tenant_id: Unique tenant identifier
        config: Custom processing configuration
        orchestrator_mode: Orchestrator operation mode
        
    Returns:
        Dict containing all deployment components:
        - deployment: AIProcessingDeployment instance
        - orchestrator: ProcessingOrchestrator instance  
        - pipeline: ProcessingPipeline instance
        - scheduler: AIProcessingScheduler instance
        - manager: DeploymentManager instance
    """
    logger.info(f"Creating enterprise deployment for tenant: {tenant_id}")
    
    # Use default config if not provided
    if config is None:
        config = create_deployment_config()
    
    # Create core deployment
    deployment = AIProcessingDeployment(config)
    await deployment.initialize()
    
    # Create orchestrator
    orchestrator = await create_orchestrator(mode=orchestrator_mode)
    
    # Create processing pipeline with all content formats
    pipeline = create_pipeline([
        ContentFormat.AUDIO,
        ContentFormat.VIDEO, 
        ContentFormat.IMAGE,
        ContentFormat.TEXT
    ])
    
    # Create scheduler with priority-based strategy
    scheduler = create_scheduler(
        strategy=SchedulingStrategy.PRIORITY_BASED,
        max_concurrent_tasks=config.max_workers * 10
    )
    
    # Create deployment manager
    manager = create_deployment_manager()
    
    # Register components with each other for coordination
    await orchestrator.register_pipeline(pipeline)
    await orchestrator.register_scheduler(scheduler)
    await deployment.register_orchestrator(orchestrator)
    
    logger.info(f"Enterprise deployment created successfully for tenant: {tenant_id}")
    
    return {
        "deployment": deployment,
        "orchestrator": orchestrator,
        "pipeline": pipeline, 
        "scheduler": scheduler,
        "manager": manager,
        "tenant_id": tenant_id,
        "created_at": datetime.utcnow(),
        "status": "ready"
    }
)

from .manager import (
    DeploymentManager,
    DeploymentStatus,
    ScalingPolicy,
    DeploymentMetrics,
    ScalingConfiguration,
    AlertConfiguration,
    create_deployment_manager,
    create_production_deployment_manager
)

__all__ = [
    # Core components
    "AIProcessingDeployment",
    "ProcessingConfig",
    "ProcessingTask", 
    "ProcessingStatus",
    "AIModelType",
    "create_deployment_config",
    
    # Orchestrator
    "ProcessingOrchestrator",
    "OrchestratorMode",
    "WorkerNode",
    "ProcessingPlan", 
    "create_orchestrator",
    
    # Pipeline
    "ProcessingPipeline",
    "PipelineConfig",
    "PipelineStage",
    "ContentFormat",
    "StageResult",
    "PipelineResult",
    "create_pipeline",
    
    # Scheduler
    "AIProcessingScheduler",
    "SchedulingConfig",
    "SchedulingStrategy",
    "TaskPriority",
    "ResourceRequirement",
    "ScheduledTask",
    "ResourcePool",
    "create_scheduler",
    "create_high_performance_scheduler",
    
    # Manager
    "DeploymentManager",
    "DeploymentStatus", 
    "ScalingPolicy",
    "DeploymentMetrics",
    "ScalingConfiguration",
    "AlertConfiguration",
    "create_deployment_manager",
    "create_production_deployment_manager"
]


def create_complete_deployment(deployment_id: str, config_path: str = None):
    """
    Create a complete AI processing deployment with all components.
    
    Args:
        deployment_id: Unique identifier for the deployment
        config_path: Optional path to configuration file
        
    Returns:
        DeploymentManager: Fully configured deployment manager
    """
    return create_deployment_manager(deployment_id, config_path)


def get_deployment_info():
    """Get information about the AI processing deployment module."""
    return {
        "module": "ai_processing_deployment",
        "version": "2.0.0",
        "author": "Fahed Mlaiel",
        "email": "mlaiel@live.de",
        "description": "Enterprise AI processing deployment infrastructure",
        "components": [
            "AIProcessingDeployment",
            "ProcessingOrchestrator", 
            "ProcessingPipeline",
            "AIProcessingScheduler",
            "DeploymentManager"
        ],
        "features": [
            "Multi-format content processing",
            "AI fingerprinting and vector embeddings",
            "Intelligent task orchestration",
            "Enterprise monitoring and scaling", 
            "Production-ready deployment management"
        ]
    }
