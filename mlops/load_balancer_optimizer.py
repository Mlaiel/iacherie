"""
⚖️ Load Balancer Optimizer Enterprise
MLOps Platform - Optimiseur de load balancer avec algorithmes ML-aware

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute tentative de vol, copie, reproduction, ingénierie inverse ou utilisation non autorisée
sans permission écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement interdite
et entraînera immédiatement des poursuites judiciaires sous le droit allemand et international.
"""

import asyncio
import json
import logging
import time
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import numpy as np
from scipy import optimize
import aiohttp

# Enterprise Monitoring & Security
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge, Summary

@dataclass
class ServerInstance:
    """Instance de serveur pour load balancing"""
    instance_id: str
    endpoint_url: str
    region: str
    model_types: List[str]
    current_load: float  # 0.0 to 1.0
    capacity: Dict[str, float]  # CPU, memory, requests/sec
    health_score: float  # 0.0 to 1.0
    latency_p95: float  # milliseconds
    active_connections: int
    total_requests: int
    error_rate: float  # 0.0 to 1.0
    last_updated: datetime

@dataclass 
class LoadBalancingRule:
    """Règle de load balancing"""
    rule_id: str
    model_type: str
    creator_type: str
    algorithm: str  # weighted_round_robin, least_connections, ml_optimized
    weights: Dict[str, float]
    priority: int
    active: bool = True

class BalancingAlgorithm(Enum):
    """Algorithmes de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    ML_OPTIMIZED = "ml_optimized"
    CREATOR_AWARE = "creator_aware"
    GEOGRAPHIC = "geographic"

class LoadBalancerOptimizer:
    """
    ⚖️ Optimiseur de load balancer enterprise avec algorithmes ML-aware
    
    Features Enterprise:
    - ML-powered intelligent request routing
    - Creator-specific optimization algorithms
    - Real-time performance adaptation
    - Multi-region global optimization
    - Predictive load balancing with traffic forecasting
    - Advanced health scoring with anomaly detection
    - Cost-optimized resource allocation
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, ServerInstance] = {}
        self.load_balancing_rules: Dict[str, LoadBalancingRule] = {}
        self.request_history: deque = deque(maxlen=10000)
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # ML Models for optimization
        self.traffic_predictor = None
        self.performance_predictor = None
        self.weights_optimizer = None
        
        # Prometheus Metrics
        self.requests_counter = Counter('lb_requests_total', 'Total requests', ['server_id', 'model_type', 'creator_type'])
        self.response_time_histogram = Histogram('lb_response_time_seconds', 'Response time', ['server_id', 'algorithm'])
        self.server_load_gauge = Gauge('lb_server_load', 'Server load %', ['server_id', 'region'])
        self.algorithm_performance = Summary('lb_algorithm_performance', 'Algorithm performance score', ['algorithm'])
        self.routing_decisions = Counter('lb_routing_decisions', 'Routing decisions', ['algorithm', 'reason'])
        
        # Configuration
        self.config = config or {
            "optimization_interval": 60,  # seconds
            "health_check_interval": 30,
            "ml_optimization_enabled": True,
            "traffic_prediction_enabled": True,
            "performance_history_size": 1000,
            "routing_cache_ttl": 300,
            "cost_optimization_enabled": True,
            "geographic_optimization": True
        }
        
        # ML-based routing cache
        self.routing_cache: Dict[str, Tuple[str, float]] = {}  # request_signature -> (server_id, timestamp)
        
        # Traffic patterns for prediction
        self.traffic_patterns: Dict[str, List[float]] = defaultdict(list)
        self.seasonal_patterns: Dict[str, Dict] = {}
        
        # Cost optimization factors
        self.cost_factors = {
            "cpu_cost_per_hour": 0.10,
            "memory_cost_per_gb_hour": 0.02,
            "bandwidth_cost_per_gb": 0.05,
            "regional_cost_multipliers": {
                "us-west": 1.0,
                "us-east": 0.95,
                "europe": 1.1,
                "asia": 0.9
            }
        }
        
        self.logger.info("⚖️ Load Balancer Optimizer initialized with ML capabilities")

    async def initialize(self) -> bool:
        """Initialize le load balancer optimizer"""
        try:
            self.logger.info("🚀 Initializing Load Balancer Optimizer...")
            
            # Initialize default load balancing rules
            await self._setup_default_rules()
            
            # Start background optimization tasks
            asyncio.create_task(self._optimization_loop())
            asyncio.create_task(self._health_monitoring_loop())
            asyncio.create_task(self._ml_training_loop())
            
            # Initialize ML models if enabled
            if self.config["ml_optimization_enabled"]:
                await self._initialize_ml_models()
            
            self.logger.info("✅ Load Balancer Optimizer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize load balancer optimizer: {e}")
            return False

    async def register_server(self, server_instance: ServerInstance) -> bool:
        """Register un nouveau serveur dans le load balancer"""
        try:
            self.servers[server_instance.instance_id] = server_instance
            
            # Update metrics
            self.server_load_gauge.labels(
                server_id=server_instance.instance_id,
                region=server_instance.region
            ).set(server_instance.current_load * 100)
            
            self.logger.info(f"✅ Registered server {server_instance.instance_id} in region {server_instance.region}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register server {server_instance.instance_id}: {e}")
            return False

    async def route_request(
        self,
        request_metadata: Dict[str, Any]
    ) -> Optional[str]:
        """
        Route une requête vers le serveur optimal avec algorithmes ML
        
        Args:
            request_metadata: Métadonnées de la requête (model_type, creator_type, région, etc.)
            
        Returns:
            Server instance ID optimal ou None si aucun serveur disponible
        """
        start_time = time.time()
        
        try:
            model_type = request_metadata.get("model_type")
            creator_type = request_metadata.get("creator_type")
            client_region = request_metadata.get("client_region")
            request_priority = request_metadata.get("priority", "normal")
            
            # Check routing cache first
            cache_key = self._generate_cache_key(request_metadata)
            cached_result = self._get_cached_route(cache_key)
            
            if cached_result:
                self.routing_decisions.labels(algorithm='cached', reason='cache_hit').inc()
                return cached_result
            
            # Get applicable load balancing rule
            rule = await self._get_applicable_rule(model_type, creator_type)
            
            if not rule:
                self.logger.warning(f"⚠️ No applicable load balancing rule found for {model_type}/{creator_type}")
                return None
            
            # Get candidate servers
            candidate_servers = await self._get_candidate_servers(model_type, client_region)
            
            if not candidate_servers:
                self.logger.warning(f"⚠️ No healthy servers available for {model_type}")
                return None
            
            # Apply load balancing algorithm
            selected_server = await self._apply_balancing_algorithm(
                rule.algorithm,
                candidate_servers,
                request_metadata,
                rule.weights
            )
            
            if selected_server:
                # Cache the routing decision
                self._cache_route(cache_key, selected_server)
                
                # Update server load and metrics
                await self._update_server_metrics(selected_server, request_metadata)
                
                # Record routing decision
                self.routing_decisions.labels(
                    algorithm=rule.algorithm,
                    reason='algorithm_selection'
                ).inc()
                
                # Log performance
                routing_time = time.time() - start_time
                self.response_time_histogram.labels(
                    server_id=selected_server,
                    algorithm=rule.algorithm
                ).observe(routing_time)
                
                self.logger.debug(f"🎯 Routed request to {selected_server} using {rule.algorithm} in {routing_time:.3f}s")
                
            return selected_server
            
        except Exception as e:
            self.logger.error(f"❌ Request routing failed: {e}")
            return None

    async def _apply_balancing_algorithm(
        self,
        algorithm: str,
        candidate_servers: List[str],
        request_metadata: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Optional[str]:
        """Apply the specified load balancing algorithm"""
        
        if algorithm == BalancingAlgorithm.ROUND_ROBIN.value:
            return await self._round_robin_selection(candidate_servers)
        
        elif algorithm == BalancingAlgorithm.WEIGHTED_ROUND_ROBIN.value:
            return await self._weighted_round_robin_selection(candidate_servers, weights)
        
        elif algorithm == BalancingAlgorithm.LEAST_CONNECTIONS.value:
            return await self._least_connections_selection(candidate_servers)
        
        elif algorithm == BalancingAlgorithm.LEAST_RESPONSE_TIME.value:
            return await self._least_response_time_selection(candidate_servers)
        
        elif algorithm == BalancingAlgorithm.ML_OPTIMIZED.value:
            return await self._ml_optimized_selection(candidate_servers, request_metadata)
        
        elif algorithm == BalancingAlgorithm.CREATOR_AWARE.value:
            return await self._creator_aware_selection(candidate_servers, request_metadata)
        
        elif algorithm == BalancingAlgorithm.GEOGRAPHIC.value:
            return await self._geographic_selection(candidate_servers, request_metadata)
        
        else:
            self.logger.warning(f"⚠️ Unknown algorithm {algorithm}, falling back to round robin")
            return await self._round_robin_selection(candidate_servers)

    async def _round_robin_selection(self, servers: List[str]) -> str:
        """Simple round robin selection"""
        if not hasattr(self, '_rr_counter'):
            self._rr_counter = 0
        
        selected = servers[self._rr_counter % len(servers)]
        self._rr_counter += 1
        return selected

    async def _weighted_round_robin_selection(
        self,
        servers: List[str],
        weights: Dict[str, float]
    ) -> str:
        """Weighted round robin based on server weights"""
        
        weighted_servers = []
        for server_id in servers:
            server = self.servers[server_id]
            weight = weights.get(server_id, 1.0)
            
            # Adjust weight based on current load and health
            adjusted_weight = weight * server.health_score * (1.0 - server.current_load)
            weighted_servers.append((server_id, adjusted_weight))
        
        # Select based on weighted probabilities
        total_weight = sum(weight for _, weight in weighted_servers)
        
        if total_weight == 0:
            return servers[0]  # Fallback
        
        import random
        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        
        for server_id, weight in weighted_servers:
            cumulative += weight
            if rand_val <= cumulative:
                return server_id
        
        return servers[-1]  # Fallback

    async def _least_connections_selection(self, servers: List[str]) -> str:
        """Select server with least active connections"""
        
        min_connections = float('inf')
        selected_server = servers[0]
        
        for server_id in servers:
            server = self.servers[server_id]
            if server.active_connections < min_connections:
                min_connections = server.active_connections
                selected_server = server_id
        
        return selected_server

    async def _least_response_time_selection(self, servers: List[str]) -> str:
        """Select server with lowest response time"""
        
        min_latency = float('inf')
        selected_server = servers[0]
        
        for server_id in servers:
            server = self.servers[server_id]
            # Combine latency with current load for better decision
            effective_latency = server.latency_p95 * (1 + server.current_load)
            
            if effective_latency < min_latency:
                min_latency = effective_latency
                selected_server = server_id
        
        return selected_server

    async def _ml_optimized_selection(
        self,
        servers: List[str],
        request_metadata: Dict[str, Any]
    ) -> str:
        """ML-optimized server selection using predictive models"""
        
        if not self.config["ml_optimization_enabled"]:
            return await self._weighted_round_robin_selection(servers, {})
        
        best_server = servers[0]
        best_score = -1
        
        for server_id in servers:
            server = self.servers[server_id]
            
            # Calculate ML-based optimization score
            score = await self._calculate_ml_score(server, request_metadata)
            
            if score > best_score:
                best_score = score
                best_server = server_id
        
        return best_server

    async def _calculate_ml_score(
        self,
        server: ServerInstance,
        request_metadata: Dict[str, Any]
    ) -> float:
        """Calculate ML-based server selection score"""
        
        # Composite score based on multiple factors
        factors = {
            "performance": self._calculate_performance_score(server),
            "availability": self._calculate_availability_score(server),
            "cost": self._calculate_cost_score(server),
            "affinity": self._calculate_affinity_score(server, request_metadata),
            "predicted_load": await self._predict_server_load(server.instance_id)
        }
        
        # Weighted combination
        weights = {
            "performance": 0.3,
            "availability": 0.25,
            "cost": 0.2,
            "affinity": 0.15,
            "predicted_load": 0.1
        }
        
        score = sum(factors[factor] * weights[factor] for factor in factors)
        return score

    def _calculate_performance_score(self, server: ServerInstance) -> float:
        """Calculate performance score for server"""
        
        # Lower latency and load = higher score
        latency_score = max(0, 1 - (server.latency_p95 / 1000))  # Normalize to 1s max
        load_score = 1 - server.current_load
        health_score = server.health_score
        error_score = 1 - server.error_rate
        
        return (latency_score + load_score + health_score + error_score) / 4

    def _calculate_availability_score(self, server: ServerInstance) -> float:
        """Calculate availability score based on historical data"""
        
        # Simplified availability calculation
        recent_uptime = 0.99  # Would calculate from historical data
        current_health = server.health_score
        
        return (recent_uptime + current_health) / 2

    def _calculate_cost_score(self, server: ServerInstance) -> float:
        """Calculate cost efficiency score"""
        
        if not self.config["cost_optimization_enabled"]:
            return 0.5  # Neutral score
        
        # Calculate cost per request based on current utilization
        regional_multiplier = self.cost_factors["regional_cost_multipliers"].get(server.region, 1.0)
        
        # Simplified cost calculation
        base_cost = (
            server.capacity.get("cpu", 0) * self.cost_factors["cpu_cost_per_hour"] +
            server.capacity.get("memory", 0) * self.cost_factors["memory_cost_per_gb_hour"]
        ) * regional_multiplier
        
        # Higher utilization = better cost efficiency
        utilization_efficiency = server.current_load if server.current_load > 0.1 else 0.1
        cost_score = utilization_efficiency / (base_cost + 0.01)
        
        return min(1.0, cost_score)

    def _calculate_affinity_score(
        self,
        server: ServerInstance,
        request_metadata: Dict[str, Any]
    ) -> float:
        """Calculate affinity score based on creator type and model type"""
        
        creator_type = request_metadata.get("creator_type", "")
        model_type = request_metadata.get("model_type", "")
        client_region = request_metadata.get("client_region", "")
        
        score = 0.0
        
        # Model type affinity
        if model_type in server.model_types:
            score += 0.4
        
        # Geographic affinity
        if client_region == server.region:
            score += 0.3
        elif self._is_nearby_region(client_region, server.region):
            score += 0.2
        
        # Creator type optimization
        creator_affinity = self._get_creator_server_affinity(creator_type, server.region)
        score += creator_affinity * 0.3
        
        return min(1.0, score)

    def _is_nearby_region(self, region1: str, region2: str) -> bool:
        """Check if two regions are geographically nearby"""
        
        region_clusters = {
            "us": ["us-west", "us-east", "us-central"],
            "europe": ["europe", "europe-west", "europe-central"],
            "asia": ["asia", "asia-east", "asia-southeast"]
        }
        
        for cluster in region_clusters.values():
            if region1 in cluster and region2 in cluster:
                return True
        
        return False

    def _get_creator_server_affinity(self, creator_type: str, server_region: str) -> float:
        """Get affinity score between creator type and server region"""
        
        # Creator-region affinity mapping based on typical usage patterns
        affinities = {
            "musician": {"us-west": 0.9, "europe": 0.8, "us-east": 0.7},
            "blogger": {"us-east": 0.9, "europe": 0.8, "us-west": 0.6},
            "photographer": {"us-west": 0.8, "europe": 0.9, "asia": 0.7},
            "influencer": {"us-west": 0.9, "us-east": 0.8, "asia": 0.8},
            "comedian": {"us-east": 0.9, "us-west": 0.8, "europe": 0.6}
        }
        
        return affinities.get(creator_type, {}).get(server_region, 0.5)

    async def _predict_server_load(self, server_id: str) -> float:
        """Predict future load for server using ML"""
        
        if not self.config["traffic_prediction_enabled"]:
            return 0.5  # Neutral prediction
        
        # Simplified prediction - would use actual ML model in production
        current_server = self.servers[server_id]
        historical_loads = self.performance_metrics[f"{server_id}_load"]
        
        if len(historical_loads) < 5:
            return current_server.current_load
        
        # Simple trend-based prediction
        recent_loads = list(historical_loads)[-5:]
        trend = (recent_loads[-1] - recent_loads[0]) / len(recent_loads)
        predicted_load = current_server.current_load + trend
        
        return max(0.0, min(1.0, predicted_load))

    async def _creator_aware_selection(
        self,
        servers: List[str],
        request_metadata: Dict[str, Any]
    ) -> str:
        """Creator-aware server selection optimized for specific creator types"""
        
        creator_type = request_metadata.get("creator_type", "")
        
        best_server = servers[0]
        best_score = -1
        
        for server_id in servers:
            server = self.servers[server_id]
            
            # Calculate creator-specific optimization score
            score = 0.0
            
            # Creator type optimization weights
            creator_weights = {
                "musician": {"latency": 0.4, "audio_capability": 0.3, "reliability": 0.3},
                "blogger": {"cost": 0.4, "text_processing": 0.3, "scalability": 0.3},
                "photographer": {"image_processing": 0.4, "storage": 0.3, "bandwidth": 0.3},
                "influencer": {"social_media": 0.4, "real_time": 0.3, "global_reach": 0.3},
                "comedian": {"video_processing": 0.4, "real_time": 0.3, "engagement": 0.3}
            }
            
            weights = creator_weights.get(creator_type, {"balanced": 1.0})
            
            # Calculate weighted score based on creator needs
            for capability, weight in weights.items():
                capability_score = self._get_server_capability_score(server, capability)
                score += capability_score * weight
            
            if score > best_score:
                best_score = score
                best_server = server_id
        
        return best_server

    def _get_server_capability_score(self, server: ServerInstance, capability: str) -> float:
        """Get server capability score for specific requirement"""
        
        # Simplified capability scoring
        capability_scores = {
            "latency": 1 - (server.latency_p95 / 1000),
            "reliability": server.health_score,
            "cost": 1 - server.current_load,  # Lower load = better cost efficiency
            "scalability": server.capacity.get("requests_per_sec", 100) / 1000,
            "audio_capability": 0.9 if "audio" in server.model_types else 0.5,
            "text_processing": 0.9 if "nlp" in server.model_types else 0.5,
            "image_processing": 0.9 if "vision" in server.model_types else 0.5,
            "video_processing": 0.9 if "video" in server.model_types else 0.5,
            "real_time": 1 - (server.latency_p95 / 500),
            "global_reach": 0.8,  # Simplified
            "social_media": 0.8,  # Simplified
            "engagement": server.health_score,
            "bandwidth": server.capacity.get("bandwidth", 100) / 1000,
            "storage": server.capacity.get("storage", 100) / 1000,
            "balanced": (server.health_score + (1 - server.current_load)) / 2
        }
        
        return max(0.0, min(1.0, capability_scores.get(capability, 0.5)))

    async def _geographic_selection(
        self,
        servers: List[str],
        request_metadata: Dict[str, Any]
    ) -> str:
        """Geographic-optimized server selection"""
        
        client_region = request_metadata.get("client_region", "")
        
        # Prioritize servers in same region
        same_region_servers = [
            s for s in servers 
            if self.servers[s].region == client_region
        ]
        
        if same_region_servers:
            # Use least response time within same region
            return await self._least_response_time_selection(same_region_servers)
        
        # Find nearby regions
        nearby_servers = [
            s for s in servers
            if self._is_nearby_region(client_region, self.servers[s].region)
        ]
        
        if nearby_servers:
            return await self._least_response_time_selection(nearby_servers)
        
        # Fallback to any available server
        return await self._least_response_time_selection(servers)

    async def _get_candidate_servers(
        self,
        model_type: str,
        client_region: Optional[str] = None
    ) -> List[str]:
        """Get candidate servers that can handle the request"""
        
        candidates = []
        
        for server_id, server in self.servers.items():
            # Check if server is healthy
            if server.health_score < 0.5:
                continue
            
            # Check if server is not overloaded
            if server.current_load > 0.9:
                continue
            
            # Check if server supports the model type
            if model_type and model_type not in server.model_types:
                continue
            
            candidates.append(server_id)
        
        return candidates

    async def _get_applicable_rule(
        self,
        model_type: str,
        creator_type: str
    ) -> Optional[LoadBalancingRule]:
        """Get the most applicable load balancing rule"""
        
        # Find exact match first
        for rule in self.load_balancing_rules.values():
            if not rule.active:
                continue
            
            if rule.model_type == model_type and rule.creator_type == creator_type:
                return rule
        
        # Find partial matches
        for rule in self.load_balancing_rules.values():
            if not rule.active:
                continue
            
            if rule.model_type == model_type or rule.creator_type == creator_type:
                return rule
        
        # Return default rule
        return self.load_balancing_rules.get("default")

    def _generate_cache_key(self, request_metadata: Dict[str, Any]) -> str:
        """Generate cache key for request routing"""
        
        key_components = [
            request_metadata.get("model_type", ""),
            request_metadata.get("creator_type", ""),
            request_metadata.get("client_region", ""),
            request_metadata.get("priority", "normal")
        ]
        
        return "|".join(key_components)

    def _get_cached_route(self, cache_key: str) -> Optional[str]:
        """Get cached routing decision if still valid"""
        
        if cache_key not in self.routing_cache:
            return None
        
        server_id, timestamp = self.routing_cache[cache_key]
        
        # Check if cache entry is still valid
        if time.time() - timestamp > self.config["routing_cache_ttl"]:
            del self.routing_cache[cache_key]
            return None
        
        # Check if server is still healthy
        if server_id not in self.servers or self.servers[server_id].health_score < 0.5:
            del self.routing_cache[cache_key]
            return None
        
        return server_id

    def _cache_route(self, cache_key -> None: str, server_id -> None: str) -> None:
        """Cache routing decision"""
        self.routing_cache[cache_key] = (server_id, time.time())

    async def _update_server_metrics(
        self,
        server_id -> None: str,
        request_metadata -> None: Dict[str, Any]
    ) -> None:
        """Update server metrics after routing decision"""
        
        if server_id not in self.servers:
            return
        
        server = self.servers[server_id]
        
        # Increment request counters
        self.requests_counter.labels(
            server_id=server_id,
            model_type=request_metadata.get("model_type", "unknown"),
            creator_type=request_metadata.get("creator_type", "unknown")
        ).inc()
        
        # Update server load gauge
        self.server_load_gauge.labels(
            server_id=server_id,
            region=server.region
        ).set(server.current_load * 100)
        
        # Store request in history
        request_record = {
            "timestamp": datetime.now(timezone.utc),
            "server_id": server_id,
            "metadata": request_metadata
        }
        self.request_history.append(request_record)

    async def _setup_default_rules(self) -> None:
        """Setup default load balancing rules"""
        
        default_rules = [
            LoadBalancingRule(
                rule_id="default",
                model_type="*",
                creator_type="*",
                algorithm=BalancingAlgorithm.ML_OPTIMIZED.value,
                weights={},
                priority=0
            ),
            LoadBalancingRule(
                rule_id="musician_audio",
                model_type="audio_processing",
                creator_type="musician",
                algorithm=BalancingAlgorithm.CREATOR_AWARE.value,
                weights={"latency": 0.6, "audio_capability": 0.4},
                priority=1
            ),
            LoadBalancingRule(
                rule_id="blogger_nlp",
                model_type="nlp",
                creator_type="blogger",
                algorithm=BalancingAlgorithm.COST_OPTIMIZED.value,
                weights={"cost": 0.5, "scalability": 0.5},
                priority=1
            ),
            LoadBalancingRule(
                rule_id="photographer_vision",
                model_type="computer_vision",
                creator_type="photographer",
                algorithm=BalancingAlgorithm.CREATOR_AWARE.value,
                weights={"image_processing": 0.6, "bandwidth": 0.4},
                priority=1
            )
        ]
        
        for rule in default_rules:
            self.load_balancing_rules[rule.rule_id] = rule
        
        self.logger.info(f"✅ Setup {len(default_rules)} default load balancing rules")

    async def _optimization_loop(self) -> None:
        """Background optimization loop"""
        
        while True:
            try:
                await self._optimize_routing_weights()
                await self._analyze_performance_patterns()
                await self._update_ml_models()
                
                await asyncio.sleep(self.config["optimization_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Optimization loop error: {e}")
                await asyncio.sleep(60)

    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring"""
        
        while True:
            try:
                await self._update_server_health_scores()
                await self._detect_performance_anomalies()
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(30)

    async def _ml_training_loop(self) -> None:
        """Background ML model training and updates"""
        
        while True:
            try:
                if self.config["ml_optimization_enabled"]:
                    await self._train_traffic_predictor()
                    await self._train_performance_predictor()
                    await self._optimize_algorithm_weights()
                
                await asyncio.sleep(1800)  # Train every 30 minutes
                
            except Exception as e:
                self.logger.error(f"❌ ML training error: {e}")
                await asyncio.sleep(300)

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for optimization"""
        # Placeholder for ML model initialization
        self.logger.info("🤖 ML models initialized for load balancing optimization")

    async def _optimize_routing_weights(self) -> None:
        """Optimize routing weights based on performance data"""
        pass  # Placeholder for weight optimization

    async def _analyze_performance_patterns(self) -> None:
        """Analyze performance patterns for optimization"""
        pass  # Placeholder for pattern analysis

    async def _update_ml_models(self) -> None:
        """Update ML models with recent data"""
        pass  # Placeholder for model updates

    async def _update_server_health_scores(self) -> None:
        """Update health scores for all servers"""
        pass  # Placeholder for health score updates

    async def _detect_performance_anomalies(self) -> None:
        """Detect performance anomalies"""
        pass  # Placeholder for anomaly detection

    async def _train_traffic_predictor(self) -> None:
        """Train traffic prediction model"""
        pass  # Placeholder for traffic prediction training

    async def _train_performance_predictor(self) -> None:
        """Train performance prediction model"""
        pass  # Placeholder for performance prediction training

    async def _optimize_algorithm_weights(self) -> None:
        """Optimize algorithm weights using ML"""
        pass  # Placeholder for algorithm weight optimization

    # Public API methods
    
    async def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        
        total_servers = len(self.servers)
        healthy_servers = sum(1 for s in self.servers.values() if s.health_score >= 0.5)
        total_requests = sum(s.total_requests for s in self.servers.values())
        
        avg_load = sum(s.current_load for s in self.servers.values()) / max(1, total_servers)
        avg_latency = sum(s.latency_p95 for s in self.servers.values()) / max(1, total_servers)
        
        return {
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "total_requests": total_requests,
            "average_load": avg_load,
            "average_latency_p95": avg_latency,
            "routing_cache_size": len(self.routing_cache),
            "active_rules": len([r for r in self.load_balancing_rules.values() if r.active])
        }

    async def update_server_status(
        self,
        server_id: str,
        status_update: Dict[str, Any]
    ) -> bool:
        """Update server status information"""
        
        if server_id not in self.servers:
            return False
        
        server = self.servers[server_id]
        
        # Update fields that are provided
        if "current_load" in status_update:
            server.current_load = status_update["current_load"]
        
        if "health_score" in status_update:
            server.health_score = status_update["health_score"]
        
        if "latency_p95" in status_update:
            server.latency_p95 = status_update["latency_p95"]
        
        if "active_connections" in status_update:
            server.active_connections = status_update["active_connections"]
        
        if "error_rate" in status_update:
            server.error_rate = status_update["error_rate"]
        
        server.last_updated = datetime.now(timezone.utc)
        
        # Update metrics
        self.server_load_gauge.labels(
            server_id=server_id,
            region=server.region
        ).set(server.current_load * 100)
        
        return True

# Example usage
async def main() -> None:
    """Example usage of Load Balancer Optimizer"""
    
    # Initialize optimizer
    optimizer = LoadBalancerOptimizer()
    await optimizer.initialize()
    
    # Register some sample servers
    servers = [
        ServerInstance(
            instance_id="server-us-west-1",
            endpoint_url="https://server-us-west-1.ainflue.com",
            region="us-west",
            model_types=["audio_processing", "nlp"],
            current_load=0.3,
            capacity={"cpu": 80, "memory": 64, "requests_per_sec": 1000},
            health_score=0.95,
            latency_p95=45.0,
            active_connections=150,
            total_requests=10000,
            error_rate=0.01,
            last_updated=datetime.now(timezone.utc)
        ),
        ServerInstance(
            instance_id="server-europe-1",
            endpoint_url="https://server-europe-1.ainflue.com",
            region="europe",
            model_types=["computer_vision", "nlp"],
            current_load=0.5,
            capacity={"cpu": 100, "memory": 128, "requests_per_sec": 1500},
            health_score=0.98,
            latency_p95=35.0,
            active_connections=200,
            total_requests=15000,
            error_rate=0.005,
            last_updated=datetime.now(timezone.utc)
        )
    ]
    
    for server in servers:
        await optimizer.register_server(server)
    
    # Route some sample requests
    request_metadata = {
        "model_type": "audio_processing",
        "creator_type": "musician",
        "client_region": "us-west",
        "priority": "high"
    }
    
    selected_server = await optimizer.route_request(request_metadata)
    print(f"🎯 Routed request to: {selected_server}")
    
    # Get stats
    stats = await optimizer.get_load_balancer_stats()
    print(f"📊 Load balancer stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())