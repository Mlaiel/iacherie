"""Event Routing Coordinator - Intelligent for Ainflue Platform

Intelligent event routing coordinator with dynamic routing rules,
load balancing, and business-aware service selection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import random

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Event routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    BUSINESS_PRIORITY = "business_priority"
    LOAD_BALANCED = "load_balanced"
    AFFINITY = "affinity"
    FAILOVER = "failover"


class ServiceHealth(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class RoutingRule:
    """Event routing rule definition"""
    name: str
    event_pattern: str
    target_services: List[str]
    routing_strategy: RoutingStrategy
    priority: int = 1
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    service_id: str
    endpoint_url: str
    weight: int = 1
    max_concurrent: int = 100
    timeout_seconds: int = 30
    health_status: ServiceHealth = ServiceHealth.UNKNOWN
    last_health_check: Optional[datetime] = None
    current_load: int = 0
    tags: Set[str] = field(default_factory=set)


@dataclass
class RoutingDecision:
    """Routing decision result"""
    event_id: str
    selected_service: str
    routing_rule: str
    routing_strategy: RoutingStrategy
    decision_factors: Dict[str, Any]
    confidence: float
    estimated_processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingMetrics:
    """Routing performance metrics"""
    total_routed: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    avg_decision_time: float = 0.0
    routes_by_service: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    routes_by_strategy: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class EventRoutingCoordinator:
    """
    Intelligent event routing coordinator for Ainflue platform
    Dynamic routing with business logic, load balancing, and service health monitoring
    """
    
    def __init__(self):
        self.routing_rules: List[RoutingRule] = []
        self.service_endpoints: Dict[str, ServiceEndpoint] = {}
        self.routing_history: deque = deque(maxlen=5000)
        self.metrics = RoutingMetrics()
        self.service_affinities: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Initialize default routing rules and services
        self._initialize_default_rules()
        self._initialize_default_services()
        
        logger.info("EventRoutingCoordinator initialized for Ainflue platform")
    
    def _initialize_default_rules(self):
        """Initialize default routing rules for Ainflue services"""
        
        self.routing_rules = [
            RoutingRule(
                name="content_upload_processing",
                event_pattern="content.upload.*",
                target_services=["content-processor", "ai-enhancement", "media-processor"],
                routing_strategy=RoutingStrategy.BUSINESS_PRIORITY,
                priority=1,
                conditions={"user_tier": ["premium", "enterprise"]}
            ),
            RoutingRule(
                name="collaboration_matching",
                event_pattern="collaboration.*",
                target_services=["collaboration-engine", "matching-service"],
                routing_strategy=RoutingStrategy.LOAD_BALANCED,
                priority=2
            ),
            RoutingRule(
                name="monetization_processing",
                event_pattern="monetization.*",
                target_services=["payment-processor", "revenue-calculator"],
                routing_strategy=RoutingStrategy.FAILOVER,
                priority=1,
                conditions={"criticality": "high"}
            ),
            RoutingRule(
                name="analytics_events",
                event_pattern="analytics.*",
                target_services=["analytics-processor", "data-warehouse"],
                routing_strategy=RoutingStrategy.ROUND_ROBIN,
                priority=3
            ),
            RoutingRule(
                name="ai_processing",
                event_pattern="ai.*",
                target_services=["ai-processor", "ml-inference", "gpu-cluster"],
                routing_strategy=RoutingStrategy.WEIGHTED,
                priority=2,
                conditions={"processing_type": ["image", "video", "audio"]}
            ),
            RoutingRule(
                name="user_events",
                event_pattern="user.*",
                target_services=["user-service", "profile-manager"],
                routing_strategy=RoutingStrategy.AFFINITY,
                priority=2
            ),
            RoutingRule(
                name="notification_delivery",
                event_pattern="notification.*",
                target_services=["notification-service", "email-service", "push-service"],
                routing_strategy=RoutingStrategy.BUSINESS_PRIORITY,
                priority=2
            )
        ]
    
    def _initialize_default_services(self):
        """Initialize default service endpoints"""
        
        services = [
            ("content-processor", "http://content-processor:8080", 3, 50),
            ("ai-enhancement", "http://ai-enhancement:8080", 2, 20),
            ("media-processor", "http://media-processor:8080", 4, 30),
            ("collaboration-engine", "http://collaboration:8080", 3, 100),
            ("matching-service", "http://matching:8080", 2, 50),
            ("payment-processor", "http://payment:8080", 5, 200),
            ("revenue-calculator", "http://revenue:8080", 3, 100),
            ("analytics-processor", "http://analytics:8080", 2, 500),
            ("data-warehouse", "http://warehouse:8080", 1, 1000),
            ("ai-processor", "http://ai-proc:8080", 4, 50),
            ("ml-inference", "http://ml-inference:8080", 5, 30),
            ("gpu-cluster", "http://gpu-cluster:8080", 6, 10),
            ("user-service", "http://user:8080", 3, 200),
            ("profile-manager", "http://profile:8080", 2, 150),
            ("notification-service", "http://notifications:8080", 3, 300),
            ("email-service", "http://email:8080", 2, 100),
            ("push-service", "http://push:8080", 4, 500)
        ]
        
        for service_id, url, weight, max_concurrent in services:
            self.service_endpoints[service_id] = ServiceEndpoint(
                service_id=service_id,
                endpoint_url=url,
                weight=weight,
                max_concurrent=max_concurrent,
                health_status=ServiceHealth.HEALTHY  # Assume healthy initially
            )
    
    async def route_event(self, event_data: Dict[str, Any]) -> RoutingDecision:
        """Route event to appropriate service"""
        
        start_time = time.time()
        event_id = event_data.get("event_id", "unknown")
        event_type = event_data.get("event_type", "")
        
        try:
            # Find matching routing rule
            matching_rule = await self._find_matching_rule(event_data)
            
            if not matching_rule:
                logger.warning(f"No routing rule found for event type: {event_type}")
                # Default to first available service
                if self.service_endpoints:
                    default_service = list(self.service_endpoints.keys())[0]
                    decision = RoutingDecision(
                        event_id=event_id,
                        selected_service=default_service,
                        routing_rule="default",
                        routing_strategy=RoutingStrategy.ROUND_ROBIN,
                        decision_factors={"reason": "no_matching_rule"},
                        confidence=0.3,
                        estimated_processing_time=5.0
                    )
                else:
                    raise ValueError("No services available for routing")
            else:
                # Apply routing strategy
                decision = await self._apply_routing_strategy(event_data, matching_rule)
            
            # Record routing decision
            self.routing_history.append(decision)
            
            # Update metrics
            self.metrics.total_routed += 1
            self.metrics.routes_by_service[decision.selected_service] += 1
            self.metrics.routes_by_strategy[decision.routing_strategy.value] += 1
            
            decision_time = (time.time() - start_time) * 1000
            self.metrics.avg_decision_time = (self.metrics.avg_decision_time * (self.metrics.total_routed - 1) + decision_time) / self.metrics.total_routed
            
            # Update service load
            if decision.selected_service in self.service_endpoints:
                self.service_endpoints[decision.selected_service].current_load += 1
            
            logger.debug(f"Routed event {event_id} to {decision.selected_service} using {decision.routing_strategy.value}")
            return decision
            
        except Exception as e:
            self.metrics.failed_routes += 1
            logger.error(f"Failed to route event {event_id}: {e}")
            raise
    
    async def _find_matching_rule(self, event_data: Dict[str, Any]) -> Optional[RoutingRule]:
        """Find routing rule that matches the event"""
        
        event_type = event_data.get("event_type", "")
        
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.routing_rules, key=lambda r: r.priority, reverse=False)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Check event pattern match
            if self._event_matches_pattern(event_type, rule.event_pattern):
                # Check additional conditions
                if await self._check_rule_conditions(event_data, rule.conditions):
                    return rule
        
        return None
    
    def _event_matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches routing pattern"""
        
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return event_type.startswith(prefix)
        
        return event_type == pattern
    
    async def _check_rule_conditions(self, event_data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if event meets rule conditions"""
        
        if not conditions:
            return True
        
        payload = event_data.get("payload", {})
        business_metadata = event_data.get("business_metadata", {})
        
        for condition_key, condition_value in conditions.items():
            # Get actual value from event
            actual_value = None
            
            if condition_key in payload:
                actual_value = payload[condition_key]
            elif condition_key in business_metadata:
                actual_value = business_metadata[condition_key]
            elif condition_key in event_data:
                actual_value = event_data[condition_key]
            
            # Check condition
            if isinstance(condition_value, list):
                if actual_value not in condition_value:
                    return False
            elif isinstance(condition_value, str):
                if actual_value != condition_value:
                    return False
            elif isinstance(condition_value, dict):
                # Complex condition (e.g., {"min": 10, "max": 100})
                if "min" in condition_value and actual_value < condition_value["min"]:
                    return False
                if "max" in condition_value and actual_value > condition_value["max"]:
                    return False
        
        return True
    
    async def _apply_routing_strategy(self, event_data: Dict[str, Any], rule: RoutingRule) -> RoutingDecision:
        """Apply routing strategy to select service"""
        
        event_id = event_data.get("event_id", "unknown")
        available_services = await self._get_available_services(rule.target_services)
        
        if not available_services:
            raise ValueError(f"No available services for rule: {rule.name}")
        
        decision_factors = {"rule": rule.name, "available_services": len(available_services)}
        
        if rule.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            selected_service = await self._round_robin_selection(available_services, decision_factors)
        
        elif rule.routing_strategy == RoutingStrategy.WEIGHTED:
            selected_service = await self._weighted_selection(available_services, decision_factors)
        
        elif rule.routing_strategy == RoutingStrategy.BUSINESS_PRIORITY:
            selected_service = await self._business_priority_selection(event_data, available_services, decision_factors)
        
        elif rule.routing_strategy == RoutingStrategy.LOAD_BALANCED:
            selected_service = await self._load_balanced_selection(available_services, decision_factors)
        
        elif rule.routing_strategy == RoutingStrategy.AFFINITY:
            selected_service = await self._affinity_selection(event_data, available_services, decision_factors)
        
        elif rule.routing_strategy == RoutingStrategy.FAILOVER:
            selected_service = await self._failover_selection(available_services, decision_factors)
        
        else:
            selected_service = available_services[0]  # Default to first
            decision_factors["strategy"] = "default"
        
        # Calculate confidence and estimated processing time
        confidence = await self._calculate_routing_confidence(selected_service, event_data, decision_factors)
        estimated_time = await self._estimate_processing_time(selected_service, event_data)
        
        return RoutingDecision(
            event_id=event_id,
            selected_service=selected_service,
            routing_rule=rule.name,
            routing_strategy=rule.routing_strategy,
            decision_factors=decision_factors,
            confidence=confidence,
            estimated_processing_time=estimated_time
        )
    
    async def _get_available_services(self, target_services: List[str]) -> List[str]:
        """Get list of available and healthy services"""
        
        available = []
        
        for service_id in target_services:
            if service_id in self.service_endpoints:
                endpoint = self.service_endpoints[service_id]
                
                # Check health and capacity
                if (endpoint.health_status in [ServiceHealth.HEALTHY, ServiceHealth.DEGRADED] and
                    endpoint.current_load < endpoint.max_concurrent):
                    available.append(service_id)
        
        return available
    
    async def _round_robin_selection(self, services: List[str], factors: Dict[str, Any]) -> str:
        """Round-robin service selection"""
        
        # Use total routed count for round-robin
        index = self.metrics.total_routed % len(services)
        factors["selection_method"] = "round_robin"
        factors["selected_index"] = index
        
        return services[index]
    
    async def _weighted_selection(self, services: List[str], factors: Dict[str, Any]) -> str:
        """Weighted service selection based on service weights"""
        
        weights = []
        for service_id in services:
            endpoint = self.service_endpoints[service_id]
            # Adjust weight based on current load
            adjusted_weight = endpoint.weight * (1 - endpoint.current_load / endpoint.max_concurrent)
            weights.append(max(0.1, adjusted_weight))  # Minimum weight of 0.1
        
        # Weighted random selection
        total_weight = sum(weights)
        random_value = random.random() * total_weight
        
        cumulative_weight = 0
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                factors["selection_method"] = "weighted"
                factors["weights"] = weights
                factors["selected_weight"] = weight
                return services[i]
        
        return services[-1]  # Fallback
    
    async def _business_priority_selection(self, event_data: Dict[str, Any], 
                                         services: List[str], factors: Dict[str, Any]) -> str:
        """Business priority-based service selection"""
        
        business_metadata = event_data.get("business_metadata", {})
        user_tier = business_metadata.get("user_tier", "free")
        business_priority = business_metadata.get("priority", "normal")
        
        # Define service tiers
        service_tiers = {
            "premium": ["ai-enhancement", "gpu-cluster", "ml-inference"],
            "standard": ["content-processor", "ai-processor", "collaboration-engine"],
            "basic": ["analytics-processor", "data-warehouse"]
        }
        
        # Select based on user tier and business priority
        if user_tier == "enterprise" or business_priority == "critical":
            preferred_services = service_tiers.get("premium", [])
        elif user_tier == "premium" or business_priority == "high":
            preferred_services = service_tiers.get("standard", [])
        else:
            preferred_services = service_tiers.get("basic", [])
        
        # Find intersection with available services
        candidates = [s for s in services if s in preferred_services]
        
        if not candidates:
            candidates = services  # Fallback to any available
        
        # Select service with lowest load among candidates
        selected = min(candidates, key=lambda s: self.service_endpoints[s].current_load)
        
        factors["selection_method"] = "business_priority"
        factors["user_tier"] = user_tier
        factors["business_priority"] = business_priority
        factors["preferred_tier"] = "premium" if user_tier == "enterprise" else "standard" if user_tier == "premium" else "basic"
        
        return selected
    
    async def _load_balanced_selection(self, services: List[str], factors: Dict[str, Any]) -> str:
        """Load-balanced service selection"""
        
        # Calculate load ratios
        load_info = []
        for service_id in services:
            endpoint = self.service_endpoints[service_id]
            load_ratio = endpoint.current_load / endpoint.max_concurrent
            load_info.append((service_id, load_ratio))
        
        # Select service with lowest load ratio
        selected_service = min(load_info, key=lambda x: x[1])[0]
        
        factors["selection_method"] = "load_balanced"
        factors["load_ratios"] = {service: ratio for service, ratio in load_info}
        
        return selected_service
    
    async def _affinity_selection(self, event_data: Dict[str, Any], 
                                services: List[str], factors: Dict[str, Any]) -> str:
        """Affinity-based service selection"""
        
        user_id = event_data.get("user_id")
        
        if user_id and user_id in self.service_affinities:
            # Find service with highest affinity score
            affinities = self.service_affinities[user_id]
            
            best_service = None
            best_affinity = -1
            
            for service_id in services:
                affinity_score = affinities.get(service_id, 0)
                if affinity_score > best_affinity:
                    best_affinity = affinity_score
                    best_service = service_id
            
            if best_service:
                factors["selection_method"] = "affinity"
                factors["affinity_score"] = best_affinity
                return best_service
        
        # Fallback to load balancing
        return await self._load_balanced_selection(services, factors)
    
    async def _failover_selection(self, services: List[str], factors: Dict[str, Any]) -> str:
        """Failover-based service selection"""
        
        # Order services by health and capacity
        service_scores = []
        
        for service_id in services:
            endpoint = self.service_endpoints[service_id]
            
            # Health score
            health_score = {
                ServiceHealth.HEALTHY: 1.0,
                ServiceHealth.DEGRADED: 0.5,
                ServiceHealth.UNHEALTHY: 0.1,
                ServiceHealth.UNKNOWN: 0.3
            }.get(endpoint.health_status, 0.3)
            
            # Capacity score
            capacity_score = 1 - (endpoint.current_load / endpoint.max_concurrent)
            
            # Combined score
            total_score = health_score * 0.7 + capacity_score * 0.3
            service_scores.append((service_id, total_score))
        
        # Select service with highest score
        selected_service = max(service_scores, key=lambda x: x[1])[0]
        
        factors["selection_method"] = "failover"
        factors["service_scores"] = {service: score for service, score in service_scores}
        
        return selected_service
    
    async def _calculate_routing_confidence(self, selected_service: str, 
                                          event_data: Dict[str, Any], 
                                          factors: Dict[str, Any]) -> float:
        """Calculate confidence in routing decision"""
        
        confidence = 0.5  # Base confidence
        
        # Service health increases confidence
        if selected_service in self.service_endpoints:
            endpoint = self.service_endpoints[selected_service]
            
            health_boost = {
                ServiceHealth.HEALTHY: 0.3,
                ServiceHealth.DEGRADED: 0.1,
                ServiceHealth.UNHEALTHY: -0.2,
                ServiceHealth.UNKNOWN: 0.0
            }.get(endpoint.health_status, 0.0)
            
            confidence += health_boost
            
            # Load factor
            load_ratio = endpoint.current_load / endpoint.max_concurrent
            load_boost = (1 - load_ratio) * 0.2
            confidence += load_boost
        
        # Rule specificity increases confidence
        if factors.get("rule") != "default":
            confidence += 0.2
        
        # Business alignment increases confidence
        if factors.get("selection_method") == "business_priority":
            confidence += 0.15
        
        return min(1.0, max(0.0, confidence))
    
    async def _estimate_processing_time(self, selected_service: str, event_data: Dict[str, Any]) -> float:
        """Estimate processing time for selected service"""
        
        base_times = {
            "content-processor": 2.0,
            "ai-enhancement": 10.0,
            "media-processor": 5.0,
            "collaboration-engine": 1.0,
            "matching-service": 3.0,
            "payment-processor": 0.5,
            "revenue-calculator": 1.0,
            "analytics-processor": 0.3,
            "data-warehouse": 2.0,
            "ai-processor": 8.0,
            "ml-inference": 12.0,
            "gpu-cluster": 15.0,
            "user-service": 0.5,
            "profile-manager": 1.0,
            "notification-service": 0.2,
            "email-service": 1.0,
            "push-service": 0.1
        }
        
        base_time = base_times.get(selected_service, 2.0)
        
        # Adjust for current load
        if selected_service in self.service_endpoints:
            endpoint = self.service_endpoints[selected_service]
            load_multiplier = 1 + (endpoint.current_load / endpoint.max_concurrent) * 0.5
            base_time *= load_multiplier
        
        # Adjust for event complexity
        payload_size = len(str(event_data.get("payload", {})))
        complexity_multiplier = 1 + (payload_size / 10000) * 0.2  # 20% increase per 10KB
        
        return base_time * complexity_multiplier
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics"""
        
        return {
            "total_events_routed": self.metrics.total_routed,
            "successful_routes": self.metrics.successful_routes,
            "failed_routes": self.metrics.failed_routes,
            "success_rate": self.metrics.successful_routes / max(1, self.metrics.total_routed),
            "average_decision_time_ms": self.metrics.avg_decision_time,
            "routes_by_service": dict(self.metrics.routes_by_service),
            "routes_by_strategy": dict(self.metrics.routes_by_strategy),
            "active_services": len([s for s in self.service_endpoints.values() if s.health_status == ServiceHealth.HEALTHY]),
            "degraded_services": len([s for s in self.service_endpoints.values() if s.health_status == ServiceHealth.DEGRADED]),
            "total_service_load": sum(s.current_load for s in self.service_endpoints.values()),
            "routing_rules_active": len([r for r in self.routing_rules if r.enabled])
        }


# Export main classes
__all__ = [
    'EventRoutingCoordinator',
    'RoutingStrategy',
    'ServiceHealth',
    'RoutingRule',
    'ServiceEndpoint',
    'RoutingDecision',
    'RoutingMetrics'
]