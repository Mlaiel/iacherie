"""🌐 Edge Deployment Manager - Global Edge Computing
=====================================================================
Module: ml/deployment/edge_deployment_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EDGE DEPLOYMENT & GLOBAL DISTRIBUTION
Advanced edge deployment for low-latency regional inference
- Global edge node management
- Intelligent model distribution strategies
- Creator-geographic optimization
- Real-time performance monitoring
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from pathlib import Path
import numpy as np
from collections import defaultdict

# Configuration
logger = logging.getLogger(__name__)

class EdgeRegion(Enum):
    """Régions edge disponibles"""
    
    US_EAST = "us-east-1"
    US_WEST = "us-west-1"
    EU_WEST = "eu-west-1"
    EU_CENTRAL = "eu-central-1"
    ASIA_PACIFIC = "ap-southeast-1"
    ASIA_NORTHEAST = "ap-northeast-1"
    MIDDLE_EAST = "me-south-1"
    AFRICA = "af-south-1"
    AUSTRALIA = "ap-southeast-2"

class DeploymentStrategy(Enum):
    """Stratégies de déploiement edge"""
    
    GLOBAL_REPLICATION = "global_replication"     # Réplication sur tous les edge
    REGIONAL_CLUSTERING = "regional_clustering"   # Clustering par région
    CREATOR_PROXIMITY = "creator_proximity"       # Proximité des creators
    DEMAND_BASED = "demand_based"                 # Basé sur la demande
    LATENCY_OPTIMIZED = "latency_optimized"       # Optimisé latence
    COST_OPTIMIZED = "cost_optimized"             # Optimisé coût

class EdgeNodeStatus(Enum):
    """Statut des nœuds edge"""
    
    ACTIVE = "active"
    DEPLOYING = "deploying"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    OVERLOADED = "overloaded"

@dataclass
class EdgeNode:
    """Nœud edge"""
    
    node_id: str
    region: EdgeRegion
    endpoint_url: str
    status: EdgeNodeStatus
    created_at: datetime
    last_heartbeat: datetime
    capacity_cpu: float         # CPU cores
    capacity_memory_gb: float   # RAM in GB
    capacity_storage_gb: float  # Storage in GB
    used_cpu: float = 0.0
    used_memory_gb: float = 0.0
    used_storage_gb: float = 0.0
    latency_ms: float = 0.0
    throughput_rps: float = 0.0  # Requests per second
    deployed_models: List[str] = field(default_factory=list)
    creator_affinity: Dict[str, float] = field(default_factory=dict)  # creator_type -> affinity score
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def cpu_utilization(self) -> float:
        return (self.used_cpu / self.capacity_cpu) * 100 if self.capacity_cpu > 0 else 0
    
    @property
    def memory_utilization(self) -> float:
        return (self.used_memory_gb / self.capacity_memory_gb) * 100 if self.capacity_memory_gb > 0 else 0
    
    @property
    def storage_utilization(self) -> float:
        return (self.used_storage_gb / self.capacity_storage_gb) * 100 if self.capacity_storage_gb > 0 else 0
    
    @property
    def overall_utilization(self) -> float:
        return max(self.cpu_utilization, self.memory_utilization, self.storage_utilization)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'region': self.region.value,
            'endpoint_url': self.endpoint_url,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'capacity': {
                'cpu': self.capacity_cpu,
                'memory_gb': self.capacity_memory_gb,
                'storage_gb': self.capacity_storage_gb
            },
            'usage': {
                'cpu': self.used_cpu,
                'memory_gb': self.used_memory_gb,
                'storage_gb': self.used_storage_gb
            },
            'performance': {
                'latency_ms': self.latency_ms,
                'throughput_rps': self.throughput_rps
            },
            'deployed_models': self.deployed_models,
            'creator_affinity': self.creator_affinity,
            'metadata': self.metadata
        }

@dataclass
class EdgeDeployment:
    """Déploiement edge"""
    
    deployment_id: str
    model_id: str
    model_version: str
    target_regions: List[EdgeRegion]
    strategy: DeploymentStrategy
    created_at: datetime
    deployed_at: Optional[datetime] = None
    status: str = "pending"
    creator_types: List[str] = field(default_factory=list)
    performance_requirements: Dict[str, float] = field(default_factory=dict)
    deployed_nodes: List[str] = field(default_factory=list)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_id': self.deployment_id,
            'model_id': self.model_id,
            'model_version': self.model_version,
            'target_regions': [r.value for r in self.target_regions],
            'strategy': self.strategy.value,
            'created_at': self.created_at.isoformat(),
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None,
            'status': self.status,
            'creator_types': self.creator_types,
            'performance_requirements': self.performance_requirements,
            'deployed_nodes': self.deployed_nodes,
            'deployment_config': self.deployment_config
        }

@dataclass
class EdgePerformanceMetrics:
    """Métriques de performance edge"""
    
    node_id: str
    timestamp: datetime
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput_rps: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    request_count: int
    creator_distribution: Dict[str, int] = field(default_factory=dict)

class EdgeDeploymentManager:
    """
    🌐 Edge Deployment Manager
    
    Gestionnaire de déploiement edge avec:
    - Distribution géographique intelligente
    - Optimisation latence creator-specific
    - Auto-scaling basé sur la demande
    - Monitoring performance en temps réel
    """
    
    def __init__(
        self,
        default_strategy: DeploymentStrategy = DeploymentStrategy.LATENCY_OPTIMIZED,
        max_nodes_per_region: int = 10,
        enable_auto_scaling: bool = True,
        heartbeat_interval: int = 30  # seconds
    ):
        self.default_strategy = default_strategy
        self.max_nodes_per_region = max_nodes_per_region
        self.enable_auto_scaling = enable_auto_scaling
        self.heartbeat_interval = heartbeat_interval
        
        # Stockage des nœuds et déploiements
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.deployments: Dict[str, EdgeDeployment] = {}
        
        # Index pour optimisation
        self.nodes_by_region: Dict[EdgeRegion, List[str]] = defaultdict(list)
        self.models_by_node: Dict[str, List[str]] = defaultdict(list)
        
        # Métriques de performance
        self.performance_history: List[EdgePerformanceMetrics] = []
        self.region_latencies: Dict[EdgeRegion, List[float]] = defaultdict(list)
        
        # Configuration creator-specific
        self.creator_region_preferences: Dict[str, List[EdgeRegion]] = {
            'musician': [EdgeRegion.US_WEST, EdgeRegion.EU_WEST, EdgeRegion.ASIA_PACIFIC],
            'blogger': [EdgeRegion.US_EAST, EdgeRegion.EU_CENTRAL, EdgeRegion.ASIA_NORTHEAST],
            'photographer': [EdgeRegion.EU_WEST, EdgeRegion.US_WEST, EdgeRegion.AUSTRALIA],
            'influencer': [EdgeRegion.US_EAST, EdgeRegion.ASIA_PACIFIC, EdgeRegion.EU_WEST]
        }
        
        # Configuration des seuils
        self.performance_thresholds = {
            'max_latency_ms': 100,      # 100ms max
            'max_cpu_utilization': 80,  # 80% max
            'max_memory_utilization': 80,
            'min_throughput_rps': 100   # 100 RPS min
        }
        
        logger.info("🌐 Edge Deployment Manager initialized")
    
    async def register_edge_node(
        self,
        region: EdgeRegion,
        endpoint_url: str,
        capacity_cpu: float,
        capacity_memory_gb: float,
        capacity_storage_gb: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Enregistrer un nouveau nœud edge"""
        
        node_id = f"edge_{region.value}_{uuid.uuid4().hex[:8]}"
        
        # Vérifier les limites par région
        if len(self.nodes_by_region[region]) >= self.max_nodes_per_region:
            raise ValueError(f"Maximum nodes reached for region {region.value}")
        
        # Créer le nœud
        node = EdgeNode(
            node_id=node_id,
            region=region,
            endpoint_url=endpoint_url,
            status=EdgeNodeStatus.ACTIVE,
            created_at=datetime.now(),
            last_heartbeat=datetime.now(),
            capacity_cpu=capacity_cpu,
            capacity_memory_gb=capacity_memory_gb,
            capacity_storage_gb=capacity_storage_gb,
            metadata=metadata or {}
        )
        
        # Enregistrer
        self.edge_nodes[node_id] = node
        self.nodes_by_region[region].append(node_id)
        
        logger.info(f"🌐 Registered edge node {node_id} in {region.value}")
        return node_id
    
    async def deploy_model_to_edge(
        self,
        model_id: str,
        model_version: str,
        creator_types: List[str],
        strategy: Optional[DeploymentStrategy] = None,
        target_regions: Optional[List[EdgeRegion]] = None,
        performance_requirements: Optional[Dict[str, float]] = None
    ) -> str:
        """Déployer un modèle sur les nœuds edge"""
        
        deployment_id = f"deploy_{uuid.uuid4().hex[:8]}"
        strategy = strategy or self.default_strategy
        
        # Déterminer les régions cibles
        if target_regions is None:
            target_regions = await self._select_optimal_regions(creator_types, strategy)
        
        # Créer le déploiement
        deployment = EdgeDeployment(
            deployment_id=deployment_id,
            model_id=model_id,
            model_version=model_version,
            target_regions=target_regions,
            strategy=strategy,
            created_at=datetime.now(),
            creator_types=creator_types,
            performance_requirements=performance_requirements or {},
            deployment_config={
                'auto_scale': self.enable_auto_scaling,
                'min_replicas': 1,
                'max_replicas': 3
            }
        )
        
        self.deployments[deployment_id] = deployment
        
        # Exécuter le déploiement
        await self._execute_deployment(deployment)
        
        logger.info(f"🚀 Deployed model {model_id} to edge with strategy {strategy.value}")
        return deployment_id
    
    async def _select_optimal_regions(
        self,
        creator_types: List[str],
        strategy: DeploymentStrategy
    ) -> List[EdgeRegion]:
        """Sélectionner les régions optimales"""
        
        if strategy == DeploymentStrategy.GLOBAL_REPLICATION:
            return list(EdgeRegion)
        
        elif strategy == DeploymentStrategy.CREATOR_PROXIMITY:
            # Sélectionner basé sur les préférences des creators
            preferred_regions = set()
            for creator_type in creator_types:
                if creator_type in self.creator_region_preferences:
                    preferred_regions.update(self.creator_region_preferences[creator_type])
            return list(preferred_regions) if preferred_regions else [EdgeRegion.US_EAST, EdgeRegion.EU_WEST]
        
        elif strategy == DeploymentStrategy.LATENCY_OPTIMIZED:
            # Sélectionner les régions avec la meilleure latence
            region_scores = {}
            for region in EdgeRegion:
                recent_latencies = self.region_latencies[region][-10:]  # 10 dernières mesures
                avg_latency = np.mean(recent_latencies) if recent_latencies else 50.0
                region_scores[region] = 1.0 / (avg_latency + 1)  # Inverse de la latence
            
            # Top 3 régions
            top_regions = sorted(region_scores.keys(), key=lambda r: region_scores[r], reverse=True)[:3]
            return top_regions
        
        elif strategy == DeploymentStrategy.DEMAND_BASED:
            # Analyser la demande par région
            region_demand = await self._analyze_regional_demand(creator_types)
            top_regions = sorted(region_demand.keys(), key=lambda r: region_demand[r], reverse=True)[:3]
            return top_regions
        
        else:
            # Par défaut: US-East et EU-West
            return [EdgeRegion.US_EAST, EdgeRegion.EU_WEST]
    
    async def _execute_deployment(self, deployment: EdgeDeployment):
        """Exécuter le déploiement sur les nœuds"""
        
        deployed_nodes = []
        
        for region in deployment.target_regions:
            # Trouver le meilleur nœud dans la région
            best_node = await self._select_best_node_in_region(region, deployment)
            
            if best_node:
                # Déployer sur le nœud
                success = await self._deploy_to_node(best_node, deployment)
                if success:
                    deployed_nodes.append(best_node.node_id)
                    best_node.deployed_models.append(deployment.model_id)
                    self.models_by_node[best_node.node_id].append(deployment.model_id)
        
        # Mettre à jour le déploiement
        deployment.deployed_nodes = deployed_nodes
        deployment.deployed_at = datetime.now()
        deployment.status = "deployed" if deployed_nodes else "failed"
        
        logger.info(f"✅ Deployment {deployment.deployment_id} completed on {len(deployed_nodes)} nodes")
    
    async def _select_best_node_in_region(
        self,
        region: EdgeRegion,
        deployment: EdgeDeployment
    ) -> Optional[EdgeNode]:
        """Sélectionner le meilleur nœud dans une région"""
        
        available_nodes = []
        
        for node_id in self.nodes_by_region[region]:
            node = self.edge_nodes[node_id]
            
            # Vérifier que le nœud est disponible
            if node.status != EdgeNodeStatus.ACTIVE:
                continue
            
            # Vérifier la capacité
            if node.overall_utilization > 80:  # 80% max
                continue
            
            # Calculer le score de compatibilité
            score = await self._calculate_node_score(node, deployment)
            available_nodes.append((node, score))
        
        if not available_nodes:
            return None
        
        # Trier par score et retourner le meilleur
        available_nodes.sort(key=lambda x: x[1], reverse=True)
        return available_nodes[0][0]
    
    async def _calculate_node_score(
        self,
        node: EdgeNode,
        deployment: EdgeDeployment
    ) -> float:
        """Calculer le score d'un nœud pour un déploiement"""
        
        score = 0.0
        
        # Score basé sur l'utilisation (moins utilisé = mieux)
        utilization_score = (100 - node.overall_utilization) / 100
        score += utilization_score * 0.3
        
        # Score basé sur la performance
        latency_score = max(0, (200 - node.latency_ms) / 200)  # 200ms = score 0
        score += latency_score * 0.3
        
        throughput_score = min(1.0, node.throughput_rps / 1000)  # 1000 RPS = score 1
        score += throughput_score * 0.2
        
        # Score basé sur l'affinité avec les creators
        affinity_score = 0.0
        for creator_type in deployment.creator_types:
            affinity_score += node.creator_affinity.get(creator_type, 0.5)
        affinity_score = affinity_score / len(deployment.creator_types) if deployment.creator_types else 0.5
        score += affinity_score * 0.2
        
        return score
    
    async def _deploy_to_node(
        self,
        node: EdgeNode,
        deployment: EdgeDeployment
    ) -> bool:
        """Déployer un modèle sur un nœud spécifique"""
        
        try:
            # Simulation du déploiement
            # Dans un vrai système, on ferait un appel API vers le nœud
            
            # Estimer les ressources nécessaires
            estimated_cpu = 1.0  # 1 CPU core
            estimated_memory = 2.0  # 2GB RAM
            estimated_storage = 1.0  # 1GB storage
            
            # Vérifier la capacité
            if (node.used_cpu + estimated_cpu > node.capacity_cpu or
                node.used_memory_gb + estimated_memory > node.capacity_memory_gb or
                node.used_storage_gb + estimated_storage > node.capacity_storage_gb):
                return False
            
            # "Déployer" (simulation)
            node.used_cpu += estimated_cpu
            node.used_memory_gb += estimated_memory
            node.used_storage_gb += estimated_storage
            
            # Mettre à jour l'affinité avec les creators
            for creator_type in deployment.creator_types:
                current_affinity = node.creator_affinity.get(creator_type, 0.5)
                node.creator_affinity[creator_type] = min(1.0, current_affinity + 0.1)
            
            logger.debug(f"📦 Deployed {deployment.model_id} to node {node.node_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed to node {node.node_id}: {e}")
            return False
    
    async def update_node_metrics(
        self,
        node_id: str,
        metrics: Dict[str, Any]
    ):
        """Mettre à jour les métriques d'un nœud"""
        
        if node_id not in self.edge_nodes:
            return
        
        node = self.edge_nodes[node_id]
        node.last_heartbeat = datetime.now()
        
        # Mettre à jour les métriques
        if 'latency_ms' in metrics:
            node.latency_ms = metrics['latency_ms']
            self.region_latencies[node.region].append(metrics['latency_ms'])
            
            # Garder seulement les 100 dernières mesures
            if len(self.region_latencies[node.region]) > 100:
                self.region_latencies[node.region] = self.region_latencies[node.region][-100:]
        
        if 'throughput_rps' in metrics:
            node.throughput_rps = metrics['throughput_rps']
        
        if 'cpu_usage' in metrics:
            node.used_cpu = metrics['cpu_usage']
        
        if 'memory_usage_gb' in metrics:
            node.used_memory_gb = metrics['memory_usage_gb']
        
        # Créer une métrique de performance
        if 'performance_metrics' in metrics:
            perf_metrics = EdgePerformanceMetrics(
                node_id=node_id,
                timestamp=datetime.now(),
                latency_p50=metrics['performance_metrics'].get('latency_p50', 0),
                latency_p95=metrics['performance_metrics'].get('latency_p95', 0),
                latency_p99=metrics['performance_metrics'].get('latency_p99', 0),
                throughput_rps=metrics['performance_metrics'].get('throughput_rps', 0),
                error_rate=metrics['performance_metrics'].get('error_rate', 0),
                cpu_usage=metrics['performance_metrics'].get('cpu_usage', 0),
                memory_usage=metrics['performance_metrics'].get('memory_usage', 0),
                request_count=metrics['performance_metrics'].get('request_count', 0),
                creator_distribution=metrics['performance_metrics'].get('creator_distribution', {})
            )
            
            self.performance_history.append(perf_metrics)
            
            # Garder seulement les 1000 dernières métriques
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
        
        # Détecter les problèmes de performance
        await self._check_node_health(node)
    
    async def _check_node_health(self, node: EdgeNode):
        """Vérifier la santé d'un nœud"""
        
        issues = []
        
        # Vérifier la latence
        if node.latency_ms > self.performance_thresholds['max_latency_ms']:
            issues.append(f"High latency: {node.latency_ms}ms")
        
        # Vérifier l'utilisation
        if node.cpu_utilization > self.performance_thresholds['max_cpu_utilization']:
            issues.append(f"High CPU usage: {node.cpu_utilization:.1f}%")
        
        if node.memory_utilization > self.performance_thresholds['max_memory_utilization']:
            issues.append(f"High memory usage: {node.memory_utilization:.1f}%")
        
        # Vérifier le débit
        if node.throughput_rps < self.performance_thresholds['min_throughput_rps']:
            issues.append(f"Low throughput: {node.throughput_rps} RPS")
        
        if issues:
            logger.warning(f"⚠️ Node {node.node_id} health issues: {', '.join(issues)}")
            
            # Auto-scaling si activé
            if self.enable_auto_scaling:
                await self._trigger_auto_scaling(node)
    
    async def _trigger_auto_scaling(self, overloaded_node: EdgeNode):
        """Déclencher l'auto-scaling"""
        
        logger.info(f"🔄 Triggering auto-scaling for region {overloaded_node.region.value}")
        
        # Dans un vrai système, on créerait de nouveaux nœuds
        # Ici, on simule en réduisant la charge du nœud
        if overloaded_node.used_cpu > 0:
            overloaded_node.used_cpu *= 0.8  # Réduire la charge de 20%
        if overloaded_node.used_memory_gb > 0:
            overloaded_node.used_memory_gb *= 0.8
    
    async def _analyze_regional_demand(
        self,
        creator_types: List[str]
    ) -> Dict[EdgeRegion, float]:
        """Analyser la demande par région"""
        
        # Analyser l'historique des métriques
        regional_demand = defaultdict(float)
        
        for metrics in self.performance_history[-100:]:  # 100 dernières métriques
            node = self.edge_nodes.get(metrics.node_id)
            if node:
                # Score basé sur le trafic et les types de creators
                demand_score = metrics.request_count
                
                for creator_type in creator_types:
                    creator_requests = metrics.creator_distribution.get(creator_type, 0)
                    demand_score += creator_requests * 2  # Pondération
                
                regional_demand[node.region] += demand_score
        
        return dict(regional_demand)
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'un déploiement"""
        
        if deployment_id not in self.deployments:
            return None
        
        deployment = self.deployments[deployment_id]
        
        # Analyser les performances des nœuds déployés
        node_performances = []
        for node_id in deployment.deployed_nodes:
            node = self.edge_nodes.get(node_id)
            if node:
                node_performances.append({
                    'node_id': node_id,
                    'region': node.region.value,
                    'status': node.status.value,
                    'utilization': node.overall_utilization,
                    'latency_ms': node.latency_ms,
                    'throughput_rps': node.throughput_rps
                })
        
        return {
            'deployment': deployment.to_dict(),
            'node_performances': node_performances,
            'overall_health': 'healthy' if all(
                p['utilization'] < 80 and p['latency_ms'] < 100
                for p in node_performances
            ) else 'degraded'
        }
    
    async def get_global_edge_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics globales edge"""
        
        # Statistiques par région
        region_stats = {}
        for region in EdgeRegion:
            nodes = [self.edge_nodes[nid] for nid in self.nodes_by_region[region]]
            active_nodes = [n for n in nodes if n.status == EdgeNodeStatus.ACTIVE]
            
            region_stats[region.value] = {
                'total_nodes': len(nodes),
                'active_nodes': len(active_nodes),
                'total_capacity_cpu': sum(n.capacity_cpu for n in nodes),
                'used_capacity_cpu': sum(n.used_cpu for n in nodes),
                'avg_latency_ms': np.mean([n.latency_ms for n in active_nodes]) if active_nodes else 0,
                'total_throughput_rps': sum(n.throughput_rps for n in active_nodes),
                'avg_utilization': np.mean([n.overall_utilization for n in active_nodes]) if active_nodes else 0
            }
        
        # Performances globales
        all_active_nodes = [n for n in self.edge_nodes.values() if n.status == EdgeNodeStatus.ACTIVE]
        
        global_stats = {
            'total_nodes': len(self.edge_nodes),
            'active_nodes': len(all_active_nodes),
            'total_deployments': len(self.deployments),
            'successful_deployments': len([d for d in self.deployments.values() if d.status == "deployed"]),
            'avg_global_latency_ms': np.mean([n.latency_ms for n in all_active_nodes]) if all_active_nodes else 0,
            'total_global_throughput_rps': sum(n.throughput_rps for n in all_active_nodes),
            'avg_global_utilization': np.mean([n.overall_utilization for n in all_active_nodes]) if all_active_nodes else 0
        }
        
        # Analyse des patterns de créateurs
        creator_analytics = {}
        for creator_type in ['musician', 'blogger', 'photographer', 'influencer']:
            creator_deployments = [
                d for d in self.deployments.values()
                if creator_type in d.creator_types
            ]
            
            creator_analytics[creator_type] = {
                'total_deployments': len(creator_deployments),
                'preferred_regions': self.creator_region_preferences.get(creator_type, []),
                'avg_deployment_regions': np.mean([
                    len(d.target_regions) for d in creator_deployments
                ]) if creator_deployments else 0
            }
        
        return {
            'global': global_stats,
            'regions': region_stats,
            'creators': creator_analytics,
            'performance_trends': {
                'latency_trend': 'improving',  # À calculer avec l'historique
                'throughput_trend': 'stable',
                'utilization_trend': 'increasing'
            }
        }

# Usage Example
async def main():
    """Exemple d'utilisation du Edge Deployment Manager"""
    
    manager = EdgeDeploymentManager(
        default_strategy=DeploymentStrategy.LATENCY_OPTIMIZED,
        enable_auto_scaling=True
    )
    
    # Enregistrer des nœuds edge
    node_us = await manager.register_edge_node(
        region=EdgeRegion.US_EAST,
        endpoint_url="https://edge-us-east.ainflue.com",
        capacity_cpu=8.0,
        capacity_memory_gb=32.0,
        capacity_storage_gb=500.0
    )
    
    node_eu = await manager.register_edge_node(
        region=EdgeRegion.EU_WEST,
        endpoint_url="https://edge-eu-west.ainflue.com",
        capacity_cpu=8.0,
        capacity_memory_gb=32.0,
        capacity_storage_gb=500.0
    )
    
    # Déployer un modèle
    deployment_id = await manager.deploy_model_to_edge(
        model_id="content_classifier_v2",
        model_version="2.1.0",
        creator_types=["musician", "blogger"],
        strategy=DeploymentStrategy.CREATOR_PROXIMITY,
        performance_requirements={
            'max_latency_ms': 50,
            'min_throughput_rps': 200
        }
    )
    
    print(f"Deployment created: {deployment_id}")
    
    # Simuler des métriques
    await manager.update_node_metrics(node_us, {
        'latency_ms': 35,
        'throughput_rps': 250,
        'cpu_usage': 4.5,
        'memory_usage_gb': 18.0,
        'performance_metrics': {
            'latency_p50': 30,
            'latency_p95': 45,
            'latency_p99': 55,
            'error_rate': 0.01,
            'request_count': 1000,
            'creator_distribution': {'musician': 600, 'blogger': 400}
        }
    })
    
    # Statut du déploiement
    status = await manager.get_deployment_status(deployment_id)
    print(f"Deployment status: {status}")
    
    # Analytics globales
    analytics = await manager.get_global_edge_analytics()
    print(f"Global analytics: {analytics['global']}")

if __name__ == "__main__":
    asyncio.run(main())