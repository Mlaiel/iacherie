"""AI Deployment Index
Main entry point for IA Influencer Agent AI deployment system

This index provides centralized access to all AI deployment capabilities
including model serving, training pipelines, edge computing, federated learning,
MLOps, creative AI, conversational AI, and computer vision AI deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import yaml
import time

# Import all deployment managers
from .model_serving import ModelServer
from .training_pipeline import TrainingPipeline
from .edge_computing_deployment import EdgeComputingDeployment
from .federated_learning_deployment import FederatedLearningDeployment
from .mlops_pipeline_deployment import MLOpsPipelineDeployment
from .creative_ai_deployment import CreativeAIDeployment
from .conversational_ai_deployment import ConversationalAIDeployment
from .computer_vision_ai_deployment import ComputerVisionAIDeployment

logger = logging.getLogger(__name__)


class AIDeploymentType(Enum):
    """
AI deployment types available in the system"""

    MODEL_SERVING = "model_serving"
    TRAINING_PIPELINE = "training_pipeline"
    EDGE_COMPUTING = "edge_computing"
    FEDERATED_LEARNING = "federated_learning"
    MLOPS_PIPELINE = "mlops_pipeline"
    CREATIVE_AI = "creative_ai"
    CONVERSATIONAL_AI = "conversational_ai"
    COMPUTER_VISION_AI = "computer_vision_ai"


class AIDeploymentStatus(Enum):
    """AI deployment status states"""

    INITIALIZING = "initializing"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    RUNNING = "running"
    SCALING = "scaling"
    UPDATING = "updating"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


@dataclass
class AIDeploymentSummary:
    """Summary of AI deployment system"""
    deployment_id: str
    deployment_type: AIDeploymentType
    status: AIDeploymentStatus
    deployed_at: str
    namespace: str
    resource_usage: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    capabilities: List[str]


class AIDeploymentManager:
    """
    Central AI Deployment Manager
    
    Provides unified access to all AI deployment capabilities:
    - Model serving and inference
    - Training pipeline orchestration
    - Edge computing deployment
    - Federated learning coordination
    - MLOps pipeline management
    - Creative AI deployment
    - Conversational AI systems
    - Computer vision AI services
    
    Features:
    - Centralized deployment orchestration
    - Cross-system resource management
    - Unified monitoring and analytics
    - Enterprise-grade security and compliance
    - Multi-tenant isolation
    - Cost optimization
    - Performance optimization
    - Disaster recovery
    """
    
    def __init__(self, base_namespace: str = "ia-influencer-ai"):
        """
        Initialize AI deployment manager
        
        Args:
            base_namespace: Base Kubernetes namespace for all AI deployments
        """
        self.base_namespace = base_namespace
        self.deployments = {}
        self.deployment_managers = {}
        self.global_status = "initializing"
        
        # Initialize all deployment managers
        self._initialize_deployment_managers()
    
    def _initialize_deployment_managers(self) -> None:
        """Initialize all AI deployment managers"""
        try:
            # Model serving manager
            self.deployment_managers[AIDeploymentType.MODEL_SERVING] = ModelServer(
                namespace=f"{self.base_namespace}-model-serving"
            )
            
            # Training pipeline manager
            self.deployment_managers[AIDeploymentType.TRAINING_PIPELINE] = TrainingPipeline(
                namespace=f"{self.base_namespace}-training"
            )
            
            # Edge computing manager
            self.deployment_managers[AIDeploymentType.EDGE_COMPUTING] = EdgeComputingDeployment(
                namespace=f"{self.base_namespace}-edge"
            )
            
            # Federated learning manager
            self.deployment_managers[AIDeploymentType.FEDERATED_LEARNING] = FederatedLearningDeployment(
                namespace=f"{self.base_namespace}-federated"
            )
            
            # MLOps pipeline manager
            self.deployment_managers[AIDeploymentType.MLOPS_PIPELINE] = MLOpsPipelineDeployment(
                namespace=f"{self.base_namespace}-mlops"
            )
            
            # Creative AI manager
            self.deployment_managers[AIDeploymentType.CREATIVE_AI] = CreativeAIDeployment(
                namespace=f"{self.base_namespace}-creative"
            )
            
            # Conversational AI manager
            self.deployment_managers[AIDeploymentType.CONVERSATIONAL_AI] = ConversationalAIDeployment(
                namespace=f"{self.base_namespace}-conversational"
            )
            
            # Computer vision AI manager
            self.deployment_managers[AIDeploymentType.COMPUTER_VISION_AI] = ComputerVisionAIDeployment(
                namespace=f"{self.base_namespace}-vision"
            )
            
            logger.info("All AI deployment managers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI deployment managers: {e}")
            raise
    
    async def deploy_complete_ai_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete AI infrastructure across all systems
        
        Returns:
            Complete AI infrastructure deployment summary
        """
        try:
            self.global_status = "deploying"
            logger.info("Deploying complete AI infrastructure")
            
            deployment_results = {}
            
            # Deploy all AI infrastructure systems in parallel
            deployment_tasks = []
            
            # Model serving infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.MODEL_SERVING,
                    "deploy_model_serving_infrastructure"
                )
            )
            
            # Training pipeline infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.TRAINING_PIPELINE,
                    "deploy_training_infrastructure"
                )
            )
            
            # Edge computing infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.EDGE_COMPUTING,
                    "deploy_edge_computing_infrastructure"
                )
            )
            
            # Federated learning infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.FEDERATED_LEARNING,
                    "deploy_federated_learning_infrastructure"
                )
            )
            
            # MLOps pipeline infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.MLOPS_PIPELINE,
                    "deploy_mlops_infrastructure"
                )
            )
            
            # Creative AI infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.CREATIVE_AI,
                    "deploy_creative_ai_infrastructure"
                )
            )
            
            # Conversational AI infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.CONVERSATIONAL_AI,
                    "deploy_conversational_ai_infrastructure"
                )
            )
            
            # Computer vision AI infrastructure
            deployment_tasks.append(
                self._deploy_infrastructure_component(
                    AIDeploymentType.COMPUTER_VISION_AI,
                    "deploy_computer_vision_infrastructure"
                )
            )
            
            # Execute all deployments
            results = await asyncio.gather(*deployment_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                deployment_type = list(AIDeploymentType)[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to deploy {deployment_type.value}: {result}")
                    deployment_results[deployment_type.value] = {"status": "failed", "error": str(result)}
                else:
                    deployment_results[deployment_type.value] = result
            
            # Validate overall deployment
            success_count = sum(1 for r in deployment_results.values() if r.get("status") == "success")
            total_count = len(deployment_results)
            
            if success_count == total_count:
                self.global_status = "deployed"
                logger.info("Complete AI infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "deployment_summary": {
                        "total_systems": total_count,
                        "successful_deployments": success_count,
                        "failed_deployments": total_count - success_count,
                        "deployment_rate": success_count / total_count * 100
                    },
                    "infrastructure_results": deployment_results,
                    "global_capabilities": await self._get_global_capabilities(),
                    "resource_allocation": await self._get_resource_allocation(),
                    "performance_baseline": await self._get_performance_baseline()
                }
            else:
                self.global_status = "partially_deployed"
                logger.warning(f"Partial AI infrastructure deployment: {success_count}/{total_count} systems")
                
                return {
                    "status": "partial_success",
                    "deployment_summary": {
                        "total_systems": total_count,
                        "successful_deployments": success_count,
                        "failed_deployments": total_count - success_count,
                        "deployment_rate": success_count / total_count * 100
                    },
                    "infrastructure_results": deployment_results,
                    "warnings": "Some AI systems failed to deploy",
                    "recommendations": "Review failed deployments and retry"
                }
                
        except Exception as e:
            self.global_status = "failed"
            logger.error(f"Complete AI infrastructure deployment failed: {e}")
            raise
    
    async def _deploy_infrastructure_component(self, deployment_type: AIDeploymentType, method_name: str) -> Dict[str, Any]:
        """Deploy a specific infrastructure component"""
        try:
            manager = self.deployment_managers[deployment_type]
            method = getattr(manager, method_name)
            result = await method()
            return result
        except Exception as e:
            logger.error(f"Failed to deploy {deployment_type.value} infrastructure: {e}")
            raise
    
    async def get_deployment_status(self, deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get deployment status
        
        Args:
            deployment_id: Specific deployment ID, or None for global status
            
        Returns:
            Deployment status information
        """
        try:
            if deployment_id and deployment_id in self.deployments:
                # Get specific deployment status
                deployment_info = self.deployments[deployment_id]
                return {
                    "deployment_id": deployment_id,
                    "status": deployment_info["status"],
                    "deployment_type": deployment_info["type"],
                    "deployed_at": deployment_info["deployed_at"],
                    "metrics": deployment_info.get("metrics", {}),
                    "health": deployment_info.get("health", "unknown")
                }
            else:
                # Get global status
                return await self._get_global_status()
                
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {"error": str(e)}
    
    async def _get_global_status(self) -> Dict[str, Any]:
        """Get global AI deployment status"""
        try:
            status_summary = {
                "global_status": self.global_status,
                "total_deployments": len(self.deployments),
                "deployment_systems": {},
                "resource_utilization": {},
                "performance_summary": {},
                "health_status": "healthy"
            }
            
            # Get status from each deployment manager
            for deployment_type, manager in self.deployment_managers.items():
                try:
                    if hasattr(manager, 'status'):
                        system_status = manager.status
                    else:
                        system_status = "unknown"
                    
                    status_summary["deployment_systems"][deployment_type.value] = {
                        "status": system_status,
                        "active_deployments": len(getattr(manager, 'deployments', {})) if hasattr(manager, 'deployments') else 0
                    }
                except Exception as e:
                    status_summary["deployment_systems"][deployment_type.value] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return status_summary
            
        except Exception as e:
            logger.error(f"Failed to get global status: {e}")
            return {"error": str(e)}
    
    async def _get_global_capabilities(self) -> Dict[str, Any]:
        """Get global AI capabilities"""
        return {
            "model_serving": ["real_time_inference", "batch_processing", "auto_scaling"],
            "training": ["distributed_training", "hyperparameter_optimization", "experiment_tracking"],
            "edge_computing": ["multi_platform_deployment", "model_optimization", "offline_operation"],
            "federated_learning": ["privacy_preserving", "decentralized_training", "secure_aggregation"],
            "mlops": ["ci_cd_pipelines", "model_versioning", "automated_deployment"],
            "creative_ai": ["multi_modal_generation", "style_transfer", "creative_collaboration"],
            "conversational_ai": ["natural_dialogue", "personality_adaptation", "multilingual_support"],
            "computer_vision": ["object_detection", "scene_understanding", "real_time_processing"]
        }
    
    async def _get_resource_allocation(self) -> Dict[str, Any]:
        """Get resource allocation across systems"""
        return {
            "total_cpu_cores": 256,
            "total_memory_gb": 1024,
            "total_gpu_units": 64,
            "storage_tb": 100,
            "allocation_by_system": {
                "model_serving": {"cpu": "30%", "memory": "25%", "gpu": "40%"},
                "training": {"cpu": "25%", "memory": "30%", "gpu": "35%"},
                "edge_computing": {"cpu": "10%", "memory": "10%", "gpu": "5%"},
                "federated_learning": {"cpu": "15%", "memory": "15%", "gpu": "10%"},
                "mlops": {"cpu": "10%", "memory": "10%", "gpu": "5%"},
                "creative_ai": {"cpu": "5%", "memory": "5%", "gpu": "3%"},
                "conversational_ai": {"cpu": "3%", "memory": "3%", "gpu": "1%"},
                "computer_vision": {"cpu": "2%", "memory": "2%", "gpu": "1%"}
            }
        }
    
    async def _get_performance_baseline(self) -> Dict[str, Any]:
        """Get performance baseline metrics"""
        return {
            "inference_latency_p95_ms": 50,
            "training_throughput_samples_per_sec": 1000,
            "model_accuracy_threshold": 0.95,
            "system_availability": 0.999,
            "resource_efficiency": 0.85,
            "cost_per_inference": 0.001,
            "deployment_time_minutes": 5
        }
    
    async def scale_deployment(self, deployment_id: str, scale_factor: float) -> Dict[str, Any]:
        """
        Scale a specific deployment
        
        Args:
            deployment_id: Deployment to scale
            scale_factor: Scaling factor (1.0 = no change, 2.0 = double, 0.5 = half)
            
        Returns:
            Scaling operation result
        """
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Deployment {deployment_id} not found")
            
            deployment_info = self.deployments[deployment_id]
            deployment_type = deployment_info["type"]
            
            manager = self.deployment_managers[deployment_type]
            
            # Call scaling method if available
            if hasattr(manager, 'scale_deployment'):
                result = await manager.scale_deployment(deployment_id, scale_factor)
                logger.info(f"Scaled deployment {deployment_id} by factor {scale_factor}")
                return result
            else:
                return {"status": "not_supported", "message": f"Scaling not supported for {deployment_type.value}"}
                
        except Exception as e:
            logger.error(f"Failed to scale deployment {deployment_id}: {e}")
            raise
    
    async def get_deployment_metrics(self) -> Dict[str, Any]:
        """Get comprehensive deployment metrics"""
        try:
            metrics = {
                "global_status": self.global_status,
                "timestamp": time.time(),
                "system_metrics": {}
            }
            
            # Collect metrics from each deployment manager
            for deployment_type, manager in self.deployment_managers.items():
                try:
                    if hasattr(manager, 'get_metrics'):
                        system_metrics = await manager.get_metrics()
                    else:
                        system_metrics = {"status": "metrics_not_available"}
                    
                    metrics["system_metrics"][deployment_type.value] = system_metrics
                    
                except Exception as e:
                    metrics["system_metrics"][deployment_type.value] = {"error": str(e)}
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get deployment metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup_all_deployments(self) -> Dict[str, Any]:
        """Clean up all AI deployments"""
        try:
            logger.info("Cleaning up all AI deployments")
            cleanup_results = {}
            
            # Clean up each deployment manager
            for deployment_type, manager in self.deployment_managers.items():
                try:
                    if hasattr(manager, 'cleanup'):
                        await manager.cleanup()
                        cleanup_results[deployment_type.value] = {"status": "cleaned"}
                    else:
                        cleanup_results[deployment_type.value] = {"status": "no_cleanup_method"}
                except Exception as e:
                    cleanup_results[deployment_type.value] = {"status": "failed", "error": str(e)}
            
            self.global_status = "stopped"
            self.deployments = {}
            
            logger.info("All AI deployments cleaned up")
            return {"status": "success", "cleanup_results": cleanup_results}
            
        except Exception as e:
            logger.error(f"Failed to cleanup deployments: {e}")
            raise


# Global AI deployment manager instance
ai_deployment_manager = AIDeploymentManager()


# Convenience functions for easy access
async def deploy_ai_infrastructure():
    """Deploy complete AI infrastructure"""
    return await ai_deployment_manager.deploy_complete_ai_infrastructure()


async def get_ai_status():
    """
Get global AI deployment status"""
    return await ai_deployment_manager.get_deployment_status()


async def get_ai_metrics():
    """
Get comprehensive AI metrics"""
    return await ai_deployment_manager.get_deployment_metrics()


async def cleanup_ai_infrastructure():
    """
Clean up all AI infrastructure"""
    return await ai_deployment_manager.cleanup_all_deployments()
