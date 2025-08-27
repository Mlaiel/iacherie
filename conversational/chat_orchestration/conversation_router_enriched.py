"""
Conversation Router - Enterprise intelligent conversation routing
================================================================

Advanced conversation routing system for multi-format content creators
with intelligent routing based on creator type, content context, workflow stage,
monetization opportunities, and collaboration potential.

Features:
- Multi-dimensional routing intelligence with creator specialization
- Workflow-aware routing for different creation stages
- Content protection and monetization routing integration
- Real-time adaptive routing based on conversation context
- Cross-platform routing optimization and analytics
- Advanced load balancing and performance monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are proprietary intellectual property of Fahed Mlaiel.
Unauthorized copying, modification, distribution, or use without explicit written
permission is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
import hashlib

from backend.ai.models import ConversationalAI
from backend.content_protection.fingerprinting import ContentProtectionService
from backend.core.config import settings
from backend.utils.load_balancer import LoadBalancer
from backend.utils.performance_monitor import PerformanceMonitor


class RoutingStrategy(Enum):
    """Different routing strategies"""
    CREATOR_SPECIALIZED = "creator_specialized"
    WORKFLOW_OPTIMIZED = "workflow_optimized"
    MONETIZATION_FOCUSED = "monetization_focused"
    COLLABORATION_ENHANCED = "collaboration_enhanced"
    PROTECTION_PRIORITY = "protection_priority"
    PERFORMANCE_BALANCED = "performance_balanced"
    CONTEXT_ADAPTIVE = "context_adaptive"
    EMERGENCY_FALLBACK = "emergency_fallback"


class RoutingPriority(Enum):
    """Routing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class RouterHealthStatus(Enum):
    """Router health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    FAILING = "failing"
    OFFLINE = "offline"


@dataclass
class RoutingDestination:
    """Routing destination configuration"""
    destination_id: str
    name: str
    specializations: List[str]
    capabilities: List[str]
    creator_types: List[str]
    workflow_stages: List[str]
    max_capacity: int
    current_load: int = 0
    performance_score: float = 1.0
    health_status: RouterHealthStatus = RouterHealthStatus.HEALTHY
    response_time_avg: float = 0.0
    success_rate: float = 1.0
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingRule:
    """Routing rule definition"""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    destination_preferences: List[str]
    priority: RoutingPriority
    weight: float = 1.0
    active: bool = True
    success_rate: float = 1.0
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingDecision:
    """Routing decision result"""
    decision_id: str
    session_id: str
    destination: RoutingDestination
    strategy: RoutingStrategy
    confidence: float
    reasoning: List[str]
    alternative_destinations: List[RoutingDestination] = field(default_factory=list)
    routing_metadata: Dict[str, Any] = field(default_factory=dict)
    performance_predictions: Dict[str, float] = field(default_factory=dict)
    estimated_response_time: float = 0.0
    priority: RoutingPriority = RoutingPriority.NORMAL
    fallback_options: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingAnalytics:
    """Routing analytics and metrics"""
    total_routes: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    avg_decision_time: float = 0.0
    avg_response_time: float = 0.0
    strategy_performance: Dict[str, float] = field(default_factory=dict)
    destination_utilization: Dict[str, float] = field(default_factory=dict)
    creator_type_distribution: Dict[str, int] = field(default_factory=dict)
    workflow_stage_distribution: Dict[str, int] = field(default_factory=dict)
    peak_load_times: List[datetime] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)


class EnterpriseConversationRouter:
    """
    Enterprise-grade conversation routing system providing intelligent routing
    decisions based on creator type, workflow context, monetization opportunities,
    and system performance for optimized AI interactions.
    
    This router provides:
    - Multi-dimensional routing intelligence with creator specialization
    - Adaptive routing strategies based on conversation context
    - Real-time load balancing and performance optimization
    - Advanced routing analytics and optimization recommendations
    - Monetization and collaboration opportunity routing
    - Content protection priority routing integration
    """
    
    def __init__(
        self,
        ai_engine: ConversationalAI,
        protection_service: ContentProtectionService,
        load_balancer: Optional[LoadBalancer] = None,
        performance_monitor: Optional[PerformanceMonitor] = None
    ):
        self.ai_engine = ai_engine
        self.protection = protection_service
        self.load_balancer = load_balancer or LoadBalancer()
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        
        # Routing infrastructure
        self.destinations: Dict[str, RoutingDestination] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.routing_history: deque = deque(maxlen=10000)
        
        # Routing strategies
        self.routing_strategies: Dict[RoutingStrategy, Callable] = {
            RoutingStrategy.CREATOR_SPECIALIZED: self._route_by_creator_specialization,
            RoutingStrategy.WORKFLOW_OPTIMIZED: self._route_by_workflow_optimization,
            RoutingStrategy.MONETIZATION_FOCUSED: self._route_by_monetization_focus,
            RoutingStrategy.COLLABORATION_ENHANCED: self._route_by_collaboration_enhancement,
            RoutingStrategy.PROTECTION_PRIORITY: self._route_by_protection_priority,
            RoutingStrategy.PERFORMANCE_BALANCED: self._route_by_performance_balance,
            RoutingStrategy.CONTEXT_ADAPTIVE: self._route_by_context_adaptation,
            RoutingStrategy.EMERGENCY_FALLBACK: self._route_emergency_fallback
        }
        
        # Analytics and monitoring
        self.analytics = RoutingAnalytics()
        self.session_routing_cache: Dict[str, RoutingDecision] = {}
        
        # Configuration
        self.enable_adaptive_routing = settings.get("routing.enable_adaptive", True)
        self.enable_load_balancing = settings.get("routing.enable_load_balancing", True)
        self.cache_routing_decisions = settings.get("routing.cache_decisions", True)
        self.health_check_interval = settings.get("routing.health_check_interval", 60)
        
        # Initialize destinations and rules
        self._initialize_routing_destinations()
        self._initialize_routing_rules()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Start background tasks
        asyncio.create_task(self._health_monitoring_loop())
        asyncio.create_task(self._analytics_optimization_loop())
    
    async def route_conversation(
        self,
        message_history: List[Dict[str, Any]],
        processed_message: Any,  # ProcessedMessage object
        creator_profile: Any,  # CreatorProfile object
        context_analysis: Any,  # ContextAnalysisResult object
        content_analysis: Optional[Dict[str, Any]] = None,
        routing_hints: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Make intelligent routing decision for conversation processing
        
        Args:
            message_history: Recent conversation history
            processed_message: Current processed message
            creator_profile: Creator profile with specializations
            context_analysis: Context analysis result
            content_analysis: Content analysis results
            routing_hints: Optional routing hints from upstream systems
            
        Returns:
            RoutingDecision with optimal destination and reasoning
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            session_id = getattr(processed_message, 'session_id', str(uuid.uuid4()))
            
            # Check for cached routing decision
            if self.cache_routing_decisions and session_id in self.session_routing_cache:
                cached_decision = self.session_routing_cache[session_id]
                if self._is_routing_cache_valid(cached_decision, context_analysis):
                    self.logger.info(f"Using cached routing decision for session {session_id}")
                    return cached_decision
            
            # Determine optimal routing strategy
            optimal_strategy = await self._determine_optimal_strategy(
                processed_message,
                creator_profile,
                context_analysis,
                content_analysis,
                routing_hints
            )
            
            # Calculate routing priority
            routing_priority = await self._calculate_routing_priority(
                processed_message,
                context_analysis,
                content_analysis
            )
            
            # Apply routing strategy
            routing_candidates = await self.routing_strategies[optimal_strategy](
                processed_message,
                creator_profile,
                context_analysis,
                content_analysis,
                routing_hints
            )
            
            # Apply load balancing and performance optimization
            if self.enable_load_balancing:
                routing_candidates = await self._apply_load_balancing(
                    routing_candidates,
                    routing_priority
                )
            
            # Select best destination
            best_destination = await self._select_best_destination(
                routing_candidates,
                processed_message,
                context_analysis,
                routing_priority
            )
            
            # Generate routing reasoning
            reasoning = await self._generate_routing_reasoning(
                optimal_strategy,
                best_destination,
                creator_profile,
                context_analysis
            )
            
            # Prepare alternative destinations
            alternative_destinations = routing_candidates[:3]  # Top 3 alternatives
            if best_destination in alternative_destinations:
                alternative_destinations.remove(best_destination)
            
            # Calculate performance predictions
            performance_predictions = await self._predict_routing_performance(
                best_destination,
                processed_message,
                context_analysis
            )
            
            # Generate fallback options
            fallback_options = await self._generate_fallback_options(
                best_destination,
                routing_candidates,
                routing_priority
            )
            
            # Calculate decision time
            decision_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create routing decision
            decision = RoutingDecision(
                decision_id=decision_id,
                session_id=session_id,
                destination=best_destination,
                strategy=optimal_strategy,
                confidence=await self._calculate_routing_confidence(
                    best_destination, routing_candidates, context_analysis
                ),
                reasoning=reasoning,
                alternative_destinations=alternative_destinations,
                routing_metadata={
                    "decision_time_ms": decision_time,
                    "strategy_scores": await self._get_strategy_scores(
                        processed_message, creator_profile, context_analysis
                    ),
                    "load_balancing_applied": self.enable_load_balancing,
                    "cache_hit": False,
                    "creator_type": creator_profile.creator_type.value,
                    "workflow_stage": getattr(context_analysis.conversation_state, 'creator_workflow_stage', 'unknown')
                },
                performance_predictions=performance_predictions,
                estimated_response_time=performance_predictions.get("response_time", 1000.0),
                priority=routing_priority,
                fallback_options=fallback_options,
                timestamp=datetime.utcnow()
            )
            
            # Cache routing decision
            if self.cache_routing_decisions:
                self.session_routing_cache[session_id] = decision
            
            # Update destination load
            best_destination.current_load += 1
            
            # Record routing analytics
            await self._record_routing_analytics(decision, start_time)
            
            # Store routing history
            self.routing_history.append({
                "decision_id": decision_id,
                "timestamp": decision.timestamp.isoformat(),
                "strategy": optimal_strategy.value,
                "destination": best_destination.destination_id,
                "creator_type": creator_profile.creator_type.value,
                "confidence": decision.confidence,
                "decision_time_ms": decision_time
            })
            
            self.logger.info(
                f"Routed conversation {decision_id} to {best_destination.name} "
                f"(strategy: {optimal_strategy.value}, confidence: {decision.confidence:.2f})"
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Failed to route conversation {decision_id}: {str(e)}")
            
            # Return emergency fallback routing
            return await self._create_emergency_routing(
                decision_id,
                getattr(processed_message, 'session_id', 'unknown'),
                creator_profile,
                str(e)
            )
    
    async def _determine_optimal_strategy(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> RoutingStrategy:
        """Determine the optimal routing strategy"""
        
        strategy_scores = {}
        
        # Score creator specialization strategy
        if creator_profile.creator_type.value in ["musician", "photographer", "blogger"]:
            strategy_scores[RoutingStrategy.CREATOR_SPECIALIZED] = 0.8
        else:
            strategy_scores[RoutingStrategy.CREATOR_SPECIALIZED] = 0.5
        
        # Score workflow optimization strategy
        workflow_stage = getattr(context_analysis.conversation_state, 'creator_workflow_stage', None)
        if workflow_stage and workflow_stage != 'unknown':
            strategy_scores[RoutingStrategy.WORKFLOW_OPTIMIZED] = 0.9
        else:
            strategy_scores[RoutingStrategy.WORKFLOW_OPTIMIZED] = 0.3
        
        # Score monetization focus strategy
        monetization_context = getattr(context_analysis, 'monetization_context', {})
        monetization_readiness = monetization_context.get("readiness", 0.0)
        strategy_scores[RoutingStrategy.MONETIZATION_FOCUSED] = monetization_readiness
        
        # Score collaboration enhancement strategy
        collaboration_opportunities = getattr(context_analysis, 'collaboration_opportunities', [])
        if collaboration_opportunities:
            strategy_scores[RoutingStrategy.COLLABORATION_ENHANCED] = 0.7
        else:
            strategy_scores[RoutingStrategy.COLLABORATION_ENHANCED] = 0.2
        
        # Score protection priority strategy
        protection_recommendations = getattr(context_analysis, 'protection_recommendations', [])
        if protection_recommendations:
            strategy_scores[RoutingStrategy.PROTECTION_PRIORITY] = 0.8
        else:
            strategy_scores[RoutingStrategy.PROTECTION_PRIORITY] = 0.3
        
        # Score performance balanced strategy
        system_load = await self._get_system_load()
        if system_load > 0.8:
            strategy_scores[RoutingStrategy.PERFORMANCE_BALANCED] = 0.9
        else:
            strategy_scores[RoutingStrategy.PERFORMANCE_BALANCED] = 0.6
        
        # Score context adaptive strategy
        context_quality = len(getattr(context_analysis, 'context_dimensions', {}))
        if context_quality > 5:
            strategy_scores[RoutingStrategy.CONTEXT_ADAPTIVE] = 0.8
        else:
            strategy_scores[RoutingStrategy.CONTEXT_ADAPTIVE] = 0.4
        
        # Apply routing hints
        if routing_hints:
            preferred_strategy = routing_hints.get("preferred_strategy")
            if preferred_strategy and preferred_strategy in strategy_scores:
                strategy_scores[RoutingStrategy(preferred_strategy)] += 0.2
        
        # Select strategy with highest score
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        
        self.logger.debug(f"Strategy scores: {strategy_scores}, selected: {best_strategy.value}")
        
        return best_strategy
    
    async def _calculate_routing_priority(
        self,
        processed_message: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]]
    ) -> RoutingPriority:
        """Calculate routing priority for the message"""
        
        priority_score = 0.5  # Base priority
        
        # Check for urgent indicators
        if hasattr(processed_message, 'urgency_indicators'):
            urgency_indicators = processed_message.urgency_indicators
            if urgency_indicators:
                priority_score += 0.3
        
        # Check protection alerts
        protection_recommendations = getattr(context_analysis, 'protection_recommendations', [])
        urgent_protection = any(
            rec.get("urgency") == "high" for rec in protection_recommendations
        )
        if urgent_protection:
            priority_score += 0.4
        
        # Check monetization opportunities
        monetization_context = getattr(context_analysis, 'monetization_context', {})
        if monetization_context.get("timeline") == "immediate":
            priority_score += 0.2
        
        # Check collaboration deadlines
        collaboration_opportunities = getattr(context_analysis, 'collaboration_opportunities', [])
        time_sensitive_collab = any(
            "deadline" in str(opp.get("description", "")).lower() 
            for opp in collaboration_opportunities
        )
        if time_sensitive_collab:
            priority_score += 0.2
        
        # Map priority score to enum
        if priority_score >= 0.9:
            return RoutingPriority.CRITICAL
        elif priority_score >= 0.7:
            return RoutingPriority.HIGH
        elif priority_score >= 0.4:
            return RoutingPriority.NORMAL
        elif priority_score >= 0.2:
            return RoutingPriority.LOW
        else:
            return RoutingPriority.BACKGROUND
    
    # Routing strategy implementations
    async def _route_by_creator_specialization(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on creator type specialization"""
        
        creator_type = creator_profile.creator_type.value
        specialized_destinations = []
        
        for destination in self.destinations.values():
            if destination.health_status == RouterHealthStatus.HEALTHY:
                # Check creator type match
                if creator_type in destination.creator_types:
                    specialized_destinations.append(destination)
                
                # Check specialization overlap
                specialization_overlap = set(creator_profile.specializations) & set(destination.specializations)
                if specialization_overlap:
                    specialized_destinations.append(destination)
        
        # Remove duplicates and sort by performance
        unique_destinations = list(set(specialized_destinations))
        return sorted(unique_destinations, key=lambda x: x.performance_score, reverse=True)
    
    async def _route_by_workflow_optimization(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on workflow stage optimization"""
        
        workflow_stage = getattr(context_analysis.conversation_state, 'creator_workflow_stage', 'planning')
        workflow_destinations = []
        
        for destination in self.destinations.values():
            if destination.health_status == RouterHealthStatus.HEALTHY:
                if workflow_stage in destination.workflow_stages:
                    workflow_destinations.append(destination)
        
        return sorted(workflow_destinations, key=lambda x: x.performance_score, reverse=True)
    
    async def _route_by_monetization_focus(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on monetization optimization"""
        
        monetization_destinations = []
        
        for destination in self.destinations.values():
            if destination.health_status == RouterHealthStatus.HEALTHY:
                if "monetization" in destination.capabilities:
                    monetization_destinations.append(destination)
        
        return sorted(monetization_destinations, key=lambda x: x.performance_score, reverse=True)
    
    async def _route_by_collaboration_enhancement(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on collaboration optimization"""
        
        collaboration_destinations = []
        
        for destination in self.destinations.values():
            if destination.health_status == RouterHealthStatus.HEALTHY:
                if "collaboration" in destination.capabilities:
                    collaboration_destinations.append(destination)
        
        return sorted(collaboration_destinations, key=lambda x: x.performance_score, reverse=True)
    
    async def _route_by_protection_priority(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on content protection priority"""
        
        protection_destinations = []
        
        for destination in self.destinations.values():
            if destination.health_status == RouterHealthStatus.HEALTHY:
                if "content_protection" in destination.capabilities:
                    protection_destinations.append(destination)
        
        return sorted(protection_destinations, key=lambda x: x.performance_score, reverse=True)
    
    async def _route_by_performance_balance(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on performance and load balancing"""
        
        # Get all healthy destinations
        healthy_destinations = [
            dest for dest in self.destinations.values()
            if dest.health_status == RouterHealthStatus.HEALTHY
        ]
        
        # Sort by load and performance
        balanced_destinations = sorted(
            healthy_destinations,
            key=lambda x: (x.current_load / x.max_capacity, -x.performance_score)
        )
        
        return balanced_destinations
    
    async def _route_by_context_adaptation(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Route based on adaptive context analysis"""
        
        # Combine multiple routing strategies based on context
        creator_destinations = await self._route_by_creator_specialization(
            processed_message, creator_profile, context_analysis, content_analysis, routing_hints
        )
        
        workflow_destinations = await self._route_by_workflow_optimization(
            processed_message, creator_profile, context_analysis, content_analysis, routing_hints
        )
        
        performance_destinations = await self._route_by_performance_balance(
            processed_message, creator_profile, context_analysis, content_analysis, routing_hints
        )
        
        # Merge and deduplicate destinations
        all_destinations = creator_destinations + workflow_destinations + performance_destinations
        unique_destinations = []
        seen_ids = set()
        
        for dest in all_destinations:
            if dest.destination_id not in seen_ids:
                unique_destinations.append(dest)
                seen_ids.add(dest.destination_id)
        
        return unique_destinations[:10]  # Limit to top 10
    
    async def _route_emergency_fallback(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any,
        content_analysis: Optional[Dict[str, Any]],
        routing_hints: Optional[Dict[str, Any]]
    ) -> List[RoutingDestination]:
        """Emergency fallback routing strategy"""
        
        # Return any available healthy destination
        emergency_destinations = [
            dest for dest in self.destinations.values()
            if dest.health_status in [RouterHealthStatus.HEALTHY, RouterHealthStatus.DEGRADED]
        ]
        
        if not emergency_destinations:
            # Create emergency fallback destination
            emergency_dest = RoutingDestination(
                destination_id="emergency_fallback",
                name="Emergency Fallback",
                specializations=["general"],
                capabilities=["basic_conversation"],
                creator_types=["all"],
                workflow_stages=["all"],
                max_capacity=1000,
                health_status=RouterHealthStatus.DEGRADED
            )
            emergency_destinations = [emergency_dest]
        
        return emergency_destinations
    
    # Helper methods
    async def _apply_load_balancing(
        self,
        destinations: List[RoutingDestination],
        priority: RoutingPriority
    ) -> List[RoutingDestination]:
        """Apply load balancing to destination list"""
        
        if not destinations:
            return destinations
        
        # Filter out overloaded destinations for non-critical priority
        if priority != RoutingPriority.CRITICAL:
            destinations = [
                dest for dest in destinations
                if (dest.current_load / dest.max_capacity) < 0.9
            ]
        
        # Sort by load and performance
        balanced_destinations = sorted(
            destinations,
            key=lambda x: (
                x.current_load / x.max_capacity,  # Load factor
                -x.performance_score,  # Performance (higher is better)
                x.response_time_avg  # Response time (lower is better)
            )
        )
        
        return balanced_destinations
    
    async def _select_best_destination(
        self,
        candidates: List[RoutingDestination],
        processed_message: Any,
        context_analysis: Any,
        priority: RoutingPriority
    ) -> RoutingDestination:
        """Select the best destination from candidates"""
        
        if not candidates:
            # Create default destination
            return RoutingDestination(
                destination_id="default",
                name="Default Handler",
                specializations=["general"],
                capabilities=["basic_conversation"],
                creator_types=["all"],
                workflow_stages=["all"],
                max_capacity=100
            )
        
        # For critical priority, always use the first (best) candidate
        if priority == RoutingPriority.CRITICAL:
            return candidates[0]
        
        # For other priorities, apply weighted random selection
        if len(candidates) == 1:
            return candidates[0]
        
        # Calculate weights based on performance and availability
        weights = []
        for dest in candidates[:5]:  # Consider top 5 candidates
            weight = dest.performance_score * (1 - dest.current_load / dest.max_capacity)
            weights.append(max(0.1, weight))  # Minimum weight
        
        # Weighted random selection
        selected_index = self._weighted_random_choice(weights)
        return candidates[selected_index]
    
    def _weighted_random_choice(self, weights: List[float]) -> int:
        """Select index based on weighted random choice"""
        total = sum(weights)
        if total == 0:
            return 0
        
        r = random.uniform(0, total)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return i
        
        return len(weights) - 1  # Fallback to last index
    
    async def _generate_routing_reasoning(
        self,
        strategy: RoutingStrategy,
        destination: RoutingDestination,
        creator_profile: Any,
        context_analysis: Any
    ) -> List[str]:
        """Generate human-readable routing reasoning"""
        
        reasoning = []
        
        # Strategy-based reasoning
        if strategy == RoutingStrategy.CREATOR_SPECIALIZED:
            reasoning.append(f"Selected for creator type specialization: {creator_profile.creator_type.value}")
        elif strategy == RoutingStrategy.WORKFLOW_OPTIMIZED:
            workflow_stage = getattr(context_analysis.conversation_state, 'creator_workflow_stage', 'unknown')
            reasoning.append(f"Optimized for workflow stage: {workflow_stage}")
        elif strategy == RoutingStrategy.MONETIZATION_FOCUSED:
            reasoning.append("Prioritized for monetization opportunities")
        elif strategy == RoutingStrategy.COLLABORATION_ENHANCED:
            reasoning.append("Enhanced for collaboration features")
        elif strategy == RoutingStrategy.PROTECTION_PRIORITY:
            reasoning.append("Prioritized for content protection capabilities")
        elif strategy == RoutingStrategy.PERFORMANCE_BALANCED:
            reasoning.append("Selected for optimal performance and load balance")
        
        # Destination-specific reasoning
        reasoning.append(f"Destination performance score: {destination.performance_score:.2f}")
        
        load_percentage = (destination.current_load / destination.max_capacity) * 100
        reasoning.append(f"Current load: {load_percentage:.1f}%")
        
        if destination.specializations:
            reasoning.append(f"Specializations: {', '.join(destination.specializations)}")
        
        return reasoning
    
    async def _predict_routing_performance(
        self,
        destination: RoutingDestination,
        processed_message: Any,
        context_analysis: Any
    ) -> Dict[str, float]:
        """Predict performance metrics for routing decision"""
        
        # Base predictions on historical data
        base_response_time = destination.response_time_avg or 1000.0
        load_factor = destination.current_load / destination.max_capacity
        
        # Adjust predictions based on load
        predicted_response_time = base_response_time * (1 + load_factor * 0.5)
        
        # Predict success rate
        predicted_success_rate = destination.success_rate * (1 - load_factor * 0.1)
        
        return {
            "response_time": predicted_response_time,
            "success_rate": predicted_success_rate,
            "load_factor": load_factor,
            "performance_score": destination.performance_score
        }
    
    async def _generate_fallback_options(
        self,
        primary_destination: RoutingDestination,
        all_candidates: List[RoutingDestination],
        priority: RoutingPriority
    ) -> List[str]:
        """Generate fallback destination options"""
        
        fallback_options = []
        
        # Add alternative healthy destinations
        for dest in all_candidates:
            if (dest.destination_id != primary_destination.destination_id and 
                dest.health_status == RouterHealthStatus.HEALTHY):
                fallback_options.append(dest.destination_id)
        
        # Add emergency fallback for critical priority
        if priority == RoutingPriority.CRITICAL:
            fallback_options.append("emergency_fallback")
        
        return fallback_options[:3]  # Limit to 3 fallback options
    
    async def _calculate_routing_confidence(
        self,
        selected_destination: RoutingDestination,
        all_candidates: List[RoutingDestination],
        context_analysis: Any
    ) -> float:
        """Calculate confidence score for routing decision"""
        
        base_confidence = 0.5
        
        # Boost confidence based on destination health
        if selected_destination.health_status == RouterHealthStatus.HEALTHY:
            base_confidence += 0.2
        
        # Boost confidence based on performance score
        base_confidence += selected_destination.performance_score * 0.2
        
        # Boost confidence based on availability
        load_factor = selected_destination.current_load / selected_destination.max_capacity
        if load_factor < 0.5:
            base_confidence += 0.1
        
        # Boost confidence based on context quality
        context_dimensions = len(getattr(context_analysis, 'context_dimensions', {}))
        if context_dimensions > 5:
            base_confidence += 0.1
        
        # Adjust based on number of candidates
        if len(all_candidates) > 1:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    async def _get_strategy_scores(
        self,
        processed_message: Any,
        creator_profile: Any,
        context_analysis: Any
    ) -> Dict[str, float]:
        """Get scoring for all routing strategies"""
        
        # This would contain the same logic as _determine_optimal_strategy
        # but return all scores instead of just the best one
        return {
            "creator_specialized": 0.8,
            "workflow_optimized": 0.7,
            "monetization_focused": 0.6,
            "collaboration_enhanced": 0.5,
            "protection_priority": 0.4,
            "performance_balanced": 0.9,
            "context_adaptive": 0.7
        }
    
    async def _get_system_load(self) -> float:
        """Get current system load"""
        if not self.destinations:
            return 0.0
        
        total_load = sum(dest.current_load for dest in self.destinations.values())
        total_capacity = sum(dest.max_capacity for dest in self.destinations.values())
        
        return total_load / total_capacity if total_capacity > 0 else 0.0
    
    def _is_routing_cache_valid(
        self,
        cached_decision: RoutingDecision,
        current_context: Any
    ) -> bool:
        """Check if cached routing decision is still valid"""
        
        # Cache is valid for 5 minutes
        cache_age = datetime.utcnow() - cached_decision.timestamp
        if cache_age > timedelta(minutes=5):
            return False
        
        # Check if destination is still healthy
        dest_id = cached_decision.destination.destination_id
        if dest_id in self.destinations:
            current_dest = self.destinations[dest_id]
            if current_dest.health_status != RouterHealthStatus.HEALTHY:
                return False
        
        return True
    
    async def _record_routing_analytics(
        self,
        decision: RoutingDecision,
        start_time: datetime
    ) -> None:
        """Record routing analytics"""
        
        decision_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update analytics
        self.analytics.total_routes += 1
        
        # Update average decision time
        total_routes = self.analytics.total_routes
        current_avg = self.analytics.avg_decision_time
        self.analytics.avg_decision_time = (
            (current_avg * (total_routes - 1) + decision_time) / total_routes
        )
        
        # Update strategy performance
        strategy_name = decision.strategy.value
        if strategy_name not in self.analytics.strategy_performance:
            self.analytics.strategy_performance[strategy_name] = decision.confidence
        else:
            current_perf = self.analytics.strategy_performance[strategy_name]
            self.analytics.strategy_performance[strategy_name] = (
                current_perf * 0.9 + decision.confidence * 0.1
            )
        
        # Update destination utilization
        dest_id = decision.destination.destination_id
        if dest_id not in self.analytics.destination_utilization:
            self.analytics.destination_utilization[dest_id] = 1
        else:
            self.analytics.destination_utilization[dest_id] += 1
    
    async def _create_emergency_routing(
        self,
        decision_id: str,
        session_id: str,
        creator_profile: Any,
        error: str
    ) -> RoutingDecision:
        """Create emergency routing decision for errors"""
        
        emergency_destination = RoutingDestination(
            destination_id="emergency",
            name="Emergency Handler",
            specializations=["emergency"],
            capabilities=["basic_conversation"],
            creator_types=["all"],
            workflow_stages=["all"],
            max_capacity=1000,
            health_status=RouterHealthStatus.DEGRADED
        )
        
        return RoutingDecision(
            decision_id=decision_id,
            session_id=session_id,
            destination=emergency_destination,
            strategy=RoutingStrategy.EMERGENCY_FALLBACK,
            confidence=0.1,
            reasoning=[f"Emergency routing due to error: {error}"],
            routing_metadata={"emergency": True, "error": error},
            priority=RoutingPriority.HIGH,
            timestamp=datetime.utcnow()
        )
    
    def _initialize_routing_destinations(self) -> None:
        """Initialize default routing destinations"""
        
        # Creator-specialized destinations
        self.destinations["musician_specialist"] = RoutingDestination(
            destination_id="musician_specialist",
            name="Music Creator Specialist",
            specializations=["music_production", "audio_editing", "composition"],
            capabilities=["music_analysis", "collaboration", "monetization"],
            creator_types=["musician"],
            workflow_stages=["creation", "editing", "distribution"],
            max_capacity=50
        )
        
        self.destinations["photographer_specialist"] = RoutingDestination(
            destination_id="photographer_specialist",
            name="Photography Specialist",
            specializations=["photography", "visual_editing", "portfolio"],
            capabilities=["image_analysis", "collaboration", "monetization"],
            creator_types=["photographer"],
            workflow_stages=["creation", "editing", "distribution"],
            max_capacity=50
        )
        
        self.destinations["content_protection"] = RoutingDestination(
            destination_id="content_protection",
            name="Content Protection Specialist",
            specializations=["copyright", "licensing", "fingerprinting"],
            capabilities=["content_protection", "legal_advice"],
            creator_types=["all"],
            workflow_stages=["protection", "distribution"],
            max_capacity=30
        )
        
        self.destinations["monetization_expert"] = RoutingDestination(
            destination_id="monetization_expert",
            name="Monetization Expert",
            specializations=["revenue_optimization", "platform_strategy", "marketing"],
            capabilities=["monetization", "analytics", "collaboration"],
            creator_types=["all"],
            workflow_stages=["monetization", "promotion"],
            max_capacity=40
        )
        
        self.destinations["general_assistant"] = RoutingDestination(
            destination_id="general_assistant",
            name="General AI Assistant",
            specializations=["general"],
            capabilities=["basic_conversation", "planning", "guidance"],
            creator_types=["all"],
            workflow_stages=["all"],
            max_capacity=100
        )
    
    def _initialize_routing_rules(self) -> None:
        """Initialize default routing rules"""
        
        # High-priority protection rule
        self.routing_rules["urgent_protection"] = RoutingRule(
            rule_id="urgent_protection",
            name="Urgent Content Protection",
            conditions={"protection_alerts": True, "urgency": "high"},
            destination_preferences=["content_protection"],
            priority=RoutingPriority.CRITICAL,
            weight=1.0
        )
        
        # Creator specialization rule
        self.routing_rules["creator_specialization"] = RoutingRule(
            rule_id="creator_specialization",
            name="Creator Type Specialization",
            conditions={"creator_type": ["musician", "photographer"]},
            destination_preferences=["musician_specialist", "photographer_specialist"],
            priority=RoutingPriority.HIGH,
            weight=0.8
        )
        
        # Monetization opportunity rule
        self.routing_rules["monetization_opportunity"] = RoutingRule(
            rule_id="monetization_opportunity",
            name="Monetization Opportunities",
            conditions={"monetization_interest": ">0.7"},
            destination_preferences=["monetization_expert"],
            priority=RoutingPriority.NORMAL,
            weight=0.6
        )
    
    # Background monitoring tasks
    async def _health_monitoring_loop(self) -> None:
        """Background task for health monitoring"""
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")
    
    async def _analytics_optimization_loop(self) -> None:
        """Background task for analytics and optimization"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._optimize_routing_rules()
                await self._cleanup_routing_cache()
            except Exception as e:
                self.logger.error(f"Analytics optimization error: {str(e)}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all destinations"""
        
        for destination in self.destinations.values():
            try:
                # Simulate health check (in real implementation, this would ping the actual service)
                health_score = random.uniform(0.8, 1.0)  # Placeholder
                
                if health_score > 0.9:
                    destination.health_status = RouterHealthStatus.HEALTHY
                elif health_score > 0.7:
                    destination.health_status = RouterHealthStatus.DEGRADED
                elif health_score > 0.5:
                    destination.health_status = RouterHealthStatus.OVERLOADED
                else:
                    destination.health_status = RouterHealthStatus.FAILING
                
                destination.last_health_check = datetime.utcnow()
                destination.performance_score = health_score
                
            except Exception as e:
                self.logger.error(f"Health check failed for {destination.destination_id}: {str(e)}")
                destination.health_status = RouterHealthStatus.FAILING
    
    async def _optimize_routing_rules(self) -> None:
        """Optimize routing rules based on analytics"""
        
        # Analyze routing performance and adjust rules
        for rule in self.routing_rules.values():
            if rule.usage_count > 100:
                # Adjust weight based on success rate
                if rule.success_rate > 0.9:
                    rule.weight = min(1.0, rule.weight + 0.1)
                elif rule.success_rate < 0.7:
                    rule.weight = max(0.1, rule.weight - 0.1)
    
    async def _cleanup_routing_cache(self) -> None:
        """Cleanup expired routing cache entries"""
        
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, decision in self.session_routing_cache.items():
            if (current_time - decision.timestamp) > timedelta(minutes=10):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_routing_cache[session_id]
    
    def get_routing_analytics(self) -> RoutingAnalytics:
        """Get current routing analytics"""
        return self.analytics
    
    def get_destination_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all destinations"""
        
        status = {}
        for dest_id, dest in self.destinations.items():
            status[dest_id] = {
                "name": dest.name,
                "health_status": dest.health_status.value,
                "current_load": dest.current_load,
                "max_capacity": dest.max_capacity,
                "load_percentage": (dest.current_load / dest.max_capacity) * 100,
                "performance_score": dest.performance_score,
                "response_time_avg": dest.response_time_avg,
                "success_rate": dest.success_rate,
                "last_health_check": dest.last_health_check.isoformat() if dest.last_health_check else None
            }
        
        return status
    
    def get_routing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent routing history"""
        
        history_list = list(self.routing_history)
        return history_list[-limit:] if limit else history_list


# Maintain backward compatibility
ConversationRouter = EnterpriseConversationRouter
