"""🔄 Sharding Controller - Horizontal Database Scaling Management
================================================================

Enterprise sharding with intelligent data distribution, consistent hashing,
and automated scaling for horizontal database partitioning.

Expert Roles Implementation:
🗄️ DBA Senior: Sharding strategies + data distribution + partition management
🏗️ Backend Senior: Shard routing + query distribution + service integration
🔗 Microservices: Multi-tenant sharding + service-specific partitioning
⚡ Performance: Shard balancing + performance monitoring + optimization
🤖 Lead Dev IA: Intelligent shard selection + predictive scaling + auto-balancing

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0 Enterprise Production
Date: December 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture sharding controller est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import hashlib
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import math
import zlib

logger = logging.getLogger(__name__)

class ShardingStrategy(Enum):
    """Stratégies de sharding supportées."""
    RANGE_BASED = "range_based"
    HASH_BASED = "hash_based"
    DIRECTORY_BASED = "directory_based"
    CONSISTENT_HASH = "consistent_hash"
    HYBRID = "hybrid"

class ShardState(Enum):
    """États des shards."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MIGRATING = "migrating"
    SPLITTING = "splitting"
    MERGING = "merging"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class RebalancingTrigger(Enum):
    """Déclencheurs de rééquilibrage."""
    SIZE_THRESHOLD = "size_threshold"
    LOAD_THRESHOLD = "load_threshold"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

class DataDistributionMethod(Enum):
    """Méthodes de distribution des données."""
    ROUND_ROBIN = "round_robin"
    CONSISTENT_HASHING = "consistent_hashing"
    RANGE_PARTITIONING = "range_partitioning"
    HASH_PARTITIONING = "hash_partitioning"
    CUSTOM = "custom"

@dataclass
class ShardConfiguration:
    """Configuration d'un shard."""
    shard_id: str
    host: str
    port: int
    database: str
    weight: float = 1.0
    max_connections: int = 100
    read_only: bool = False
    priority: int = 1
    region: str = "default"
    rack: str = "default"

@dataclass
class ShardKeyMapping:
    """Mapping des clés de sharding."""
    table_name: str
    shard_key_columns: List[str]
    sharding_strategy: ShardingStrategy
    distribution_method: DataDistributionMethod
    shard_count: int
    replication_factor: int = 1

@dataclass
class ShardMetrics:
    """Métriques de performance d'un shard."""
    shard_id: str
    state: ShardState
    row_count: int
    size_mb: float
    read_ops_per_sec: float
    write_ops_per_sec: float
    avg_response_time: float
    cpu_utilization: float
    memory_utilization: float
    disk_utilization: float
    connection_count: int
    last_updated: datetime
    health_score: float

@dataclass
class RebalancingPlan:
    """Plan de rééquilibrage des shards."""
    plan_id: str
    trigger: RebalancingTrigger
    affected_shards: List[str]
    data_movement: List[Dict[str, Any]]
    estimated_duration: int
    estimated_downtime: int
    risk_level: str
    rollback_strategy: str

@dataclass
class QueryRoutingInfo:
    """Information de routage pour une requête."""
    query_hash: str
    target_shards: List[str]
    routing_strategy: str
    cross_shard_required: bool
    estimated_cost: float

class ConsistentHashRing:
    """🔄 Anneau de hachage cohérent pour la distribution."""
    
    def __init__(self, virtual_nodes: int = 150):
        """Initialise l'anneau de hachage."""
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.nodes: Set[str] = set()
        
    def add_node(self, node_id: str, weight: float = 1.0) -> None:
        """Ajoute un nœud à l'anneau."""
        self.nodes.add(node_id)
        
        # Calcul du nombre de nœuds virtuels basé sur le poids
        virtual_count = int(self.virtual_nodes * weight)
        
        for i in range(virtual_count):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node_id
        
        logger.debug(f"Node {node_id} added to ring with {virtual_count} virtual nodes")
    
    def remove_node(self, node_id: str) -> None:
        """Supprime un nœud de l'anneau."""
        if node_id not in self.nodes:
            return
            
        self.nodes.discard(node_id)
        
        # Supprime tous les nœuds virtuels
        keys_to_remove = [k for k, v in self.ring.items() if v == node_id]
        for key in keys_to_remove:
            del self.ring[key]
        
        logger.debug(f"Node {node_id} removed from ring")
    
    def get_node(self, key: str) -> Optional[str]:
        """Trouve le nœud responsable d'une clé."""
        if not self.ring:
            return None
            
        hash_value = self._hash(key)
        
        # Trouve le premier nœud dans le sens horaire
        for ring_key in sorted(self.ring.keys()):
            if ring_key >= hash_value:
                return self.ring[ring_key]
        
        # Si aucun nœud trouvé, prend le premier de l'anneau
        return self.ring[min(self.ring.keys())]
    
    def get_nodes(self, key: str, count: int) -> List[str]:
        """Obtient plusieurs nœuds pour la réplication."""
        if not self.ring or count <= 0:
            return []
            
        hash_value = self._hash(key)
        nodes = []
        seen = set()
        
        sorted_keys = sorted(self.ring.keys())
        start_idx = 0
        
        # Trouve l'index de départ
        for i, ring_key in enumerate(sorted_keys):
            if ring_key >= hash_value:
                start_idx = i
                break
        
        # Collecte les nœuds uniques
        for i in range(len(sorted_keys)):
            idx = (start_idx + i) % len(sorted_keys)
            node = self.ring[sorted_keys[idx]]
            
            if node not in seen:
                nodes.append(node)
                seen.add(node)
                
                if len(nodes) >= count:
                    break
        
        return nodes
    
    def _hash(self, key: str) -> int:
        """Calcule le hash d'une clé."""
        return zlib.crc32(key.encode()) & 0xffffffff


class ShardingController:
    """🔄 Contrôleur principal de sharding avec intelligence artificielle."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le contrôleur de sharding."""
        self.config = config or {}
        
        # Configuration
        self.default_strategy = ShardingStrategy(
            self.config.get("default_strategy", "consistent_hash")
        )
        self.auto_rebalancing = self.config.get("auto_rebalancing", True)
        self.rebalancing_threshold = self.config.get("rebalancing_threshold", 0.2)
        
        # État des shards
        self.shards: Dict[str, ShardConfiguration] = {}
        self.shard_metrics: Dict[str, ShardMetrics] = {}
        self.shard_mappings: Dict[str, ShardKeyMapping] = {}
        
        # Routing
        self.hash_ring = ConsistentHashRing()
        self.query_routing_cache: Dict[str, QueryRoutingInfo] = {}
        
        # Monitoring
        self.performance_history: deque = deque(maxlen=1000)
        self.rebalancing_history: List[RebalancingPlan] = []
        
        # Statistics
        self.stats = {
            "total_queries_routed": 0,
            "cross_shard_queries": 0,
            "rebalancing_operations": 0,
            "avg_routing_time": 0.0
        }
        
        logger.info("Sharding Controller initialized with intelligent distribution")

    async def register_shard(self, shard_config: ShardConfiguration) -> bool:
        """📍 Enregistre un nouveau shard dans le cluster."""
        try:
            # Validate shard configuration
            if not await self._validate_shard_config(shard_config):
                return False
            
            # Add to shard registry
            self.shards[shard_config.shard_id] = shard_config
            
            # Add to consistent hash ring
            self.hash_ring.add_node(shard_config.shard_id, shard_config.weight)
            
            # Initialize metrics
            self.shard_metrics[shard_config.shard_id] = ShardMetrics(
                shard_id=shard_config.shard_id,
                state=ShardState.ACTIVE,
                row_count=0,
                size_mb=0.0,
                read_ops_per_sec=0.0,
                write_ops_per_sec=0.0,
                avg_response_time=0.0,
                cpu_utilization=0.0,
                memory_utilization=0.0,
                disk_utilization=0.0,
                connection_count=0,
                last_updated=datetime.now(),
                health_score=1.0
            )
            
            logger.info(f"Shard registered: {shard_config.shard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register shard {shard_config.shard_id}: {str(e)}")
            return False

    async def configure_table_sharding(self, mapping: ShardKeyMapping) -> bool:
        """🗂️ Configure le sharding pour une table."""
        try:
            # Validate mapping
            if not await self._validate_shard_mapping(mapping):
                return False
            
            # Store mapping
            self.shard_mappings[mapping.table_name] = mapping
            
            # Initialize table distribution if needed
            await self._initialize_table_distribution(mapping)
            
            logger.info(f"Table sharding configured: {mapping.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure sharding for {mapping.table_name}: {str(e)}")
            return False

    async def route_query(self, 
                         table_name: str, 
                         query: str, 
                         shard_key_values: Optional[Dict[str, Any]] = None) -> QueryRoutingInfo:
        """🎯 Route une requête vers les shards appropriés."""
        start_time = time.time()
        
        try:
            # Get shard mapping
            if table_name not in self.shard_mappings:
                raise ValueError(f"No sharding configuration for table: {table_name}")
            
            mapping = self.shard_mappings[table_name]
            
            # Generate query hash for caching
            query_hash = hashlib.md5(f"{table_name}:{query}".encode()).hexdigest()[:16]
            
            # Check cache
            if query_hash in self.query_routing_cache:
                cached_info = self.query_routing_cache[query_hash]
                # Validate cached info is still valid
                if await self._validate_routing_cache(cached_info):
                    return cached_info
            
            # Determine target shards
            target_shards = await self._determine_target_shards(mapping, query, shard_key_values)
            
            # Create routing info
            routing_info = QueryRoutingInfo(
                query_hash=query_hash,
                target_shards=target_shards,
                routing_strategy=mapping.sharding_strategy.value,
                cross_shard_required=len(target_shards) > 1,
                estimated_cost=self._estimate_query_cost(target_shards, query)
            )
            
            # Cache routing info
            self.query_routing_cache[query_hash] = routing_info
            
            # Update statistics
            self.stats["total_queries_routed"] += 1
            if routing_info.cross_shard_required:
                self.stats["cross_shard_queries"] += 1
            
            routing_time = time.time() - start_time
            self.stats["avg_routing_time"] = (
                (self.stats["avg_routing_time"] * (self.stats["total_queries_routed"] - 1) + routing_time) /
                self.stats["total_queries_routed"]
            )
            
            return routing_info
            
        except Exception as e:
            logger.error(f"Query routing failed: {str(e)}")
            raise

    async def update_shard_metrics(self, shard_id: str, metrics_data: Dict[str, Any]) -> None:
        """📊 Met à jour les métriques d'un shard."""
        if shard_id not in self.shard_metrics:
            logger.warning(f"Unknown shard ID: {shard_id}")
            return
        
        metrics = self.shard_metrics[shard_id]
        
        # Update metrics
        metrics.row_count = metrics_data.get("row_count", metrics.row_count)
        metrics.size_mb = metrics_data.get("size_mb", metrics.size_mb)
        metrics.read_ops_per_sec = metrics_data.get("read_ops_per_sec", metrics.read_ops_per_sec)
        metrics.write_ops_per_sec = metrics_data.get("write_ops_per_sec", metrics.write_ops_per_sec)
        metrics.avg_response_time = metrics_data.get("avg_response_time", metrics.avg_response_time)
        metrics.cpu_utilization = metrics_data.get("cpu_utilization", metrics.cpu_utilization)
        metrics.memory_utilization = metrics_data.get("memory_utilization", metrics.memory_utilization)
        metrics.disk_utilization = metrics_data.get("disk_utilization", metrics.disk_utilization)
        metrics.connection_count = metrics_data.get("connection_count", metrics.connection_count)
        metrics.last_updated = datetime.now()
        
        # Calculate health score
        metrics.health_score = self._calculate_shard_health_score(metrics)
        
        # Store in performance history
        self.performance_history.append({
            "timestamp": datetime.now(),
            "shard_id": shard_id,
            "metrics": metrics_data
        })
        
        # Check if rebalancing is needed
        if self.auto_rebalancing:
            await self._check_rebalancing_trigger(shard_id, metrics)

    async def create_rebalancing_plan(self, 
                                    trigger: RebalancingTrigger,
                                    target_shards: Optional[List[str]] = None) -> RebalancingPlan:
        """⚖️ Crée un plan de rééquilibrage intelligent."""
        plan_id = f"rebalance_{int(time.time())}"
        
        # Analyze current shard distribution
        distribution_analysis = await self._analyze_shard_distribution()
        
        # Identify overloaded and underloaded shards
        overloaded_shards = distribution_analysis["overloaded_shards"]
        underloaded_shards = distribution_analysis["underloaded_shards"]
        
        if not overloaded_shards:
            logger.info("No rebalancing needed - cluster is balanced")
            return None
        
        # Generate data movement plan
        data_movement = await self._generate_data_movement_plan(
            overloaded_shards, underloaded_shards
        )
        
        # Estimate duration and risk
        duration_estimate = self._estimate_rebalancing_duration(data_movement)
        downtime_estimate = self._estimate_downtime(data_movement)
        risk_level = self._assess_rebalancing_risk(data_movement)
        
        plan = RebalancingPlan(
            plan_id=plan_id,
            trigger=trigger,
            affected_shards=list(set(overloaded_shards + underloaded_shards)),
            data_movement=data_movement,
            estimated_duration=duration_estimate,
            estimated_downtime=downtime_estimate,
            risk_level=risk_level,
            rollback_strategy=self._create_rollback_strategy(data_movement)
        )
        
        self.rebalancing_history.append(plan)
        
        logger.info(f"Rebalancing plan created: {plan_id}")
        return plan

    async def execute_rebalancing_plan(self, plan: RebalancingPlan) -> Dict[str, Any]:
        """🚀 Exécute un plan de rééquilibrage."""
        execution_result = {
            "plan_id": plan.plan_id,
            "status": "started",
            "progress": 0,
            "completed_movements": [],
            "failed_movements": [],
            "start_time": datetime.now(),
            "estimated_completion": datetime.now() + timedelta(minutes=plan.estimated_duration)
        }
        
        try:
            logger.info(f"Starting rebalancing plan: {plan.plan_id}")
            
            # Execute data movements sequentially
            for i, movement in enumerate(plan.data_movement):
                try:
                    await self._execute_data_movement(movement)
                    execution_result["completed_movements"].append(movement)
                    
                    # Update progress
                    execution_result["progress"] = (i + 1) / len(plan.data_movement) * 100
                    
                    logger.debug(f"Completed movement {i+1}/{len(plan.data_movement)}")
                    
                except Exception as e:
                    logger.error(f"Data movement failed: {str(e)}")
                    execution_result["failed_movements"].append({
                        "movement": movement,
                        "error": str(e)
                    })
            
            # Update statistics
            self.stats["rebalancing_operations"] += 1
            
            execution_result["status"] = "completed"
            execution_result["end_time"] = datetime.now()
            
            logger.info(f"Rebalancing plan completed: {plan.plan_id}")
            
        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["error"] = str(e)
            logger.error(f"Rebalancing plan failed: {str(e)}")
        
        return execution_result

    async def get_cluster_status(self) -> Dict[str, Any]:
        """📊 Retourne le statut complet du cluster."""
        total_shards = len(self.shards)
        active_shards = len([s for s in self.shard_metrics.values() 
                           if s.state == ShardState.ACTIVE])
        
        # Calculate cluster metrics
        if self.shard_metrics:
            total_size = sum(m.size_mb for m in self.shard_metrics.values())
            total_rows = sum(m.row_count for m in self.shard_metrics.values())
            avg_health = statistics.mean([m.health_score for m in self.shard_metrics.values()])
            avg_response_time = statistics.mean([m.avg_response_time for m in self.shard_metrics.values()])
        else:
            total_size = total_rows = avg_health = avg_response_time = 0
        
        # Distribution balance
        distribution_balance = await self._calculate_distribution_balance()
        
        status = {
            "cluster_summary": {
                "total_shards": total_shards,
                "active_shards": active_shards,
                "total_size_mb": total_size,
                "total_rows": total_rows,
                "avg_health_score": avg_health,
                "avg_response_time": avg_response_time,
                "distribution_balance": distribution_balance
            },
            "shard_details": [
                {
                    "shard_id": shard_id,
                    "state": metrics.state.value,
                    "size_mb": metrics.size_mb,
                    "row_count": metrics.row_count,
                    "health_score": metrics.health_score,
                    "utilization": {
                        "cpu": metrics.cpu_utilization,
                        "memory": metrics.memory_utilization,
                        "disk": metrics.disk_utilization
                    }
                }
                for shard_id, metrics in self.shard_metrics.items()
            ],
            "performance_stats": self.stats.copy(),
            "sharding_config": {
                "tables": list(self.shard_mappings.keys()),
                "default_strategy": self.default_strategy.value,
                "auto_rebalancing": self.auto_rebalancing
            }
        }
        
        return status

    # Méthodes privées d'assistance

    async def _validate_shard_config(self, config: ShardConfiguration) -> bool:
        """Valide la configuration d'un shard."""
        if config.shard_id in self.shards:
            logger.error(f"Shard ID already exists: {config.shard_id}")
            return False
        
        if not config.host or not config.port:
            logger.error("Invalid host or port in shard configuration")
            return False
        
        return True

    async def _validate_shard_mapping(self, mapping: ShardKeyMapping) -> bool:
        """Valide une configuration de sharding."""
        if not mapping.shard_key_columns:
            logger.error("Shard key columns cannot be empty")
            return False
        
        if mapping.shard_count <= 0:
            logger.error("Shard count must be positive")
            return False
        
        return True

    async def _initialize_table_distribution(self, mapping: ShardKeyMapping) -> None:
        """Initialise la distribution d'une table."""
        # Implementation would depend on the specific database system
        logger.debug(f"Initializing distribution for table: {mapping.table_name}")

    async def _determine_target_shards(self, 
                                     mapping: ShardKeyMapping,
                                     query: str, 
                                     shard_key_values: Optional[Dict[str, Any]]) -> List[str]:
        """Détermine les shards cibles pour une requête."""
        if mapping.sharding_strategy == ShardingStrategy.CONSISTENT_HASH:
            return await self._route_consistent_hash(mapping, shard_key_values)
        elif mapping.sharding_strategy == ShardingStrategy.RANGE_BASED:
            return await self._route_range_based(mapping, shard_key_values)
        elif mapping.sharding_strategy == ShardingStrategy.HASH_BASED:
            return await self._route_hash_based(mapping, shard_key_values)
        else:
            # Default: broadcast to all shards
            return list(self.shards.keys())

    async def _route_consistent_hash(self, 
                                   mapping: ShardKeyMapping,
                                   shard_key_values: Optional[Dict[str, Any]]) -> List[str]:
        """Route avec hachage cohérent."""
        if not shard_key_values:
            return list(self.shards.keys())  # Broadcast
        
        # Build shard key
        key_parts = []
        for column in mapping.shard_key_columns:
            if column in shard_key_values:
                key_parts.append(str(shard_key_values[column]))
        
        if not key_parts:
            return list(self.shards.keys())  # Broadcast
        
        shard_key = ":".join(key_parts)
        
        # Get target shards for replication
        target_shards = self.hash_ring.get_nodes(shard_key, mapping.replication_factor)
        
        return target_shards or list(self.shards.keys())[:1]

    async def _route_range_based(self, 
                               mapping: ShardKeyMapping,
                               shard_key_values: Optional[Dict[str, Any]]) -> List[str]:
        """Route basé sur les plages."""
        # Simplified implementation - would need range configuration
        if not shard_key_values:
            return list(self.shards.keys())
        
        # For demonstration, use hash of first shard key column
        if mapping.shard_key_columns and mapping.shard_key_columns[0] in shard_key_values:
            value = shard_key_values[mapping.shard_key_columns[0]]
            shard_index = hash(str(value)) % len(self.shards)
            return [list(self.shards.keys())[shard_index]]
        
        return list(self.shards.keys())

    async def _route_hash_based(self, 
                              mapping: ShardKeyMapping,
                              shard_key_values: Optional[Dict[str, Any]]) -> List[str]:
        """Route basé sur le hachage simple."""
        if not shard_key_values:
            return list(self.shards.keys())
        
        # Build hash from shard key values
        key_parts = []
        for column in mapping.shard_key_columns:
            if column in shard_key_values:
                key_parts.append(str(shard_key_values[column]))
        
        if key_parts:
            hash_value = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            shard_index = int(hash_value, 16) % len(self.shards)
            return [list(self.shards.keys())[shard_index]]
        
        return list(self.shards.keys())

    async def _validate_routing_cache(self, routing_info: QueryRoutingInfo) -> bool:
        """Valide si les informations de routage en cache sont toujours valides."""
        # Check if target shards still exist and are active
        for shard_id in routing_info.target_shards:
            if shard_id not in self.shards:
                return False
            if (shard_id in self.shard_metrics and 
                self.shard_metrics[shard_id].state != ShardState.ACTIVE):
                return False
        
        return True

    def _estimate_query_cost(self, target_shards: List[str], query: str) -> float:
        """Estime le coût d'une requête."""
        # Simplified cost estimation
        base_cost = 1.0
        
        # Cross-shard queries are more expensive
        if len(target_shards) > 1:
            base_cost *= 2.0
        
        # Complex queries (joins, aggregations) are more expensive
        query_lower = query.lower()
        if 'join' in query_lower:
            base_cost *= 1.5
        if any(agg in query_lower for agg in ['group by', 'order by', 'count(', 'sum(']):
            base_cost *= 1.3
        
        return base_cost

    def _calculate_shard_health_score(self, metrics: ShardMetrics) -> float:
        """Calcule le score de santé d'un shard."""
        score = 1.0
        
        # CPU utilization impact
        if metrics.cpu_utilization > 80:
            score -= 0.3
        elif metrics.cpu_utilization > 60:
            score -= 0.1
        
        # Memory utilization impact
        if metrics.memory_utilization > 90:
            score -= 0.3
        elif metrics.memory_utilization > 70:
            score -= 0.1
        
        # Response time impact
        if metrics.avg_response_time > 1000:  # >1 second
            score -= 0.2
        elif metrics.avg_response_time > 500:  # >0.5 second
            score -= 0.1
        
        return max(0.0, score)

    async def _check_rebalancing_trigger(self, shard_id: str, metrics: ShardMetrics) -> None:
        """Vérifie si un rééquilibrage est nécessaire."""
        # Check various trigger conditions
        triggers = []
        
        # Size-based trigger
        if metrics.size_mb > self.config.get("max_shard_size_mb", 10000):
            triggers.append(RebalancingTrigger.SIZE_THRESHOLD)
        
        # Load-based trigger
        if (metrics.cpu_utilization > 80 or 
            metrics.memory_utilization > 90 or
            metrics.read_ops_per_sec + metrics.write_ops_per_sec > 1000):
            triggers.append(RebalancingTrigger.LOAD_THRESHOLD)
        
        # Performance degradation trigger
        if metrics.avg_response_time > 1000:  # >1 second
            triggers.append(RebalancingTrigger.PERFORMANCE_DEGRADATION)
        
        # Trigger rebalancing if conditions are met
        if triggers and self.auto_rebalancing:
            logger.info(f"Rebalancing triggered for shard {shard_id}: {triggers}")
            await self.create_rebalancing_plan(triggers[0], [shard_id])

    async def _analyze_shard_distribution(self) -> Dict[str, Any]:
        """Analyse la distribution actuelle des shards."""
        if not self.shard_metrics:
            return {"overloaded_shards": [], "underloaded_shards": [], "balance_score": 1.0}
        
        # Calculate average metrics
        avg_size = statistics.mean([m.size_mb for m in self.shard_metrics.values()])
        avg_load = statistics.mean([
            m.read_ops_per_sec + m.write_ops_per_sec 
            for m in self.shard_metrics.values()
        ])
        
        overloaded_shards = []
        underloaded_shards = []
        
        for shard_id, metrics in self.shard_metrics.items():
            load = metrics.read_ops_per_sec + metrics.write_ops_per_sec
            
            # Check if overloaded
            if (metrics.size_mb > avg_size * (1 + self.rebalancing_threshold) or
                load > avg_load * (1 + self.rebalancing_threshold)):
                overloaded_shards.append(shard_id)
            
            # Check if underloaded
            elif (metrics.size_mb < avg_size * (1 - self.rebalancing_threshold) and
                  load < avg_load * (1 - self.rebalancing_threshold)):
                underloaded_shards.append(shard_id)
        
        # Calculate balance score
        size_variance = statistics.variance([m.size_mb for m in self.shard_metrics.values()])
        balance_score = 1.0 / (1.0 + size_variance / max(1, avg_size))
        
        return {
            "overloaded_shards": overloaded_shards,
            "underloaded_shards": underloaded_shards,
            "balance_score": balance_score,
            "avg_size_mb": avg_size,
            "avg_load": avg_load
        }

    async def _generate_data_movement_plan(self, 
                                         overloaded_shards: List[str],
                                         underloaded_shards: List[str]) -> List[Dict[str, Any]]:
        """Génère un plan de mouvement de données."""
        movement_plan = []
        
        for overloaded_shard in overloaded_shards:
            if not underloaded_shards:
                break
                
            source_metrics = self.shard_metrics[overloaded_shard]
            target_shard = underloaded_shards[0]  # Simple selection
            
            # Calculate how much data to move
            avg_size = statistics.mean([m.size_mb for m in self.shard_metrics.values()])
            excess_data = source_metrics.size_mb - avg_size
            move_amount = min(excess_data * 0.5, source_metrics.size_mb * 0.3)
            
            if move_amount > 100:  # Only move if significant amount
                movement = {
                    "source_shard": overloaded_shard,
                    "target_shard": target_shard,
                    "estimated_data_mb": move_amount,
                    "estimated_rows": int(move_amount / source_metrics.size_mb * source_metrics.row_count),
                    "method": "hot_migration",
                    "priority": "normal"
                }
                movement_plan.append(movement)
        
        return movement_plan

    def _estimate_rebalancing_duration(self, data_movement: List[Dict[str, Any]]) -> int:
        """Estime la durée de rééquilibrage en minutes."""
        total_data_mb = sum(m["estimated_data_mb"] for m in data_movement)
        
        # Estimate based on data transfer rate (simplified)
        transfer_rate_mb_per_min = 1000  # 1GB per minute
        duration = max(30, int(total_data_mb / transfer_rate_mb_per_min))
        
        return duration

    def _estimate_downtime(self, data_movement: List[Dict[str, Any]]) -> int:
        """Estime le temps d'arrêt nécessaire."""
        # Most operations can be done online
        return 5  # 5 minutes for coordination

    def _assess_rebalancing_risk(self, data_movement: List[Dict[str, Any]]) -> str:
        """Évalue le risque du rééquilibrage."""
        total_movements = len(data_movement)
        total_data = sum(m["estimated_data_mb"] for m in data_movement)
        
        if total_movements > 5 or total_data > 50000:  # >50GB
            return "high"
        elif total_movements > 2 or total_data > 10000:  # >10GB
            return "medium"
        else:
            return "low"

    def _create_rollback_strategy(self, data_movement: List[Dict[str, Any]]) -> str:
        """Crée une stratégie de rollback."""
        return "Reverse data movements in case of failure, restore from backup if needed"

    async def _execute_data_movement(self, movement: Dict[str, Any]) -> None:
        """Exécute un mouvement de données."""
        # This would implement the actual data movement logic
        # For demonstration, we'll simulate the operation
        logger.info(f"Simulating data movement: {movement['estimated_data_mb']}MB "
                   f"from {movement['source_shard']} to {movement['target_shard']}")
        
        # Simulate some work
        await asyncio.sleep(1)

    async def _calculate_distribution_balance(self) -> float:
        """Calcule l'équilibre de distribution du cluster."""
        if not self.shard_metrics:
            return 1.0
        
        sizes = [m.size_mb for m in self.shard_metrics.values()]
        
        if not sizes or max(sizes) == 0:
            return 1.0
        
        # Calculate coefficient of variation
        mean_size = statistics.mean(sizes)
        if mean_size == 0:
            return 1.0
        
        std_dev = statistics.stdev(sizes) if len(sizes) > 1 else 0
        cv = std_dev / mean_size
        
        # Convert to balance score (1 = perfectly balanced, 0 = completely unbalanced)
        balance = 1.0 / (1.0 + cv)
        
        return balance


# Fonction d'initialisation
async def initialize_sharding_controller(config: Optional[Dict[str, Any]] = None) -> ShardingController:
    """🚀 Initialise le contrôleur de sharding."""
    controller = ShardingController(config)
    logger.info("Sharding Controller ready for enterprise horizontal scaling")
    return controller


# Export des classes principales
__all__ = [
    "ShardingController",
    "ConsistentHashRing",
    "ShardConfiguration",
    "ShardKeyMapping",
    "ShardMetrics",
    "RebalancingPlan",
    "QueryRoutingInfo",
    "ShardingStrategy",
    "ShardState",
    "RebalancingTrigger",
    "DataDistributionMethod",
    "initialize_sharding_controller"
]