"""
Model Router
Intelligent model routing and version management for serving

This module provides:
- Dynamic model routing based on request characteristics
- A/B testing traffic splitting for model versions
- Canary deployment routing
- Model version management
- Request routing optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
import numpy as np

logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    PERFORMANCE_BASED = "performance_based"
    A_B_TEST = "a_b_test"
    CANARY = "canary"
    FEATURE_BASED = "feature_based"
    GEO_BASED = "geo_based"

class ModelStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    WARMING_UP = "warming_up"
    DRAINING = "draining"
    FAILED = "failed"

@dataclass
class ModelEndpoint:
    """Model endpoint configuration"""
    endpoint_id: str
    model_id: str
    model_version: str
    endpoint_url: str
    model_type: str
    status: ModelStatus
    weight: float = 1.0
    performance_metrics: Optional[Dict[str, float]] = None
    health_check_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RoutingRule:
    """Routing rule configuration"""
    rule_id: str
    name: str
    strategy: RoutingStrategy
    conditions: Dict[str, Any]
    target_endpoints: List[str]
    traffic_allocation: Dict[str, float]
    priority: int = 0
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class RoutingRequest:
    """Request to be routed"""
    request_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    request_data: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    routing_context: Optional[Dict[str, Any]] = None

@dataclass
class RoutingDecision:
    """Routing decision result"""
    request_id: str
    selected_endpoint: str
    routing_reason: str
    confidence_score: float
    fallback_endpoints: List[str]
    routing_metadata: Dict[str, Any]
    decision_timestamp: datetime

class ModelRouter:
    """
    Intelligent model router for enterprise serving infrastructure
    Handles dynamic routing, A/B testing, and performance optimization
    """
    
    def __init__(self):
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.routing_history: List[RoutingDecision] = []
        self.performance_cache: Dict[str, Dict[str, float]] = {}
        self.connection_counts: Dict[str, int] = {}
        self.round_robin_counters: Dict[str, int] = {}
        
    async def register_model_endpoint(
        self,
        model_id: str,
        model_version: str,
        endpoint_url: str,
        model_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new model endpoint
        
        Args:
            model_id: Model identifier
            model_version: Model version
            endpoint_url: Endpoint URL for inference
            model_type: Type of model (nlp, cv, audio, etc.)
            weight: Traffic weight for weighted routing
            metadata: Additional metadata
            
        Returns:
            endpoint_id: Unique endpoint identifier
        """
        try:
            endpoint_id = f"{model_id}_{model_version}_{uuid.uuid4().hex[:8]}"
            
            endpoint = ModelEndpoint(
                endpoint_id=endpoint_id,
                model_id=model_id,
                model_version=model_version,
                endpoint_url=endpoint_url,
                model_type=model_type,
                status=ModelStatus.WARMING_UP,
                weight=weight,
                performance_metrics={},
                health_check_url=f"{endpoint_url}/health",
                metadata=metadata or {}
            )
            
            self.endpoints[endpoint_id] = endpoint
            self.connection_counts[endpoint_id] = 0
            
            # Perform health check
            await self._perform_health_check(endpoint_id)
            
            logger.info(f"Registered model endpoint {endpoint_id} for {model_id}:{model_version}")
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to register model endpoint: {e}")
            raise
    
    async def create_routing_rule(
        self,
        name: str,
        strategy: RoutingStrategy,
        conditions: Dict[str, Any],
        target_endpoints: List[str],
        traffic_allocation: Optional[Dict[str, float]] = None,
        priority: int = 0
    ) -> str:
        """
        Create a new routing rule
        
        Args:
            name: Rule name
            strategy: Routing strategy to use
            conditions: Conditions for rule activation
            target_endpoints: List of target endpoint IDs
            traffic_allocation: Traffic allocation per endpoint
            priority: Rule priority (higher = more important)
            
        Returns:
            rule_id: Unique rule identifier
        """
        try:
            rule_id = str(uuid.uuid4())
            
            # Validate target endpoints
            for endpoint_id in target_endpoints:
                if endpoint_id not in self.endpoints:
                    raise ValueError(f"Endpoint {endpoint_id} not found")
            
            # Default traffic allocation
            if traffic_allocation is None:
                weight_per_endpoint = 1.0 / len(target_endpoints)
                traffic_allocation = {ep: weight_per_endpoint for ep in target_endpoints}
            
            # Validate traffic allocation
            if abs(sum(traffic_allocation.values()) - 1.0) > 0.001:
                raise ValueError("Traffic allocation must sum to 1.0")
            
            rule = RoutingRule(
                rule_id=rule_id,
                name=name,
                strategy=strategy,
                conditions=conditions,
                target_endpoints=target_endpoints,
                traffic_allocation=traffic_allocation,
                priority=priority
            )
            
            self.routing_rules[rule_id] = rule
            
            logger.info(f"Created routing rule {rule_id}: {name}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to create routing rule: {e}")
            raise
    
    async def route_request(self, request: RoutingRequest) -> RoutingDecision:
        """
        Route a request to appropriate model endpoint
        
        Args:
            request: Request to route
            
        Returns:
            routing_decision: Routing decision with selected endpoint
        """
        try:
            # Find applicable routing rules
            applicable_rules = await self._find_applicable_rules(request)
            
            if not applicable_rules:
                # Default routing to any active endpoint
                return await self._default_routing(request)
            
            # Sort by priority
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            # Apply highest priority rule
            selected_rule = applicable_rules[0]
            
            # Route based on strategy
            decision = await self._apply_routing_strategy(request, selected_rule)
            
            # Update connection counts
            self.connection_counts[decision.selected_endpoint] = \
                self.connection_counts.get(decision.selected_endpoint, 0) + 1
            
            # Store routing decision
            self.routing_history.append(decision)
            
            # Clean up old history (keep last 10,000 decisions)
            if len(self.routing_history) > 10000:
                self.routing_history = self.routing_history[-10000:]
            
            logger.debug(f"Routed request {request.request_id} to {decision.selected_endpoint}")
            return decision
            
        except Exception as e:
            logger.error(f"Failed to route request: {e}")
            # Fallback to any available endpoint
            return await self._emergency_fallback_routing(request)
    
    async def setup_ab_test_routing(
        self,
        name: str,
        control_endpoint: str,
        treatment_endpoint: str,
        traffic_split: float = 0.5,
        user_based: bool = True
    ) -> str:
        """
        Setup A/B test routing between two model versions
        
        Args:
            name: A/B test name
            control_endpoint: Control model endpoint ID
            treatment_endpoint: Treatment model endpoint ID
            traffic_split: Percentage of traffic to treatment (0.0-1.0)
            user_based: Whether to use consistent user-based routing
            
        Returns:
            rule_id: Created routing rule ID
        """
        try:
            conditions = {
                "ab_test": True,
                "user_based_routing": user_based
            }
            
            traffic_allocation = {
                control_endpoint: 1.0 - traffic_split,
                treatment_endpoint: traffic_split
            }
            
            rule_id = await self.create_routing_rule(
                name=f"AB_Test_{name}",
                strategy=RoutingStrategy.A_B_TEST,
                conditions=conditions,
                target_endpoints=[control_endpoint, treatment_endpoint],
                traffic_allocation=traffic_allocation,
                priority=100  # High priority for A/B tests
            )
            
            logger.info(f"Setup A/B test routing: {traffic_split:.1%} traffic to treatment")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to setup A/B test routing: {e}")
            raise
    
    async def setup_canary_deployment(
        self,
        name: str,
        stable_endpoint: str,
        canary_endpoint: str,
        canary_percentage: float = 0.05
    ) -> str:
        """
        Setup canary deployment routing
        
        Args:
            name: Canary deployment name
            stable_endpoint: Stable model endpoint ID
            canary_endpoint: Canary model endpoint ID
            canary_percentage: Percentage of traffic to canary
            
        Returns:
            rule_id: Created routing rule ID
        """
        try:
            conditions = {
                "canary_deployment": True,
                "deployment_name": name
            }
            
            traffic_allocation = {
                stable_endpoint: 1.0 - canary_percentage,
                canary_endpoint: canary_percentage
            }
            
            rule_id = await self.create_routing_rule(
                name=f"Canary_{name}",
                strategy=RoutingStrategy.CANARY,
                conditions=conditions,
                target_endpoints=[stable_endpoint, canary_endpoint],
                traffic_allocation=traffic_allocation,
                priority=90  # High priority for canary deployments
            )
            
            logger.info(f"Setup canary deployment: {canary_percentage:.1%} traffic to canary")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to setup canary deployment: {e}")
            raise
    
    async def update_endpoint_performance(
        self,
        endpoint_id: str,
        performance_metrics: Dict[str, float]
    ) -> None:
        """
        Update performance metrics for an endpoint
        
        Args:
            endpoint_id: Endpoint identifier
            performance_metrics: Updated performance metrics
        """
        try:
            if endpoint_id not in self.endpoints:
                raise ValueError(f"Endpoint {endpoint_id} not found")
            
            self.endpoints[endpoint_id].performance_metrics = performance_metrics
            self.performance_cache[endpoint_id] = performance_metrics
            
            logger.debug(f"Updated performance metrics for endpoint {endpoint_id}")
            
        except Exception as e:
            logger.error(f"Failed to update endpoint performance: {e}")
    
    async def get_routing_analytics(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get routing analytics and performance data
        
        Args:
            time_window_hours: Time window for analytics
            
        Returns:
            analytics: Routing analytics data
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Filter recent decisions
            recent_decisions = [
                d for d in self.routing_history
                if d.decision_timestamp >= cutoff_time
            ]
            
            if not recent_decisions:
                return {"message": "No routing data in time window"}
            
            # Calculate analytics
            total_requests = len(recent_decisions)
            endpoint_counts = {}
            endpoint_confidence = {}
            
            for decision in recent_decisions:
                endpoint = decision.selected_endpoint
                endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
                
                if endpoint not in endpoint_confidence:
                    endpoint_confidence[endpoint] = []
                endpoint_confidence[endpoint].append(decision.confidence_score)
            
            # Calculate distribution
            endpoint_distribution = {
                ep: count / total_requests 
                for ep, count in endpoint_counts.items()
            }
            
            # Calculate average confidence
            avg_confidence = {
                ep: np.mean(scores) 
                for ep, scores in endpoint_confidence.items()
            }
            
            analytics = {
                "time_window_hours": time_window_hours,
                "total_requests": total_requests,
                "endpoint_distribution": endpoint_distribution,
                "endpoint_request_counts": endpoint_counts,
                "average_confidence_scores": avg_confidence,
                "active_endpoints": len([ep for ep in self.endpoints.values() if ep.status == ModelStatus.ACTIVE]),
                "total_endpoints": len(self.endpoints),
                "routing_rules_count": len([r for r in self.routing_rules.values() if r.enabled])
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get routing analytics: {e}")
            raise
    
    async def _find_applicable_rules(self, request: RoutingRequest) -> List[RoutingRule]:
        """Find routing rules applicable to the request"""
        applicable_rules = []
        
        for rule in self.routing_rules.values():
            if not rule.enabled:
                continue
                
            # Check if rule conditions match request
            if await self._evaluate_rule_conditions(rule, request):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _evaluate_rule_conditions(
        self,
        rule: RoutingRule,
        request: RoutingRequest
    ) -> bool:
        """Evaluate if rule conditions match the request"""
        conditions = rule.conditions
        
        # Model type condition
        if "model_type" in conditions:
            required_type = conditions["model_type"]
            request_type = request.routing_context.get("model_type") if request.routing_context else None
            if request_type != required_type:
                return False
        
        # User ID condition
        if "user_ids" in conditions:
            if request.user_id not in conditions["user_ids"]:
                return False
        
        # Geographic condition
        if "geography" in conditions:
            user_geography = request.headers.get("X-User-Geography")
            if user_geography not in conditions["geography"]:
                return False
        
        # Time-based condition
        if "time_range" in conditions:
            current_hour = datetime.utcnow().hour
            if not (conditions["time_range"]["start"] <= current_hour <= conditions["time_range"]["end"]):
                return False
        
        return True
    
    async def _apply_routing_strategy(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Apply routing strategy from rule"""
        strategy = rule.strategy
        target_endpoints = rule.target_endpoints
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._round_robin_routing(request, rule)
        elif strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_routing(request, rule)
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_routing(request, rule)
        elif strategy == RoutingStrategy.PERFORMANCE_BASED:
            return await self._performance_based_routing(request, rule)
        elif strategy == RoutingStrategy.A_B_TEST:
            return await self._ab_test_routing(request, rule)
        elif strategy == RoutingStrategy.CANARY:
            return await self._canary_routing(request, rule)
        else:
            # Default to round robin
            return await self._round_robin_routing(request, rule)
    
    async def _round_robin_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Round robin routing strategy"""
        rule_key = rule.rule_id
        
        if rule_key not in self.round_robin_counters:
            self.round_robin_counters[rule_key] = 0
        
        # Get active endpoints
        active_endpoints = [
            ep_id for ep_id in rule.target_endpoints
            if self.endpoints[ep_id].status == ModelStatus.ACTIVE
        ]
        
        if not active_endpoints:
            raise ValueError("No active endpoints available")
        
        # Select next endpoint
        selected_endpoint = active_endpoints[
            self.round_robin_counters[rule_key] % len(active_endpoints)
        ]
        
        self.round_robin_counters[rule_key] += 1
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_endpoint=selected_endpoint,
            routing_reason=f"Round robin routing (rule: {rule.name})",
            confidence_score=1.0,
            fallback_endpoints=active_endpoints[1:],
            routing_metadata={"strategy": "round_robin", "rule_id": rule.rule_id},
            decision_timestamp=datetime.utcnow()
        )
    
    async def _weighted_round_robin_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Weighted round robin routing strategy"""
        # Implementation would use traffic allocation weights
        return await self._round_robin_routing(request, rule)  # Simplified
    
    async def _least_connections_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Least connections routing strategy"""
        active_endpoints = [
            ep_id for ep_id in rule.target_endpoints
            if self.endpoints[ep_id].status == ModelStatus.ACTIVE
        ]
        
        if not active_endpoints:
            raise ValueError("No active endpoints available")
        
        # Select endpoint with least connections
        selected_endpoint = min(
            active_endpoints,
            key=lambda ep: self.connection_counts.get(ep, 0)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_endpoint=selected_endpoint,
            routing_reason=f"Least connections routing (rule: {rule.name})",
            confidence_score=1.0,
            fallback_endpoints=[ep for ep in active_endpoints if ep != selected_endpoint],
            routing_metadata={"strategy": "least_connections", "rule_id": rule.rule_id},
            decision_timestamp=datetime.utcnow()
        )
    
    async def _performance_based_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Performance-based routing strategy"""
        active_endpoints = [
            ep_id for ep_id in rule.target_endpoints
            if self.endpoints[ep_id].status == ModelStatus.ACTIVE
        ]
        
        if not active_endpoints:
            raise ValueError("No active endpoints available")
        
        # Select endpoint with best performance
        best_endpoint = None
        best_score = -1
        
        for ep_id in active_endpoints:
            performance = self.performance_cache.get(ep_id, {})
            # Composite score: accuracy - latency penalty
            score = performance.get("accuracy", 0.5) - (performance.get("latency_ms", 100) / 1000)
            
            if score > best_score:
                best_score = score
                best_endpoint = ep_id
        
        if best_endpoint is None:
            best_endpoint = active_endpoints[0]  # Fallback
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_endpoint=best_endpoint,
            routing_reason=f"Performance-based routing (rule: {rule.name})",
            confidence_score=min(1.0, best_score + 0.5),
            fallback_endpoints=[ep for ep in active_endpoints if ep != best_endpoint],
            routing_metadata={"strategy": "performance_based", "rule_id": rule.rule_id, "score": best_score},
            decision_timestamp=datetime.utcnow()
        )
    
    async def _ab_test_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """A/B test routing strategy"""
        target_endpoints = rule.target_endpoints
        traffic_allocation = rule.traffic_allocation
        
        # Use user ID for consistent routing if available
        if request.user_id and rule.conditions.get("user_based_routing", True):
            # Hash user ID to get consistent routing
            user_hash = int(hashlib.md5(request.user_id.encode()).hexdigest(), 16)
            hash_bucket = (user_hash % 100) / 100.0
        else:
            # Random routing
            hash_bucket = np.random.random()
        
        # Select endpoint based on traffic allocation
        cumulative_prob = 0
        selected_endpoint = target_endpoints[0]  # Default
        
        for endpoint, allocation in traffic_allocation.items():
            cumulative_prob += allocation
            if hash_bucket <= cumulative_prob:
                selected_endpoint = endpoint
                break
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_endpoint=selected_endpoint,
            routing_reason=f"A/B test routing (rule: {rule.name})",
            confidence_score=1.0,
            fallback_endpoints=[ep for ep in target_endpoints if ep != selected_endpoint],
            routing_metadata={"strategy": "a_b_test", "rule_id": rule.rule_id, "hash_bucket": hash_bucket},
            decision_timestamp=datetime.utcnow()
        )
    
    async def _canary_routing(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> RoutingDecision:
        """Canary deployment routing strategy"""
        # Similar to A/B test but with specific canary logic
        return await self._ab_test_routing(request, rule)
    
    async def _default_routing(self, request: RoutingRequest) -> RoutingDecision:
        """Default routing when no rules apply"""
        active_endpoints = [
            ep_id for ep_id, ep in self.endpoints.items()
            if ep.status == ModelStatus.ACTIVE
        ]
        
        if not active_endpoints:
            raise ValueError("No active endpoints available")
        
        # Simple round robin for default
        selected_endpoint = active_endpoints[hash(request.request_id) % len(active_endpoints)]
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_endpoint=selected_endpoint,
            routing_reason="Default routing - no applicable rules",
            confidence_score=0.8,
            fallback_endpoints=active_endpoints[1:],
            routing_metadata={"strategy": "default"},
            decision_timestamp=datetime.utcnow()
        )
    
    async def _emergency_fallback_routing(self, request: RoutingRequest) -> RoutingDecision:
        """Emergency fallback routing"""
        # Return any available endpoint
        for ep_id, endpoint in self.endpoints.items():
            if endpoint.status in [ModelStatus.ACTIVE, ModelStatus.WARMING_UP]:
                return RoutingDecision(
                    request_id=request.request_id,
                    selected_endpoint=ep_id,
                    routing_reason="Emergency fallback routing",
                    confidence_score=0.5,
                    fallback_endpoints=[],
                    routing_metadata={"strategy": "emergency_fallback"},
                    decision_timestamp=datetime.utcnow()
                )
        
        raise ValueError("No endpoints available for routing")
    
    async def _perform_health_check(self, endpoint_id: str) -> bool:
        """Perform health check on endpoint"""
        try:
            endpoint = self.endpoints[endpoint_id]
            
            # In a real implementation, this would make an HTTP request to the health check URL
            # For now, we'll simulate a successful health check
            endpoint.status = ModelStatus.ACTIVE
            
            logger.info(f"Health check passed for endpoint {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for endpoint {endpoint_id}: {e}")
            if endpoint_id in self.endpoints:
                self.endpoints[endpoint_id].status = ModelStatus.FAILED
            return False