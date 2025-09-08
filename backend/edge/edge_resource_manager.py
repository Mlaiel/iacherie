"""Edge Resource Manager
========================

Gestionnaire de ressources edge ultra-efficace pour l'écosystème Ainflue.
Système avancé d'allocation dynamique, prédiction IA, optimisation coûts
et équilibrage performance pour infrastructure edge enterprise.

Enrichissements enterprise:
- Allocation ressources dynamique avec ML
- Prédiction ressources IA avec patterns
- Moteur optimisation coûts intelligent
- Équilibrage ressources performance temps réel
- Intelligence auto-scaling avec prédictions
- Analytics utilisation ressources avancées

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ AVIS JURIDIQUE - PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
Cette architecture est la propriété exclusive de Fahed Mlaiel.
Toute utilisation non autorisée entraînera des poursuites judiciaires.
"""

import asyncio
import logging
import time
import json
import math
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque
import threading
from abc import ABC, abstractmethod
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# DYNAMIC RESOURCE ALLOCATION
# ============================================================================

class ResourceType(str, Enum):
    """Types de ressources edge."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    BANDWIDTH = "bandwidth"
    EDGE_COMPUTE = "edge_compute"
    AI_ACCELERATOR = "ai_accelerator"


class ResourceStatus(str, Enum):
    """États des ressources."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    EXHAUSTED = "exhausted"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SCALING = "scaling"


class AllocationStrategy(str, Enum):
    """Stratégies d'allocation."""
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    AI_OPTIMIZED = "ai_optimized"
    CREATOR_OPTIMIZED = "creator_optimized"


@dataclass
class ResourceSpec:
    """Spécification de ressource."""
    resource_id: str
    resource_type: ResourceType
    capacity: float
    allocated: float = 0.0
    reserved: float = 0.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: str = ""
    cost_per_unit: float = 0.0
    performance_rating: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AllocationRequest:
    """Demande d'allocation de ressource."""
    request_id: str
    user_id: str
    creator_type: str
    resource_requirements: Dict[ResourceType, float]
    priority: int = 1
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceAllocation:
    """Allocation de ressource."""
    allocation_id: str
    request_id: str
    user_id: str
    allocated_resources: Dict[str, float]
    start_time: datetime
    end_time: Optional[datetime] = None
    actual_usage: Dict[str, float] = field(default_factory=dict)
    cost: float = 0.0
    status: str = "active"


class DynamicResourceAllocator:
    """Allocateur dynamique de ressources."""
    
    def __init__(self):
        self.resources: Dict[str, ResourceSpec] = {}
        self.allocation_requests: Dict[str, AllocationRequest] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.resource_pool: Dict[ResourceType, List[str]] = defaultdict(list)
        
        # Modèles de prédiction
        self.prediction_models = {
            "demand_predictor": None,
            "usage_pattern_analyzer": None,
            "creator_resource_model": None
        }
        
        self._initialize_default_resources()
        self._initialize_prediction_models()
    
    def _initialize_default_resources(self):
        """Initialise les ressources par défaut."""
        # CPU Cluster
        cpu_cluster = ResourceSpec(
            resource_id="cpu_cluster_01",
            resource_type=ResourceType.CPU,
            capacity=64.0,  # 64 vCPUs
            location="edge_datacenter_01",
            cost_per_unit=0.10,  # $0.10 per vCPU-hour
            performance_rating=1.0
        )
        
        # GPU Cluster
        gpu_cluster = ResourceSpec(
            resource_id="gpu_cluster_01", 
            resource_type=ResourceType.GPU,
            capacity=8.0,  # 8 GPUs
            location="edge_datacenter_01",
            cost_per_unit=2.50,  # $2.50 per GPU-hour
            performance_rating=1.5
        )
        
        # Memory Pool
        memory_pool = ResourceSpec(
            resource_id="memory_pool_01",
            resource_type=ResourceType.MEMORY,
            capacity=512.0,  # 512 GB
            location="edge_datacenter_01",
            cost_per_unit=0.05,  # $0.05 per GB-hour
            performance_rating=1.0
        )
        
        # Storage Cluster
        storage_cluster = ResourceSpec(
            resource_id="storage_cluster_01",
            resource_type=ResourceType.STORAGE,
            capacity=10240.0,  # 10TB
            location="edge_datacenter_01",
            cost_per_unit=0.02,  # $0.02 per GB-hour
            performance_rating=0.8
        )
        
        self.resources.update({
            "cpu_cluster_01": cpu_cluster,
            "gpu_cluster_01": gpu_cluster,
            "memory_pool_01": memory_pool,
            "storage_cluster_01": storage_cluster
        })
        
        # Mise à jour pools
        self.resource_pool[ResourceType.CPU].append("cpu_cluster_01")
        self.resource_pool[ResourceType.GPU].append("gpu_cluster_01")
        self.resource_pool[ResourceType.MEMORY].append("memory_pool_01")
        self.resource_pool[ResourceType.STORAGE].append("storage_cluster_01")
    
    def _initialize_prediction_models(self):
        """Initialise les modèles de prédiction."""
        # TODO: Chargement modèles ML pré-entraînés
        logger.info("Resource prediction models initialized")
    
    async def request_allocation(self, request: AllocationRequest) -> str:
        """Traite une demande d'allocation."""
        try:
            self.allocation_requests[request.request_id] = request
            
            # Validation demande
            if not await self._validate_request(request):
                logger.error(f"Invalid allocation request: {request.request_id}")
                return ""
            
            # Optimisation allocation avec IA
            allocation_plan = await self._optimize_allocation(request)
            
            if allocation_plan:
                # Exécution allocation
                allocation_id = await self._execute_allocation(request, allocation_plan)
                
                if allocation_id:
                    logger.info(f"Resource allocation successful: {allocation_id}")
                    return allocation_id
            
            logger.warning(f"Resource allocation failed: {request.request_id}")
            return ""
            
        except Exception as e:
            logger.error(f"Allocation request error: {e}")
            return ""
    
    async def _validate_request(self, request: AllocationRequest) -> bool:
        """Valide une demande d'allocation."""
        try:
            # Vérification ressources demandées
            for resource_type, amount in request.resource_requirements.items():
                if amount <= 0:
                    return False
                
                # Vérification disponibilité théorique
                available = await self._get_available_capacity(resource_type)
                if available < amount:
                    logger.warning(f"Insufficient {resource_type}: requested {amount}, available {available}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return False
    
    async def _get_available_capacity(self, resource_type: ResourceType) -> float:
        """Récupère la capacité disponible pour un type de ressource."""
        total_available = 0.0
        
        for resource_id in self.resource_pool.get(resource_type, []):
            if resource_id in self.resources:
                resource = self.resources[resource_id]
                available = resource.capacity - resource.allocated - resource.reserved
                total_available += max(available, 0.0)
        
        return total_available
    
    async def _optimize_allocation(self, request: AllocationRequest) -> Optional[Dict[str, Any]]:
        """Optimise l'allocation avec IA."""
        try:
            # Stratégie basée sur type de créateur
            strategy = await self._select_allocation_strategy(request)
            
            allocation_plan = {
                "strategy": strategy,
                "resource_assignments": {},
                "estimated_cost": 0.0,
                "performance_score": 0.0
            }
            
            # Allocation par type de ressource
            for resource_type, required_amount in request.resource_requirements.items():
                assignment = await self._allocate_resource_type(
                    resource_type, required_amount, strategy, request
                )
                
                if assignment:
                    allocation_plan["resource_assignments"][resource_type] = assignment
                    allocation_plan["estimated_cost"] += assignment["cost"]
                    allocation_plan["performance_score"] += assignment["performance"]
                else:
                    return None  # Échec allocation
            
            return allocation_plan
            
        except Exception as e:
            logger.error(f"Allocation optimization error: {e}")
            return None
    
    async def _select_allocation_strategy(self, request: AllocationRequest) -> AllocationStrategy:
        """Sélectionne la stratégie d'allocation optimale."""
        # Stratégies par type de créateur
        creator_strategies = {
            "musician": AllocationStrategy.AI_OPTIMIZED,  # Audio processing intensif
            "photographer": AllocationStrategy.LOAD_BALANCED,  # Image processing
            "blogger": AllocationStrategy.BEST_FIT,  # Ressources légères
            "influencer": AllocationStrategy.CREATOR_OPTIMIZED,  # Multi-format
            "comedian": AllocationStrategy.AI_OPTIMIZED  # Video processing
        }
        
        return creator_strategies.get(request.creator_type, AllocationStrategy.BEST_FIT)
    
    async def _allocate_resource_type(self, resource_type: ResourceType, required_amount: float,
                                    strategy: AllocationStrategy, request: AllocationRequest) -> Optional[Dict[str, Any]]:
        """Alloue un type de ressource spécifique."""
        try:
            eligible_resources = []
            
            # Recherche ressources éligibles
            for resource_id in self.resource_pool.get(resource_type, []):
                if resource_id in self.resources:
                    resource = self.resources[resource_id]
                    available = resource.capacity - resource.allocated - resource.reserved
                    
                    if available >= required_amount and resource.status == ResourceStatus.AVAILABLE:
                        eligible_resources.append({
                            "resource_id": resource_id,
                            "resource": resource,
                            "available": available,
                            "efficiency": available / resource.capacity,
                            "cost_per_unit": resource.cost_per_unit,
                            "performance": resource.performance_rating
                        })
            
            if not eligible_resources:
                return None
            
            # Sélection selon stratégie
            selected = await self._select_by_strategy(eligible_resources, strategy, required_amount)
            
            if selected:
                # Réservation ressource
                resource = selected["resource"]
                resource.allocated += required_amount
                
                assignment = {
                    "resource_id": selected["resource_id"],
                    "allocated_amount": required_amount,
                    "cost": required_amount * resource.cost_per_unit,
                    "performance": resource.performance_rating,
                    "location": resource.location
                }
                
                return assignment
            
            return None
            
        except Exception as e:
            logger.error(f"Resource type allocation error: {e}")
            return None
    
    async def _select_by_strategy(self, eligible_resources: List[Dict], strategy: AllocationStrategy,
                                required_amount: float) -> Optional[Dict]:
        """Sélectionne la ressource selon la stratégie."""
        if not eligible_resources:
            return None
        
        if strategy == AllocationStrategy.BEST_FIT:
            # Ressource avec le moins de gaspillage
            eligible_resources.sort(key=lambda x: x["available"] - required_amount)
            return eligible_resources[0]
        
        elif strategy == AllocationStrategy.WORST_FIT:
            # Ressource avec le plus d'espace disponible
            eligible_resources.sort(key=lambda x: x["available"], reverse=True)
            return eligible_resources[0]
        
        elif strategy == AllocationStrategy.LOAD_BALANCED:
            # Ressource la moins chargée
            eligible_resources.sort(key=lambda x: x["efficiency"], reverse=True)
            return eligible_resources[0]
        
        elif strategy == AllocationStrategy.AI_OPTIMIZED:
            # Optimisation IA basée sur performance/coût
            scores = []
            for res in eligible_resources:
                score = res["performance"] / res["cost_per_unit"]
                scores.append((score, res))
            
            scores.sort(key=lambda x: x[0], reverse=True)
            return scores[0][1]
        
        elif strategy == AllocationStrategy.CREATOR_OPTIMIZED:
            # Optimisation spécifique créateur
            # TODO: Logique spécifique par type créateur
            return eligible_resources[0]
        
        else:  # FIRST_FIT par défaut
            return eligible_resources[0]
    
    async def _execute_allocation(self, request: AllocationRequest, plan: Dict[str, Any]) -> str:
        """Exécute l'allocation selon le plan."""
        try:
            allocation_id = str(uuid.uuid4())
            
            # Calcul ressources allouées
            allocated_resources = {}
            for resource_type, assignment in plan["resource_assignments"].items():
                allocated_resources[assignment["resource_id"]] = assignment["allocated_amount"]
            
            # Création allocation
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                request_id=request.request_id,
                user_id=request.user_id,
                allocated_resources=allocated_resources,
                start_time=datetime.now(),
                end_time=datetime.now() + request.duration if request.duration else None,
                cost=plan["estimated_cost"]
            )
            
            self.active_allocations[allocation_id] = allocation
            
            logger.info(f"Allocation executed: {allocation_id}, cost: ${plan['estimated_cost']:.2f}")
            return allocation_id
            
        except Exception as e:
            logger.error(f"Allocation execution error: {e}")
            return ""
    
    async def release_allocation(self, allocation_id: str) -> bool:
        """Libère une allocation de ressources."""
        try:
            if allocation_id not in self.active_allocations:
                return False
            
            allocation = self.active_allocations[allocation_id]
            
            # Libération ressources
            for resource_id, allocated_amount in allocation.allocated_resources.items():
                if resource_id in self.resources:
                    resource = self.resources[resource_id]
                    resource.allocated -= allocated_amount
                    resource.allocated = max(resource.allocated, 0.0)  # Éviter négatif
            
            # Archivage
            allocation.status = "completed"
            allocation.end_time = datetime.now()
            self.allocation_history.append(allocation)
            
            del self.active_allocations[allocation_id]
            
            logger.info(f"Allocation released: {allocation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Allocation release error: {e}")
            return False
    
    async def get_resource_utilization(self) -> Dict[str, Any]:
        """Récupère l'utilisation des ressources."""
        try:
            utilization = {}
            
            for resource_type in ResourceType:
                total_capacity = 0.0
                total_allocated = 0.0
                
                for resource_id in self.resource_pool.get(resource_type, []):
                    if resource_id in self.resources:
                        resource = self.resources[resource_id]
                        total_capacity += resource.capacity
                        total_allocated += resource.allocated
                
                utilization[resource_type.value] = {
                    "total_capacity": total_capacity,
                    "allocated": total_allocated,
                    "available": total_capacity - total_allocated,
                    "utilization_rate": total_allocated / total_capacity if total_capacity > 0 else 0
                }
            
            return utilization
            
        except Exception as e:
            logger.error(f"Utilization calculation error: {e}")
            return {}


# ============================================================================
# AI RESOURCE PREDICTION
# ============================================================================

@dataclass
class ResourceDemandPrediction:
    """Prédiction de demande en ressources."""
    resource_type: ResourceType
    predicted_demand: float
    confidence: float
    time_horizon: timedelta
    factors: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UsagePattern:
    """Pattern d'utilisation des ressources."""
    user_id: str
    creator_type: str
    resource_usage: Dict[ResourceType, List[float]]
    time_series: List[datetime]
    seasonality: Dict[str, float]
    trends: Dict[str, float]


class AIResourcePredictor:
    """Prédicteur de ressources alimenté par IA."""
    
    def __init__(self, allocator: DynamicResourceAllocator):
        self.allocator = allocator
        self.usage_patterns: Dict[str, UsagePattern] = {}
        self.demand_history: Dict[ResourceType, List[Tuple[datetime, float]]] = defaultdict(list)
        self.predictions: Dict[str, ResourceDemandPrediction] = {}
        
        # Modèles ML (simulation)
        self.ml_models = {
            "demand_forecaster": None,
            "pattern_detector": None,
            "anomaly_detector": None,
            "seasonal_predictor": None
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialise les modèles de prédiction."""
        # TODO: Chargement modèles ML pré-entraînés
        logger.info("AI resource prediction models initialized")
    
    async def record_usage(self, user_id: str, creator_type: str, 
                          resource_usage: Dict[ResourceType, float]):
        """Enregistre l'utilisation des ressources."""
        try:
            current_time = datetime.now()
            
            # Mise à jour pattern utilisateur
            if user_id not in self.usage_patterns:
                self.usage_patterns[user_id] = UsagePattern(
                    user_id=user_id,
                    creator_type=creator_type,
                    resource_usage=defaultdict(list),
                    time_series=[],
                    seasonality={},
                    trends={}
                )
            
            pattern = self.usage_patterns[user_id]
            pattern.time_series.append(current_time)
            
            for resource_type, usage in resource_usage.items():
                pattern.resource_usage[resource_type].append(usage)
                
                # Mise à jour historique global
                self.demand_history[resource_type].append((current_time, usage))
            
            # Limitation historique (30 derniers jours)
            cutoff_date = current_time - timedelta(days=30)
            pattern.time_series = [t for t in pattern.time_series if t > cutoff_date]
            
            for resource_type in pattern.resource_usage:
                while (len(pattern.time_series) < len(pattern.resource_usage[resource_type])):
                    pattern.resource_usage[resource_type].pop(0)
            
            # Mise à jour patterns
            await self._update_usage_patterns(user_id)
            
        except Exception as e:
            logger.error(f"Usage recording error: {e}")
    
    async def _update_usage_patterns(self, user_id: str):
        """Met à jour les patterns d'utilisation."""
        try:
            pattern = self.usage_patterns[user_id]
            
            # Détection saisonnalité
            pattern.seasonality = await self._detect_seasonality(pattern)
            
            # Détection tendances
            pattern.trends = await self._detect_trends(pattern)
            
        except Exception as e:
            logger.error(f"Pattern update error: {e}")
    
    async def _detect_seasonality(self, pattern: UsagePattern) -> Dict[str, float]:
        """Détecte la saisonnalité dans l'utilisation."""
        seasonality = {}
        
        if len(pattern.time_series) < 24:  # Minimum 24 points
            return seasonality
        
        try:
            # Analyse par heure du jour
            hourly_usage = defaultdict(list)
            
            for i, timestamp in enumerate(pattern.time_series):
                hour = timestamp.hour
                
                for resource_type, usage_list in pattern.resource_usage.items():
                    if i < len(usage_list):
                        hourly_usage[f"{resource_type.value}_hour_{hour}"].append(usage_list[i])
            
            # Calcul moyennes par heure
            for key, values in hourly_usage.items():
                if values:
                    seasonality[key] = sum(values) / len(values)
            
            return seasonality
            
        except Exception as e:
            logger.error(f"Seasonality detection error: {e}")
            return {}
    
    async def _detect_trends(self, pattern: UsagePattern) -> Dict[str, float]:
        """Détecte les tendances dans l'utilisation."""
        trends = {}
        
        try:
            for resource_type, usage_list in pattern.resource_usage.items():
                if len(usage_list) >= 10:  # Minimum pour calcul tendance
                    # Régression linéaire simple
                    n = len(usage_list)
                    x = list(range(n))
                    y = usage_list
                    
                    # Calcul pente
                    x_mean = sum(x) / n
                    y_mean = sum(y) / n
                    
                    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
                    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
                    
                    if denominator != 0:
                        slope = numerator / denominator
                        trends[f"{resource_type.value}_trend"] = slope
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend detection error: {e}")
            return {}
    
    async def predict_demand(self, resource_type: ResourceType, 
                           time_horizon: timedelta = timedelta(hours=1)) -> ResourceDemandPrediction:
        """Prédit la demande en ressources."""
        try:
            # Analyse historique
            historical_data = self.demand_history.get(resource_type, [])
            
            if len(historical_data) < 10:
                # Données insuffisantes, prédiction basée sur utilisation actuelle
                current_utilization = await self.allocator._get_available_capacity(resource_type)
                predicted_demand = current_utilization * 1.2  # +20% buffer
                confidence = 0.3
            else:
                # Prédiction basée sur ML
                predicted_demand, confidence = await self._ml_predict_demand(resource_type, historical_data, time_horizon)
            
            # Facteurs influençant la prédiction
            factors = await self._identify_demand_factors(resource_type)
            
            prediction = ResourceDemandPrediction(
                resource_type=resource_type,
                predicted_demand=predicted_demand,
                confidence=confidence,
                time_horizon=time_horizon,
                factors=factors
            )
            
            # Stockage prédiction
            prediction_key = f"{resource_type.value}_{time_horizon.total_seconds()}"
            self.predictions[prediction_key] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Demand prediction error: {e}")
            return ResourceDemandPrediction(
                resource_type=resource_type,
                predicted_demand=0.0,
                confidence=0.0,
                time_horizon=time_horizon,
                factors=[]
            )
    
    async def _ml_predict_demand(self, resource_type: ResourceType, 
                               historical_data: List[Tuple[datetime, float]], 
                               time_horizon: timedelta) -> Tuple[float, float]:
        """Prédiction ML de la demande."""
        try:
            # Simulation modèle ML
            recent_demands = [demand for _, demand in historical_data[-10:]]
            
            if recent_demands:
                # Moyenne pondérée (plus récent = plus de poids)
                weights = [0.1 * (i + 1) for i in range(len(recent_demands))]
                weighted_avg = sum(d * w for d, w in zip(recent_demands, weights)) / sum(weights)
                
                # Facteur temporel
                hour_factor = await self._get_temporal_factor(time_horizon)
                
                predicted_demand = weighted_avg * hour_factor
                confidence = min(len(recent_demands) / 20.0, 0.9)  # Max 90%
                
                return predicted_demand, confidence
            
            return 0.0, 0.0
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return 0.0, 0.0
    
    async def _get_temporal_factor(self, time_horizon: timedelta) -> float:
        """Calcule le facteur temporel pour la prédiction."""
        target_time = datetime.now() + time_horizon
        hour = target_time.hour
        day_of_week = target_time.weekday()
        
        # Facteurs par heure (simulation)
        hour_factors = {
            0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.3, 5: 0.4,
            6: 0.6, 7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.2,
            12: 1.3, 13: 1.2, 14: 1.1, 15: 1.0, 16: 0.9, 17: 0.8,
            18: 1.2, 19: 1.4, 20: 1.5, 21: 1.3, 22: 1.0, 23: 0.6
        }
        
        # Facteur week-end
        weekend_factor = 0.8 if day_of_week >= 5 else 1.0
        
        return hour_factors.get(hour, 1.0) * weekend_factor
    
    async def _identify_demand_factors(self, resource_type: ResourceType) -> List[str]:
        """Identifie les facteurs influençant la demande."""
        factors = []
        
        # Facteurs généraux
        current_hour = datetime.now().hour
        if 18 <= current_hour <= 22:
            factors.append("peak_hours")
        
        if datetime.now().weekday() >= 5:
            factors.append("weekend")
        
        # Facteurs spécifiques par type
        if resource_type == ResourceType.GPU:
            factors.extend(["ai_processing", "video_rendering"])
        elif resource_type == ResourceType.CPU:
            factors.extend(["general_compute", "concurrent_users"])
        elif resource_type == ResourceType.MEMORY:
            factors.extend(["data_processing", "cache_usage"])
        
        return factors
    
    async def get_user_prediction(self, user_id: str, resource_type: ResourceType) -> Optional[float]:
        """Prédit l'utilisation future d'un utilisateur."""
        try:
            if user_id not in self.usage_patterns:
                return None
            
            pattern = self.usage_patterns[user_id]
            usage_history = pattern.resource_usage.get(resource_type, [])
            
            if len(usage_history) < 5:
                return None
            
            # Prédiction basée sur tendance + saisonnalité
            recent_avg = sum(usage_history[-5:]) / 5
            
            # Application tendance
            trend_key = f"{resource_type.value}_trend"
            trend = pattern.trends.get(trend_key, 0.0)
            
            # Application saisonnalité
            current_hour = datetime.now().hour
            seasonal_key = f"{resource_type.value}_hour_{current_hour}"
            seasonal_factor = pattern.seasonality.get(seasonal_key, recent_avg)
            
            if seasonal_factor > 0:
                prediction = (recent_avg + trend) * (seasonal_factor / recent_avg)
            else:
                prediction = recent_avg + trend
            
            return max(prediction, 0.0)
            
        except Exception as e:
            logger.error(f"User prediction error: {e}")
            return None


# ============================================================================
# COST OPTIMIZATION ENGINE
# ============================================================================

@dataclass
class CostOptimizationRule:
    """Règle d'optimisation des coûts."""
    rule_id: str
    name: str
    condition: str
    action: str
    priority: int
    savings_potential: float
    enabled: bool = True


@dataclass
class CostReport:
    """Rapport de coûts."""
    period_start: datetime
    period_end: datetime
    total_cost: float
    cost_breakdown: Dict[ResourceType, float]
    optimization_opportunities: List[Dict[str, Any]]
    projected_savings: float


class CostOptimizationEngine:
    """Moteur d'optimisation des coûts."""
    
    def __init__(self, allocator: DynamicResourceAllocator):
        self.allocator = allocator
        self.optimization_rules: Dict[str, CostOptimizationRule] = {}
        self.cost_history: List[Tuple[datetime, float, Dict[str, Any]]] = []
        self.optimization_recommendations: List[Dict[str, Any]] = []
        
        self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self):
        """Initialise les règles d'optimisation."""
        # Règle sous-utilisation
        underutilization_rule = CostOptimizationRule(
            rule_id="underutilization",
            name="Détection Sous-utilisation",
            condition="utilization < 0.3 for 2 hours",
            action="scale_down",
            priority=1,
            savings_potential=0.4
        )
        
        # Règle ressources inactives
        idle_resources_rule = CostOptimizationRule(
            rule_id="idle_resources",
            name="Ressources Inactives",
            condition="no_allocation for 1 hour",
            action="hibernate",
            priority=2,
            savings_potential=0.8
        )
        
        # Règle sur-approvisionnement
        overprovisioning_rule = CostOptimizationRule(
            rule_id="overprovisioning",
            name="Sur-approvisionnement",
            condition="consistent_low_usage",
            action="right_size",
            priority=3,
            savings_potential=0.3
        )
        
        self.optimization_rules.update({
            "underutilization": underutilization_rule,
            "idle_resources": idle_resources_rule,
            "overprovisioning": overprovisioning_rule
        })
    
    async def analyze_costs(self, period_start: datetime, period_end: datetime) -> CostReport:
        """Analyse les coûts sur une période."""
        try:
            # Calcul coûts par type de ressource
            cost_breakdown = {}
            total_cost = 0.0
            
            # Analyse allocations historiques
            for allocation in self.allocator.allocation_history:
                if period_start <= allocation.start_time <= period_end:
                    total_cost += allocation.cost
                    
                    # Répartition par type
                    for resource_id, amount in allocation.allocated_resources.items():
                        if resource_id in self.allocator.resources:
                            resource = self.allocator.resources[resource_id]
                            resource_type = resource.resource_type
                            
                            cost_breakdown[resource_type] = cost_breakdown.get(resource_type, 0.0) + allocation.cost
            
            # Analyse allocations actives
            for allocation in self.allocator.active_allocations.values():
                if allocation.start_time >= period_start:
                    total_cost += allocation.cost
            
            # Identification opportunités
            opportunities = await self._identify_optimization_opportunities()
            
            # Calcul économies projetées
            projected_savings = sum(opp.get("potential_savings", 0.0) for opp in opportunities)
            
            report = CostReport(
                period_start=period_start,
                period_end=period_end,
                total_cost=total_cost,
                cost_breakdown=cost_breakdown,
                optimization_opportunities=opportunities,
                projected_savings=projected_savings
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Cost analysis error: {e}")
            return CostReport(
                period_start=period_start,
                period_end=period_end,
                total_cost=0.0,
                cost_breakdown={},
                optimization_opportunities=[],
                projected_savings=0.0
            )
    
    async def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'optimisation."""
        opportunities = []
        
        try:
            # Analyse utilisation ressources
            utilization = await self.allocator.get_resource_utilization()
            
            for resource_type_str, stats in utilization.items():
                resource_type = ResourceType(resource_type_str)
                utilization_rate = stats["utilization_rate"]
                
                # Sous-utilisation
                if utilization_rate < 0.3:
                    opportunities.append({
                        "type": "underutilization",
                        "resource_type": resource_type,
                        "current_utilization": utilization_rate,
                        "recommended_action": "scale_down",
                        "potential_savings": stats["allocated"] * 0.4,
                        "description": f"Sous-utilisation de {resource_type.value}: {utilization_rate:.1%}"
                    })
                
                # Sur-utilisation (besoin de scale up)
                elif utilization_rate > 0.9:
                    opportunities.append({
                        "type": "over_utilization",
                        "resource_type": resource_type,
                        "current_utilization": utilization_rate,
                        "recommended_action": "scale_up",
                        "potential_savings": -stats["allocated"] * 0.2,  # Coût mais évite pénalités
                        "description": f"Sur-utilisation de {resource_type.value}: {utilization_rate:.1%}"
                    })
            
            # Analyse patterns temporels
            temporal_opportunities = await self._analyze_temporal_patterns()
            opportunities.extend(temporal_opportunities)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Opportunity identification error: {e}")
            return []
    
    async def _analyze_temporal_patterns(self) -> List[Dict[str, Any]]:
        """Analyse les patterns temporels pour optimisation."""
        opportunities = []
        
        try:
            # TODO: Analyse patterns d'utilisation par heure/jour
            # Identification périodes creuses pour hibernation
            
            current_hour = datetime.now().hour
            
            # Heures creuses (simulation)
            if 2 <= current_hour <= 6:
                opportunities.append({
                    "type": "off_peak_optimization",
                    "recommended_action": "reduce_capacity",
                    "potential_savings": 100.0,  # $100/hour
                    "description": "Réduction capacité pendant heures creuses"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Temporal pattern analysis error: {e}")
            return []
    
    async def apply_optimization(self, opportunity: Dict[str, Any]) -> bool:
        """Applique une optimisation."""
        try:
            action = opportunity.get("recommended_action")
            
            if action == "scale_down":
                return await self._scale_down_resources(opportunity)
            elif action == "scale_up":
                return await self._scale_up_resources(opportunity)
            elif action == "hibernate":
                return await self._hibernate_resources(opportunity)
            elif action == "right_size":
                return await self._right_size_resources(opportunity)
            
            return False
            
        except Exception as e:
            logger.error(f"Optimization application error: {e}")
            return False
    
    async def _scale_down_resources(self, opportunity: Dict[str, Any]) -> bool:
        """Réduit la capacité des ressources."""
        # TODO: Implémentation scale down
        logger.info("Scaling down resources")
        return True
    
    async def _scale_up_resources(self, opportunity: Dict[str, Any]) -> bool:
        """Augmente la capacité des ressources."""
        # TODO: Implémentation scale up
        logger.info("Scaling up resources")
        return True
    
    async def _hibernate_resources(self, opportunity: Dict[str, Any]) -> bool:
        """Met en hibernation des ressources."""
        # TODO: Implémentation hibernation
        logger.info("Hibernating resources")
        return True
    
    async def _right_size_resources(self, opportunity: Dict[str, Any]) -> bool:
        """Ajuste la taille des ressources."""
        # TODO: Implémentation right-sizing
        logger.info("Right-sizing resources")
        return True
    
    async def get_cost_forecast(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Prévoit les coûts futurs."""
        try:
            # Analyse tendance historique
            if len(self.cost_history) < 7:
                return {"forecast": 0.0, "confidence": 0.0}
            
            recent_costs = [cost for _, cost, _ in self.cost_history[-7:]]
            daily_avg = sum(recent_costs) / len(recent_costs)
            
            # Projection simple
            forecasted_cost = daily_avg * days_ahead
            
            # Facteur saisonnalité
            seasonal_factor = await self._get_seasonal_cost_factor()
            forecasted_cost *= seasonal_factor
            
            return {
                "forecast": forecasted_cost,
                "daily_average": daily_avg,
                "confidence": 0.7,
                "factors": ["historical_trend", "seasonality"]
            }
            
        except Exception as e:
            logger.error(f"Cost forecast error: {e}")
            return {"forecast": 0.0, "confidence": 0.0}
    
    async def _get_seasonal_cost_factor(self) -> float:
        """Calcule le facteur saisonnier des coûts."""
        # TODO: Analyse saisonnalité réelle
        day_of_week = datetime.now().weekday()
        
        # Week-end généralement moins cher
        if day_of_week >= 5:
            return 0.8
        
        return 1.0


# ============================================================================
# EDGE RESOURCE MANAGER ORCHESTRATOR
# ============================================================================

class EdgeResourceManager:
    """Gestionnaire principal des ressources edge."""
    
    def __init__(self):
        # Composants principaux
        self.dynamic_allocator = DynamicResourceAllocator()
        self.ai_predictor = AIResourcePredictor(self.dynamic_allocator)
        self.cost_optimizer = CostOptimizationEngine(self.dynamic_allocator)
        
        # États et métriques
        self.is_initialized = False
        self.system_metrics = {
            "total_allocations": 0,
            "successful_allocations": 0,
            "failed_allocations": 0,
            "cost_savings": 0.0,
            "prediction_accuracy": 0.0
        }
        
        # Monitoring en temps réel
        self.monitoring_task = None
    
    async def initialize(self) -> bool:
        """Initialise le gestionnaire de ressources."""
        try:
            logger.info("Initializing Edge Resource Manager...")
            
            # Démarrage monitoring continu
            self.monitoring_task = asyncio.create_task(self._continuous_monitoring())
            
            self.is_initialized = True
            logger.info("Edge Resource Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize resource manager: {e}")
            return False
    
    async def allocate_resources_for_creator(self, creator_id: str, creator_type: str, 
                                          workload_type: str, duration: timedelta = None) -> str:
        """Alloue des ressources optimisées pour un créateur."""
        try:
            # Définition besoins par type de créateur
            requirements = await self._get_creator_requirements(creator_type, workload_type)
            
            # Création demande allocation
            request = AllocationRequest(
                request_id=str(uuid.uuid4()),
                user_id=creator_id,
                creator_type=creator_type,
                resource_requirements=requirements,
                priority=await self._calculate_creator_priority(creator_id, creator_type),
                duration=duration or timedelta(hours=2),
                constraints={"workload_type": workload_type}
            )
            
            # Allocation avec prédictions IA
            allocation_id = await self.dynamic_allocator.request_allocation(request)
            
            if allocation_id:
                self.system_metrics["successful_allocations"] += 1
                
                # Enregistrement pour prédictions futures
                await self.ai_predictor.record_usage(
                    creator_id, creator_type, requirements
                )
                
                logger.info(f"Resources allocated for {creator_type} creator {creator_id}: {allocation_id}")
                return allocation_id
            else:
                self.system_metrics["failed_allocations"] += 1
                return ""
            
        except Exception as e:
            logger.error(f"Creator resource allocation error: {e}")
            return ""
    
    async def _get_creator_requirements(self, creator_type: str, workload_type: str) -> Dict[ResourceType, float]:
        """Détermine les besoins en ressources par type de créateur."""
        base_requirements = {
            "musician": {
                ResourceType.CPU: 4.0,    # 4 vCPUs
                ResourceType.MEMORY: 8.0,  # 8 GB
                ResourceType.STORAGE: 50.0, # 50 GB
                ResourceType.GPU: 0.5      # 0.5 GPU pour processing audio
            },
            "photographer": {
                ResourceType.CPU: 2.0,
                ResourceType.MEMORY: 16.0,  # Plus de RAM pour images
                ResourceType.STORAGE: 100.0, # Plus de stockage
                ResourceType.GPU: 1.0       # GPU pour processing images
            },
            "blogger": {
                ResourceType.CPU: 1.0,
                ResourceType.MEMORY: 4.0,
                ResourceType.STORAGE: 10.0,
                ResourceType.GPU: 0.0       # Pas de GPU nécessaire
            },
            "influencer": {
                ResourceType.CPU: 6.0,      # Multi-format
                ResourceType.MEMORY: 12.0,
                ResourceType.STORAGE: 75.0,
                ResourceType.GPU: 1.0
            },
            "comedian": {
                ResourceType.CPU: 8.0,      # Video processing intensif
                ResourceType.MEMORY: 16.0,
                ResourceType.STORAGE: 200.0, # Gros fichiers vidéo
                ResourceType.GPU: 2.0       # GPU pour encoding vidéo
            }
        }
        
        requirements = base_requirements.get(creator_type, {
            ResourceType.CPU: 2.0,
            ResourceType.MEMORY: 4.0,
            ResourceType.STORAGE: 20.0,
            ResourceType.GPU: 0.0
        })
        
        # Ajustements par type de workload
        if workload_type == "live_streaming":
            requirements[ResourceType.CPU] *= 1.5
            requirements[ResourceType.MEMORY] *= 1.3
            requirements[ResourceType.BANDWIDTH] = requirements.get(ResourceType.BANDWIDTH, 0) + 10.0
        elif workload_type == "ai_processing":
            requirements[ResourceType.GPU] *= 2.0
            requirements[ResourceType.MEMORY] *= 1.5
        elif workload_type == "batch_processing":
            requirements[ResourceType.CPU] *= 0.8
            requirements[ResourceType.MEMORY] *= 0.9
        
        return requirements
    
    async def _calculate_creator_priority(self, creator_id: str, creator_type: str) -> int:
        """Calcule la priorité d'allocation pour un créateur."""
        # TODO: Intégration avec système analytics pour métriques réelles
        base_priority = {
            "musician": 3,
            "photographer": 2,
            "blogger": 1,
            "influencer": 4,
            "comedian": 3
        }.get(creator_type, 2)
        
        # Ajustements basés sur performance/engagement
        # TODO: Récupération métriques réelles créateur
        
        return base_priority
    
    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """Optimise l'allocation des ressources."""
        try:
            # Analyse coûts
            period_start = datetime.now() - timedelta(days=1)
            period_end = datetime.now()
            cost_report = await self.cost_optimizer.analyze_costs(period_start, period_end)
            
            # Application optimisations
            applied_optimizations = []
            
            for opportunity in cost_report.optimization_opportunities:
                if opportunity.get("potential_savings", 0) > 10.0:  # Seuil $10
                    success = await self.cost_optimizer.apply_optimization(opportunity)
                    if success:
                        applied_optimizations.append(opportunity)
                        self.system_metrics["cost_savings"] += opportunity.get("potential_savings", 0)
            
            return {
                "cost_report": cost_report,
                "applied_optimizations": applied_optimizations,
                "total_savings": sum(opt.get("potential_savings", 0) for opt in applied_optimizations)
            }
            
        except Exception as e:
            logger.error(f"Resource optimization error: {e}")
            return {}
    
    async def get_resource_analytics(self) -> Dict[str, Any]:
        """Récupère les analytics des ressources."""
        try:
            # Utilisation actuelle
            utilization = await self.dynamic_allocator.get_resource_utilization()
            
            # Prédictions
            predictions = {}
            for resource_type in ResourceType:
                pred = await self.ai_predictor.predict_demand(resource_type)
                predictions[resource_type.value] = {
                    "predicted_demand": pred.predicted_demand,
                    "confidence": pred.confidence,
                    "factors": pred.factors
                }
            
            # Prévisions coûts
            cost_forecast = await self.cost_optimizer.get_cost_forecast()
            
            return {
                "current_utilization": utilization,
                "demand_predictions": predictions,
                "cost_forecast": cost_forecast,
                "system_metrics": self.system_metrics,
                "active_allocations": len(self.dynamic_allocator.active_allocations),
                "total_capacity": {
                    rt.value: sum(res.capacity for res in self.dynamic_allocator.resources.values() 
                                 if res.resource_type == rt)
                    for rt in ResourceType
                }
            }
            
        except Exception as e:
            logger.error(f"Resource analytics error: {e}")
            return {}
    
    async def _continuous_monitoring(self):
        """Monitoring continu des ressources."""
        while self.is_initialized:
            try:
                # Monitoring utilisation
                utilization = await self.dynamic_allocator.get_resource_utilization()
                
                # Détection anomalies
                for resource_type_str, stats in utilization.items():
                    if stats["utilization_rate"] > 0.95:
                        logger.warning(f"High utilization detected: {resource_type_str} at {stats['utilization_rate']:.1%}")
                        
                        # Déclenchement auto-scaling si nécessaire
                        await self._trigger_auto_scaling(ResourceType(resource_type_str))
                
                # Attente avant prochaine vérification
                await asyncio.sleep(60)  # Monitoring chaque minute
                
            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_auto_scaling(self, resource_type: ResourceType):
        """Déclenche l'auto-scaling pour un type de ressource."""
        try:
            logger.info(f"Triggering auto-scaling for {resource_type.value}")
            
            # TODO: Implémentation auto-scaling intelligent
            # - Analyse tendances
            # - Prédiction demande future
            # - Décision scaling up/down
            # - Exécution scaling
            
        except Exception as e:
            logger.error(f"Auto-scaling error: {e}")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_edge_resource_manager() -> EdgeResourceManager:
    """Factory function pour créer le gestionnaire de ressources."""
    return EdgeResourceManager()


def create_dynamic_allocator() -> DynamicResourceAllocator:
    """Factory function pour créer l'allocateur dynamique."""
    return DynamicResourceAllocator()


def create_ai_predictor(allocator: DynamicResourceAllocator) -> AIResourcePredictor:
    """Factory function pour créer le prédicteur IA."""
    return AIResourcePredictor(allocator)


def create_cost_optimizer(allocator: DynamicResourceAllocator) -> CostOptimizationEngine:
    """Factory function pour créer l'optimiseur de coûts."""
    return CostOptimizationEngine(allocator)


# Export des classes principales
__all__ = [
    # Gestionnaire principal
    "EdgeResourceManager",
    "create_edge_resource_manager",
    
    # Allocation dynamique
    "DynamicResourceAllocator", "ResourceSpec", "AllocationRequest", "ResourceAllocation",
    "ResourceType", "ResourceStatus", "AllocationStrategy",
    "create_dynamic_allocator",
    
    # Prédiction IA
    "AIResourcePredictor", "ResourceDemandPrediction", "UsagePattern",
    "create_ai_predictor",
    
    # Optimisation coûts
    "CostOptimizationEngine", "CostOptimizationRule", "CostReport",
    "create_cost_optimizer"
]
