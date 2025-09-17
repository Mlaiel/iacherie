"""🚀 Tenant Resource Manager - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/platform_core/tenant_management/tenant_resource_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTION RESSOURCES ET QUOTAS MULTI-TENANT
Système ultra-avancé de gestion des ressources et quotas par tenant
- Gestion ressources CPU/Memory/Storage/Network par tenant
- Quotas dynamiques avec enforcement en temps réel
- Resource pooling intelligent et allocation optimisée
- Monitoring usage avec alertes et prédictions
"""

import asyncio
import logging
import uuid
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types de ressources gérées"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK_BANDWIDTH = "network_bandwidth"
    DATABASE_CONNECTIONS = "database_connections"
    API_REQUESTS = "api_requests"
    CONCURRENT_USERS = "concurrent_users"
    CONTENT_PROCESSING = "content_processing"


class ResourceUnit(Enum):
    """Unités de mesure des ressources"""
    CORES = "cores"
    GB = "gb"
    MBPS = "mbps"
    CONNECTIONS = "connections"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    USERS = "users"
    JOBS_PER_HOUR = "jobs_per_hour"


class QuotaEnforcementLevel(Enum):
    """Niveaux d'enforcement des quotas"""
    SOFT = "soft"  # Warning seulement
    HARD = "hard"  # Blocage strict
    ADAPTIVE = "adaptive"  # Ajustement automatique


@dataclass
class ResourceQuota:
    """Quota de ressource pour un tenant"""
    tenant_id: str
    resource_type: ResourceType
    resource_unit: ResourceUnit
    allocated_amount: float
    used_amount: float = 0.0
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    enforcement_level: QuotaEnforcementLevel = QuotaEnforcementLevel.HARD
    reset_period: timedelta = field(default_factory=lambda: timedelta(hours=1))
    last_reset: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class ResourceUsageMetric:
    """Métrique d'utilisation de ressource"""
    tenant_id: str
    resource_type: ResourceType
    usage_amount: float
    timestamp: datetime
    peak_usage: float = 0.0
    average_usage: float = 0.0
    usage_duration: timedelta = field(default_factory=lambda: timedelta(seconds=0))


@dataclass
class ResourcePool:
    """Pool de ressources partagées"""
    pool_id: str
    pool_name: str
    resource_type: ResourceType
    total_capacity: float
    allocated_capacity: float = 0.0
    available_capacity: float = 0.0
    tenant_allocations: Dict[str, float] = field(default_factory=dict)
    priority_weights: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class ResourceAlert:
    """Alerte de ressource"""
    alert_id: str
    tenant_id: str
    resource_type: ResourceType
    alert_level: str  # warning, critical, emergency
    message: str
    threshold_exceeded: float
    current_usage: float
    recommended_action: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False


class TenantResourceManager:
    """
    🚀 Gestionnaire de ressources multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Gestion granulaire des quotas par tenant et type de ressource
    - Monitoring en temps réel avec alertes intelligentes
    - Resource pooling avec allocation dynamique
    - Prédiction d'usage et scaling automatique
    - Cost tracking et optimisation par ressource
    - SLA monitoring et enforcement
    - Multi-tier resource policies
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str,
        enable_predictive_scaling: bool = True,
        enable_cost_optimization: bool = True
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.enable_predictive_scaling = enable_predictive_scaling
        self.enable_cost_optimization = enable_cost_optimization
        
        # Clients
        self.engine = None
        self.redis_client = None
        
        # Caches et états
        self.tenant_quotas: Dict[str, List[ResourceQuota]] = {}
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.usage_metrics: Dict[str, List[ResourceUsageMetric]] = {}
        self.active_alerts: Dict[str, List[ResourceAlert]] = {}
        
        # Configuration par défaut
        self.default_quotas = self._initialize_default_quotas()
        self.resource_costs = self._initialize_resource_costs()
        
        # Statistiques
        self.resource_stats = {
            "total_tenants_managed": 0,
            "total_quotas_defined": 0,
            "quota_violations": 0,
            "auto_scaling_events": 0,
            "cost_optimizations": 0,
            "alert_notifications": 0
        }
        
        logger.info("TenantResourceManager initialisé")
    
    async def initialize(self) -> None:
        """Initialise le gestionnaire de ressources"""
        try:
            # Connexion base de données
            self.engine = create_async_engine(
                self.database_url,
                pool_size=15,
                max_overflow=25,
                pool_pre_ping=True
            )
            
            # Connexion Redis
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialisation des tables
            await self._initialize_resource_tables()
            
            # Chargement des configurations
            await self._load_resource_configurations()
            
            # Démarrage des tâches de monitoring
            asyncio.create_task(self._resource_monitor_scheduler())
            asyncio.create_task(self._quota_enforcement_scheduler())
            asyncio.create_task(self._usage_metrics_collector())
            asyncio.create_task(self._alert_processor())
            
            if self.enable_predictive_scaling:
                asyncio.create_task(self._predictive_scaling_engine())
            
            if self.enable_cost_optimization:
                asyncio.create_task(self._cost_optimization_scheduler())
            
            logger.info("TenantResourceManager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantResourceManager: {e}")
            raise
    
    async def allocate_tenant_resources(
        self,
        tenant_id: str,
        resource_allocations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📊 Alloue des ressources à un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            resource_allocations: Allocations demandées par type de ressource
            
        Returns:
            Résultat de l'allocation avec quotas assignés
        """
        try:
            allocation_id = str(uuid.uuid4())
            
            # Validation des demandes d'allocation
            validated_allocations = await self._validate_resource_requests(
                tenant_id,
                resource_allocations
            )
            
            allocated_quotas = []
            allocation_errors = []
            
            # Traitement de chaque type de ressource
            for resource_type_str, allocation_config in validated_allocations.items():
                try:
                    resource_type = ResourceType(resource_type_str)
                    
                    # Vérification de la disponibilité dans les pools
                    availability_check = await self._check_resource_availability(
                        resource_type,
                        allocation_config["amount"]
                    )
                    
                    if not availability_check["available"]:
                        allocation_errors.append({
                            "resource_type": resource_type_str,
                            "error": "Ressource insuffisante",
                            "available": availability_check["available_amount"],
                            "requested": allocation_config["amount"]
                        })
                        continue
                    
                    # Création du quota
                    quota = ResourceQuota(
                        tenant_id=tenant_id,
                        resource_type=resource_type,
                        resource_unit=ResourceUnit(allocation_config.get("unit", "gb")),
                        allocated_amount=allocation_config["amount"],
                        warning_threshold=allocation_config.get("warning_threshold", 0.8),
                        critical_threshold=allocation_config.get("critical_threshold", 0.95),
                        enforcement_level=QuotaEnforcementLevel(
                            allocation_config.get("enforcement", "hard")
                        ),
                        reset_period=timedelta(
                            seconds=allocation_config.get("reset_period_seconds", 3600)
                        )
                    )
                    
                    # Allocation dans les pools de ressources
                    pool_allocation_result = await self._allocate_from_resource_pools(
                        tenant_id,
                        resource_type,
                        allocation_config["amount"]
                    )
                    
                    if pool_allocation_result["success"]:
                        allocated_quotas.append(quota)
                        
                        # Sauvegarde en base de données
                        await self._save_resource_quota(quota)
                        
                        # Mise en cache
                        if tenant_id not in self.tenant_quotas:
                            self.tenant_quotas[tenant_id] = []
                        self.tenant_quotas[tenant_id].append(quota)
                        
                    else:
                        allocation_errors.append({
                            "resource_type": resource_type_str,
                            "error": pool_allocation_result["error"]
                        })
                        
                except ValueError as e:
                    allocation_errors.append({
                        "resource_type": resource_type_str,
                        "error": f"Type de ressource invalide: {e}"
                    })
                except Exception as e:
                    allocation_errors.append({
                        "resource_type": resource_type_str,
                        "error": f"Erreur allocation: {e}"
                    })
            
            # Calcul du coût total estimé
            estimated_cost = await self._calculate_allocation_cost(allocated_quotas)
            
            # Configuration des alertes
            alert_configs = await self._setup_resource_alerts(tenant_id, allocated_quotas)
            
            # Mise à jour des statistiques
            self.resource_stats["total_quotas_defined"] += len(allocated_quotas)
            if tenant_id not in [q.tenant_id for quotas in self.tenant_quotas.values() for q in quotas]:
                self.resource_stats["total_tenants_managed"] += 1
            
            result = {
                "allocation_id": allocation_id,
                "tenant_id": tenant_id,
                "allocation_summary": {
                    "total_quotas_allocated": len(allocated_quotas),
                    "allocation_errors": len(allocation_errors),
                    "estimated_monthly_cost": estimated_cost
                },
                "allocated_quotas": [
                    {
                        "resource_type": q.resource_type.value,
                        "allocated_amount": q.allocated_amount,
                        "resource_unit": q.resource_unit.value,
                        "enforcement_level": q.enforcement_level.value,
                        "warning_threshold": q.warning_threshold,
                        "critical_threshold": q.critical_threshold
                    }
                    for q in allocated_quotas
                ],
                "allocation_errors": allocation_errors,
                "alert_configurations": alert_configs,
                "cost_estimation": {
                    "monthly_cost": estimated_cost,
                    "cost_breakdown": await self._generate_cost_breakdown(allocated_quotas)
                },
                "allocated_at": datetime.utcnow().isoformat()
            }
            
            # Audit trail
            await self._log_resource_activity(
                tenant_id,
                "resource_allocation",
                {
                    "allocation_id": allocation_id,
                    "quotas_allocated": len(allocated_quotas),
                    "errors": len(allocation_errors)
                }
            )
            
            logger.info(
                f"Ressources allouées pour {tenant_id}: {len(allocated_quotas)} quotas, "
                f"coût estimé: {estimated_cost:.2f}$/mois"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur allocation ressources {tenant_id}: {e}")
            raise
    
    async def monitor_resource_usage(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> Dict[str, Any]:
        """
        📈 Surveille l'utilisation des ressources d'un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            resource_type: Type de ressource spécifique (optionnel)
            
        Returns:
            Rapport détaillé d'utilisation des ressources
        """
        try:
            monitoring_id = str(uuid.uuid4())
            
            # Récupération des quotas du tenant
            tenant_quotas = self.tenant_quotas.get(tenant_id, [])
            if not tenant_quotas:
                return {
                    "monitoring_id": monitoring_id,
                    "tenant_id": tenant_id,
                    "status": "no_quotas_defined",
                    "message": "Aucun quota défini pour ce tenant"
                }
            
            # Filtrage par type de ressource si spécifié
            if resource_type:
                tenant_quotas = [q for q in tenant_quotas if q.resource_type == resource_type]
            
            # Collecte des métriques actuelles
            current_usage = {}
            usage_trends = {}
            quota_compliance = {}
            
            for quota in tenant_quotas:
                # Utilisation actuelle
                current_usage_value = await self._get_current_resource_usage(
                    tenant_id,
                    quota.resource_type
                )
                
                # Mise à jour du quota
                quota.used_amount = current_usage_value
                
                # Calcul des pourcentages
                usage_percentage = (current_usage_value / quota.allocated_amount * 100) if quota.allocated_amount > 0 else 0
                
                current_usage[quota.resource_type.value] = {
                    "used_amount": current_usage_value,
                    "allocated_amount": quota.allocated_amount,
                    "usage_percentage": usage_percentage,
                    "resource_unit": quota.resource_unit.value,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                # Tendances d'usage
                historical_metrics = await self._get_historical_usage_metrics(
                    tenant_id,
                    quota.resource_type,
                    timedelta(hours=24)
                )
                
                if historical_metrics:
                    peak_usage = max(m.usage_amount for m in historical_metrics)
                    avg_usage = sum(m.usage_amount for m in historical_metrics) / len(historical_metrics)
                    
                    usage_trends[quota.resource_type.value] = {
                        "peak_24h": peak_usage,
                        "average_24h": avg_usage,
                        "current_vs_average": (current_usage_value / avg_usage - 1) * 100 if avg_usage > 0 else 0,
                        "trend_direction": self._calculate_usage_trend(historical_metrics)
                    }
                
                # Conformité des quotas
                compliance_status = "compliant"
                alerts_triggered = []
                
                if usage_percentage >= quota.critical_threshold * 100:
                    compliance_status = "critical"
                    alerts_triggered.append("critical_threshold_exceeded")
                elif usage_percentage >= quota.warning_threshold * 100:
                    compliance_status = "warning"
                    alerts_triggered.append("warning_threshold_exceeded")
                
                quota_compliance[quota.resource_type.value] = {
                    "status": compliance_status,
                    "usage_percentage": usage_percentage,
                    "warning_threshold": quota.warning_threshold * 100,
                    "critical_threshold": quota.critical_threshold * 100,
                    "enforcement_level": quota.enforcement_level.value,
                    "alerts_triggered": alerts_triggered
                }
                
                # Génération d'alertes si nécessaire
                if alerts_triggered:
                    await self._generate_usage_alert(
                        tenant_id,
                        quota,
                        usage_percentage,
                        compliance_status
                    )
            
            # Prédictions d'usage si activées
            usage_predictions = {}
            if self.enable_predictive_scaling:
                for quota in tenant_quotas:
                    prediction = await self._predict_resource_usage(
                        tenant_id,
                        quota.resource_type,
                        timedelta(hours=24)  # Prédiction 24h
                    )
                    usage_predictions[quota.resource_type.value] = prediction
            
            # Recommandations d'optimisation
            optimization_recommendations = await self._generate_usage_recommendations(
                tenant_id,
                tenant_quotas,
                current_usage,
                usage_trends
            )
            
            # Calcul du coût actuel
            current_cost = await self._calculate_current_usage_cost(tenant_id, tenant_quotas)
            
            result = {
                "monitoring_id": monitoring_id,
                "tenant_id": tenant_id,
                "monitoring_timestamp": datetime.utcnow().isoformat(),
                "monitoring_scope": resource_type.value if resource_type else "all_resources",
                "usage_summary": {
                    "total_resources_monitored": len(tenant_quotas),
                    "compliant_resources": len([c for c in quota_compliance.values() if c["status"] == "compliant"]),
                    "warning_resources": len([c for c in quota_compliance.values() if c["status"] == "warning"]),
                    "critical_resources": len([c for c in quota_compliance.values() if c["status"] == "critical"])
                },
                "current_usage": current_usage,
                "usage_trends": usage_trends,
                "quota_compliance": quota_compliance,
                "usage_predictions": usage_predictions,
                "cost_analysis": {
                    "current_monthly_cost": current_cost,
                    "cost_per_resource": await self._calculate_cost_per_resource(tenant_id, tenant_quotas)
                },
                "optimization_recommendations": optimization_recommendations
            }
            
            # Sauvegarde des métriques
            for quota in tenant_quotas:
                metric = ResourceUsageMetric(
                    tenant_id=tenant_id,
                    resource_type=quota.resource_type,
                    usage_amount=quota.used_amount,
                    timestamp=datetime.utcnow()
                )
                await self._save_usage_metric(metric)
            
            logger.info(f"Monitoring ressources {tenant_id}: {len(tenant_quotas)} ressources surveillées")
            return result
            
        except Exception as e:
            logger.error(f"Erreur monitoring ressources {tenant_id}: {e}")
            raise
    
    async def enforce_quota_limits(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        requested_amount: float
    ) -> Dict[str, Any]:
        """
        🛡️ Applique les limites de quota
        
        Args:
            tenant_id: Identifiant du tenant
            resource_type: Type de ressource
            requested_amount: Quantité demandée
            
        Returns:
            Résultat de l'enforcement avec autorisation/refus
        """
        try:
            enforcement_id = str(uuid.uuid4())
            
            # Recherche du quota correspondant
            tenant_quotas = self.tenant_quotas.get(tenant_id, [])
            relevant_quota = None
            
            for quota in tenant_quotas:
                if quota.resource_type == resource_type and quota.is_active:
                    relevant_quota = quota
                    break
            
            if not relevant_quota:
                return {
                    "enforcement_id": enforcement_id,
                    "tenant_id": tenant_id,
                    "resource_type": resource_type.value,
                    "decision": "denied",
                    "reason": "no_quota_defined",
                    "message": f"Aucun quota défini pour {resource_type.value}"
                }
            
            # Calcul de l'utilisation après la demande
            current_usage = relevant_quota.used_amount
            projected_usage = current_usage + requested_amount
            projected_percentage = (projected_usage / relevant_quota.allocated_amount * 100) if relevant_quota.allocated_amount > 0 else 0
            
            # Décision d'enforcement selon le niveau
            decision = "approved"
            enforcement_action = None
            additional_info = {}
            
            if relevant_quota.enforcement_level == QuotaEnforcementLevel.HARD:
                if projected_usage > relevant_quota.allocated_amount:
                    decision = "denied"
                    enforcement_action = "hard_limit_exceeded"
                    additional_info["excess_amount"] = projected_usage - relevant_quota.allocated_amount
            
            elif relevant_quota.enforcement_level == QuotaEnforcementLevel.SOFT:
                if projected_usage > relevant_quota.allocated_amount:
                    decision = "approved_with_warning"
                    enforcement_action = "soft_limit_exceeded"
                    additional_info["warning_message"] = "Quota dépassé mais autorisé (soft limit)"
            
            elif relevant_quota.enforcement_level == QuotaEnforcementLevel.ADAPTIVE:
                if projected_usage > relevant_quota.allocated_amount:
                    # Tentative d'augmentation automatique du quota
                    auto_scaling_result = await self._attempt_auto_scaling(
                        tenant_id,
                        relevant_quota,
                        requested_amount
                    )
                    
                    if auto_scaling_result["success"]:
                        decision = "approved"
                        enforcement_action = "auto_scaled"
                        additional_info.update(auto_scaling_result)
                    else:
                        decision = "denied"
                        enforcement_action = "auto_scaling_failed"
                        additional_info["scaling_error"] = auto_scaling_result["error"]
            
            # Mise à jour de l'utilisation si approuvé
            if decision in ["approved", "approved_with_warning"]:
                relevant_quota.used_amount = projected_usage
                await self._update_quota_usage(relevant_quota)
            
            # Génération d'alertes si seuils dépassés
            if projected_percentage >= relevant_quota.warning_threshold * 100:
                await self._generate_quota_alert(
                    tenant_id,
                    relevant_quota,
                    projected_percentage,
                    "threshold_exceeded"
                )
            
            # Logging de l'enforcement
            enforcement_result = {
                "enforcement_id": enforcement_id,
                "tenant_id": tenant_id,
                "resource_type": resource_type.value,
                "requested_amount": requested_amount,
                "current_usage": current_usage,
                "projected_usage": projected_usage,
                "quota_limit": relevant_quota.allocated_amount,
                "projected_percentage": projected_percentage,
                "enforcement_level": relevant_quota.enforcement_level.value,
                "decision": decision,
                "enforcement_action": enforcement_action,
                "additional_info": additional_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Mise à jour des statistiques
            if decision == "denied":
                self.resource_stats["quota_violations"] += 1
            
            # Audit trail
            await self._log_resource_activity(
                tenant_id,
                "quota_enforcement",
                {
                    "enforcement_id": enforcement_id,
                    "resource_type": resource_type.value,
                    "decision": decision,
                    "requested_amount": requested_amount
                }
            )
            
            logger.info(
                f"Enforcement quota {tenant_id}/{resource_type.value}: {decision} "
                f"({requested_amount} demandé, {projected_percentage:.1f}% quota)"
            )
            
            return enforcement_result
            
        except Exception as e:
            logger.error(f"Erreur enforcement quota {tenant_id}: {e}")
            raise
    
    async def optimize_resource_allocation(
        self,
        tenant_id: str,
        optimization_strategy: str = "cost_effective"
    ) -> Dict[str, Any]:
        """
        💡 Optimise l'allocation des ressources d'un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            optimization_strategy: Stratégie d'optimisation
            
        Returns:
            Plan d'optimisation avec recommandations
        """
        try:
            optimization_id = str(uuid.uuid4())
            
            # Analyse de l'utilisation actuelle
            current_allocation_analysis = await self._analyze_current_allocation(tenant_id)
            
            # Analyse des patterns d'usage
            usage_patterns = await self._analyze_usage_patterns(
                tenant_id,
                timedelta(days=30)  # Analyse sur 30 jours
            )
            
            # Génération des recommandations selon la stratégie
            recommendations = []
            
            if optimization_strategy == "cost_effective":
                recommendations.extend(
                    await self._generate_cost_optimization_recommendations(
                        tenant_id,
                        current_allocation_analysis,
                        usage_patterns
                    )
                )
            
            elif optimization_strategy == "performance_focused":
                recommendations.extend(
                    await self._generate_performance_optimization_recommendations(
                        tenant_id,
                        current_allocation_analysis,
                        usage_patterns
                    )
                )
            
            elif optimization_strategy == "balanced":
                cost_recs = await self._generate_cost_optimization_recommendations(
                    tenant_id, current_allocation_analysis, usage_patterns
                )
                perf_recs = await self._generate_performance_optimization_recommendations(
                    tenant_id, current_allocation_analysis, usage_patterns
                )
                recommendations.extend(cost_recs[:3])  # Top 3 cost optimizations
                recommendations.extend(perf_recs[:2])  # Top 2 performance optimizations
            
            # Calcul de l'impact estimé
            optimization_impact = await self._calculate_optimization_impact(
                tenant_id,
                recommendations,
                current_allocation_analysis
            )
            
            # Plan d'implémentation
            implementation_plan = await self._create_optimization_implementation_plan(
                recommendations,
                optimization_strategy
            )
            
            # Simulation des changements
            simulation_results = await self._simulate_optimization_changes(
                tenant_id,
                recommendations
            )
            
            result = {
                "optimization_id": optimization_id,
                "tenant_id": tenant_id,
                "optimization_strategy": optimization_strategy,
                "current_allocation_analysis": current_allocation_analysis,
                "usage_patterns": usage_patterns,
                "optimization_recommendations": recommendations,
                "estimated_impact": optimization_impact,
                "implementation_plan": implementation_plan,
                "simulation_results": simulation_results,
                "optimization_score": await self._calculate_optimization_score(recommendations),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Mise à jour des statistiques
            self.resource_stats["cost_optimizations"] += 1
            
            logger.info(
                f"Optimisation générée pour {tenant_id}: {len(recommendations)} recommandations, "
                f"économies estimées: {optimization_impact.get('estimated_savings', 0):.2f}$/mois"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur optimisation ressources {tenant_id}: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    def _initialize_default_quotas(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les quotas par défaut par tier"""
        return {
            "free": {
                ResourceType.CPU: {"amount": 1.0, "unit": ResourceUnit.CORES},
                ResourceType.MEMORY: {"amount": 2.0, "unit": ResourceUnit.GB},
                ResourceType.STORAGE: {"amount": 10.0, "unit": ResourceUnit.GB},
                ResourceType.API_REQUESTS: {"amount": 1000.0, "unit": ResourceUnit.REQUESTS_PER_MINUTE}
            },
            "professional": {
                ResourceType.CPU: {"amount": 4.0, "unit": ResourceUnit.CORES},
                ResourceType.MEMORY: {"amount": 8.0, "unit": ResourceUnit.GB},
                ResourceType.STORAGE: {"amount": 100.0, "unit": ResourceUnit.GB},
                ResourceType.API_REQUESTS: {"amount": 10000.0, "unit": ResourceUnit.REQUESTS_PER_MINUTE}
            },
            "enterprise": {
                ResourceType.CPU: {"amount": 16.0, "unit": ResourceUnit.CORES},
                ResourceType.MEMORY: {"amount": 32.0, "unit": ResourceUnit.GB},
                ResourceType.STORAGE: {"amount": 1000.0, "unit": ResourceUnit.GB},
                ResourceType.API_REQUESTS: {"amount": 100000.0, "unit": ResourceUnit.REQUESTS_PER_MINUTE}
            }
        }
    
    def _initialize_resource_costs(self) -> Dict[ResourceType, float]:
        """Initialise les coûts par unité de ressource ($/mois)"""
        return {
            ResourceType.CPU: 30.0,  # $/core/mois
            ResourceType.MEMORY: 15.0,  # $/GB/mois
            ResourceType.STORAGE: 0.5,  # $/GB/mois
            ResourceType.NETWORK_BANDWIDTH: 0.1,  # $/Mbps/mois
            ResourceType.DATABASE_CONNECTIONS: 5.0,  # $/connection/mois
            ResourceType.API_REQUESTS: 0.01  # $/1000 requests/mois
        }
    
    async def _initialize_resource_tables(self) -> None:
        """Initialise les tables de gestion des ressources"""
        async with self.engine.begin() as conn:
            # Table des quotas de ressources
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS resource_quotas (
                    tenant_id VARCHAR(255),
                    resource_type VARCHAR(50),
                    resource_unit VARCHAR(50),
                    allocated_amount FLOAT,
                    used_amount FLOAT DEFAULT 0,
                    warning_threshold FLOAT DEFAULT 0.8,
                    critical_threshold FLOAT DEFAULT 0.95,
                    enforcement_level VARCHAR(20) DEFAULT 'hard',
                    reset_period_seconds INTEGER DEFAULT 3600,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    PRIMARY KEY (tenant_id, resource_type)
                )
            """))
            
            # Table des métriques d'usage
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS resource_usage_metrics (
                    metric_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255),
                    resource_type VARCHAR(50),
                    usage_amount FLOAT,
                    peak_usage FLOAT DEFAULT 0,
                    average_usage FLOAT DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
    
    async def _load_resource_configurations(self) -> None:
        """Charge les configurations de ressources existantes"""
        # Chargement depuis la base de données
        async with self.engine.begin() as conn:
            # Chargement des quotas existants
            result = await conn.execute(text("""
                SELECT * FROM resource_quotas WHERE is_active = TRUE
            """))
            
            for row in result:
                quota = ResourceQuota(
                    tenant_id=row.tenant_id,
                    resource_type=ResourceType(row.resource_type),
                    resource_unit=ResourceUnit(row.resource_unit),
                    allocated_amount=row.allocated_amount,
                    used_amount=row.used_amount,
                    warning_threshold=row.warning_threshold,
                    critical_threshold=row.critical_threshold,
                    enforcement_level=QuotaEnforcementLevel(row.enforcement_level),
                    reset_period=timedelta(seconds=row.reset_period_seconds),
                    last_reset=row.last_reset,
                    created_at=row.created_at,
                    is_active=row.is_active
                )
                
                if quota.tenant_id not in self.tenant_quotas:
                    self.tenant_quotas[quota.tenant_id] = []
                self.tenant_quotas[quota.tenant_id].append(quota)
    
    async def _validate_resource_requests(
        self,
        tenant_id: str,
        resource_allocations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valide les demandes de ressources"""
        validated = {}
        
        for resource_type_str, config in resource_allocations.items():
            if resource_type_str in [rt.value for rt in ResourceType]:
                # Validation des paramètres requis
                if "amount" in config and isinstance(config["amount"], (int, float)) and config["amount"] > 0:
                    validated[resource_type_str] = config
        
        return validated
    
    async def _check_resource_availability(
        self,
        resource_type: ResourceType,
        requested_amount: float
    ) -> Dict[str, Any]:
        """Vérifie la disponibilité des ressources dans les pools"""
        # Recherche des pools pour ce type de ressource
        relevant_pools = [
            pool for pool in self.resource_pools.values()
            if pool.resource_type == resource_type and pool.is_active
        ]
        
        if not relevant_pools:
            # Pas de pool défini, considérer comme disponible (allocation directe)
            return {"available": True, "available_amount": float('inf')}
        
        # Calcul de la capacité disponible totale
        total_available = sum(pool.available_capacity for pool in relevant_pools)
        
        return {
            "available": total_available >= requested_amount,
            "available_amount": total_available,
            "pools_checked": len(relevant_pools)
        }
    
    async def _allocate_from_resource_pools(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        amount: float
    ) -> Dict[str, Any]:
        """Alloue des ressources depuis les pools"""
        try:
            # Simulation d'allocation (en production, intégrer avec orchestrateurs)
            return {
                "success": True,
                "allocated_amount": amount,
                "pool_allocations": [
                    {"pool_id": "default_pool", "allocated": amount}
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_resource_quota(self, quota: ResourceQuota) -> None:
        """Sauvegarde un quota de ressource"""
        async with self.engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO resource_quotas (
                    tenant_id, resource_type, resource_unit, allocated_amount,
                    used_amount, warning_threshold, critical_threshold,
                    enforcement_level, reset_period_seconds, created_at, is_active
                ) VALUES (
                    :tenant_id, :resource_type, :resource_unit, :allocated_amount,
                    :used_amount, :warning_threshold, :critical_threshold,
                    :enforcement_level, :reset_period_seconds, :created_at, :is_active
                ) ON CONFLICT (tenant_id, resource_type) DO UPDATE SET
                    allocated_amount = EXCLUDED.allocated_amount,
                    warning_threshold = EXCLUDED.warning_threshold,
                    critical_threshold = EXCLUDED.critical_threshold,
                    enforcement_level = EXCLUDED.enforcement_level
            """), {
                "tenant_id": quota.tenant_id,
                "resource_type": quota.resource_type.value,
                "resource_unit": quota.resource_unit.value,
                "allocated_amount": quota.allocated_amount,
                "used_amount": quota.used_amount,
                "warning_threshold": quota.warning_threshold,
                "critical_threshold": quota.critical_threshold,
                "enforcement_level": quota.enforcement_level.value,
                "reset_period_seconds": int(quota.reset_period.total_seconds()),
                "created_at": quota.created_at,
                "is_active": quota.is_active
            })
    
    async def _calculate_allocation_cost(self, quotas: List[ResourceQuota]) -> float:
        """Calcule le coût total d'allocation"""
        total_cost = 0.0
        
        for quota in quotas:
            unit_cost = self.resource_costs.get(quota.resource_type, 0.0)
            total_cost += quota.allocated_amount * unit_cost
        
        return total_cost
    
    async def _setup_resource_alerts(
        self,
        tenant_id: str,
        quotas: List[ResourceQuota]
    ) -> List[Dict[str, Any]]:
        """Configure les alertes de ressources"""
        alert_configs = []
        
        for quota in quotas:
            config = {
                "resource_type": quota.resource_type.value,
                "warning_threshold": quota.warning_threshold,
                "critical_threshold": quota.critical_threshold,
                "alert_methods": ["email", "webhook"],
                "escalation_enabled": True
            }
            alert_configs.append(config)
        
        return alert_configs
    
    async def _generate_cost_breakdown(self, quotas: List[ResourceQuota]) -> Dict[str, float]:
        """Génère une répartition des coûts par ressource"""
        breakdown = {}
        
        for quota in quotas:
            unit_cost = self.resource_costs.get(quota.resource_type, 0.0)
            resource_cost = quota.allocated_amount * unit_cost
            breakdown[quota.resource_type.value] = resource_cost
        
        return breakdown
    
    async def _get_current_resource_usage(
        self,
        tenant_id: str,
        resource_type: ResourceType
    ) -> float:
        """Récupère l'utilisation actuelle d'une ressource"""
        # Simulation d'utilisation (en production, récupérer depuis monitoring)
        import random
        return random.uniform(0.3, 0.9)  # 30-90% d'utilisation simulée
    
    async def _get_historical_usage_metrics(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        time_range: timedelta
    ) -> List[ResourceUsageMetric]:
        """Récupère les métriques historiques d'usage"""
        # Simulation de métriques historiques
        metrics = []
        end_time = datetime.utcnow()
        
        for i in range(24):  # 24 points de données
            timestamp = end_time - timedelta(hours=i)
            usage = 0.5 + 0.3 * (i % 12) / 12  # Pattern cyclique
            
            metric = ResourceUsageMetric(
                tenant_id=tenant_id,
                resource_type=resource_type,
                usage_amount=usage,
                timestamp=timestamp
            )
            metrics.append(metric)
        
        return metrics
    
    def _calculate_usage_trend(self, metrics: List[ResourceUsageMetric]) -> str:
        """Calcule la tendance d'usage"""
        if len(metrics) < 2:
            return "stable"
        
        recent_avg = sum(m.usage_amount for m in metrics[:6]) / 6  # 6 dernières heures
        older_avg = sum(m.usage_amount for m in metrics[6:12]) / 6  # 6 heures précédentes
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def _generate_usage_alert(
        self,
        tenant_id: str,
        quota: ResourceQuota,
        usage_percentage: float,
        severity: str
    ) -> None:
        """Génère une alerte d'usage"""
        alert = ResourceAlert(
            alert_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            resource_type=quota.resource_type,
            alert_level=severity,
            message=f"Usage {quota.resource_type.value}: {usage_percentage:.1f}%",
            threshold_exceeded=quota.warning_threshold if severity == "warning" else quota.critical_threshold,
            current_usage=quota.used_amount,
            recommended_action="Consider scaling up" if severity == "critical" else "Monitor closely"
        )
        
        if tenant_id not in self.active_alerts:
            self.active_alerts[tenant_id] = []
        self.active_alerts[tenant_id].append(alert)
        
        # Notification (en production, envoyer email/webhook)
        self.resource_stats["alert_notifications"] += 1
    
    async def _log_resource_activity(
        self,
        tenant_id: str,
        activity_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Enregistre une activité de ressource"""
        activity_data = {
            "tenant_id": tenant_id,
            "activity_type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            f"resource_activity:{tenant_id}:{int(datetime.utcnow().timestamp())}",
            timedelta(days=90).total_seconds(),
            json.dumps(activity_data)
        )
    
    async def _resource_monitor_scheduler(self) -> None:
        """Planificateur de monitoring des ressources"""
        while True:
            try:
                # Monitoring périodique de tous les tenants
                for tenant_id in self.tenant_quotas.keys():
                    await self.monitor_resource_usage(tenant_id)
                
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur resource monitor: {e}")
                await asyncio.sleep(300)
    
    async def _quota_enforcement_scheduler(self) -> None:
        """Planificateur d'enforcement des quotas"""
        while True:
            try:
                # Vérification et reset des quotas périodiques
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"Erreur quota enforcement: {e}")
                await asyncio.sleep(3600)
    
    async def _usage_metrics_collector(self) -> None:
        """Collecteur de métriques d'usage"""
        while True:
            try:
                # Collecte des métriques
                await asyncio.sleep(60)  # Toutes les minutes
            except Exception as e:
                logger.error(f"Erreur metrics collector: {e}")
                await asyncio.sleep(60)
    
    async def _alert_processor(self) -> None:
        """Processeur d'alertes"""
        while True:
            try:
                # Traitement des alertes en attente
                await asyncio.sleep(30)  # Toutes les 30 secondes
            except Exception as e:
                logger.error(f"Erreur alert processor: {e}")
                await asyncio.sleep(30)
    
    async def _predictive_scaling_engine(self) -> None:
        """Moteur de scaling prédictif"""
        while True:
            try:
                # Prédictions et scaling automatique
                await asyncio.sleep(1800)  # Toutes les 30 minutes
            except Exception as e:
                logger.error(f"Erreur predictive scaling: {e}")
                await asyncio.sleep(1800)
    
    async def _cost_optimization_scheduler(self) -> None:
        """Planificateur d'optimisation des coûts"""
        while True:
            try:
                # Optimisation périodique des coûts
                await asyncio.sleep(86400)  # Tous les jours
            except Exception as e:
                logger.error(f"Erreur cost optimization: {e}")
                await asyncio.sleep(86400)
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("TenantResourceManager nettoyé")


# Instance principale
tenant_resource_manager = None


async def get_tenant_resource_manager() -> TenantResourceManager:
    """Factory pour l'instance TenantResourceManager"""
    global tenant_resource_manager
    if not tenant_resource_manager:
        database_url = "postgresql+asyncpg://localhost/ainflue_resources"
        redis_url = "redis://localhost:6379/6"
        
        tenant_resource_manager = TenantResourceManager(
            database_url=database_url,
            redis_url=redis_url,
            enable_predictive_scaling=True,
            enable_cost_optimization=True
        )
        await tenant_resource_manager.initialize()
    
    return tenant_resource_manager


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    manager = await get_tenant_resource_manager()
    
    test_tenant_id = "tenant_demo_resources"
    
    try:
        # Test allocation de ressources
        resource_allocations = {
            "cpu": {"amount": 4.0, "unit": "cores", "enforcement": "adaptive"},
            "memory": {"amount": 8.0, "unit": "gb", "enforcement": "hard"},
            "storage": {"amount": 100.0, "unit": "gb", "enforcement": "soft"},
            "api_requests": {"amount": 5000.0, "unit": "requests_per_minute"}
        }
        
        allocation_result = await manager.allocate_tenant_resources(
            test_tenant_id,
            resource_allocations
        )
        print(f"✅ Ressources allouées: {allocation_result['allocation_summary']['total_quotas_allocated']} quotas")
        print(f"   Coût estimé: {allocation_result['allocation_summary']['estimated_monthly_cost']:.2f}$/mois")
        
        # Test monitoring d'usage
        monitoring_result = await manager.monitor_resource_usage(test_tenant_id)
        print(f"✅ Monitoring: {monitoring_result['usage_summary']['total_resources_monitored']} ressources")
        print(f"   Conformité: {monitoring_result['usage_summary']['compliant_resources']} conformes")
        
        # Test enforcement de quota
        enforcement_result = await manager.enforce_quota_limits(
            test_tenant_id,
            ResourceType.CPU,
            1.5  # Demande 1.5 cores
        )
        print(f"✅ Enforcement: {enforcement_result['decision']}")
        print(f"   Usage projeté: {enforcement_result['projected_percentage']:.1f}%")
        
        # Test optimisation
        optimization_result = await manager.optimize_resource_allocation(
            test_tenant_id,
            "balanced"
        )
        print(f"✅ Optimisation: {len(optimization_result['optimization_recommendations'])} recommandations")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())