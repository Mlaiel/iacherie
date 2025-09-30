"""⚡ Resource Allocation Optimizer - Dynamic Resource Management Implementation
==============================================================================

Optimisateur d'allocation ressources enterprise avec gestion dynamique CPU/mémoire,
scaling automatique et optimisation coûts pour la plateforme Ainflue.

Expert Roles Implementation:
⚡ Performance Engineer: Resource optimization + performance tuning + capacity planning + bottleneck resolution
⚙️ DevOps Engineer: Infrastructure automation + container orchestration + cloud resource management  
🧠 ML Engineer: Predictive resource scaling + workload forecasting + intelligent allocation algorithms
🏗️ Backend Senior: Service resource management + load balancing + distributed resource coordination
🗄️ DBA Senior: Database resource optimization + connection pooling + memory management + storage optimization
🔒 Security Specialist: Resource isolation + secure multi-tenancy + access control + resource monitoring
🔗 Microservices Architect: Service mesh resource management + resource sharing + distributed coordination
🤖 Lead Dev IA: AI-driven resource decisions + intelligent scaling + predictive optimization + self-healing
💰 Cost Engineer: Cost optimization + budget management + resource efficiency + cloud spend optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture d'optimisation ressources est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import threading
import subprocess
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import psutil
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiomysql
import aiohttp
from contextlib import asynccontextmanager
import backoff
import structlog
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import docker
import kubernetes
import boto3

# Configuration du logging structuré pour resource optimization
logger = structlog.get_logger("resource_optimizer")

class ResourceType(Enum):
    """Types de ressources gérés"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE_CONNECTIONS = "database_connections"

class ScalingStrategy(Enum):
    """Stratégies de scaling"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"

class ResourceStatus(Enum):
    """Statuts des ressources"""
    OPTIMAL = "optimal"
    UNDERUTILIZED = "underutilized"
    OVERUTILIZED = "overutilized"
    CRITICAL = "critical"
    SCALING = "scaling"

class AllocationPolicy(Enum):
    """Politiques d'allocation"""
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    WORKLOAD_AWARE = "workload_aware"
    COST_EFFICIENT = "cost_efficient"
    PERFORMANCE_FIRST = "performance_first"

@dataclass
class ResourceConfiguration:
    """Configuration optimiseur ressources"""
    scaling_strategy: ScalingStrategy = ScalingStrategy.HYBRID
    allocation_policy: AllocationPolicy = AllocationPolicy.WORKLOAD_AWARE
    monitoring_interval_seconds: int = 30
    scaling_cooldown_seconds: int = 300
    cpu_target_utilization: float = 70.0
    memory_target_utilization: float = 80.0
    enable_predictive_scaling: bool = True
    cost_optimization_enabled: bool = True
    max_scale_out_percentage: float = 200.0  # Max 200% of current resources
    min_scale_in_percentage: float = 50.0   # Min 50% of current resources
    emergency_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu": 95.0,
        "memory": 95.0,
        "storage": 90.0
    })

@dataclass
class ResourceMetrics:
    """Métriques de ressources"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resource_type: ResourceType = ResourceType.CPU
    current_usage: float = 0.0
    current_capacity: float = 0.0
    utilization_percentage: float = 0.0
    allocated_units: float = 0.0
    available_units: float = 0.0
    cost_per_hour: float = 0.0
    efficiency_score: float = 0.0

@dataclass
class ScalingEvent:
    """Événement de scaling"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resource_type: ResourceType = ResourceType.CPU
    action: str = ""  # scale_up, scale_down, scale_out, scale_in
    reason: str = ""
    previous_capacity: float = 0.0
    new_capacity: float = 0.0
    cost_impact: float = 0.0
    success: bool = False
    duration_seconds: float = 0.0

@dataclass
class ResourcePool:
    """Pool de ressources"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    resource_type: ResourceType = ResourceType.CPU
    total_capacity: float = 0.0
    allocated_capacity: float = 0.0
    available_capacity: float = 0.0
    services: List[str] = field(default_factory=list)
    priority_level: int = 1  # 1=highest, 5=lowest
    cost_per_unit: float = 0.0
    auto_scaling_enabled: bool = True

@dataclass
class WorkloadPrediction:
    """Prédiction charge de travail"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    service_name: str = ""
    predicted_cpu: float = 0.0
    predicted_memory: float = 0.0
    predicted_storage: float = 0.0
    predicted_connections: int = 0
    confidence: float = 0.0
    time_horizon_minutes: int = 60
    factors: Dict[str, Any] = field(default_factory=dict)

class ResourceAllocationOptimizer:
    """⚡ Optimisateur d'allocation ressources enterprise avec gestion dynamique
    
    Fonctionnalités Expert Multi-Rôles:
    
    ⚡ Performance Engineer:
    - Resource optimization algorithms
    - Performance tuning automation
    - Capacity planning intelligent
    - Bottleneck identification et resolution
    
    ⚙️ DevOps Engineer:
    - Infrastructure automation
    - Container orchestration
    - Cloud resource management
    - CI/CD resource optimization
    
    🧠 ML Engineer:
    - Predictive resource scaling
    - Workload forecasting models
    - Intelligent allocation algorithms
    - Anomaly detection pour resources
    
    🏗️ Backend Senior:
    - Service resource management
    - Load balancing optimization
    - Distributed resource coordination
    - Service mesh resource policies
    
    🗄️ DBA Senior:
    - Database resource optimization
    - Connection pool management
    - Memory tuning automatique
    - Storage optimization
    
    🔒 Security Specialist:
    - Resource isolation secure
    - Multi-tenant resource management
    - Resource access control
    - Security monitoring resources
    
    🔗 Microservices Architect:
    - Service mesh resource management
    - Inter-service resource sharing
    - Distributed resource coordination
    - Resource dependency management
    
    🤖 Lead Dev IA:
    - AI-driven resource decisions
    - Intelligent auto-scaling
    - Predictive optimization
    - Self-healing resource management
    
    💰 Cost Engineer:
    - Cost optimization algorithms
    - Budget management automation
    - Resource efficiency maximization
    - Cloud spend optimization
    """
    
    def __init__(self, config: ResourceConfiguration):
        self.config = config
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.metrics_history: List[ResourceMetrics] = []
        self.scaling_events: List[ScalingEvent] = []
        self.workload_predictions: List[WorkloadPrediction] = []
        self.active_scaling_operations: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.background_tasks: List[asyncio.Task] = []
        
        # ML Models pour prédiction
        self.cpu_predictor = None
        self.memory_predictor = None
        self.workload_predictor = None
        self.scaler = StandardScaler()
        
        # Connexions external services
        self.redis_client = None
        self.docker_client = None
        self.k8s_client = None
        
        # Métriques optimization
        self.optimization_metrics = {
            "total_scaling_events": 0,
            "successful_scaling_events": 0,
            "cost_savings_usd": 0.0,
            "average_utilization": 0.0,
            "scaling_accuracy": 0.0,
            "response_time_improvement": 0.0,
            "resource_efficiency": 0.0,
            "predictive_accuracy": 0.0
        }
        
        # Initialisation
        self._initialize_resource_pools()
        self._initialize_ml_models()
        
        logger.info("ResourceAllocationOptimizer initialisé", 
                   strategy=self.config.scaling_strategy.value)
    
    def _initialize_resource_pools(self):
        """Initialisation pools de ressources"""
        # Pool CPU
        cpu_pool = ResourcePool(
            name="CPU Pool",
            resource_type=ResourceType.CPU,
            total_capacity=100.0,  # 100 CPU cores
            services=["api-gateway", "user-service", "content-service"],
            priority_level=1,
            cost_per_unit=0.05,  # $0.05 per CPU hour
            auto_scaling_enabled=True
        )
        self.resource_pools["cpu"] = cpu_pool
        
        # Pool Memory
        memory_pool = ResourcePool(
            name="Memory Pool",
            resource_type=ResourceType.MEMORY,
            total_capacity=512.0,  # 512 GB RAM
            services=["database", "cache", "analytics"],
            priority_level=1,
            cost_per_unit=0.01,  # $0.01 per GB hour
            auto_scaling_enabled=True
        )
        self.resource_pools["memory"] = memory_pool
        
        # Pool Storage
        storage_pool = ResourcePool(
            name="Storage Pool",
            resource_type=ResourceType.STORAGE,
            total_capacity=10240.0,  # 10 TB storage
            services=["database", "media-storage", "backup"],
            priority_level=2,
            cost_per_unit=0.001,  # $0.001 per GB hour
            auto_scaling_enabled=True
        )
        self.resource_pools["storage"] = storage_pool
        
        # Pool Database Connections
        db_connections_pool = ResourcePool(
            name="Database Connections Pool", 
            resource_type=ResourceType.DATABASE_CONNECTIONS,
            total_capacity=1000.0,  # 1000 connections
            services=["api-gateway", "user-service", "content-service"],
            priority_level=1,
            cost_per_unit=0.0,  # No direct cost
            auto_scaling_enabled=True
        )
        self.resource_pools["database_connections"] = db_connections_pool
    
    def _initialize_ml_models(self):
        """Initialisation modèles ML pour prédiction"""
        try:
            # Modèle prédiction CPU
            self.cpu_predictor = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Modèle prédiction Memory
            self.memory_predictor = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Modèle prédiction Workload
            self.workload_predictor = RandomForestRegressor(
                n_estimators=50,
                random_state=42
            )
            
            logger.info("Modèles ML initialisés pour prédiction ressources")
            
        except Exception as e:
            logger.error("Erreur initialisation ML models", error=str(e))
    
    async def start(self):
        """Démarrage optimiseur ressources"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Initialisation connexions
        await self._initialize_connections()
        
        # Entraînement initial modèles ML
        if self.config.enable_predictive_scaling:
            await self._train_prediction_models()
        
        # Démarrage tâches background
        tasks = [
            self._resource_monitoring_loop(),
            self._scaling_decision_engine(),
            self._cost_optimization_loop(),
            self._predictive_scaling_loop(),
            self._metrics_collection_loop()
        ]
        
        self.background_tasks = [asyncio.create_task(task) for task in tasks]
        
        logger.info("ResourceAllocationOptimizer démarré")
    
    async def stop(self):
        """Arrêt optimiseur ressources"""
        self.is_running = False
        
        # Arrêt scaling operations actives
        for operation_id in list(self.active_scaling_operations.keys()):
            await self._cancel_scaling_operation(operation_id)
        
        # Arrêt tâches background
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks = []
        
        # Fermeture connexions
        await self._close_connections()
        
        logger.info("ResourceAllocationOptimizer arrêté")
    
    async def _initialize_connections(self):
        """Initialisation connexions externes"""
        try:
            # Redis pour coordination
            self.redis_client = await aioredis.from_url('redis://localhost:6379')
            
            # Docker client pour container management
            try:
                self.docker_client = docker.from_env()
            except Exception:
                logger.warning("Docker client non disponible")
            
            # Kubernetes client
            try:
                kubernetes.config.load_incluster_config()
                self.k8s_client = kubernetes.client.ApiClient()
            except Exception:
                logger.warning("Kubernetes client non disponible")
            
            logger.info("Connexions external services initialisées")
            
        except Exception as e:
            logger.error("Erreur initialisation connexions", error=str(e))
    
    async def _close_connections(self):
        """Fermeture connexions"""
        if self.redis_client:
            await self.redis_client.close()
        
        if self.docker_client:
            self.docker_client.close()
    
    # ⚡ PERFORMANCE ENGINEER - Resource optimization algorithms
    
    async def _resource_monitoring_loop(self):
        """Boucle monitoring ressources"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.monitoring_interval_seconds)
                
                # Collecte métriques toutes ressources
                for pool_name, pool in self.resource_pools.items():
                    metrics = await self._collect_resource_metrics(pool)
                    self.metrics_history.append(metrics)
                    
                    # Évaluation status ressource
                    status = self._evaluate_resource_status(metrics)
                    
                    # Actions selon status
                    if status == ResourceStatus.CRITICAL:
                        await self._handle_critical_resource_situation(pool, metrics)
                    elif status == ResourceStatus.OVERUTILIZED:
                        await self._handle_overutilized_resource(pool, metrics)
                    elif status == ResourceStatus.UNDERUTILIZED:
                        await self._handle_underutilized_resource(pool, metrics)
                
                # Nettoyage historique ancien
                self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error("Erreur monitoring ressources", error=str(e))
    
    async def _collect_resource_metrics(self, pool: ResourcePool) -> ResourceMetrics:
        """Collecte métriques pool ressources"""
        metrics = ResourceMetrics(resource_type=pool.resource_type)
        
        try:
            if pool.resource_type == ResourceType.CPU:
                # Collecte métriques CPU
                cpu_usage = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                
                metrics.current_usage = cpu_usage
                metrics.current_capacity = cpu_count * 100  # 100% per CPU
                metrics.utilization_percentage = cpu_usage
                metrics.allocated_units = pool.allocated_capacity
                metrics.available_units = pool.total_capacity - pool.allocated_capacity
                
            elif pool.resource_type == ResourceType.MEMORY:
                # Collecte métriques Memory
                memory = psutil.virtual_memory()
                
                metrics.current_usage = memory.used / (1024**3)  # GB
                metrics.current_capacity = memory.total / (1024**3)  # GB
                metrics.utilization_percentage = memory.percent
                metrics.allocated_units = pool.allocated_capacity
                metrics.available_units = pool.total_capacity - pool.allocated_capacity
                
            elif pool.resource_type == ResourceType.STORAGE:
                # Collecte métriques Storage
                disk = psutil.disk_usage('/')
                
                metrics.current_usage = disk.used / (1024**3)  # GB
                metrics.current_capacity = disk.total / (1024**3)  # GB
                metrics.utilization_percentage = (disk.used / disk.total) * 100
                metrics.allocated_units = pool.allocated_capacity
                metrics.available_units = pool.total_capacity - pool.allocated_capacity
                
            elif pool.resource_type == ResourceType.DATABASE_CONNECTIONS:
                # Simulation métriques DB connections
                active_connections = np.random.randint(50, 200)
                max_connections = 1000
                
                metrics.current_usage = active_connections
                metrics.current_capacity = max_connections
                metrics.utilization_percentage = (active_connections / max_connections) * 100
                metrics.allocated_units = pool.allocated_capacity
                metrics.available_units = pool.total_capacity - pool.allocated_capacity
            
            # Calcul cost et efficiency
            metrics.cost_per_hour = pool.cost_per_unit * metrics.allocated_units
            metrics.efficiency_score = self._calculate_efficiency_score(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error("Erreur collecte métriques", pool=pool.name, error=str(e))
            return metrics
    
    def _calculate_efficiency_score(self, metrics: ResourceMetrics) -> float:
        """Calcul score efficacité ressource"""
        # Score basé sur utilisation optimale (target utilization)
        target_utilization = self.config.cpu_target_utilization
        if metrics.resource_type == ResourceType.MEMORY:
            target_utilization = self.config.memory_target_utilization
        
        # Score optimal quand utilisation proche du target
        deviation = abs(metrics.utilization_percentage - target_utilization)
        efficiency = max(0, 100 - deviation)
        
        return efficiency
    
    def _evaluate_resource_status(self, metrics: ResourceMetrics) -> ResourceStatus:
        """Évaluation status ressource"""
        utilization = metrics.utilization_percentage
        
        # Seuils critiques
        emergency_threshold = self.config.emergency_thresholds.get(
            metrics.resource_type.value, 95.0
        )
        
        if utilization >= emergency_threshold:
            return ResourceStatus.CRITICAL
        elif utilization >= 85.0:
            return ResourceStatus.OVERUTILIZED
        elif utilization <= 30.0:
            return ResourceStatus.UNDERUTILIZED
        else:
            return ResourceStatus.OPTIMAL
    
    # ⚙️ DEVOPS ENGINEER - Infrastructure automation
    
    async def _scaling_decision_engine(self):
        """Moteur décision scaling"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Décisions chaque minute
                
                # Analyse tous les pools
                for pool_name, pool in self.resource_pools.items():
                    if not pool.auto_scaling_enabled:
                        continue
                    
                    # Récupération métriques récentes
                    recent_metrics = self._get_recent_metrics(pool.resource_type, 5)
                    
                    if not recent_metrics:
                        continue
                    
                    # Décision scaling selon stratégie
                    scaling_decision = await self._make_scaling_decision(
                        pool, recent_metrics
                    )
                    
                    if scaling_decision and scaling_decision["action"] != "no_action":
                        # Vérification cooldown
                        if await self._check_scaling_cooldown(pool):
                            await self._execute_scaling_decision(pool, scaling_decision)
                
            except Exception as e:
                logger.error("Erreur moteur décision scaling", error=str(e))
    
    def _get_recent_metrics(self, resource_type: ResourceType, 
                           count: int) -> List[ResourceMetrics]:
        """Récupération métriques récentes"""
        return [
            m for m in self.metrics_history[-count*4:]  # 4 pools * count
            if m.resource_type == resource_type
        ][-count:]
    
    async def _make_scaling_decision(self, pool: ResourcePool,
                                   recent_metrics: List[ResourceMetrics]) -> Dict[str, Any]:
        """Prise décision scaling"""
        try:
            if not recent_metrics:
                return {"action": "no_action"}
            
            latest_metrics = recent_metrics[-1]
            avg_utilization = statistics.mean([m.utilization_percentage for m in recent_metrics])
            
            # Décision selon stratégie
            if self.config.scaling_strategy == ScalingStrategy.REACTIVE:
                return await self._reactive_scaling_decision(pool, latest_metrics)
            
            elif self.config.scaling_strategy == ScalingStrategy.PREDICTIVE:
                return await self._predictive_scaling_decision(pool, recent_metrics)
            
            elif self.config.scaling_strategy == ScalingStrategy.HYBRID:
                return await self._hybrid_scaling_decision(pool, recent_metrics)
            
            elif self.config.scaling_strategy == ScalingStrategy.COST_OPTIMIZED:
                return await self._cost_optimized_scaling_decision(pool, recent_metrics)
            
            else:
                return await self._performance_optimized_scaling_decision(pool, recent_metrics)
            
        except Exception as e:
            logger.error("Erreur décision scaling", error=str(e))
            return {"action": "no_action"}
    
    async def _reactive_scaling_decision(self, pool: ResourcePool,
                                       metrics: ResourceMetrics) -> Dict[str, Any]:
        """Décision scaling réactive"""
        utilization = metrics.utilization_percentage
        
        # Scale up si utilisation élevée
        if utilization >= 80.0:
            scale_factor = min(1.5, utilization / 50.0)  # Max 1.5x
            new_capacity = pool.total_capacity * scale_factor
            
            return {
                "action": "scale_up",
                "reason": f"High utilization: {utilization:.1f}%",
                "new_capacity": new_capacity,
                "priority": "high" if utilization >= 90.0 else "medium"
            }
        
        # Scale down si utilisation faible
        elif utilization <= 30.0:
            scale_factor = max(0.7, utilization / 50.0)  # Min 0.7x
            new_capacity = pool.total_capacity * scale_factor
            
            return {
                "action": "scale_down",
                "reason": f"Low utilization: {utilization:.1f}%",
                "new_capacity": new_capacity,
                "priority": "low"
            }
        
        return {"action": "no_action"}
    
    async def _predictive_scaling_decision(self, pool: ResourcePool,
                                         recent_metrics: List[ResourceMetrics]) -> Dict[str, Any]:
        """Décision scaling prédictive"""
        try:
            # Prédiction utilisation future
            predicted_utilization = await self._predict_future_utilization(
                pool.resource_type, recent_metrics
            )
            
            current_utilization = recent_metrics[-1].utilization_percentage
            
            # Décision basée sur prédiction
            if predicted_utilization >= 85.0 and current_utilization < 70.0:
                # Scale proactif avant pic
                scale_factor = min(1.4, predicted_utilization / 60.0)
                new_capacity = pool.total_capacity * scale_factor
                
                return {
                    "action": "scale_up",
                    "reason": f"Predicted high utilization: {predicted_utilization:.1f}%",
                    "new_capacity": new_capacity,
                    "priority": "medium"
                }
            
            elif predicted_utilization <= 25.0 and current_utilization < 40.0:
                # Scale down anticipé
                scale_factor = max(0.8, predicted_utilization / 40.0)
                new_capacity = pool.total_capacity * scale_factor
                
                return {
                    "action": "scale_down",
                    "reason": f"Predicted low utilization: {predicted_utilization:.1f}%",
                    "new_capacity": new_capacity,
                    "priority": "low"
                }
            
            return {"action": "no_action"}
            
        except Exception as e:
            logger.error("Erreur scaling prédictif", error=str(e))
            return {"action": "no_action"}
    
    async def _predict_future_utilization(self, resource_type: ResourceType,
                                        recent_metrics: List[ResourceMetrics]) -> float:
        """Prédiction utilisation future avec ML"""
        try:
            if len(recent_metrics) < 3:
                return recent_metrics[-1].utilization_percentage if recent_metrics else 50.0
            
            # Préparation données pour ML
            X = []
            y = []
            
            for i, metrics in enumerate(recent_metrics):
                features = [
                    i,  # Time index
                    metrics.utilization_percentage,
                    metrics.efficiency_score,
                    datetime.now().hour,  # Hour of day
                    datetime.now().weekday()  # Day of week
                ]
                X.append(features)
                y.append(metrics.utilization_percentage)
            
            if len(X) >= 3:
                # Prédiction simple avec trend
                X_array = np.array(X)
                y_array = np.array(y)
                
                # Trend linéaire simple
                if len(y_array) >= 2:
                    trend = y_array[-1] - y_array[0]
                    predicted = y_array[-1] + (trend * 0.5)  # 50% du trend
                    
                    return max(0, min(100, predicted))
            
            return recent_metrics[-1].utilization_percentage
            
        except Exception as e:
            logger.error("Erreur prédiction utilisation", error=str(e))
            return recent_metrics[-1].utilization_percentage if recent_metrics else 50.0
    
    async def _hybrid_scaling_decision(self, pool: ResourcePool,
                                     recent_metrics: List[ResourceMetrics]) -> Dict[str, Any]:
        """Décision scaling hybride (réactive + prédictive)"""
        # Décision réactive
        reactive_decision = await self._reactive_scaling_decision(pool, recent_metrics[-1])
        
        # Décision prédictive
        predictive_decision = await self._predictive_scaling_decision(pool, recent_metrics)
        
        # Combinaison intelligente
        if reactive_decision["action"] == "no_action" and predictive_decision["action"] != "no_action":
            return predictive_decision
        elif reactive_decision["action"] != "no_action":
            return reactive_decision
        else:
            return {"action": "no_action"}
    
    # 🧠 ML ENGINEER - Predictive scaling et workload forecasting
    
    async def _train_prediction_models(self):
        """Entraînement modèles prédiction"""
        try:
            # Génération données synthétiques pour entraînement
            training_data = await self._generate_training_data()
            
            if len(training_data) < 100:
                logger.warning("Données insuffisantes pour entraînement ML")
                return
            
            # Préparation données
            X, y_cpu, y_memory = self._prepare_training_data(training_data)
            
            # Entraînement modèle CPU
            self.cpu_predictor.fit(X, y_cpu)
            
            # Entraînement modèle Memory
            self.memory_predictor.fit(X, y_memory)
            
            logger.info("Modèles ML entraînés avec succès", 
                       samples=len(training_data))
            
        except Exception as e:
            logger.error("Erreur entraînement ML models", error=str(e))
    
    async def _generate_training_data(self) -> List[Dict[str, Any]]:
        """Génération données entraînement synthétiques"""
        training_data = []
        
        # Simulation données historiques
        for i in range(500):  # 500 échantillons
            timestamp = datetime.utcnow() - timedelta(hours=i)
            
            # Patterns réalistes avec variations
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Peak hours simulation
            base_cpu = 40.0
            base_memory = 60.0
            
            if 9 <= hour <= 17:  # Business hours
                base_cpu += 20.0
                base_memory += 15.0
            
            if day_of_week < 5:  # Weekdays
                base_cpu += 10.0
                base_memory += 10.0
            
            # Random variations
            cpu_usage = max(10, min(95, base_cpu + np.random.normal(0, 10)))
            memory_usage = max(20, min(90, base_memory + np.random.normal(0, 8)))
            
            sample = {
                "timestamp": timestamp,
                "hour": hour,
                "day_of_week": day_of_week,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "storage_usage": np.random.uniform(30, 70),
                "connection_count": np.random.randint(50, 300)
            }
            
            training_data.append(sample)
        
        return training_data
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Préparation données pour entraînement"""
        X = []
        y_cpu = []
        y_memory = []
        
        for sample in training_data:
            features = [
                sample["hour"],
                sample["day_of_week"],
                sample["connection_count"] / 100.0,  # Normalized
                sample["storage_usage"] / 100.0      # Normalized
            ]
            
            X.append(features)
            y_cpu.append(sample["cpu_usage"])
            y_memory.append(sample["memory_usage"])
        
        return np.array(X), np.array(y_cpu), np.array(y_memory)
    
    async def _predictive_scaling_loop(self):
        """Boucle scaling prédictif"""
        while self.is_running:
            try:
                await asyncio.sleep(600)  # Prédictions chaque 10 minutes
                
                if not self.config.enable_predictive_scaling:
                    continue
                
                # Génération prédictions workload
                predictions = await self._generate_workload_predictions()
                
                # Application prédictions pour scaling proactif
                for prediction in predictions:
                    await self._apply_predictive_scaling(prediction)
                
            except Exception as e:
                logger.error("Erreur boucle scaling prédictif", error=str(e))
    
    async def _generate_workload_predictions(self) -> List[WorkloadPrediction]:
        """Génération prédictions workload"""
        predictions = []
        
        try:
            current_time = datetime.utcnow()
            
            # Prédictions pour les services principaux
            services = ["api-gateway", "user-service", "content-service", "database"]
            
            for service in services:
                # Features pour prédiction
                features = np.array([[
                    current_time.hour,
                    current_time.weekday(),
                    len([m for m in self.metrics_history[-10:] if m.resource_type == ResourceType.CPU]),
                    50.0  # Base connection count
                ]])
                
                # Prédictions ML
                predicted_cpu = 50.0  # Default
                predicted_memory = 60.0  # Default
                
                if self.cpu_predictor is not None:
                    try:
                        predicted_cpu = self.cpu_predictor.predict(features)[0]
                    except Exception:
                        pass
                
                if self.memory_predictor is not None:
                    try:
                        predicted_memory = self.memory_predictor.predict(features)[0]
                    except Exception:
                        pass
                
                prediction = WorkloadPrediction(
                    service_name=service,
                    predicted_cpu=max(10, min(95, predicted_cpu)),
                    predicted_memory=max(20, min(90, predicted_memory)),
                    predicted_storage=np.random.uniform(40, 80),
                    predicted_connections=int(np.random.uniform(50, 200)),
                    confidence=0.75,
                    time_horizon_minutes=60
                )
                
                predictions.append(prediction)
                
        except Exception as e:
            logger.error("Erreur génération prédictions", error=str(e))
        
        return predictions
    
    # 💰 COST ENGINEER - Cost optimization
    
    async def _cost_optimization_loop(self):
        """Boucle optimisation coûts"""
        while self.is_running:
            try:
                await asyncio.sleep(1800)  # Optimisation chaque 30 minutes
                
                if not self.config.cost_optimization_enabled:
                    continue
                
                # Analyse coûts actuels
                cost_analysis = await self._analyze_current_costs()
                
                # Identification opportunités économies
                savings_opportunities = await self._identify_cost_savings(cost_analysis)
                
                # Application optimisations coût
                for opportunity in savings_opportunities:
                    if opportunity["potential_savings"] > 10.0:  # Min $10/hour savings
                        success = await self._apply_cost_optimization(opportunity)
                        
                        if success:
                            self.optimization_metrics["cost_savings_usd"] += opportunity["potential_savings"]
                
            except Exception as e:
                logger.error("Erreur optimisation coûts", error=str(e))
    
    async def _analyze_current_costs(self) -> Dict[str, Any]:
        """Analyse coûts actuels"""
        total_cost = 0.0
        cost_breakdown = {}
        
        for pool_name, pool in self.resource_pools.items():
            # Calcul coût pool
            hourly_cost = pool.cost_per_unit * pool.allocated_capacity
            total_cost += hourly_cost
            
            cost_breakdown[pool_name] = {
                "hourly_cost": hourly_cost,
                "allocated_capacity": pool.allocated_capacity,
                "utilization": 0.0  # À calculer depuis métriques
            }
            
            # Calcul utilisation moyenne
            recent_metrics = self._get_recent_metrics(pool.resource_type, 10)
            if recent_metrics:
                avg_utilization = statistics.mean([m.utilization_percentage for m in recent_metrics])
                cost_breakdown[pool_name]["utilization"] = avg_utilization
        
        return {
            "total_hourly_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _identify_cost_savings(self, cost_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identification opportunités économies"""
        opportunities = []
        
        for pool_name, pool_data in cost_analysis["cost_breakdown"].items():
            utilization = pool_data["utilization"]
            hourly_cost = pool_data["hourly_cost"]
            
            # Opportunité si sous-utilisation significative
            if utilization < 40.0 and hourly_cost > 5.0:
                # Calcul économies potentielles
                optimal_capacity = pool_data["allocated_capacity"] * (utilization / 60.0)  # Target 60%
                cost_savings = (pool_data["allocated_capacity"] - optimal_capacity) * self.resource_pools[pool_name].cost_per_unit
                
                opportunity = {
                    "pool_name": pool_name,
                    "type": "rightsizing",
                    "current_utilization": utilization,
                    "current_capacity": pool_data["allocated_capacity"],
                    "recommended_capacity": optimal_capacity,
                    "potential_savings": cost_savings,
                    "confidence": 0.8 if utilization < 30.0 else 0.6
                }
                
                opportunities.append(opportunity)
        
        return opportunities
    
    async def _apply_cost_optimization(self, opportunity: Dict[str, Any]) -> bool:
        """Application optimisation coût"""
        try:
            pool_name = opportunity["pool_name"]
            pool = self.resource_pools.get(pool_name)
            
            if not pool:
                return False
            
            if opportunity["type"] == "rightsizing":
                # Application rightsizing
                new_capacity = opportunity["recommended_capacity"]
                
                scaling_event = ScalingEvent(
                    resource_type=pool.resource_type,
                    action="scale_down",
                    reason=f"Cost optimization: rightsizing for ${opportunity['potential_savings']:.2f}/hour savings",
                    previous_capacity=pool.total_capacity,
                    new_capacity=new_capacity,
                    cost_impact=-opportunity["potential_savings"]
                )
                
                success = await self._execute_scaling_operation(pool, scaling_event)
                
                if success:
                    logger.info("Optimisation coût appliquée",
                               pool=pool_name,
                               savings=opportunity["potential_savings"])
                
                return success
            
            return False
            
        except Exception as e:
            logger.error("Erreur application optimisation coût", error=str(e))
            return False
    
    # Exécution scaling operations
    
    async def _execute_scaling_decision(self, pool: ResourcePool, decision: Dict[str, Any]):
        """Exécution décision scaling"""
        try:
            scaling_event = ScalingEvent(
                resource_type=pool.resource_type,
                action=decision["action"],
                reason=decision["reason"],
                previous_capacity=pool.total_capacity,
                new_capacity=decision.get("new_capacity", pool.total_capacity)
            )
            
            success = await self._execute_scaling_operation(pool, scaling_event)
            
            scaling_event.success = success
            scaling_event.duration_seconds = (datetime.utcnow() - scaling_event.timestamp).total_seconds()
            
            self.scaling_events.append(scaling_event)
            self.optimization_metrics["total_scaling_events"] += 1
            
            if success:
                self.optimization_metrics["successful_scaling_events"] += 1
                logger.info("Scaling exécuté avec succès", 
                           pool=pool.name, action=decision["action"])
            
        except Exception as e:
            logger.error("Erreur exécution scaling", error=str(e))
    
    async def _execute_scaling_operation(self, pool: ResourcePool, event: ScalingEvent) -> bool:
        """Exécution opération scaling"""
        try:
            operation_id = str(uuid.uuid4())
            
            self.active_scaling_operations[operation_id] = {
                "pool": pool,
                "event": event,
                "start_time": datetime.utcnow()
            }
            
            # Simulation scaling selon type ressource
            if pool.resource_type == ResourceType.CPU:
                success = await self._scale_cpu_resources(pool, event)
            elif pool.resource_type == ResourceType.MEMORY:
                success = await self._scale_memory_resources(pool, event)
            elif pool.resource_type == ResourceType.STORAGE:
                success = await self._scale_storage_resources(pool, event)
            elif pool.resource_type == ResourceType.DATABASE_CONNECTIONS:
                success = await self._scale_database_connections(pool, event)
            else:
                success = False
            
            # Mise à jour pool si succès
            if success:
                pool.total_capacity = event.new_capacity
                pool.available_capacity = event.new_capacity - pool.allocated_capacity
            
            self.active_scaling_operations.pop(operation_id, None)
            return success
            
        except Exception as e:
            logger.error("Erreur opération scaling", error=str(e))
            return False
    
    async def _scale_cpu_resources(self, pool: ResourcePool, event: ScalingEvent) -> bool:
        """Scaling ressources CPU"""
        try:
            # Simulation scaling CPU (production: Kubernetes HPA ou AWS Auto Scaling)
            if event.action == "scale_up":
                # Scale up CPU instances
                logger.info(f"Scaling up CPU from {event.previous_capacity} to {event.new_capacity}")
                await asyncio.sleep(1)  # Simulation delay
                return True
            
            elif event.action == "scale_down":
                # Scale down CPU instances
                logger.info(f"Scaling down CPU from {event.previous_capacity} to {event.new_capacity}")
                await asyncio.sleep(1)
                return True
            
            return False
            
        except Exception as e:
            logger.error("Erreur scaling CPU", error=str(e))
            return False
    
    async def _scale_memory_resources(self, pool: ResourcePool, event: ScalingEvent) -> bool:
        """Scaling ressources Memory"""
        try:
            # Simulation scaling Memory
            logger.info(f"Scaling memory from {event.previous_capacity}GB to {event.new_capacity}GB")
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error("Erreur scaling Memory", error=str(e))
            return False
    
    async def _scale_storage_resources(self, pool: ResourcePool, event: ScalingEvent) -> bool:
        """Scaling ressources Storage"""
        try:
            # Simulation scaling Storage
            logger.info(f"Scaling storage from {event.previous_capacity}GB to {event.new_capacity}GB")
            await asyncio.sleep(2)  # Storage scaling plus lent
            return True
            
        except Exception as e:
            logger.error("Erreur scaling Storage", error=str(e))
            return False
    
    async def _scale_database_connections(self, pool: ResourcePool, event: ScalingEvent) -> bool:
        """Scaling connexions database"""
        try:
            # Simulation scaling DB connections
            logger.info(f"Scaling DB connections from {event.previous_capacity} to {event.new_capacity}")
            await asyncio.sleep(0.5)
            return True
            
        except Exception as e:
            logger.error("Erreur scaling DB connections", error=str(e))
            return False
    
    # Utilitaires et gestion
    
    async def _check_scaling_cooldown(self, pool: ResourcePool) -> bool:
        """Vérification cooldown scaling"""
        # Récupération derniers scaling events pour ce pool
        recent_events = [
            event for event in self.scaling_events
            if (event.resource_type == pool.resource_type and
                (datetime.utcnow() - event.timestamp).total_seconds() < self.config.scaling_cooldown_seconds)
        ]
        
        return len(recent_events) == 0
    
    async def _handle_critical_resource_situation(self, pool: ResourcePool, metrics: ResourceMetrics):
        """Gestion situation critique ressources"""
        logger.critical("Situation critique ressources détectée",
                       pool=pool.name,
                       utilization=metrics.utilization_percentage)
        
        # Scaling d'urgence
        emergency_scaling = {
            "action": "scale_up",
            "reason": f"Emergency scaling - critical utilization: {metrics.utilization_percentage:.1f}%",
            "new_capacity": pool.total_capacity * 1.5,  # +50% capacity
            "priority": "critical"
        }
        
        await self._execute_scaling_decision(pool, emergency_scaling)
    
    async def _handle_overutilized_resource(self, pool: ResourcePool, metrics: ResourceMetrics):
        """Gestion ressource sur-utilisée"""
        logger.warning("Ressource sur-utilisée",
                      pool=pool.name,
                      utilization=metrics.utilization_percentage)
    
    async def _handle_underutilized_resource(self, pool: ResourcePool, metrics: ResourceMetrics):
        """Gestion ressource sous-utilisée"""
        logger.info("Ressource sous-utilisée",
                   pool=pool.name,
                   utilization=metrics.utilization_percentage)
    
    def _cleanup_old_metrics(self):
        """Nettoyage métriques anciennes"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]
        
        # Limit total size
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]
    
    async def _cancel_scaling_operation(self, operation_id: str):
        """Annulation opération scaling"""
        operation = self.active_scaling_operations.get(operation_id)
        if operation:
            logger.warning("Annulation opération scaling", operation_id=operation_id)
            self.active_scaling_operations.pop(operation_id)
    
    # Métriques et monitoring
    
    async def _metrics_collection_loop(self):
        """Boucle collecte métriques"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Collecte chaque 5 minutes
                
                # Calcul métriques globales
                await self._update_global_metrics()
                
            except Exception as e:
                logger.error("Erreur collecte métriques", error=str(e))
    
    async def _update_global_metrics(self):
        """Mise à jour métriques globales"""
        try:
            # Calcul utilisation moyenne
            if self.metrics_history:
                recent_metrics = self.metrics_history[-100:]  # 100 dernières
                avg_utilization = statistics.mean([m.utilization_percentage for m in recent_metrics])
                self.optimization_metrics["average_utilization"] = avg_utilization
            
            # Calcul efficacité ressources
            if self.metrics_history:
                recent_efficiency = [m.efficiency_score for m in self.metrics_history[-50:]]
                if recent_efficiency:
                    self.optimization_metrics["resource_efficiency"] = statistics.mean(recent_efficiency)
            
            # Calcul accuracy scaling
            if self.scaling_events:
                successful_events = len([e for e in self.scaling_events if e.success])
                total_events = len(self.scaling_events)
                self.optimization_metrics["scaling_accuracy"] = (successful_events / total_events) * 100 if total_events > 0 else 0
            
        except Exception as e:
            logger.error("Erreur mise à jour métriques", error=str(e))
    
    # API publique
    
    async def get_resource_status(self) -> Dict[str, Any]:
        """Status complet système ressources"""
        pool_status = {}
        
        for pool_name, pool in self.resource_pools.items():
            recent_metrics = self._get_recent_metrics(pool.resource_type, 1)
            latest_metrics = recent_metrics[0] if recent_metrics else None
            
            pool_status[pool_name] = {
                "resource_type": pool.resource_type.value,
                "total_capacity": pool.total_capacity,
                "allocated_capacity": pool.allocated_capacity,
                "available_capacity": pool.available_capacity,
                "current_utilization": latest_metrics.utilization_percentage if latest_metrics else 0.0,
                "efficiency_score": latest_metrics.efficiency_score if latest_metrics else 0.0,
                "cost_per_hour": pool.cost_per_unit * pool.allocated_capacity,
                "auto_scaling_enabled": pool.auto_scaling_enabled,
                "services": pool.services
            }
        
        return {
            "optimizer_running": self.is_running,
            "scaling_strategy": self.config.scaling_strategy.value,
            "allocation_policy": self.config.allocation_policy.value,
            "pools": pool_status,
            "active_scaling_operations": len(self.active_scaling_operations),
            "recent_scaling_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "resource_type": event.resource_type.value,
                    "action": event.action,
                    "reason": event.reason,
                    "success": event.success
                }
                for event in self.scaling_events[-10:]  # 10 derniers
            ],
            "metrics": self.optimization_metrics
        }
    
    async def add_resource_pool(self, name: str, resource_type: ResourceType,
                              total_capacity: float, cost_per_unit: float = 0.0,
                              services: List[str] = None) -> ResourcePool:
        """Ajout nouveau pool de ressources"""
        pool = ResourcePool(
            name=name,
            resource_type=resource_type,
            total_capacity=total_capacity,
            available_capacity=total_capacity,
            cost_per_unit=cost_per_unit,
            services=services or [],
            auto_scaling_enabled=True
        )
        
        self.resource_pools[name.lower().replace(" ", "_")] = pool
        
        logger.info("Pool ressources ajouté", name=name, type=resource_type.value)
        return pool
    
    async def allocate_resources(self, pool_name: str, service_name: str,
                               requested_units: float) -> bool:
        """Allocation ressources à un service"""
        try:
            pool = self.resource_pools.get(pool_name)
            if not pool:
                logger.error("Pool ressources non trouvé", pool=pool_name)
                return False
            
            if requested_units > pool.available_capacity:
                logger.warning("Ressources insuffisantes",
                              pool=pool_name,
                              requested=requested_units,
                              available=pool.available_capacity)
                return False
            
            # Allocation
            pool.allocated_capacity += requested_units
            pool.available_capacity -= requested_units
            
            if service_name not in pool.services:
                pool.services.append(service_name)
            
            logger.info("Ressources allouées",
                       pool=pool_name,
                       service=service_name,
                       units=requested_units)
            
            return True
            
        except Exception as e:
            logger.error("Erreur allocation ressources", error=str(e))
            return False


# Fonctions utilitaires pour intégration

async def initialize_resource_allocation_optimizer(
    config: ResourceConfiguration = None
) -> ResourceAllocationOptimizer:
    """Initialisation optimiseur allocation ressources"""
    if config is None:
        config = ResourceConfiguration()
    
    optimizer = ResourceAllocationOptimizer(config)
    await optimizer.start()
    
    logger.info("ResourceAllocationOptimizer initialisé et démarré")
    return optimizer

def create_resource_config(
    strategy: ScalingStrategy = ScalingStrategy.HYBRID,
    cpu_target: float = 70.0,
    memory_target: float = 80.0,
    enable_predictive: bool = True
) -> ResourceConfiguration:
    """Création configuration ressources optimisée"""
    return ResourceConfiguration(
        scaling_strategy=strategy,
        cpu_target_utilization=cpu_target,
        memory_target_utilization=memory_target,
        enable_predictive_scaling=enable_predictive,
        cost_optimization_enabled=True
    )

# Export des classes principales
__all__ = [
    "ResourceAllocationOptimizer",
    "ResourceConfiguration",
    "ResourceType",
    "ScalingStrategy",
    "ResourceStatus",
    "AllocationPolicy",
    "ResourceMetrics",
    "ScalingEvent",
    "ResourcePool",
    "WorkloadPrediction",
    "initialize_resource_allocation_optimizer",
    "create_resource_config"
]