"""🚀 MLOps Model Deployment - Enterprise Orchestrator
============================================================
Module: mlops/model_deployment/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, modification, distribution ou
reproduction est strictement interdite et peut entraîner des poursuites
judiciaires. Tous droits réservés.

🎯 ENTERPRISE MODEL DEPLOYMENT ORCHESTRATOR
Main entry point for all ML model deployment operations in the Creator Economy platform
- Centralized deployment coordination
- Multi-strategy deployment management
- Creator-specific deployment optimization
- Zero-downtime deployment guarantees
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from enum import Enum
from pathlib import Path
import json

from .deployment_orchestration_engine import DeploymentOrchestrationEngine
from .container_orchestration_manager import ContainerOrchestrationManager
from .model_versioning_controller import ModelVersioningController
from .blue_green_deployment_manager import BlueGreenDeploymentManager
from .serverless_deployment_engine import ServerlessDeploymentEngine
from .canary_deployment_engine import CanaryDeploymentEngine
from .auto_scaling_manager import AutoScalingManager
from .model_endpoint_security import ModelEndpointSecurity
from .deployment_validation_engine import DeploymentValidationEngine

logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    """Supported deployment strategies for Creator Economy"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    SERVERLESS = "serverless"
    MULTI_CLOUD = "multi_cloud"

class CreatorTier(Enum):
    """Creator subscription tiers for deployment optimization"""
    FREE = "free"
    CREATOR = "creator"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ModelDeploymentOrchestrator:
    """🎛️ Enterprise Model Deployment Orchestrator
    
    Central orchestrator for all ML model deployments in the iacherie Creator Economy platform.
    Provides intelligent deployment strategy selection, creator-specific optimization,
    and enterprise-grade reliability with zero-downtime guarantees.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the deployment orchestrator"""
        self.config = config or {}
        self.deployment_engines: Dict[str, Any] = {}
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        # Initialize enterprise components
        self._initialize_deployment_engines()
        
        # Creator-specific configurations
        self.creator_configs: Dict[str, Dict[str, Any]] = {}
        self.tier_configurations = self._setup_tier_configurations()
        
        logger.info("ModelDeploymentOrchestrator initialized successfully")
    
    def _initialize_deployment_engines(self) -> None:
        """Initialize all deployment engines"""
        try:
            self.deployment_engines = {
                'orchestration': DeploymentOrchestrationEngine(self.config.get('orchestration', {})),
                'container': ContainerOrchestrationManager(self.config.get('container', {})),
                'versioning': ModelVersioningController(self.config.get('versioning', {})),
                'blue_green': BlueGreenDeploymentManager(self.config.get('blue_green', {})),
                'serverless': ServerlessDeploymentEngine(self.config.get('serverless', {})),
                'canary': CanaryDeploymentEngine(self.config.get('canary', {})),
                'auto_scaling': AutoScalingManager(self.config.get('auto_scaling', {})),
                'security': ModelEndpointSecurity(self.config.get('security', {})),
                'validation': DeploymentValidationEngine(self.config.get('validation', {}))
            }
            logger.info("All deployment engines initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize deployment engines: {str(e)}")
            raise
    
    def _setup_tier_configurations(self) -> Dict[CreatorTier, Dict[str, Any]]:
        """Setup deployment configurations per creator tier"""
        return {
            CreatorTier.FREE: {
                'max_replicas': 2,
                'cpu_limit': '500m',
                'memory_limit': '1Gi',
                'auto_scaling': False,
                'priority_class': 'low',
                'sla_target': 0.95
            },
            CreatorTier.CREATOR: {
                'max_replicas': 5,
                'cpu_limit': '1',
                'memory_limit': '2Gi',
                'auto_scaling': True,
                'priority_class': 'normal',
                'sla_target': 0.99
            },
            CreatorTier.PROFESSIONAL: {
                'max_replicas': 10,
                'cpu_limit': '2',
                'memory_limit': '4Gi',
                'auto_scaling': True,
                'priority_class': 'high',
                'sla_target': 0.995
            },
            CreatorTier.ENTERPRISE: {
                'max_replicas': 50,
                'cpu_limit': '4',
                'memory_limit': '8Gi',
                'auto_scaling': True,
                'priority_class': 'critical',
                'sla_target': 0.999
            }
        }
    
    async def deploy_model(
        self,
        model_id: str,
        creator_id: str,
        strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN,
        environment: str = "production",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """🚀 Deploy ML model with specified strategy
        
        Args:
            model_id: Unique identifier for the model
            creator_id: Creator who owns the model
            strategy: Deployment strategy to use
            environment: Target environment
            options: Additional deployment options
            
        Returns:
            Deployment result with status and metadata
        """
        deployment_id = f"{model_id}_{creator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Starting deployment {deployment_id} with strategy {strategy.value}")
            
            # Get creator configuration
            creator_config = await self._get_creator_configuration(creator_id)
            
            # Prepare deployment context
            deployment_context = {
                'deployment_id': deployment_id,
                'model_id': model_id,
                'creator_id': creator_id,
                'strategy': strategy,
                'environment': environment,
                'creator_config': creator_config,
                'options': options or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Execute pre-deployment validations
            validation_result = await self._validate_deployment(deployment_context)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'deployment_id': deployment_id,
                    'error': f"Pre-deployment validation failed: {validation_result['errors']}"
                }
            
            # Execute deployment based on strategy
            deployment_result = await self._execute_deployment_strategy(deployment_context)
            
            # Track deployment
            self.active_deployments[deployment_id] = deployment_context
            self.deployment_history.append({
                **deployment_context,
                'result': deployment_result,
                'completed_at': datetime.now().isoformat()
            })
            
            logger.info(f"Deployment {deployment_id} completed successfully")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {str(e)}")
            return {
                'success': False,
                'deployment_id': deployment_id,
                'error': str(e)
            }
    
    async def _get_creator_configuration(self, creator_id: str) -> Dict[str, Any]:
        """Get deployment configuration for specific creator"""
        if creator_id in self.creator_configs:
            return self.creator_configs[creator_id]
        
        # Default configuration based on tier (this would typically come from database)
        # For now, defaulting to CREATOR tier
        tier = CreatorTier.CREATOR
        base_config = self.tier_configurations[tier].copy()
        
        creator_config = {
            'creator_id': creator_id,
            'tier': tier.value,
            **base_config
        }
        
        self.creator_configs[creator_id] = creator_config
        return creator_config
    
    async def _validate_deployment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment before execution"""
        try:
            validation_engine = self.deployment_engines['validation']
            return await validation_engine.validate_pre_deployment(context)
        except Exception as e:
            logger.error(f"Pre-deployment validation error: {str(e)}")
            return {'valid': False, 'errors': [str(e)]}
    
    async def _execute_deployment_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment using the specified strategy"""
        strategy = context['strategy']
        
        if strategy == DeploymentStrategy.BLUE_GREEN:
            return await self._deploy_blue_green(context)
        elif strategy == DeploymentStrategy.CANARY:
            return await self._deploy_canary(context)
        elif strategy == DeploymentStrategy.SERVERLESS:
            return await self._deploy_serverless(context)
        elif strategy == DeploymentStrategy.ROLLING:
            return await self._deploy_rolling(context)
        elif strategy == DeploymentStrategy.MULTI_CLOUD:
            return await self._deploy_multi_cloud(context)
        else:
            raise ValueError(f"Unsupported deployment strategy: {strategy}")
    
    async def _deploy_blue_green(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blue-green deployment"""
        blue_green_manager = self.deployment_engines['blue_green']
        return await blue_green_manager.deploy(context)
    
    async def _deploy_canary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute canary deployment"""
        canary_engine = self.deployment_engines['canary']
        return await canary_engine.deploy(context)
    
    async def _deploy_serverless(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute serverless deployment"""
        serverless_engine = self.deployment_engines['serverless']
        return await serverless_engine.deploy(context)
    
    async def _deploy_rolling(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rolling deployment"""
        orchestration_engine = self.deployment_engines['orchestration']
        return await orchestration_engine.deploy_rolling(context)
    
    async def _deploy_multi_cloud(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-cloud deployment"""
        # This would integrate with the multi-cloud orchestrator when implemented
        orchestration_engine = self.deployment_engines['orchestration']
        return await orchestration_engine.deploy_multi_cloud(context)
    
    async def rollback_deployment(
        self,
        deployment_id: str,
        target_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """🔄 Rollback deployment to previous version
        
        Args:
            deployment_id: ID of deployment to rollback
            target_version: Specific version to rollback to (optional)
            
        Returns:
            Rollback result with status and metadata
        """
        try:
            if deployment_id not in self.active_deployments:
                return {
                    'success': False,
                    'error': f"Deployment {deployment_id} not found"
                }
            
            deployment_context = self.active_deployments[deployment_id]
            strategy = deployment_context['strategy']
            
            # Use appropriate engine for rollback
            if strategy == DeploymentStrategy.BLUE_GREEN:
                engine = self.deployment_engines['blue_green']
            elif strategy == DeploymentStrategy.CANARY:
                engine = self.deployment_engines['canary']
            else:
                engine = self.deployment_engines['orchestration']
            
            rollback_result = await engine.rollback(deployment_id, target_version)
            
            # Update deployment status
            if rollback_result['success']:
                deployment_context['status'] = 'rolled_back'
                deployment_context['rollback_timestamp'] = datetime.now().isoformat()
            
            return rollback_result
            
        except Exception as e:
            logger.error(f"Rollback failed for deployment {deployment_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """📊 Get deployment status and metrics"""
        if deployment_id not in self.active_deployments:
            return {
                'found': False,
                'error': f"Deployment {deployment_id} not found"
            }
        
        deployment_context = self.active_deployments[deployment_id]
        
        # Get real-time metrics from validation engine
        validation_engine = self.deployment_engines['validation']
        metrics = await validation_engine.get_deployment_metrics(deployment_id)
        
        return {
            'found': True,
            'deployment_id': deployment_id,
            'context': deployment_context,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    async def list_active_deployments(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """📋 List all active deployments, optionally filtered by creator"""
        deployments = list(self.active_deployments.values())
        
        if creator_id:
            deployments = [d for d in deployments if d.get('creator_id') == creator_id]
        
        return deployments
    
    async def cleanup_completed_deployments(self, max_age_days: int = 30) -> Dict[str, Any]:
        """🧹 Cleanup old completed deployments"""
        cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        cleaned_count = 0
        for deployment_id, context in list(self.active_deployments.items()):
            if context.get('status') in ['completed', 'failed', 'rolled_back']:
                deployment_time = datetime.fromisoformat(context['timestamp']).timestamp()
                if deployment_time < cutoff_date:
                    del self.active_deployments[deployment_id]
                    cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old deployments")
        return {
            'cleaned_count': cleaned_count,
            'active_deployments': len(self.active_deployments)
        }

# Global orchestrator instance
_deployment_orchestrator: Optional[ModelDeploymentOrchestrator] = None

def get_deployment_orchestrator(config: Optional[Dict[str, Any]] = None) -> ModelDeploymentOrchestrator:
    """Get or create the global deployment orchestrator instance"""
    global _deployment_orchestrator
    
    if _deployment_orchestrator is None:
        _deployment_orchestrator = ModelDeploymentOrchestrator(config)
    
    return _deployment_orchestrator

# Convenience functions for direct access
async def deploy_model(
    model_id: str,
    creator_id: str,
    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN,
    environment: str = "production",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """🚀 Convenience function for model deployment"""
    orchestrator = get_deployment_orchestrator()
    return await orchestrator.deploy_model(model_id, creator_id, strategy, environment, options)

async def rollback_deployment(
    deployment_id: str,
    target_version: Optional[str] = None
) -> Dict[str, Any]:
    """🔄 Convenience function for deployment rollback"""
    orchestrator = get_deployment_orchestrator()
    return await orchestrator.rollback_deployment(deployment_id, target_version)

async def get_deployment_status(deployment_id: str) -> Dict[str, Any]:
    """📊 Convenience function for deployment status"""
    orchestrator = get_deployment_orchestrator()
    return await orchestrator.get_deployment_status(deployment_id)

def get_supported_strategies() -> List[str]:
    """📋 Get list of supported deployment strategies"""
    return [strategy.value for strategy in DeploymentStrategy]

def get_creator_tiers() -> List[str]:
    """👥 Get list of available creator tiers"""
    return [tier.value for tier in CreatorTier]

# Export all main components and functions
__all__ = [
    'ModelDeploymentOrchestrator',
    'DeploymentStrategy',
    'CreatorTier',
    'get_deployment_orchestrator',
    'deploy_model',
    'rollback_deployment', 
    'get_deployment_status',
    'get_supported_strategies',
    'get_creator_tiers'
]

# Usage Example
async def main():
    """Example usage of the deployment orchestrator"""
    orchestrator = get_deployment_orchestrator()
    
    # Deploy a model for a creator
    result = await deploy_model(
        model_id="creator_content_analyzer_v2",
        creator_id="creator_123",
        strategy=DeploymentStrategy.BLUE_GREEN,
        environment="production"
    )
    
    print(f"Deployment result: {result}")
    
    if result['success']:
        # Check status
        status = await get_deployment_status(result['deployment_id'])
        print(f"Deployment status: {status}")

if __name__ == "__main__":
    asyncio.run(main())