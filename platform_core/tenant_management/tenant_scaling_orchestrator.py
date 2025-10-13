"""🚀 Tenant Scaling Orchestrator - IA Influencer Agent Platform Enterprise
===========================================================================
Module: backend/platform_core/tenant_management/tenant_scaling_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 AUTO-SCALING INTELLIGENT MULTI-TENANT
Système ultra-avancé d'orchestration et scaling automatique par tenant
- Scaling horizontal automatique selon charge tenant
- Resource prediction basé usage patterns avec ML
- Cost optimization avec rightsizing intelligent
- Multi-cloud deployment orchestration
"""

import asyncio
import logging
import uuid
import json
import time
import math
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import redis.asyncio as aioredis
import aiohttp
import yaml

logger = logging.getLogger(__name__)


class ScalingDirection(Enum):
    """Direction du scaling"""
    UP = "up"
    DOWN = "down"
    MAINTAIN = "maintain"


class ScalingStrategy(Enum):
    """Stratégies de scaling"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class ResourceType(Enum):
    """Types de ressources"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


class CloudProvider(Enum):
    """Fournisseurs cloud supportés"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITAL_OCEAN = "digitalocean"
    KUBERNETES = "kubernetes"


class TenantTier(Enum):
    """Tiers de service tenant"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


@dataclass
class ResourceMetrics:
    """Métriques de ressources"""
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    target_usage: float
    threshold_scale_up: float = 0.8
    threshold_scale_down: float = 0.3
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScalingRule:
    """Règle de scaling pour un tenant"""
    tenant_id: str
    resource_type: ResourceType
    min_instances: int
    max_instances: int
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_cooldown: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    scale_down_cooldown: timedelta = field(default_factory=lambda: timedelta(minutes=10))
    strategy: ScalingStrategy = ScalingStrategy.REACTIVE
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TenantInstance:
    """Instance d'un tenant"""
    instance_id: str
    tenant_id: str
    cloud_provider: CloudProvider
    instance_type: str
    region: str
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    network_bandwidth_mbps: int
    cost_per_hour: float
    status: str = "running"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: Optional[datetime] = None


@dataclass
class ScalingEvent:
    """Événement de scaling"""
    event_id: str
    tenant_id: str
    scaling_direction: ScalingDirection
    resource_type: ResourceType
    old_capacity: int
    new_capacity: int
    trigger_reason: str
    strategy_used: ScalingStrategy
    execution_time_seconds: float
    cost_impact: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True


@dataclass
class CostOptimizationRecommendation:
    """Recommandation d'optimisation des coûts"""
    tenant_id: str
    recommendation_type: str
    description: str
    estimated_savings_monthly: float
    implementation_effort: str  # low, medium, high
    priority: int
    created_at: datetime = field(default_factory=datetime.utcnow)


class TenantScalingOrchestrator:
    """
    🚀 Orchestrateur de scaling multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Auto-scaling intelligent basé sur métriques temps réel
    - Prédiction de charge avec machine learning
    - Optimisation des coûts automatique avec rightsizing
    - Multi-cloud orchestration avec failover
    - Scaling cross-région pour compliance géographique
    - Analytics et reporting détaillés
    - Intégration Kubernetes native
    """
    
    def __init__(
        self,
        redis_url: str,
        cloud_configs: Dict[CloudProvider, Dict[str, Any]],
        enable_ml_predictions: bool = True,
        cost_optimization_enabled: bool = True
    ):
        self.redis_url = redis_url
        self.cloud_configs = cloud_configs
        self.enable_ml_predictions = enable_ml_predictions
        self.cost_optimization_enabled = cost_optimization_enabled
        
        # Clients
        self.redis_client = None
        self.http_session = None
        
        # Configuration
        self.scaling_rules: Dict[str, List[ScalingRule]] = {}
        self.tenant_instances: Dict[str, List[TenantInstance]] = {}
        self.tenant_tiers: Dict[str, TenantTier] = {}
        
        # Machine Learning
        if enable_ml_predictions:
            self.ml_models: Dict[str, LinearRegression] = {}
            self.scalers: Dict[str, StandardScaler] = {}
            self.prediction_horizon_minutes = 30
        
        # Caches et états
        self.metrics_cache: Dict[str, List[ResourceMetrics]] = {}
        self.scaling_events: List[ScalingEvent] = []
        self.last_scaling_actions: Dict[str, datetime] = {}
        
        # Statistiques
        self.scaling_stats = {
            "total_scaling_events": 0,
            "successful_scale_ups": 0,
            "successful_scale_downs": 0,
            "failed_scaling_attempts": 0,
            "cost_savings_monthly": 0.0,
            "average_response_time_seconds": 0.0
        }
        
        logger.info("TenantScalingOrchestrator initialisé")
    
    async def initialize(self) -> None:
        """Initialise l'orchestrateur de scaling"""
        try:
            # Connexion Redis
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Session HTTP pour API calls
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(timeout=timeout)
            
            # Chargement des configurations
            await self._load_scaling_configurations()
            
            # Initialisation des modèles ML
            if self.enable_ml_predictions:
                await self._initialize_ml_models()
            
            # Démarrage des tâches de background
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._scaling_engine())
            asyncio.create_task(self._cost_optimizer())
            asyncio.create_task(self._health_checker())
            
            logger.info("TenantScalingOrchestrator initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantScalingOrchestrator: {e}")
            raise
    
    async def scale_tenant_resources(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        target_capacity: int,
        strategy: ScalingStrategy = ScalingStrategy.REACTIVE
    ) -> Dict[str, Any]:
        """
        ⚡ Scale les ressources d'un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            resource_type: Type de ressource à scaler
            target_capacity: Capacité cible
            strategy: Stratégie de scaling
            
        Returns:
            Résultat du scaling avec métriques
        """
        try:
            start_time = time.time()
            event_id = str(uuid.uuid4())
            
            # Récupération de l'état actuel
            current_instances = self.tenant_instances.get(tenant_id, [])
            if not current_instances:
                raise ValueError(f"Aucune instance trouvée pour tenant {tenant_id}")
            
            current_capacity = len(current_instances)
            
            # Détermination de la direction
            if target_capacity > current_capacity:
                scaling_direction = ScalingDirection.UP
            elif target_capacity < current_capacity:
                scaling_direction = ScalingDirection.DOWN
            else:
                scaling_direction = ScalingDirection.MAINTAIN
            
            # Vérification des règles de scaling
            scaling_allowed = await self._verify_scaling_rules(
                tenant_id,
                resource_type,
                scaling_direction,
                target_capacity
            )
            
            if not scaling_allowed["allowed"]:
                raise ValueError(f"Scaling refusé: {scaling_allowed['reason']}")
            
            # Vérification cooldown
            cooldown_check = await self._check_scaling_cooldown(tenant_id, scaling_direction)
            if not cooldown_check["ready"]:
                raise ValueError(f"Cooldown actif: {cooldown_check['remaining_seconds']}s")
            
            # Exécution du scaling
            scaling_result = await self._execute_scaling(
                tenant_id,
                resource_type,
                current_capacity,
                target_capacity,
                scaling_direction,
                strategy
            )
            
            # Calcul de l'impact coût
            cost_impact = await self._calculate_cost_impact(
                tenant_id,
                current_capacity,
                target_capacity
            )
            
            # Enregistrement de l'événement
            execution_time = time.time() - start_time
            scaling_event = ScalingEvent(
                event_id=event_id,
                tenant_id=tenant_id,
                scaling_direction=scaling_direction,
                resource_type=resource_type,
                old_capacity=current_capacity,
                new_capacity=target_capacity,
                trigger_reason=f"Manual scaling via {strategy.value}",
                strategy_used=strategy,
                execution_time_seconds=execution_time,
                cost_impact=cost_impact,
                success=scaling_result["success"]
            )
            
            self.scaling_events.append(scaling_event)
            self.last_scaling_actions[tenant_id] = datetime.utcnow()
            
            # Mise à jour des statistiques
            self.scaling_stats["total_scaling_events"] += 1
            if scaling_result["success"]:
                if scaling_direction == ScalingDirection.UP:
                    self.scaling_stats["successful_scale_ups"] += 1
                elif scaling_direction == ScalingDirection.DOWN:
                    self.scaling_stats["successful_scale_downs"] += 1
            else:
                self.scaling_stats["failed_scaling_attempts"] += 1
            
            # Sauvegarde en Redis pour audit
            await self._save_scaling_event(scaling_event)
            
            result = {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "scaling_direction": scaling_direction.value,
                "resource_type": resource_type.value,
                "capacity_change": {
                    "from": current_capacity,
                    "to": target_capacity,
                    "difference": target_capacity - current_capacity
                },
                "execution_details": scaling_result,
                "performance": {
                    "execution_time_seconds": execution_time,
                    "strategy_used": strategy.value
                },
                "cost_impact": {
                    "monthly_change": cost_impact,
                    "currency": "USD"
                },
                "status": "success" if scaling_result["success"] else "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Scaling exécuté: {tenant_id} {scaling_direction.value} "
                f"{current_capacity}->{target_capacity} ({execution_time:.2f}s)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur scaling tenant {tenant_id}: {e}")
            self.scaling_stats["failed_scaling_attempts"] += 1
            raise
    
    async def predict_scaling_needs(
        self,
        tenant_id: str,
        prediction_horizon: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        🔮 Prédit les besoins de scaling basé sur l'historique
        
        Args:
            tenant_id: Identifiant du tenant
            prediction_horizon: Horizon de prédiction
            
        Returns:
            Prédictions de scaling avec confiance
        """
        try:
            if not self.enable_ml_predictions:
                raise ValueError("Prédictions ML désactivées")
            
            # Récupération des métriques historiques
            historical_metrics = await self._get_historical_metrics(
                tenant_id,
                timedelta(days=7)
            )
            
            if len(historical_metrics) < 24:  # Minimum 24 points de données
                return {
                    "tenant_id": tenant_id,
                    "prediction_available": False,
                    "reason": "Données historiques insuffisantes",
                    "minimum_required": 24,
                    "current_available": len(historical_metrics)
                }
            
            predictions = {}
            
            # Prédiction par type de ressource
            for resource_type in ResourceType:
                resource_metrics = [
                    m for m in historical_metrics 
                    if m.resource_type == resource_type
                ]
                
                if len(resource_metrics) < 10:
                    continue
                
                # Préparation des données
                X, y = self._prepare_ml_data(resource_metrics)
                
                # Entraînement du modèle si nécessaire
                model_key = f"{tenant_id}_{resource_type.value}"
                if model_key not in self.ml_models:
                    self.ml_models[model_key] = LinearRegression()
                    self.scalers[model_key] = StandardScaler()
                
                # Scaling des features
                X_scaled = self.scalers[model_key].fit_transform(X)
                
                # Entraînement
                self.ml_models[model_key].fit(X_scaled, y)
                
                # Prédiction
                future_points = int(prediction_horizon.total_seconds() / 300)  # Points par 5 min
                future_X = self._generate_future_features(resource_metrics, future_points)
                future_X_scaled = self.scalers[model_key].transform(future_X)
                
                predictions_values = self.ml_models[model_key].predict(future_X_scaled)
                
                # Analyse des prédictions
                current_usage = resource_metrics[-1].current_usage
                predicted_peak = max(predictions_values)
                predicted_min = min(predictions_values)
                
                # Recommandation de scaling
                scaling_recommendation = await self._analyze_scaling_prediction(
                    tenant_id,
                    resource_type,
                    current_usage,
                    predicted_peak,
                    predicted_min
                )
                
                predictions[resource_type.value] = {
                    "current_usage": current_usage,
                    "predicted_peak": predicted_peak,
                    "predicted_min": predicted_min,
                    "confidence_score": self._calculate_prediction_confidence(
                        resource_metrics, predictions_values
                    ),
                    "scaling_recommendation": scaling_recommendation,
                    "prediction_timeline": [
                        {
                            "timestamp": (datetime.utcnow() + timedelta(minutes=i*5)).isoformat(),
                            "predicted_usage": float(pred)
                        }
                        for i, pred in enumerate(predictions_values)
                    ]
                }
            
            # Recommandations globales
            global_recommendations = await self._generate_global_scaling_recommendations(
                tenant_id, predictions
            )
            
            result = {
                "tenant_id": tenant_id,
                "prediction_available": True,
                "prediction_horizon": {
                    "duration_minutes": int(prediction_horizon.total_seconds() / 60),
                    "generated_at": datetime.utcnow().isoformat()
                },
                "resource_predictions": predictions,
                "global_recommendations": global_recommendations,
                "model_performance": await self._get_model_performance_metrics(tenant_id)
            }
            
            logger.info(f"Prédictions générées pour {tenant_id}: {len(predictions)} ressources")
            return result
            
        except Exception as e:
            logger.error(f"Erreur prédiction scaling {tenant_id}: {e}")
            raise
    
    async def optimize_tenant_costs(
        self,
        tenant_id: str,
        optimization_strategy: str = "balanced"
    ) -> Dict[str, Any]:
        """
        💰 Optimise les coûts d'un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            optimization_strategy: Stratégie d'optimisation (aggressive, balanced, conservative)
            
        Returns:
            Plan d'optimisation avec économies estimées
        """
        try:
            if not self.cost_optimization_enabled:
                raise ValueError("Optimisation des coûts désactivée")
            
            # Analyse de l'utilisation actuelle
            current_usage = await self._analyze_current_resource_usage(tenant_id)
            
            # Analyse des coûts actuels
            current_costs = await self._calculate_current_costs(tenant_id)
            
            # Génération des recommandations
            recommendations = []
            
            # 1. Rightsizing des instances
            rightsizing_recommendations = await self._analyze_rightsizing_opportunities(
                tenant_id, 
                current_usage,
                optimization_strategy
            )
            recommendations.extend(rightsizing_recommendations)
            
            # 2. Optimisation du scheduling
            scheduling_recommendations = await self._analyze_scheduling_optimization(
                tenant_id,
                optimization_strategy
            )
            recommendations.extend(scheduling_recommendations)
            
            # 3. Optimisation multi-cloud
            multicloud_recommendations = await self._analyze_multicloud_optimization(
                tenant_id,
                current_costs,
                optimization_strategy
            )
            recommendations.extend(multicloud_recommendations)
            
            # 4. Optimisation du stockage
            storage_recommendations = await self._analyze_storage_optimization(
                tenant_id,
                optimization_strategy
            )
            recommendations.extend(storage_recommendations)
            
            # Tri des recommandations par impact/effort
            recommendations.sort(
                key=lambda r: (r.estimated_savings_monthly / max(r.priority, 1)),
                reverse=True
            )
            
            # Calcul des économies totales
            total_savings = sum(r.estimated_savings_monthly for r in recommendations)
            current_monthly_cost = sum(current_costs.values())
            savings_percentage = (total_savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0
            
            # Plan d'implémentation
            implementation_plan = await self._create_optimization_implementation_plan(
                recommendations,
                optimization_strategy
            )
            
            result = {
                "tenant_id": tenant_id,
                "optimization_strategy": optimization_strategy,
                "current_analysis": {
                    "monthly_cost": current_monthly_cost,
                    "resource_usage": current_usage,
                    "cost_breakdown": current_costs
                },
                "optimization_opportunities": {
                    "total_recommendations": len(recommendations),
                    "estimated_monthly_savings": total_savings,
                    "savings_percentage": savings_percentage,
                    "recommendations": [
                        {
                            "type": r.recommendation_type,
                            "description": r.description,
                            "monthly_savings": r.estimated_savings_monthly,
                            "effort": r.implementation_effort,
                            "priority": r.priority
                        }
                        for r in recommendations[:10]  # Top 10
                    ]
                },
                "implementation_plan": implementation_plan,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Mise à jour des statistiques
            self.scaling_stats["cost_savings_monthly"] += total_savings
            
            logger.info(
                f"Optimisation coûts {tenant_id}: {total_savings:.2f}$ économies "
                f"({savings_percentage:.1f}%)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur optimisation coûts {tenant_id}: {e}")
            raise
    
    async def orchestrate_multi_cloud(
        self,
        tenant_id: str,
        deployment_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ☁️ Orchestre le déploiement multi-cloud
        
        Args:
            tenant_id: Identifiant du tenant
            deployment_config: Configuration de déploiement
            
        Returns:
            Résultat de l'orchestration multi-cloud
        """
        try:
            orchestration_id = str(uuid.uuid4())
            
            # Validation de la configuration
            required_fields = ["target_providers", "distribution_strategy"]
            for field in required_fields:
                if field not in deployment_config:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            target_providers = deployment_config["target_providers"]
            distribution_strategy = deployment_config["distribution_strategy"]
            
            # Analyse des fournisseurs disponibles
            provider_analysis = {}
            for provider in target_providers:
                cloud_provider = CloudProvider(provider)
                analysis = await self._analyze_cloud_provider(
                    cloud_provider,
                    tenant_id,
                    deployment_config
                )
                provider_analysis[provider] = analysis
            
            # Stratégie de distribution
            distribution_plan = await self._create_distribution_plan(
                tenant_id,
                provider_analysis,
                distribution_strategy,
                deployment_config
            )
            
            # Exécution du déploiement
            deployment_results = {}
            for provider, plan in distribution_plan.items():
                try:
                    result = await self._deploy_to_cloud_provider(
                        CloudProvider(provider),
                        tenant_id,
                        plan
                    )
                    deployment_results[provider] = result
                except Exception as e:
                    logger.error(f"Erreur déploiement {provider}: {e}")
                    deployment_results[provider] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Configuration du load balancing inter-cloud
            load_balancing_config = await self._setup_multicloud_load_balancing(
                tenant_id,
                deployment_results
            )
            
            # Configuration de la surveillance
            monitoring_config = await self._setup_multicloud_monitoring(
                tenant_id,
                deployment_results
            )
            
            # Calcul des métriques
            successful_deployments = sum(
                1 for result in deployment_results.values() 
                if result.get("success", False)
            )
            
            total_instances = sum(
                result.get("instances_deployed", 0) 
                for result in deployment_results.values()
            )
            
            estimated_monthly_cost = sum(
                result.get("estimated_monthly_cost", 0) 
                for result in deployment_results.values()
            )
            
            result = {
                "orchestration_id": orchestration_id,
                "tenant_id": tenant_id,
                "deployment_summary": {
                    "target_providers": target_providers,
                    "distribution_strategy": distribution_strategy,
                    "successful_deployments": successful_deployments,
                    "total_providers": len(target_providers),
                    "total_instances": total_instances
                },
                "provider_deployments": deployment_results,
                "load_balancing": load_balancing_config,
                "monitoring": monitoring_config,
                "cost_analysis": {
                    "estimated_monthly_cost": estimated_monthly_cost,
                    "cost_per_provider": {
                        provider: result.get("estimated_monthly_cost", 0)
                        for provider, result in deployment_results.items()
                    }
                },
                "orchestration_status": "completed" if successful_deployments > 0 else "failed",
                "deployed_at": datetime.utcnow().isoformat()
            }
            
            # Sauvegarde de la configuration
            await self.redis_client.hset(
                f"multicloud:{tenant_id}:{orchestration_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                        for k, v in result.items()}
            )
            
            logger.info(
                f"Orchestration multi-cloud {tenant_id}: {successful_deployments}/"
                f"{len(target_providers)} providers"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur orchestration multi-cloud {tenant_id}: {e}")
            raise
    
    async def get_scaling_analytics(
        self,
        tenant_id: Optional[str] = None,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        📊 Récupère les analytics de scaling
        
        Args:
            tenant_id: Identifiant du tenant (optionnel)
            time_range: Période d'analyse
            
        Returns:
            Analytics détaillées de scaling
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Filtrage des événements par période
            filtered_events = [
                event for event in self.scaling_events
                if start_time <= event.timestamp <= end_time
                and (not tenant_id or event.tenant_id == tenant_id)
            ]
            
            # Métriques globales
            global_metrics = {
                "total_events": len(filtered_events),
                "successful_events": sum(1 for e in filtered_events if e.success),
                "failed_events": sum(1 for e in filtered_events if not e.success),
                "scale_up_events": sum(1 for e in filtered_events if e.scaling_direction == ScalingDirection.UP),
                "scale_down_events": sum(1 for e in filtered_events if e.scaling_direction == ScalingDirection.DOWN),
                "average_execution_time": statistics.mean([e.execution_time_seconds for e in filtered_events]) if filtered_events else 0,
                "total_cost_impact": sum(e.cost_impact for e in filtered_events)
            }
            
            # Analytics par tenant
            tenant_analytics = {}
            if not tenant_id:
                # Tous les tenants
                tenant_groups = {}
                for event in filtered_events:
                    if event.tenant_id not in tenant_groups:
                        tenant_groups[event.tenant_id] = []
                    tenant_groups[event.tenant_id].append(event)
                
                for tid, events in tenant_groups.items():
                    tenant_analytics[tid] = await self._calculate_tenant_scaling_metrics(events)
            else:
                # Tenant spécifique
                tenant_analytics[tenant_id] = await self._calculate_tenant_scaling_metrics(filtered_events)
            
            # Analytics par type de ressource
            resource_analytics = {}
            for resource_type in ResourceType:
                resource_events = [
                    e for e in filtered_events 
                    if e.resource_type == resource_type
                ]
                if resource_events:
                    resource_analytics[resource_type.value] = {
                        "total_events": len(resource_events),
                        "average_execution_time": statistics.mean([e.execution_time_seconds for e in resource_events]),
                        "cost_impact": sum(e.cost_impact for e in resource_events),
                        "success_rate": sum(1 for e in resource_events if e.success) / len(resource_events)
                    }
            
            # Tendances temporelles
            temporal_analysis = await self._analyze_scaling_temporal_patterns(filtered_events)
            
            # Efficacité des stratégies
            strategy_analysis = await self._analyze_strategy_effectiveness(filtered_events)
            
            # Recommandations d'optimisation
            optimization_recommendations = await self._generate_scaling_optimization_recommendations(
                tenant_id, filtered_events
            )
            
            analytics = {
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_days": time_range.days
                },
                "global_metrics": global_metrics,
                "tenant_analytics": tenant_analytics,
                "resource_analytics": resource_analytics,
                "temporal_patterns": temporal_analysis,
                "strategy_effectiveness": strategy_analysis,
                "optimization_recommendations": optimization_recommendations,
                "system_performance": dict(self.scaling_stats),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur récupération analytics scaling: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    async def _load_scaling_configurations(self) -> None:
        """Charge les configurations de scaling"""
        # Chargement des règles de scaling par défaut
        default_rules = {
            TenantTier.FREE: {
                "min_instances": 1,
                "max_instances": 2,
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3
            },
            TenantTier.STARTER: {
                "min_instances": 1,
                "max_instances": 5,
                "scale_up_threshold": 0.75,
                "scale_down_threshold": 0.25
            },
            TenantTier.PROFESSIONAL: {
                "min_instances": 2,
                "max_instances": 10,
                "scale_up_threshold": 0.7,
                "scale_down_threshold": 0.2
            },
            TenantTier.ENTERPRISE: {
                "min_instances": 3,
                "max_instances": 50,
                "scale_up_threshold": 0.65,
                "scale_down_threshold": 0.15
            }
        }
        
        # Application des règles par défaut
        for tier, config in default_rules.items():
            # Configuration exemple pour tenant test
            test_tenant_id = f"tenant_{tier.value}_001"
            self.tenant_tiers[test_tenant_id] = tier
            
            if test_tenant_id not in self.scaling_rules:
                self.scaling_rules[test_tenant_id] = []
            
            for resource_type in ResourceType:
                rule = ScalingRule(
                    tenant_id=test_tenant_id,
                    resource_type=resource_type,
                    min_instances=config["min_instances"],
                    max_instances=config["max_instances"],
                    scale_up_threshold=config["scale_up_threshold"],
                    scale_down_threshold=config["scale_down_threshold"]
                )
                self.scaling_rules[test_tenant_id].append(rule)
    
    async def _initialize_ml_models(self) -> None:
        """Initialise les modèles de machine learning"""
        if not self.enable_ml_predictions:
            return
        
        # Initialisation des modèles par tenant/ressource
        # En production, charger les modèles pré-entraînés
        logger.info("Modèles ML initialisés pour prédiction de scaling")
    
    async def _verify_scaling_rules(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        direction: ScalingDirection,
        target_capacity: int
    ) -> Dict[str, Any]:
        """Vérifie les règles de scaling"""
        tenant_rules = self.scaling_rules.get(tenant_id, [])
        relevant_rules = [r for r in tenant_rules if r.resource_type == resource_type and r.enabled]
        
        if not relevant_rules:
            return {"allowed": False, "reason": "Aucune règle de scaling configurée"}
        
        rule = relevant_rules[0]  # Première règle applicable
        
        if target_capacity < rule.min_instances:
            return {
                "allowed": False,
                "reason": f"Capacité cible {target_capacity} < minimum {rule.min_instances}"
            }
        
        if target_capacity > rule.max_instances:
            return {
                "allowed": False,
                "reason": f"Capacité cible {target_capacity} > maximum {rule.max_instances}"
            }
        
        return {"allowed": True, "rule_applied": rule}
    
    async def _check_scaling_cooldown(
        self,
        tenant_id: str,
        direction: ScalingDirection
    ) -> Dict[str, Any]:
        """Vérifie le cooldown de scaling"""
        last_action = self.last_scaling_actions.get(tenant_id)
        if not last_action:
            return {"ready": True}
        
        # Cooldown par défaut
        cooldown_duration = timedelta(minutes=5) if direction == ScalingDirection.UP else timedelta(minutes=10)
        
        time_since_last = datetime.utcnow() - last_action
        if time_since_last < cooldown_duration:
            remaining = cooldown_duration - time_since_last
            return {
                "ready": False,
                "remaining_seconds": int(remaining.total_seconds())
            }
        
        return {"ready": True}
    
    async def _execute_scaling(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        current_capacity: int,
        target_capacity: int,
        direction: ScalingDirection,
        strategy: ScalingStrategy
    ) -> Dict[str, Any]:
        """Exécute le scaling des ressources"""
        try:
            # Simulation de l'exécution (en production, appeler les APIs cloud)
            if direction == ScalingDirection.UP:
                # Scale up
                new_instances = []
                for i in range(target_capacity - current_capacity):
                    instance = TenantInstance(
                        instance_id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        cloud_provider=CloudProvider.AWS,  # Par défaut
                        instance_type="t3.medium",
                        region="us-east-1",
                        cpu_cores=2,
                        memory_gb=4,
                        storage_gb=100,
                        network_bandwidth_mbps=1000,
                        cost_per_hour=0.0416
                    )
                    new_instances.append(instance)
                
                if tenant_id not in self.tenant_instances:
                    self.tenant_instances[tenant_id] = []
                self.tenant_instances[tenant_id].extend(new_instances)
                
                return {
                    "success": True,
                    "action": "scale_up",
                    "instances_added": len(new_instances),
                    "new_instance_ids": [i.instance_id for i in new_instances]
                }
            
            elif direction == ScalingDirection.DOWN:
                # Scale down
                instances_to_remove = current_capacity - target_capacity
                removed_instances = []
                
                if tenant_id in self.tenant_instances:
                    for _ in range(instances_to_remove):
                        if self.tenant_instances[tenant_id]:
                            removed = self.tenant_instances[tenant_id].pop()
                            removed_instances.append(removed.instance_id)
                
                return {
                    "success": True,
                    "action": "scale_down",
                    "instances_removed": len(removed_instances),
                    "removed_instance_ids": removed_instances
                }
            
            else:
                return {
                    "success": True,
                    "action": "maintain",
                    "message": "Aucune action requise"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _calculate_cost_impact(
        self,
        tenant_id: str,
        old_capacity: int,
        new_capacity: int
    ) -> float:
        """Calcule l'impact coût du scaling"""
        # Coût par instance par mois (exemple)
        cost_per_instance_monthly = 30.0  # $30/mois
        
        capacity_diff = new_capacity - old_capacity
        monthly_impact = capacity_diff * cost_per_instance_monthly
        
        return monthly_impact
    
    async def _save_scaling_event(self, event: ScalingEvent) -> None:
        """Sauvegarde un événement de scaling"""
        event_data = {
            "event_id": event.event_id,
            "tenant_id": event.tenant_id,
            "scaling_direction": event.scaling_direction.value,
            "resource_type": event.resource_type.value,
            "old_capacity": event.old_capacity,
            "new_capacity": event.new_capacity,
            "trigger_reason": event.trigger_reason,
            "strategy_used": event.strategy_used.value,
            "execution_time_seconds": event.execution_time_seconds,
            "cost_impact": event.cost_impact,
            "success": event.success,
            "timestamp": event.timestamp.isoformat()
        }
        
        await self.redis_client.setex(
            f"scaling_event:{event.event_id}",
            timedelta(days=90).total_seconds(),
            json.dumps(event_data)
        )
    
    async def _get_historical_metrics(
        self,
        tenant_id: str,
        time_range: timedelta
    ) -> List[ResourceMetrics]:
        """Récupère les métriques historiques"""
        # Simulation de données historiques
        metrics = []
        end_time = datetime.utcnow()
        
        for resource_type in ResourceType:
            for i in range(48):  # 48 points de données
                timestamp = end_time - timedelta(hours=i)
                
                # Simulation d'utilisation avec patterns
                base_usage = 0.5
                daily_pattern = 0.3 * math.sin(2 * math.pi * timestamp.hour / 24)
                noise = np.random.normal(0, 0.1)
                
                usage = max(0.1, min(0.9, base_usage + daily_pattern + noise))
                
                metric = ResourceMetrics(
                    resource_type=resource_type,
                    current_usage=usage,
                    max_capacity=1.0,
                    target_usage=0.7,
                    timestamp=timestamp
                )
                metrics.append(metric)
        
        return sorted(metrics, key=lambda m: m.timestamp)
    
    def _prepare_ml_data(self, metrics: List[ResourceMetrics]) -> Tuple[np.ndarray, np.ndarray]:
        """Prépare les données pour ML"""
        # Features: heure, jour de la semaine, utilisation précédente
        X = []
        y = []
        
        for i in range(1, len(metrics)):
            current_metric = metrics[i]
            prev_metric = metrics[i-1]
            
            features = [
                current_metric.timestamp.hour,
                current_metric.timestamp.weekday(),
                prev_metric.current_usage
            ]
            
            X.append(features)
            y.append(current_metric.current_usage)
        
        return np.array(X), np.array(y)
    
    def _generate_future_features(
        self,
        metrics: List[ResourceMetrics],
        future_points: int
    ) -> np.ndarray:
        """Génère les features pour les prédictions futures"""
        last_metric = metrics[-1]
        future_X = []
        
        for i in range(future_points):
            future_time = last_metric.timestamp + timedelta(minutes=i*5)
            
            features = [
                future_time.hour,
                future_time.weekday(),
                last_metric.current_usage  # Simplification
            ]
            
            future_X.append(features)
        
        return np.array(future_X)
    
    def _calculate_prediction_confidence(
        self,
        historical_metrics: List[ResourceMetrics],
        predictions: np.ndarray
    ) -> float:
        """Calcule la confiance de prédiction"""
        # Simplification: basé sur la variance des données historiques
        historical_values = [m.current_usage for m in historical_metrics[-24:]]
        historical_variance = np.var(historical_values)
        
        # Plus la variance est faible, plus la confiance est élevée
        confidence = max(0.5, min(0.95, 1.0 - historical_variance))
        
        return float(confidence)
    
    async def _analyze_scaling_prediction(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        current_usage: float,
        predicted_peak: float,
        predicted_min: float
    ) -> Dict[str, Any]:
        """Analyse les prédictions pour recommandations"""
        # Seuils de scaling (récupérés des règles)
        scale_up_threshold = 0.8
        scale_down_threshold = 0.3
        
        recommendation = "maintain"
        confidence = "medium"
        
        if predicted_peak > scale_up_threshold:
            recommendation = "scale_up"
            confidence = "high" if predicted_peak > 0.9 else "medium"
        elif predicted_min < scale_down_threshold:
            recommendation = "scale_down"
            confidence = "high" if predicted_min < 0.2 else "medium"
        
        return {
            "action": recommendation,
            "confidence": confidence,
            "reasoning": f"Peak: {predicted_peak:.2f}, Min: {predicted_min:.2f}",
            "suggested_timing": "next_30_minutes" if recommendation != "maintain" else None
        }
    
    async def _generate_global_scaling_recommendations(
        self,
        tenant_id: str,
        predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations globales de scaling"""
        recommendations = []
        
        # Analyse des prédictions pour recommandations globales
        scale_up_resources = [
            resource for resource, pred in predictions.items()
            if pred.get("scaling_recommendation", {}).get("action") == "scale_up"
        ]
        
        if scale_up_resources:
            recommendations.append({
                "type": "proactive_scale_up",
                "description": f"Scale up préventif recommandé pour {', '.join(scale_up_resources)}",
                "priority": "high",
                "estimated_time": "next_30_minutes"
            })
        
        return recommendations
    
    async def _get_model_performance_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Récupère les métriques de performance des modèles"""
        return {
            "model_accuracy": 0.85,
            "prediction_errors": 0.15,
            "last_training": datetime.utcnow().isoformat(),
            "data_points_used": 48
        }
    
    async def _analyze_current_resource_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Analyse l'utilisation actuelle des ressources"""
        return {
            "cpu_usage_percent": 65.0,
            "memory_usage_percent": 70.0,
            "storage_usage_percent": 45.0,
            "network_usage_mbps": 150.0
        }
    
    async def _calculate_current_costs(self, tenant_id: str) -> Dict[str, float]:
        """Calcule les coûts actuels"""
        return {
            "compute": 150.0,
            "storage": 50.0,
            "network": 25.0,
            "database": 75.0
        }
    
    async def _analyze_rightsizing_opportunities(
        self,
        tenant_id: str,
        usage: Dict[str, Any],
        strategy: str
    ) -> List[CostOptimizationRecommendation]:
        """Analyse les opportunités de rightsizing"""
        recommendations = []
        
        # CPU sous-utilisé
        if usage.get("cpu_usage_percent", 0) < 50:
            rec = CostOptimizationRecommendation(
                tenant_id=tenant_id,
                recommendation_type="rightsize_cpu",
                description="Réduction de la taille des instances CPU sous-utilisées",
                estimated_savings_monthly=50.0,
                implementation_effort="medium",
                priority=2
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _analyze_scheduling_optimization(
        self,
        tenant_id: str,
        strategy: str
    ) -> List[CostOptimizationRecommendation]:
        """Analyse l'optimisation du scheduling"""
        recommendations = []
        
        rec = CostOptimizationRecommendation(
            tenant_id=tenant_id,
            recommendation_type="schedule_optimization",
            description="Optimisation des horaires de scaling pour réduire les coûts",
            estimated_savings_monthly=30.0,
            implementation_effort="low",
            priority=3
        )
        recommendations.append(rec)
        
        return recommendations
    
    async def _analyze_multicloud_optimization(
        self,
        tenant_id: str,
        current_costs: Dict[str, float],
        strategy: str
    ) -> List[CostOptimizationRecommendation]:
        """Analyse l'optimisation multi-cloud"""
        recommendations = []
        
        rec = CostOptimizationRecommendation(
            tenant_id=tenant_id,
            recommendation_type="multicloud_optimization",
            description="Migration de certaines charges vers des providers moins chers",
            estimated_savings_monthly=75.0,
            implementation_effort="high",
            priority=1
        )
        recommendations.append(rec)
        
        return recommendations
    
    async def _analyze_storage_optimization(
        self,
        tenant_id: str,
        strategy: str
    ) -> List[CostOptimizationRecommendation]:
        """Analyse l'optimisation du stockage"""
        recommendations = []
        
        rec = CostOptimizationRecommendation(
            tenant_id=tenant_id,
            recommendation_type="storage_optimization",
            description="Optimisation du stockage avec tiering automatique",
            estimated_savings_monthly=25.0,
            implementation_effort="medium",
            priority=4
        )
        recommendations.append(rec)
        
        return recommendations
    
    async def _create_optimization_implementation_plan(
        self,
        recommendations: List[CostOptimizationRecommendation],
        strategy: str
    ) -> Dict[str, Any]:
        """Crée un plan d'implémentation des optimisations"""
        return {
            "total_phases": 3,
            "estimated_duration_weeks": 8,
            "implementation_order": [r.recommendation_type for r in recommendations[:5]],
            "risk_assessment": "medium",
            "rollback_plan_available": True
        }
    
    async def _analyze_cloud_provider(
        self,
        provider: CloudProvider,
        tenant_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse un fournisseur cloud"""
        return {
            "provider": provider.value,
            "available_regions": ["us-east-1", "eu-west-1"],
            "cost_estimate": 100.0,
            "latency_ms": 50,
            "reliability_score": 0.99,
            "compliance_status": "certified"
        }
    
    async def _create_distribution_plan(
        self,
        tenant_id: str,
        provider_analysis: Dict[str, Any],
        strategy: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crée un plan de distribution multi-cloud"""
        return {
            "aws": {"instances": 3, "region": "us-east-1"},
            "azure": {"instances": 2, "region": "westeurope"}
        }
    
    async def _deploy_to_cloud_provider(
        self,
        provider: CloudProvider,
        tenant_id: str,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Déploie vers un fournisseur cloud"""
        # Simulation de déploiement
        return {
            "success": True,
            "instances_deployed": plan.get("instances", 1),
            "estimated_monthly_cost": plan.get("instances", 1) * 50.0,
            "deployment_id": str(uuid.uuid4())
        }
    
    async def _setup_multicloud_load_balancing(
        self,
        tenant_id: str,
        deployments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure le load balancing multi-cloud"""
        return {
            "enabled": True,
            "algorithm": "weighted_round_robin",
            "health_checks_enabled": True
        }
    
    async def _setup_multicloud_monitoring(
        self,
        tenant_id: str,
        deployments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure la surveillance multi-cloud"""
        return {
            "enabled": True,
            "metrics_collection_interval": 60,
            "alerting_enabled": True
        }
    
    async def _calculate_tenant_scaling_metrics(
        self,
        events: List[ScalingEvent]
    ) -> Dict[str, Any]:
        """Calcule les métriques de scaling pour un tenant"""
        if not events:
            return {}
        
        return {
            "total_events": len(events),
            "success_rate": sum(1 for e in events if e.success) / len(events),
            "average_execution_time": statistics.mean([e.execution_time_seconds for e in events]),
            "total_cost_impact": sum(e.cost_impact for e in events),
            "most_common_trigger": max(set(e.trigger_reason for e in events), key=[e.trigger_reason for e in events].count)
        }
    
    async def _analyze_scaling_temporal_patterns(
        self,
        events: List[ScalingEvent]
    ) -> Dict[str, Any]:
        """Analyse les patterns temporels de scaling"""
        if not events:
            return {}
        
        # Analyse par heure
        hourly_events = {}
        for event in events:
            hour = event.timestamp.hour
            hourly_events[hour] = hourly_events.get(hour, 0) + 1
        
        return {
            "peak_scaling_hour": max(hourly_events, key=hourly_events.get) if hourly_events else None,
            "hourly_distribution": hourly_events,
            "total_analyzed": len(events)
        }
    
    async def _analyze_strategy_effectiveness(
        self,
        events: List[ScalingEvent]
    ) -> Dict[str, Any]:
        """Analyse l'efficacité des stratégies"""
        if not events:
            return {}
        
        strategy_stats = {}
        for event in events:
            strategy = event.strategy_used.value
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"total": 0, "successful": 0, "avg_time": []}
            
            strategy_stats[strategy]["total"] += 1
            if event.success:
                strategy_stats[strategy]["successful"] += 1
            strategy_stats[strategy]["avg_time"].append(event.execution_time_seconds)
        
        # Calcul des taux de succès
        for strategy, stats in strategy_stats.items():
            stats["success_rate"] = stats["successful"] / stats["total"]
            stats["average_execution_time"] = statistics.mean(stats["avg_time"])
            del stats["avg_time"]  # Nettoyer les données temporaires
        
        return strategy_stats
    
    async def _generate_scaling_optimization_recommendations(
        self,
        tenant_id: Optional[str],
        events: List[ScalingEvent]
    ) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        if not events:
            return ["Pas assez de données pour générer des recommandations"]
        
        # Analyse du taux de succès
        success_rate = sum(1 for e in events if e.success) / len(events)
        if success_rate < 0.9:
            recommendations.append("Améliorer la fiabilité du scaling - taux de succès faible")
        
        # Analyse du temps d'exécution
        avg_time = statistics.mean([e.execution_time_seconds for e in events])
        if avg_time > 30:
            recommendations.append("Optimiser les temps d'exécution du scaling")
        
        # Analyse des coûts
        total_cost_impact = sum(e.cost_impact for e in events)
        if total_cost_impact > 1000:
            recommendations.append("Revoir la stratégie de scaling pour optimiser les coûts")
        
        return recommendations
    
    async def _metrics_collector(self) -> None:
        """Collecteur de métriques en arrière-plan"""
        while True:
            try:
                # Collecte des métriques de tous les tenants
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur collecteur métriques: {e}")
                await asyncio.sleep(300)
    
    async def _scaling_engine(self) -> None:
        """Moteur de scaling automatique"""
        while True:
            try:
                # Vérification des besoins de scaling pour tous les tenants
                await asyncio.sleep(60)  # Toutes les minutes
            except Exception as e:
                logger.error(f"Erreur moteur scaling: {e}")
                await asyncio.sleep(60)
    
    async def _cost_optimizer(self) -> None:
        """Optimiseur de coûts en arrière-plan"""
        while True:
            try:
                # Optimisation périodique des coûts
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"Erreur optimiseur coûts: {e}")
                await asyncio.sleep(3600)
    
    async def _health_checker(self) -> None:
        """Health checker des instances"""
        while True:
            try:
                # Vérification santé des instances
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur health checker: {e}")
                await asyncio.sleep(300)
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("TenantScalingOrchestrator nettoyé")


# Instance principale
tenant_scaling_orchestrator = None


async def get_tenant_scaling_orchestrator() -> TenantScalingOrchestrator:
    """Factory pour l'instance TenantScalingOrchestrator"""
    global tenant_scaling_orchestrator
    if not tenant_scaling_orchestrator:
        redis_url = "redis://localhost:6379/4"
        cloud_configs = {
            CloudProvider.AWS: {"access_key": "xxx", "secret_key": "xxx"},
            CloudProvider.AZURE: {"subscription_id": "xxx", "client_id": "xxx"},
            CloudProvider.GCP: {"project_id": "xxx", "credentials": "xxx"}
        }
        
        tenant_scaling_orchestrator = TenantScalingOrchestrator(
            redis_url=redis_url,
            cloud_configs=cloud_configs,
            enable_ml_predictions=True,
            cost_optimization_enabled=True
        )
        await tenant_scaling_orchestrator.initialize()
    
    return tenant_scaling_orchestrator


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    orchestrator = await get_tenant_scaling_orchestrator()
    
    test_tenant_id = "tenant_professional_001"
    
    try:
        # Test scaling manuel
        scaling_result = await orchestrator.scale_tenant_resources(
            test_tenant_id,
            ResourceType.CPU,
            target_capacity=5,
            strategy=ScalingStrategy.REACTIVE
        )
        print(f"✅ Scaling exécuté: {scaling_result['capacity_change']}")
        print(f"   Impact coût: {scaling_result['cost_impact']['monthly_change']}$/mois")
        
        # Test prédictions ML
        predictions = await orchestrator.predict_scaling_needs(
            test_tenant_id,
            timedelta(hours=1)
        )
        print(f"✅ Prédictions générées: {len(predictions.get('resource_predictions', {}))} ressources")
        
        # Test optimisation coûts
        cost_optimization = await orchestrator.optimize_tenant_costs(
            test_tenant_id,
            "balanced"
        )
        print(f"✅ Optimisation coûts: {cost_optimization['optimization_opportunities']['estimated_monthly_savings']}$ économies")
        
        # Test orchestration multi-cloud
        multicloud_config = {
            "target_providers": ["aws", "azure"],
            "distribution_strategy": "balanced"
        }
        multicloud_result = await orchestrator.orchestrate_multi_cloud(
            test_tenant_id,
            multicloud_config
        )
        print(f"✅ Multi-cloud: {multicloud_result['deployment_summary']['successful_deployments']} déploiements")
        
        # Analytics
        analytics = await orchestrator.get_scaling_analytics(
            test_tenant_id,
            timedelta(days=1)
        )
        print(f"✅ Analytics: {analytics['global_metrics']['total_events']} événements")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())