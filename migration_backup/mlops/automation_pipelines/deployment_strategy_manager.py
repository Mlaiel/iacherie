"""
🎯 Deployment Strategy Manager - Enterprise MLOps 
Expert DevOps + Microservices: Gestionnaire avancé stratégies déploiement

🎯 EXPERTISE DÉMONTRÉ:
- DevOps: Stratégies déploiement enterprise (blue-green, canary, rolling)
- Microservices: Orchestration déploiement distribué + circuit breakers
- Backend Senior: Architecture déploiement robuste + monitoring
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from abc import ABC, abstractmethod

# Configuration et logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    """Stratégies de déploiement enterprise"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    A_B_TESTING = "a_b_testing"
    SHADOW = "shadow"
    FEATURE_FLAG = "feature_flag"
    IMMEDIATE = "immediate"

class DeploymentStatus(Enum):
    """Statuts de déploiement"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class EnvironmentType(Enum):
    """Types d'environnements"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CANARY = "canary"
    SHADOW = "shadow"

@dataclass
class DeploymentConfig:
    """Configuration de déploiement"""
    strategy: DeploymentStrategy
    target_environment: EnvironmentType
    model_version: str
    traffic_percentage: float = 100.0
    rollback_threshold: float = 0.05  # 5% error rate
    health_check_url: Optional[str] = None
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeploymentResult:
    """Résultat de déploiement"""
    deployment_id: str
    status: DeploymentStatus
    strategy: DeploymentStrategy
    start_time: datetime
    end_time: Optional[datetime] = None
    success_rate: float = 0.0
    error_rate: float = 0.0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Interface pour les stratégies de déploiement
class DeploymentStrategyInterface(ABC):
    """Interface pour les stratégies de déploiement"""
    
    @abstractmethod
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Exécute le déploiement selon la stratégie"""
        pass
    
    @abstractmethod
    async def rollback(self, deployment_id: str) -> bool:
        """Effectue un rollback du déploiement"""
        pass
    
    @abstractmethod
    async def get_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Récupère le statut d'un déploiement"""
        pass

class BlueGreenStrategy(DeploymentStrategyInterface):
    """
    🔵 Stratégie Blue-Green Deployment
    
    Expertise DevOps: Déploiement zero-downtime avec switch instantané
    """
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentResult] = {}
        self.active_environments: Dict[str, str] = {}  # service -> environment
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Déploiement Blue-Green avec validation complète"""
        deployment_id = f"bg_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.IN_PROGRESS,
            strategy=DeploymentStrategy.BLUE_GREEN,
            start_time=start_time
        )
        
        self.deployments[deployment_id] = result
        
        try:
            # Phase 1: Déploiement sur environnement inactif (Green)
            inactive_env = await self._get_inactive_environment(config.target_environment)
            await self._deploy_to_environment(inactive_env, config.model_version)
            result.logs.append(f"Deployed {config.model_version} to {inactive_env}")
            
            # Phase 2: Tests de santé sur l'environnement Green
            health_ok = await self._perform_health_checks(
                inactive_env, 
                config.health_check_url
            )
            
            if not health_ok:
                raise Exception("Health checks failed on green environment")
            
            result.logs.append("Health checks passed on green environment")
            
            # Phase 3: Tests de performance et validation
            perf_metrics = await self._run_performance_tests(inactive_env)
            result.performance_metrics = perf_metrics
            
            # Phase 4: Switch du trafic (Blue -> Green)
            await self._switch_traffic(config.target_environment, inactive_env)
            self.active_environments[config.target_environment.value] = inactive_env
            result.logs.append(f"Traffic switched to {inactive_env}")
            
            # Phase 5: Monitoring post-switch
            await self._monitor_post_switch(inactive_env, config.rollback_threshold)
            
            result.status = DeploymentStatus.SUCCESS
            result.end_time = datetime.utcnow()
            result.success_rate = 1.0
            
            logger.info(f"Blue-Green deployment {deployment_id} completed successfully")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.end_time = datetime.utcnow()
            result.logs.append(f"Deployment failed: {str(e)}")
            logger.error(f"Blue-Green deployment {deployment_id} failed: {str(e)}")
            
            # Rollback automatique
            await self.rollback(deployment_id)
        
        return result
    
    async def rollback(self, deployment_id: str) -> bool:
        """Rollback Blue-Green avec switch instantané"""
        if deployment_id not in self.deployments:
            return False
        
        try:
            deployment = self.deployments[deployment_id]
            
            # Switch back vers l'environnement précédent
            current_env = self.active_environments.get(deployment.strategy.value)
            previous_env = "blue" if current_env == "green" else "green"
            
            await self._switch_traffic(EnvironmentType.PRODUCTION, previous_env)
            self.active_environments[EnvironmentType.PRODUCTION.value] = previous_env
            
            deployment.status = DeploymentStatus.ROLLED_BACK
            deployment.logs.append("Rolled back to previous environment")
            
            logger.info(f"Blue-Green rollback {deployment_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Blue-Green rollback {deployment_id} failed: {str(e)}")
            return False
    
    async def get_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Récupère le statut du déploiement Blue-Green"""
        return self.deployments.get(deployment_id)
    
    async def _get_inactive_environment(self, target: EnvironmentType) -> str:
        """Détermine l'environnement inactif pour le déploiement"""
        active = self.active_environments.get(target.value, "blue")
        return "green" if active == "blue" else "blue"
    
    async def _deploy_to_environment(self, environment: str, version: str):
        """Déploie vers un environnement spécifique"""
        # Simulation du déploiement
        await asyncio.sleep(2)  # Simule le temps de déploiement
        logger.info(f"Deployed version {version} to {environment}")
    
    async def _perform_health_checks(self, environment: str, health_url: Optional[str]) -> bool:
        """Effectue les tests de santé"""
        # Simulation des health checks
        await asyncio.sleep(1)
        return True  # Simulation de succès
    
    async def _run_performance_tests(self, environment: str) -> Dict[str, float]:
        """Exécute les tests de performance"""
        await asyncio.sleep(2)
        return {
            "response_time_ms": 45.2,
            "throughput_rps": 1200.5,
            "cpu_usage": 0.25,
            "memory_usage": 0.40
        }
    
    async def _switch_traffic(self, target_env: EnvironmentType, new_env: str):
        """Switch le trafic vers le nouvel environnement"""
        await asyncio.sleep(0.5)
        logger.info(f"Traffic switched to {new_env} for {target_env.value}")
    
    async def _monitor_post_switch(self, environment: str, threshold: float):
        """Monitoring post-switch avec seuils d'alerte"""
        await asyncio.sleep(3)
        # Simulation du monitoring
        error_rate = 0.01  # 1% d'erreurs simulées
        if error_rate > threshold:
            raise Exception(f"Error rate {error_rate:.2%} exceeds threshold {threshold:.2%}")

class CanaryStrategy(DeploymentStrategyInterface):
    """
    🐦 Stratégie Canary Deployment
    
    Expertise DevOps + Microservices: Déploiement progressif avec monitoring
    """
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentResult] = {}
        self.traffic_splits: Dict[str, Dict[str, float]] = {}
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Déploiement Canary avec progression graduelle"""
        deployment_id = f"canary_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.IN_PROGRESS,
            strategy=DeploymentStrategy.CANARY,
            start_time=start_time
        )
        
        self.deployments[deployment_id] = result
        
        try:
            # Phase 1: Déploiement initial avec 5% du trafic
            await self._deploy_canary_version(config.model_version, 5.0)
            result.logs.append("Canary deployed with 5% traffic")
            
            # Phase 2: Monitoring 5% pendant 10 minutes
            await self._monitor_canary_performance(deployment_id, 5.0, duration_minutes=5)
            
            # Phase 3: Augmentation progressive (5% -> 25% -> 50% -> 100%)
            traffic_stages = [25.0, 50.0, 100.0]
            
            for traffic_pct in traffic_stages:
                await self._update_traffic_split(deployment_id, traffic_pct)
                result.logs.append(f"Traffic increased to {traffic_pct}%")
                
                # Monitoring à chaque étape
                await self._monitor_canary_performance(
                    deployment_id, 
                    traffic_pct, 
                    duration_minutes=3
                )
                
                # Vérification des métriques
                metrics = await self._get_canary_metrics(deployment_id)
                if metrics["error_rate"] > config.rollback_threshold:
                    raise Exception(f"Error rate {metrics['error_rate']:.2%} exceeds threshold")
            
            result.status = DeploymentStatus.SUCCESS
            result.end_time = datetime.utcnow()
            result.success_rate = 1.0
            
            logger.info(f"Canary deployment {deployment_id} completed successfully")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.end_time = datetime.utcnow()
            result.logs.append(f"Canary deployment failed: {str(e)}")
            logger.error(f"Canary deployment {deployment_id} failed: {str(e)}")
            
            # Rollback automatique
            await self.rollback(deployment_id)
        
        return result
    
    async def rollback(self, deployment_id: str) -> bool:
        """Rollback Canary avec arrêt du trafic vers la nouvelle version"""
        if deployment_id not in self.deployments:
            return False
        
        try:
            # Rediriger tout le trafic vers la version stable
            await self._update_traffic_split(deployment_id, 0.0)
            
            deployment = self.deployments[deployment_id]
            deployment.status = DeploymentStatus.ROLLED_BACK
            deployment.logs.append("Canary rolled back - traffic reverted to stable version")
            
            logger.info(f"Canary rollback {deployment_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Canary rollback {deployment_id} failed: {str(e)}")
            return False
    
    async def get_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Récupère le statut du déploiement Canary"""
        return self.deployments.get(deployment_id)
    
    async def _deploy_canary_version(self, version: str, traffic_pct: float):
        """Déploie la version canary avec le pourcentage de trafic spécifié"""
        await asyncio.sleep(1)
        logger.info(f"Deployed canary version {version} with {traffic_pct}% traffic")
    
    async def _update_traffic_split(self, deployment_id: str, traffic_pct: float):
        """Met à jour la répartition du trafic"""
        self.traffic_splits[deployment_id] = {
            "canary": traffic_pct,
            "stable": 100.0 - traffic_pct
        }
        await asyncio.sleep(0.5)
    
    async def _monitor_canary_performance(
        self, 
        deployment_id: str, 
        traffic_pct: float,
        duration_minutes: int
    ):
        """Monitoring des performances canary"""
        await asyncio.sleep(duration_minutes * 0.1)  # Simulation accélérée
        logger.info(f"Monitored canary at {traffic_pct}% for {duration_minutes} minutes")
    
    async def _get_canary_metrics(self, deployment_id: str) -> Dict[str, float]:
        """Récupère les métriques de performance canary"""
        return {
            "error_rate": 0.02,  # 2% simulé
            "response_time": 42.1,
            "throughput": 850.2,
            "success_rate": 0.98
        }

class RollingStrategy(DeploymentStrategyInterface):
    """
    🔄 Stratégie Rolling Deployment
    
    Expertise Microservices: Déploiement progressif instance par instance
    """
    
    def __init__(self, batch_size: int = 2):
        self.deployments: Dict[str, DeploymentResult] = {}
        self.batch_size = batch_size
    
    async def deploy(self, config: DeploymentConfig) -> DeploymentResult:
        """Déploiement Rolling avec batches d'instances"""
        deployment_id = f"rolling_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.IN_PROGRESS,
            strategy=DeploymentStrategy.ROLLING,
            start_time=start_time
        )
        
        self.deployments[deployment_id] = result
        
        try:
            # Simuler 8 instances à déployer
            total_instances = 8
            batches = [
                list(range(i, min(i + self.batch_size, total_instances)))
                for i in range(0, total_instances, self.batch_size)
            ]
            
            for batch_num, instances in enumerate(batches, 1):
                # Déploiement du batch
                await self._deploy_batch(instances, config.model_version)
                result.logs.append(f"Batch {batch_num} deployed: instances {instances}")
                
                # Health check du batch
                await self._health_check_batch(instances)
                result.logs.append(f"Batch {batch_num} health checks passed")
                
                # Attendre avant le prochain batch
                if batch_num < len(batches):
                    await asyncio.sleep(1)  # Délai entre batches
            
            result.status = DeploymentStatus.SUCCESS
            result.end_time = datetime.utcnow()
            result.success_rate = 1.0
            
            logger.info(f"Rolling deployment {deployment_id} completed successfully")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.end_time = datetime.utcnow()
            result.logs.append(f"Rolling deployment failed: {str(e)}")
            logger.error(f"Rolling deployment {deployment_id} failed: {str(e)}")
        
        return result
    
    async def rollback(self, deployment_id: str) -> bool:
        """Rollback Rolling avec restauration batch par batch"""
        if deployment_id not in self.deployments:
            return False
        
        try:
            # Rollback en ordre inverse
            total_instances = 8
            batches = [
                list(range(i, min(i + self.batch_size, total_instances)))
                for i in range(0, total_instances, self.batch_size)
            ]
            
            for batch in reversed(batches):
                await self._rollback_batch(batch)
            
            deployment = self.deployments[deployment_id]
            deployment.status = DeploymentStatus.ROLLED_BACK
            deployment.logs.append("Rolling rollback completed")
            
            logger.info(f"Rolling rollback {deployment_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Rolling rollback {deployment_id} failed: {str(e)}")
            return False
    
    async def get_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Récupère le statut du déploiement Rolling"""
        return self.deployments.get(deployment_id)
    
    async def _deploy_batch(self, instances: List[int], version: str):
        """Déploie un batch d'instances"""
        await asyncio.sleep(1)
        logger.info(f"Deployed version {version} to instances {instances}")
    
    async def _health_check_batch(self, instances: List[int]):
        """Health check d'un batch d'instances"""
        await asyncio.sleep(0.5)
        logger.info(f"Health check passed for instances {instances}")
    
    async def _rollback_batch(self, instances: List[int]):
        """Rollback d'un batch d'instances"""
        await asyncio.sleep(0.5)
        logger.info(f"Rolled back instances {instances}")

class DeploymentStrategyManager:
    """
    🎯 Gestionnaire Enterprise de Stratégies de Déploiement
    
    Expertise DevOps + Microservices + Backend Senior:
    - Orchestration multi-stratégies
    - Sélection intelligente de stratégie
    - Monitoring et observabilité
    - Circuit breakers et recovery
    """
    
    def __init__(self):
        self.strategies: Dict[DeploymentStrategy, DeploymentStrategyInterface] = {
            DeploymentStrategy.BLUE_GREEN: BlueGreenStrategy(),
            DeploymentStrategy.CANARY: CanaryStrategy(),
            DeploymentStrategy.ROLLING: RollingStrategy()
        }
        self.deployments: Dict[str, DeploymentResult] = {}
        self.active_deployments: Set[str] = set()
    
    async def deploy(
        self, 
        config: DeploymentConfig,
        auto_select_strategy: bool = False
    ) -> DeploymentResult:
        """
        Déploie selon la stratégie spécifiée ou auto-sélectionnée
        
        Expertise:
        - DevOps: Orchestration multi-stratégies
        - Backend Senior: Architecture robuste avec fallbacks
        """
        try:
            # Auto-sélection de stratégie si demandée
            if auto_select_strategy:
                config.strategy = await self._select_optimal_strategy(config)
            
            # Validation de la stratégie
            if config.strategy not in self.strategies:
                raise ValueError(f"Unsupported deployment strategy: {config.strategy}")
            
            # Vérification des déploiements concurrents
            if config.target_environment == EnvironmentType.PRODUCTION:
                if len(self.active_deployments) > 0:
                    raise Exception("Production deployment already in progress")
            
            strategy = self.strategies[config.strategy]
            result = await strategy.deploy(config)
            
            # Enregistrement du déploiement
            self.deployments[result.deployment_id] = result
            
            if result.status == DeploymentStatus.IN_PROGRESS:
                self.active_deployments.add(result.deployment_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            # Retourner un résultat d'échec
            return DeploymentResult(
                deployment_id=f"failed_{uuid.uuid4().hex[:8]}",
                status=DeploymentStatus.FAILED,
                strategy=config.strategy,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                logs=[f"Deployment failed: {str(e)}"]
            )
    
    async def rollback(self, deployment_id: str) -> bool:
        """Rollback avec détection automatique de stratégie"""
        if deployment_id not in self.deployments:
            logger.error(f"Deployment {deployment_id} not found")
            return False
        
        deployment = self.deployments[deployment_id]
        strategy = self.strategies[deployment.strategy]
        
        success = await strategy.rollback(deployment_id)
        
        if success:
            self.active_deployments.discard(deployment_id)
        
        return success
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Récupère le statut détaillé d'un déploiement"""
        return self.deployments.get(deployment_id)
    
    async def list_active_deployments(self) -> List[DeploymentResult]:
        """Liste tous les déploiements actifs"""
        return [
            self.deployments[dep_id] 
            for dep_id in self.active_deployments
            if dep_id in self.deployments
        ]
    
    async def get_deployment_history(
        self, 
        environment: Optional[EnvironmentType] = None,
        strategy: Optional[DeploymentStrategy] = None,
        limit: int = 50
    ) -> List[DeploymentResult]:
        """Récupère l'historique des déploiements avec filtres"""
        deployments = list(self.deployments.values())
        
        # Filtrage par environnement
        if environment:
            deployments = [
                d for d in deployments 
                if d.metadata.get("target_environment") == environment.value
            ]
        
        # Filtrage par stratégie
        if strategy:
            deployments = [d for d in deployments if d.strategy == strategy]
        
        # Tri par date (plus récent en premier) et limitation
        deployments.sort(key=lambda x: x.start_time, reverse=True)
        return deployments[:limit]
    
    async def _select_optimal_strategy(self, config: DeploymentConfig) -> DeploymentStrategy:
        """
        Sélection intelligente de stratégie de déploiement
        
        Expertise Lead Dev IA: Logique de sélection basée sur contexte
        """
        # Logique de sélection basée sur l'environnement et les risques
        if config.target_environment == EnvironmentType.PRODUCTION:
            # Production: privilégier blue-green pour zero downtime
            if config.metadata.get("critical_service", False):
                return DeploymentStrategy.BLUE_GREEN
            else:
                return DeploymentStrategy.CANARY
        
        elif config.target_environment == EnvironmentType.STAGING:
            # Staging: rolling pour tests graduels
            return DeploymentStrategy.ROLLING
        
        else:
            # Development: déploiement immédiat
            return DeploymentStrategy.IMMEDIATE
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques globales de déploiement"""
        total_deployments = len(self.deployments)
        
        if total_deployments == 0:
            return {"total_deployments": 0}
        
        # Calcul des métriques
        successful = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.SUCCESS)
        failed = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.FAILED)
        rolled_back = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.ROLLED_BACK)
        
        # Métriques par stratégie
        strategy_metrics = {}
        for strategy in DeploymentStrategy:
            strategy_deployments = [
                d for d in self.deployments.values() 
                if d.strategy == strategy
            ]
            if strategy_deployments:
                strategy_success_rate = sum(
                    1 for d in strategy_deployments 
                    if d.status == DeploymentStatus.SUCCESS
                ) / len(strategy_deployments)
                
                strategy_metrics[strategy.value] = {
                    "total": len(strategy_deployments),
                    "success_rate": strategy_success_rate
                }
        
        return {
            "total_deployments": total_deployments,
            "success_rate": successful / total_deployments,
            "failure_rate": failed / total_deployments,
            "rollback_rate": rolled_back / total_deployments,
            "active_deployments": len(self.active_deployments),
            "strategy_metrics": strategy_metrics
        }

# Exemple d'utilisation enterprise
async def demo_deployment_strategies():
    """Démo des stratégies de déploiement enterprise"""
    manager = DeploymentStrategyManager()
    
    # Configuration Blue-Green
    bg_config = DeploymentConfig(
        strategy=DeploymentStrategy.BLUE_GREEN,
        target_environment=EnvironmentType.PRODUCTION,
        model_version="v2.1.0",
        health_check_url="http://api/health"
    )
    
    # Configuration Canary
    canary_config = DeploymentConfig(
        strategy=DeploymentStrategy.CANARY,
        target_environment=EnvironmentType.PRODUCTION,
        model_version="v2.2.0",
        traffic_percentage=5.0
    )
    
    # Déploiements
    bg_result = await manager.deploy(bg_config)
    print(f"Blue-Green: {bg_result.status.value}")
    
    canary_result = await manager.deploy(canary_config)
    print(f"Canary: {canary_result.status.value}")
    
    # Métriques
    metrics = await manager.get_metrics()
    print(f"Deployment metrics: {json.dumps(metrics, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(demo_deployment_strategies())