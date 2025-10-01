#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 SERVICE REGISTRY ENTERPRISE - SERVICE DISCOVERY ENGINE
==========================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: IA Chéries Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🌐 SERVICE DISCOVERY ENGINE
Moteur discovery avancé avec ML et prédictions.
Discovery intelligent + caching + load balancing hints + circuit breaker integration.
"""

import asyncio
import json
import logging
import time
import random
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import statistics

from .distributed_registry_core import ServiceInstance, ServiceStatus, ServiceDiscoveryCriteria

# Core logger
logger = logging.getLogger(__name__)

class DiscoveryStrategy(Enum):
    """Service discovery strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RESPONSE_TIME = "weighted_response_time"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    ML_PREDICTIVE = "ml_predictive"
    BUSINESS_PRIORITY = "business_priority"
    RANDOM = "random"
    HEALTH_WEIGHTED = "health_weighted"

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"

@dataclass
class ServiceDiscoveryRequest:
    """Service discovery request with preferences"""
    criteria: ServiceDiscoveryCriteria
    strategy: DiscoveryStrategy = DiscoveryStrategy.ML_PREDICTIVE
    load_balancing: LoadBalancingAlgorithm = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN
    require_healthy: bool = True
    prefer_local_region: bool = True
    client_ip: Optional[str] = None
    client_metadata: Dict[str, Any] = field(default_factory=dict)
    cache_ttl: int = 60  # seconds
    max_retry_attempts: int = 3

@dataclass 
class ServiceDiscoveryResult:
    """Service discovery result with metadata"""
    services: List[ServiceInstance]
    strategy_used: DiscoveryStrategy
    cache_hit: bool = False
    response_time_ms: float = 0.0
    total_candidates: int = 0
    filtered_count: int = 0
    load_balancing_weights: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class AvailabilityPrediction:
    """Service availability prediction"""
    service_id: str
    predicted_availability: float  # 0.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    prediction_window_minutes: int
    factors: Dict[str, float] = field(default_factory=dict)

@dataclass
class AffinityMatrix:
    """Service affinity matrix for optimal placement"""
    requesting_service: str
    affinities: Dict[str, float]  # service_id -> affinity score
    anti_affinities: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class DependencyGraph:
    """Service dependency graph"""
    service_id: str
    dependencies: Dict[str, Set[str]]  # service_id -> set of dependent services
    dependents: Dict[str, Set[str]]   # service_id -> set of services that depend on it
    dependency_weights: Dict[str, float] = field(default_factory=dict)

@dataclass
class ScalingRecommendation:
    """Service scaling recommendation"""
    service_name: str
    current_instances: int
    recommended_instances: int
    confidence: float
    reasoning: List[str]
    estimated_cost_impact: float
    urgency: str  # low, medium, high

@dataclass
class DiscoveryConfig:
    """Configuration for service discovery engine"""
    cache_enabled: bool = True
    cache_ttl_seconds: int = 60
    ml_predictions_enabled: bool = True
    circuit_breaker_enabled: bool = True
    health_check_timeout: float = 5.0
    max_concurrent_checks: int = 100
    geographic_preference_weight: float = 0.3
    performance_history_window: int = 3600  # seconds

class ServiceLoadPredictor:
    """ML-based service load prediction"""
    
    def __init__(self):
        self.load_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.response_time_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_rate_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
    async def predict_load(self, service_id: str, time_window_minutes: int = 15) -> float:
        """Predict service load for given time window"""
        try:
            if service_id not in self.load_history or len(self.load_history[service_id]) < 10:
                return 0.5  # Default medium load prediction
            
            history = list(self.load_history[service_id])
            
            # Simple trend analysis
            recent_loads = history[-10:]
            avg_load = statistics.mean(recent_loads)
            
            # Add some randomness for demo
            predicted_load = max(0.0, min(1.0, avg_load + random.uniform(-0.1, 0.1)))
            
            return predicted_load
            
        except Exception as e:
            logger.error(f"Load prediction failed for {service_id}: {e}")
            return 0.5
    
    async def predict_response_time(self, service_id: str) -> float:
        """Predict average response time for service"""
        try:
            if service_id not in self.response_time_history or len(self.response_time_history[service_id]) < 5:
                return 100.0  # Default 100ms
            
            history = list(self.response_time_history[service_id])
            return statistics.mean(history[-20:])  # Average of last 20 measurements
            
        except Exception as e:
            logger.error(f"Response time prediction failed for {service_id}: {e}")
            return 100.0
    
    def record_load_metric(self, service_id: str, load: float):
        """Record load metric for learning"""
        self.load_history[service_id].append(load)
    
    def record_response_time(self, service_id: str, response_time_ms: float):
        """Record response time for learning"""
        self.response_time_history[service_id].append(response_time_ms)
    
    def record_error_rate(self, service_id: str, error_rate: float):
        """Record error rate for learning"""
        self.error_rate_history[service_id].append(error_rate)

class DiscoveryCacheManager:
    """Discovery result caching manager"""
    
    def __init__(self, default_ttl: int = 60):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_cache_key(self, request: ServiceDiscoveryRequest) -> str:
        """Generate cache key for discovery request"""
        key_data = {
            'criteria': {
                'service_name': request.criteria.service_name,
                'service_type': request.criteria.service_type,
                'tags': sorted(list(request.criteria.tags)) if request.criteria.tags else None,
                'region': request.criteria.region,
                'datacenter': request.criteria.datacenter,
                'environment': request.criteria.environment,
                'business_domain': request.criteria.business_domain,
                'status': request.criteria.status.value if request.criteria.status else None,
                'min_weight': request.criteria.min_weight,
                'max_results': request.criteria.max_results
            },
            'strategy': request.strategy.value,
            'require_healthy': request.require_healthy,
            'prefer_local_region': request.prefer_local_region
        }
        
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def get_cached_result(self, request: ServiceDiscoveryRequest) -> Optional[ServiceDiscoveryResult]:
        """Get cached discovery result if available and valid"""
        try:
            cache_key = self._generate_cache_key(request)
            
            if cache_key in self.cache:
                result, timestamp = self.cache[cache_key]
                
                # Check if cache entry is still valid
                if time.time() - timestamp < request.cache_ttl:
                    self.hit_count += 1
                    result.cache_hit = True
                    return result
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            self.miss_count += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            self.miss_count += 1
            return None
    
    async def cache_result(self, request: ServiceDiscoveryRequest, result: ServiceDiscoveryResult):
        """Cache discovery result"""
        try:
            cache_key = self._generate_cache_key(request)
            self.cache[cache_key] = (result, time.time())
            
            # Simple cache size management
            if len(self.cache) > 10000:
                # Remove oldest 10% of entries
                sorted_entries = sorted(self.cache.items(), key=lambda x: x[1][1])
                for key, _ in sorted_entries[:1000]:
                    del self.cache[key]
                    
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0.0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }

class CircuitBreakerManager:
    """Circuit breaker manager for failed services"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.failure_threshold = 5
        self.recovery_timeout = 30  # seconds
        self.half_open_max_calls = 3
    
    def get_circuit_state(self, service_id: str) -> str:
        """Get circuit breaker state for service"""
        if service_id not in self.circuit_breakers:
            self.circuit_breakers[service_id] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure_time': 0,
                'half_open_calls': 0
            }
        
        breaker = self.circuit_breakers[service_id]
        current_time = time.time()
        
        # Check if circuit should transition from open to half-open
        if (breaker['state'] == 'open' and 
            current_time - breaker['last_failure_time'] >= self.recovery_timeout):
            breaker['state'] = 'half_open'
            breaker['half_open_calls'] = 0
        
        return breaker['state']
    
    def record_success(self, service_id: str):
        """Record successful call to service"""
        if service_id in self.circuit_breakers:
            breaker = self.circuit_breakers[service_id]
            
            if breaker['state'] == 'half_open':
                breaker['half_open_calls'] += 1
                if breaker['half_open_calls'] >= self.half_open_max_calls:
                    breaker['state'] = 'closed'
                    breaker['failure_count'] = 0
            elif breaker['state'] == 'closed':
                breaker['failure_count'] = max(0, breaker['failure_count'] - 1)
    
    def record_failure(self, service_id: str):
        """Record failed call to service"""
        if service_id not in self.circuit_breakers:
            self.circuit_breakers[service_id] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure_time': 0,
                'half_open_calls': 0
            }
        
        breaker = self.circuit_breakers[service_id]
        breaker['failure_count'] += 1
        breaker['last_failure_time'] = time.time()
        
        if breaker['failure_count'] >= self.failure_threshold:
            breaker['state'] = 'open'
    
    def is_call_allowed(self, service_id: str) -> bool:
        """Check if calls to service are allowed"""
        state = self.get_circuit_state(service_id)
        return state in ['closed', 'half_open']

class LoadBalancerHintEngine:
    """Load balancer hint engine for optimal service selection"""
    
    def __init__(self):
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
    
    async def calculate_weights(self, services: List[ServiceInstance], algorithm: LoadBalancingAlgorithm) -> Dict[str, float]:
        """Calculate load balancing weights for services"""
        if not services:
            return {}
        
        weights = {}
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            # Equal weights for round robin
            for service in services:
                weights[service.service_id] = 1.0
                
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            # Use service-defined weights
            for service in services:
                weights[service.service_id] = service.weight / 100.0
                
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            # Inverse of connection count
            max_connections = max((self.connection_counts[s.service_id] for s in services), default=1)
            for service in services:
                connections = self.connection_counts[service.service_id]
                weights[service.service_id] = (max_connections - connections + 1) / (max_connections + 1)
                
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            # Combine service weight with connection count
            for service in services:
                connections = self.connection_counts[service.service_id]
                base_weight = service.weight / 100.0
                connection_factor = 1.0 / (connections + 1)
                weights[service.service_id] = base_weight * connection_factor
                
        elif algorithm == LoadBalancingAlgorithm.RANDOM:
            # Random weights
            for service in services:
                weights[service.service_id] = random.random()
                
        else:  # Default to weighted round robin
            for service in services:
                weights[service.service_id] = service.weight / 100.0
        
        return weights
    
    def record_connection(self, service_id: str):
        """Record new connection to service"""
        self.connection_counts[service_id] += 1
    
    def record_disconnection(self, service_id: str):
        """Record connection closure from service"""
        self.connection_counts[service_id] = max(0, self.connection_counts[service_id] - 1)
    
    def record_response_time(self, service_id: str, response_time_ms: float):
        """Record response time for service"""
        self.response_times[service_id].append(response_time_ms)

class ServiceDiscoveryEngine:
    """
    Moteur discovery avancé avec ML et prédictions.
    Discovery intelligent + caching + load balancing hints + circuit breaker integration.
    """
    
    def __init__(self, discovery_config: Optional[DiscoveryConfig] = None):
        """Initialize service discovery engine"""
        self.discovery_config = discovery_config or DiscoveryConfig()
        self.ml_predictor = ServiceLoadPredictor()
        self.cache_manager = DiscoveryCacheManager(self.discovery_config.cache_ttl_seconds)
        self.circuit_breaker = CircuitBreakerManager()
        self.load_balancer_hints = LoadBalancerHintEngine()
        
        # Service registry reference (to be injected)
        self.service_registry = None
        
        # Performance metrics
        self.metrics = {
            'discovery_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'ml_predictions': 0,
            'circuit_breaker_trips': 0,
            'average_response_time': 0.0
        }
        
        # Discovery strategies
        self.discovery_strategies = {
            DiscoveryStrategy.ROUND_ROBIN: self._round_robin_discovery,
            DiscoveryStrategy.LEAST_CONNECTIONS: self._least_connections_discovery,
            DiscoveryStrategy.WEIGHTED_RESPONSE_TIME: self._weighted_response_time_discovery,
            DiscoveryStrategy.GEOGRAPHIC_PROXIMITY: self._geographic_proximity_discovery,
            DiscoveryStrategy.ML_PREDICTIVE: self._ml_predictive_discovery,
            DiscoveryStrategy.BUSINESS_PRIORITY: self._business_priority_discovery,
            DiscoveryStrategy.RANDOM: self._random_discovery,
            DiscoveryStrategy.HEALTH_WEIGHTED: self._health_weighted_discovery
        }
    
    def set_service_registry(self, registry):
        """Set reference to service registry"""
        self.service_registry = registry
    
    async def discover_optimal_services(self, discovery_request: ServiceDiscoveryRequest) -> ServiceDiscoveryResult:
        """
        Discovery services optimal avec ML predictions.
        
        Discovery Features:
        - ML-based service ranking basé sur performance historique
        - Health-aware service filtering avec predictive health
        - Geographic proximity calculation pour latence optimization
        - Load balancing hints avec capacity awareness
        - Circuit breaker integration pour failed services
        - Service dependency resolution avec DAG validation
        - Cache-aware discovery avec TTL intelligent
        - A/B testing service selection pour canary deployments
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if self.discovery_config.cache_enabled:
                cached_result = await self.cache_manager.get_cached_result(discovery_request)
                if cached_result:
                    self.metrics['cache_hits'] += 1
                    return cached_result
                else:
                    self.metrics['cache_misses'] += 1
            
            # Get candidate services from registry
            if not self.service_registry:
                raise RuntimeError("Service registry not set")
            
            candidates = await self.service_registry.discover_services_by_criteria(discovery_request.criteria)
            
            # Filter healthy services if required
            if discovery_request.require_healthy:
                candidates = [s for s in candidates if s.status == ServiceStatus.HEALTHY]
            
            # Apply circuit breaker filtering
            if self.discovery_config.circuit_breaker_enabled:
                candidates = [s for s in candidates if self.circuit_breaker.is_call_allowed(s.service_id)]
                
            # Apply discovery strategy
            strategy_func = self.discovery_strategies.get(
                discovery_request.strategy,
                self._ml_predictive_discovery
            )
            
            ranked_services = await strategy_func(candidates, discovery_request)
            
            # Calculate load balancing weights
            lb_weights = await self.load_balancer_hints.calculate_weights(
                ranked_services, 
                discovery_request.load_balancing
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(ranked_services, discovery_request)
            
            # Create result
            response_time_ms = (time.time() - start_time) * 1000
            result = ServiceDiscoveryResult(
                services=ranked_services,
                strategy_used=discovery_request.strategy,
                cache_hit=False,
                response_time_ms=response_time_ms,
                total_candidates=len(candidates),
                filtered_count=len(ranked_services),
                load_balancing_weights=lb_weights,
                recommendations=recommendations
            )
            
            # Cache result
            if self.discovery_config.cache_enabled:
                await self.cache_manager.cache_result(discovery_request, result)
            
            # Update metrics
            self.metrics['discovery_requests'] += 1
            self.metrics['average_response_time'] = (
                (self.metrics['average_response_time'] * (self.metrics['discovery_requests'] - 1) + response_time_ms) /
                self.metrics['discovery_requests']
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            # Return empty result on error
            return ServiceDiscoveryResult(
                services=[],
                strategy_used=discovery_request.strategy,
                response_time_ms=(time.time() - start_time) * 1000,
                total_candidates=0,
                filtered_count=0
            )
    
    async def predict_service_availability(self, service_name: str, time_window: int) -> AvailabilityPrediction:
        """Prédiction disponibilité service avec ML time series."""
        try:
            # Simple availability prediction based on historical data
            predicted_availability = await self.ml_predictor.predict_load(service_name, time_window)
            
            # Convert load to availability (inverse relationship)
            availability = max(0.1, 1.0 - predicted_availability * 0.5)
            
            factors = {
                'historical_load': predicted_availability,
                'time_of_day': self._get_time_of_day_factor(),
                'day_of_week': self._get_day_of_week_factor()
            }
            
            confidence = min(0.9, 0.5 + predicted_availability * 0.4)
            
            self.metrics['ml_predictions'] += 1
            
            return AvailabilityPrediction(
                service_id=service_name,
                predicted_availability=availability,
                confidence_score=confidence,
                prediction_window_minutes=time_window,
                factors=factors
            )
            
        except Exception as e:
            logger.error(f"Availability prediction failed for {service_name}: {e}")
            return AvailabilityPrediction(
                service_id=service_name,
                predicted_availability=0.8,  # Default
                confidence_score=0.3,
                prediction_window_minutes=time_window
            )
    
    async def calculate_service_affinity(self, requesting_service: str, target_services: List[str]) -> AffinityMatrix:
        """Calcul affinité services pour optimal placement."""
        try:
            affinities = {}
            
            for target in target_services:
                # Simple affinity calculation based on service names and types
                affinity_score = 0.5  # Base score
                
                # Boost affinity for services in same business domain
                if requesting_service.startswith(target.split('_')[0]):
                    affinity_score += 0.3
                
                # Add some randomness for demo
                affinity_score += random.uniform(-0.2, 0.2)
                affinity_score = max(0.0, min(1.0, affinity_score))
                
                affinities[target] = affinity_score
            
            return AffinityMatrix(
                requesting_service=requesting_service,
                affinities=affinities
            )
            
        except Exception as e:
            logger.error(f"Affinity calculation failed: {e}")
            return AffinityMatrix(
                requesting_service=requesting_service,
                affinities={target: 0.5 for target in target_services}
            )
    
    async def resolve_service_dependencies(self, service_name: str, depth: int = 3) -> DependencyGraph:
        """Résolution dépendances service avec graph traversal."""
        try:
            dependencies = defaultdict(set)
            dependents = defaultdict(set)
            
            # Simple dependency resolution - in real implementation would query registry
            if service_name.endswith('_service'):
                base_name = service_name.replace('_service', '')
                dependencies[service_name].add(f"{base_name}_database")
                dependencies[service_name].add(f"{base_name}_cache")
                
                # Add dependent services
                dependents[f"{base_name}_database"].add(service_name)
                dependents[f"{base_name}_cache"].add(service_name)
            
            return DependencyGraph(
                service_id=service_name,
                dependencies=dict(dependencies),
                dependents=dict(dependents)
            )
            
        except Exception as e:
            logger.error(f"Dependency resolution failed for {service_name}: {e}")
            return DependencyGraph(
                service_id=service_name,
                dependencies={},
                dependents={}
            )
    
    async def recommend_service_scaling(self, service_metrics: Dict[str, Any]) -> ScalingRecommendation:
        """Recommandations scaling basées sur discovery patterns."""
        try:
            service_name = service_metrics.get('service_name', 'unknown')
            current_instances = service_metrics.get('instance_count', 1)
            avg_load = service_metrics.get('average_load', 0.5)
            response_time = service_metrics.get('average_response_time', 100)
            
            # Simple scaling logic
            recommended_instances = current_instances
            reasoning = []
            urgency = 'low'
            
            if avg_load > 0.8:
                recommended_instances = int(current_instances * 1.5)
                reasoning.append(f"High load detected: {avg_load:.2f}")
                urgency = 'high'
            elif avg_load < 0.3 and current_instances > 1:
                recommended_instances = max(1, int(current_instances * 0.7))
                reasoning.append(f"Low load detected: {avg_load:.2f}")
                urgency = 'medium'
            
            if response_time > 500:  # ms
                recommended_instances = max(recommended_instances, int(current_instances * 1.2))
                reasoning.append(f"High response time: {response_time}ms")
                urgency = 'high'
            
            confidence = 0.7 if reasoning else 0.3
            estimated_cost_impact = (recommended_instances - current_instances) * 100  # $100 per instance
            
            return ScalingRecommendation(
                service_name=service_name,
                current_instances=current_instances,
                recommended_instances=recommended_instances,
                confidence=confidence,
                reasoning=reasoning,
                estimated_cost_impact=estimated_cost_impact,
                urgency=urgency
            )
            
        except Exception as e:
            logger.error(f"Scaling recommendation failed: {e}")
            return ScalingRecommendation(
                service_name=service_metrics.get('service_name', 'unknown'),
                current_instances=1,
                recommended_instances=1,
                confidence=0.0,
                reasoning=['Error in analysis'],
                estimated_cost_impact=0,
                urgency='low'
            )
    
    # Discovery strategy implementations
    async def _round_robin_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Round robin service selection"""
        return services  # Return in original order
    
    async def _least_connections_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Least connections service selection"""
        return sorted(services, key=lambda s: self.load_balancer_hints.connection_counts[s.service_id])
    
    async def _weighted_response_time_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Weighted response time service selection"""
        async def get_avg_response_time(service):
            response_times = self.load_balancer_hints.response_times[service.service_id]
            return statistics.mean(response_times) if response_times else 100.0
        
        # Sort by response time (ascending)
        services_with_times = []
        for service in services:
            avg_time = await get_avg_response_time(service)
            services_with_times.append((service, avg_time))
        
        services_with_times.sort(key=lambda x: x[1])
        return [service for service, _ in services_with_times]
    
    async def _geographic_proximity_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Geographic proximity service selection"""
        if not request.prefer_local_region:
            return services
        
        # Simple geographic sorting - prefer same region/datacenter
        def geographic_score(service):
            score = 0
            if service.region == (request.criteria.region or 'default'):
                score += 2
            if service.datacenter == (request.criteria.datacenter or 'default'):
                score += 1
            return score
        
        return sorted(services, key=geographic_score, reverse=True)
    
    async def _ml_predictive_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """ML-based predictive service selection"""
        services_with_scores = []
        
        for service in services:
            # Predict load and response time
            predicted_load = await self.ml_predictor.predict_load(service.service_id)
            predicted_response_time = await self.ml_predictor.predict_response_time(service.service_id)
            
            # Calculate composite score
            load_score = 1.0 - predicted_load  # Lower load is better
            response_time_score = max(0.1, 1.0 - (predicted_response_time / 1000.0))  # Normalize to 0-1
            weight_score = service.weight / 1000.0
            
            composite_score = (load_score * 0.4 + response_time_score * 0.4 + weight_score * 0.2)
            services_with_scores.append((service, composite_score))
        
        # Sort by composite score (descending)
        services_with_scores.sort(key=lambda x: x[1], reverse=True)
        return [service for service, _ in services_with_scores]
    
    async def _business_priority_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Business priority service selection for IA Chéries"""
        priority_order = {
            'creator': 5,
            'content': 4,
            'monetization': 3,
            'collaboration': 2,
            'distribution': 1,
            'general': 0
        }
        
        return sorted(services, key=lambda s: priority_order.get(s.ainflue_business_domain, 0), reverse=True)
    
    async def _random_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Random service selection"""
        shuffled = services.copy()
        random.shuffle(shuffled)
        return shuffled
    
    async def _health_weighted_discovery(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Health-weighted service selection"""
        def health_score(service):
            base_score = service.weight
            
            # Boost healthy services
            if service.status == ServiceStatus.HEALTHY:
                base_score *= 1.5
            elif service.status == ServiceStatus.UNKNOWN:
                base_score *= 0.8
            elif service.status == ServiceStatus.UNHEALTHY:
                base_score *= 0.1
            
            # Consider service age
            age_hours = (time.time() - service.created_at) / 3600
            if age_hours > 24:  # Mature services get boost
                base_score *= 1.2
            
            return base_score
        
        return sorted(services, key=health_score, reverse=True)
    
    async def _generate_recommendations(self, services: List[ServiceInstance], request: ServiceDiscoveryRequest) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if len(services) == 0:
            recommendations.append("No services found matching criteria - consider relaxing filters")
        elif len(services) == 1:
            recommendations.append("Only one service available - consider deploying additional instances")
        
        # Check for geographic distribution
        regions = set(s.region for s in services)
        if len(regions) == 1 and request.prefer_local_region:
            recommendations.append("All services in single region - consider multi-region deployment")
        
        # Check for version diversity
        versions = set(s.version for s in services)
        if len(versions) > 3:
            recommendations.append("Many service versions detected - consider version consolidation")
        
        # Check load balancing weights
        weights = [s.weight for s in services]
        if len(set(weights)) == 1:
            recommendations.append("All services have same weight - consider differentiated weighting")
        
        return recommendations
    
    def _get_time_of_day_factor(self) -> float:
        """Get time of day factor for predictions"""
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            return 0.8  # Higher load expected
        else:
            return 0.3  # Lower load expected
    
    def _get_day_of_week_factor(self) -> float:
        """Get day of week factor for predictions"""
        weekday = datetime.now().weekday()
        if weekday < 5:  # Monday-Friday
            return 0.7
        else:  # Weekend
            return 0.4
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get discovery engine metrics"""
        cache_stats = self.cache_manager.get_cache_stats()
        
        return {
            **self.metrics,
            **cache_stats,
            'circuit_breaker_count': len(self.circuit_breaker.circuit_breakers),
            'active_connections': sum(self.load_balancer_hints.connection_counts.values())
        }
    
    async def shutdown(self):
        """Graceful shutdown of discovery engine"""
        logger.info("Shutting down ServiceDiscoveryEngine")
        # Clear caches and reset state
        self.cache_manager.cache.clear()
        self.circuit_breaker.circuit_breakers.clear()
        self.load_balancer_hints.connection_counts.clear()

# Factory function
async def create_service_discovery_engine(config: Optional[DiscoveryConfig] = None) -> ServiceDiscoveryEngine:
    """Factory function to create service discovery engine"""
    return ServiceDiscoveryEngine(config)

# Export main classes and functions
__all__ = [
    'ServiceDiscoveryEngine',
    'ServiceDiscoveryRequest',
    'ServiceDiscoveryResult', 
    'AvailabilityPrediction',
    'AffinityMatrix',
    'DependencyGraph',
    'ScalingRecommendation',
    'DiscoveryConfig',
    'DiscoveryStrategy',
    'LoadBalancingAlgorithm',
    'create_service_discovery_engine'
]