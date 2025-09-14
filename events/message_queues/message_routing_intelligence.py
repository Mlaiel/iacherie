"""Message Routing Intelligence Module

Intelligent message routing with load balancing and failover automation
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Message Routing Intelligence architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import hashlib

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Message routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    HASH_BASED = "hash_based"
    GEOGRAPHIC = "geographic"
    RESOURCE_BASED = "resource_based"
    INTELLIGENT = "intelligent"


class DestinationType(Enum):
    """Types of routing destinations"""
    QUEUE = "queue"
    WORKER = "worker"
    SERVICE = "service"
    REGION = "region"
    CLUSTER = "cluster"


class HealthStatus(Enum):
    """Health status of routing destinations"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class RoutingDestination:
    """Routing destination configuration"""
    destination_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    destination_type: DestinationType = DestinationType.QUEUE
    endpoint: str = ""
    
    # Capacity and performance
    weight: float = 1.0
    max_capacity: int = 1000
    current_load: int = 0
    avg_response_time: float = 0.0
    
    # Health monitoring
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Geographic and resource info
    region: str = "default"
    zone: str = "default"
    resources: Dict[str, Any] = field(default_factory=dict)
    
    # Routing preferences
    supported_message_types: List[str] = field(default_factory=list)
    priority_levels: List[str] = field(default_factory=list)
    
    # Statistics
    total_messages_routed: int = 0
    successful_messages: int = 0
    failed_messages: int = 0
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class RoutingRule:
    """Message routing rule"""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    priority: int = 100
    
    # Matching criteria
    message_type_patterns: List[str] = field(default_factory=list)
    sender_patterns: List[str] = field(default_factory=list)
    content_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Routing configuration
    strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    destination_pool: List[str] = field(default_factory=list)  # destination_ids
    fallback_destinations: List[str] = field(default_factory=list)
    
    # Load balancing
    load_balancing_enabled: bool = True
    failover_enabled: bool = True
    circuit_breaker_enabled: bool = True
    
    # Business logic
    business_context_required: Dict[str, Any] = field(default_factory=dict)
    custom_routing_function: Optional[str] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    message_id: str
    selected_destination: str
    strategy_used: RoutingStrategy
    decision_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    selection_criteria: Dict[str, Any] = field(default_factory=dict)
    fallback_used: bool = False
    decision_duration_ms: float = 0.0


@dataclass
class RoutingMetrics:
    """Routing system metrics"""
    total_messages: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    avg_decision_time: float = 0.0
    strategy_usage: Dict[str, int] = field(default_factory=dict)
    destination_utilization: Dict[str, float] = field(default_factory=dict)
    health_status_distribution: Dict[str, int] = field(default_factory=dict)


class AinflueBusiness:
    """Ainflue Business Routing Configuration"""
    
    # Routing destinations by service type
    ROUTING_DESTINATIONS = {
        # Content processing destinations
        "content_processors": [
            RoutingDestination(
                destination_id="content_proc_primary",
                name="Primary Content Processor",
                destination_type=DestinationType.SERVICE,
                endpoint="content-processor-primary.ainflue.internal",
                weight=2.0,
                max_capacity=500,
                supported_message_types=["content_upload", "content_validation", "content_transformation"],
                region="us-east-1",
                zone="us-east-1a"
            ),
            RoutingDestination(
                destination_id="content_proc_secondary",
                name="Secondary Content Processor", 
                destination_type=DestinationType.SERVICE,
                endpoint="content-processor-secondary.ainflue.internal",
                weight=1.5,
                max_capacity=300,
                supported_message_types=["content_upload", "content_validation"],
                region="us-east-1",
                zone="us-east-1b"
            )
        ],
        
        # AI processing destinations
        "ai_processors": [
            RoutingDestination(
                destination_id="ai_proc_gpu_cluster",
                name="GPU AI Processing Cluster",
                destination_type=DestinationType.CLUSTER,
                endpoint="ai-gpu-cluster.ainflue.internal",
                weight=3.0,
                max_capacity=100,
                supported_message_types=["ai_content_analysis", "ai_generation", "ml_inference"],
                region="us-west-2",
                zone="us-west-2a",
                resources={"gpu_count": 8, "memory_gb": 256}
            ),
            RoutingDestination(
                destination_id="ai_proc_cpu_cluster",
                name="CPU AI Processing Cluster",
                destination_type=DestinationType.CLUSTER,
                endpoint="ai-cpu-cluster.ainflue.internal",
                weight=1.0,
                max_capacity=200,
                supported_message_types=["ai_content_analysis", "text_processing"],
                region="us-west-2",
                zone="us-west-2b",
                resources={"cpu_count": 32, "memory_gb": 128}
            )
        ],
        
        # Payment processing destinations
        "payment_processors": [
            RoutingDestination(
                destination_id="payment_proc_primary",
                name="Primary Payment Processor",
                destination_type=DestinationType.SERVICE,
                endpoint="payment-processor.ainflue.internal",
                weight=1.0,
                max_capacity=50,
                supported_message_types=["payment_processing", "payout_request"],
                region="us-east-1",
                zone="us-east-1a"
            )
        ],
        
        # Analytics processing destinations
        "analytics_processors": [
            RoutingDestination(
                destination_id="analytics_batch",
                name="Batch Analytics Processor",
                destination_type=DestinationType.QUEUE,
                endpoint="analytics-batch-queue",
                weight=1.0,
                max_capacity=2000,
                supported_message_types=["analytics_processing", "report_generation"],
                region="us-central-1"
            ),
            RoutingDestination(
                destination_id="analytics_realtime",
                name="Real-time Analytics Processor",
                destination_type=DestinationType.SERVICE,
                endpoint="analytics-realtime.ainflue.internal",
                weight=2.0,
                max_capacity=500,
                supported_message_types=["realtime_analytics", "live_metrics"],
                region="us-central-1"
            )
        ]
    }
    
    # Routing rules by message type
    ROUTING_RULES = {
        "content_upload": RoutingRule(
            rule_id="content_upload_rule",
            name="Content Upload Routing",
            priority=100,
            message_type_patterns=["content_upload", "video_upload", "audio_upload"],
            strategy=RoutingStrategy.WEIGHTED_ROUND_ROBIN,
            destination_pool=["content_proc_primary", "content_proc_secondary"],
            fallback_destinations=["content_proc_secondary"],
            load_balancing_enabled=True,
            failover_enabled=True
        ),
        
        "ai_processing": RoutingRule(
            rule_id="ai_processing_rule",
            name="AI Processing Routing",
            priority=90,
            message_type_patterns=["ai_content_analysis", "ai_generation", "ml_inference"],
            strategy=RoutingStrategy.RESOURCE_BASED,
            destination_pool=["ai_proc_gpu_cluster", "ai_proc_cpu_cluster"],
            fallback_destinations=["ai_proc_cpu_cluster"],
            load_balancing_enabled=True,
            business_context_required={"requires_gpu": bool}
        ),
        
        "payment_processing": RoutingRule(
            rule_id="payment_processing_rule",
            name="Payment Processing Routing",
            priority=200,  # Highest priority
            message_type_patterns=["payment_processing", "payout_request", "refund_processing"],
            strategy=RoutingStrategy.LEAST_CONNECTIONS,
            destination_pool=["payment_proc_primary"],
            fallback_destinations=[],
            load_balancing_enabled=False,  # Single destination for consistency
            failover_enabled=False
        ),
        
        "analytics": RoutingRule(
            rule_id="analytics_rule",
            name="Analytics Processing Routing",
            priority=50,
            message_type_patterns=["analytics_processing", "report_generation"],
            strategy=RoutingStrategy.INTELLIGENT,
            destination_pool=["analytics_batch", "analytics_realtime"],
            fallback_destinations=["analytics_batch"],
            custom_routing_function="route_analytics_by_urgency"
        ),
        
        "collaboration": RoutingRule(
            rule_id="collaboration_rule",
            name="Collaboration Routing",
            priority=80,
            message_type_patterns=["collaboration_match", "collaboration_request"],
            strategy=RoutingStrategy.GEOGRAPHIC,
            destination_pool=["content_proc_primary", "content_proc_secondary"],
            load_balancing_enabled=True
        )
    }
    
    # Geographic routing preferences
    GEOGRAPHIC_PREFERENCES = {
        "us-east": ["us-east-1", "us-central-1", "us-west-2"],
        "us-west": ["us-west-2", "us-central-1", "us-east-1"],
        "eu": ["eu-west-1", "eu-central-1", "us-east-1"],
        "asia": ["ap-southeast-1", "ap-northeast-1", "us-west-2"]
    }
    
    # Custom routing functions
    CUSTOM_ROUTING_FUNCTIONS = {
        "route_analytics_by_urgency": lambda message, destinations: "analytics_realtime" 
            if message.get("business_context", {}).get("urgency") == "high" 
            else "analytics_batch",
        
        "route_by_creator_tier": lambda message, destinations: 
            next((d for d in destinations if "premium" in d), destinations[0])
            if message.get("business_context", {}).get("creator_tier") == "premium"
            else destinations[0],
        
        "route_by_content_size": lambda message, destinations:
            next((d for d in destinations if "large" in d), destinations[0])
            if message.get("business_context", {}).get("content_size", 0) > 100_000_000
            else destinations[0]
    }


class MessageRoutingIntelligence:
    """
    Intelligent message routing with load balancing and failover automation
    Supports multiple routing strategies and adaptive routing decisions
    """
    
    def __init__(self,
                 metrics_collector -> None: Optional[MetricsCollector] = None,
                 encryption_manager -> None: Optional[EncryptionManager] = None) -> None:
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Routing configuration
        self.destinations = {}  # destination_id -> RoutingDestination
        self.routing_rules = {}  # rule_id -> RoutingRule
        self.custom_routing_functions = {}  # function_name -> function
        
        # Routing state
        self.round_robin_counters = defaultdict(int)
        self.destination_connections = defaultdict(int)
        self.destination_response_times = defaultdict(deque)
        
        # Health monitoring
        self.health_check_interval = 30.0  # seconds
        self.health_check_tasks = {}
        
        # Performance tracking
        self.routing_metrics = RoutingMetrics()
        self.routing_history = deque(maxlen=10000)  # Last 10k routing decisions
        
        # Circuit breaker state
        self.circuit_breakers = {}  # destination_id -> state
        
        # Intelligent routing ML state
        self.routing_patterns = defaultdict(list)
        self.adaptive_weights = {}
        
        logger.info("Initialized Message Routing Intelligence")
    
    async def start(self) -> bool:
        """Start the routing intelligence system"""
        try:
            # Load business routing configuration
            await self._load_business_configuration()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            logger.info("Message Routing Intelligence started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start routing intelligence: {str(e)}")
            raise MessageQueueError(f"Routing intelligence startup failed: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the routing intelligence system"""
        try:
            # Stop health monitoring
            for task in self.health_check_tasks.values():
                task.cancel()
            
            logger.info("Message Routing Intelligence stopped")
            
        except Exception as e:
            logger.error(f"Error stopping routing intelligence: {str(e)}")
    
    async def route_message(self,
                          message_id: str,
                          message_type: str,
                          message_content: Dict[str, Any],
                          business_context: Dict[str, Any] = None) -> RoutingDecision:
        """Route a message to the best destination"""
        try:
            start_time = time.time()
            business_context = business_context or {}
            
            # Find applicable routing rule
            rule = await self._find_applicable_rule(message_type, message_content, business_context)
            
            if not rule:
                # No specific rule, use default routing
                rule = await self._get_default_rule()
            
            # Get available destinations
            available_destinations = await self._get_available_destinations(rule)
            
            if not available_destinations:
                raise MessageQueueError("No available destinations for routing")
            
            # Select destination based on strategy
            selected_destination = await self._select_destination(
                rule, available_destinations, message_content, business_context
            )
            
            # Create routing decision
            decision_time = time.time() - start_time
            decision = RoutingDecision(
                message_id=message_id,
                selected_destination=selected_destination,
                strategy_used=rule.strategy,
                decision_duration_ms=decision_time * 1000,
                selection_criteria={
                    "rule_id": rule.rule_id,
                    "available_destinations": len(available_destinations),
                    "strategy": rule.strategy.value
                }
            )
            
            # Update routing state
            await self._update_routing_state(selected_destination, decision)
            
            # Record decision
            self.routing_history.append(decision)
            
            # Update metrics
            await self._update_routing_metrics(decision)
            
            logger.debug(f"Routed message {message_id} to {selected_destination} using {rule.strategy.value}")
            return decision
            
        except Exception as e:
            logger.error(f"Error routing message {message_id}: {str(e)}")
            raise MessageQueueError(f"Message routing failed: {str(e)}")
    
    async def register_destination(self, destination: RoutingDestination) -> str:
        """Register a new routing destination"""
        try:
            self.destinations[destination.destination_id] = destination
            
            # Initialize health monitoring
            if destination.is_active:
                await self._start_destination_health_monitoring(destination.destination_id)
            
            logger.info(f"Registered routing destination: {destination.name}")
            return destination.destination_id
            
        except Exception as e:
            logger.error(f"Error registering destination: {str(e)}")
            raise MessageQueueError(f"Failed to register destination: {str(e)}")
    
    async def register_routing_rule(self, rule: RoutingRule) -> str:
        """Register a new routing rule"""
        try:
            self.routing_rules[rule.rule_id] = rule
            
            logger.info(f"Registered routing rule: {rule.name}")
            return rule.rule_id
            
        except Exception as e:
            logger.error(f"Error registering routing rule: {str(e)}")
            raise MessageQueueError(f"Failed to register rule: {str(e)}")
    
    async def update_destination_health(self, destination_id: str, 
                                      health_status: HealthStatus,
                                      response_time: Optional[float] = None) -> bool:
        """Update destination health status"""
        try:
            if destination_id not in self.destinations:
                return False
            
            destination = self.destinations[destination_id]
            old_status = destination.health_status
            
            destination.health_status = health_status
            destination.last_health_check = datetime.now(timezone.utc)
            
            if response_time is not None:
                # Update response time tracking
                response_times = self.destination_response_times[destination_id]
                response_times.append(response_time)
                
                # Keep only recent response times
                while len(response_times) > 100:
                    response_times.popleft()
                
                # Update average
                if response_times:
                    destination.avg_response_time = sum(response_times) / len(response_times)
            
            # Handle health status changes
            if old_status != health_status:
                await self._handle_health_status_change(destination_id, old_status, health_status)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating destination health: {str(e)}")
            return False
    
    async def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing system statistics"""
        try:
            # Calculate destination utilization
            destination_stats = {}
            for dest_id, destination in self.destinations.items():
                utilization = 0.0
                if destination.max_capacity > 0:
                    utilization = (destination.current_load / destination.max_capacity) * 100
                
                success_rate = 0.0
                if destination.total_messages_routed > 0:
                    success_rate = (destination.successful_messages / destination.total_messages_routed) * 100
                
                destination_stats[dest_id] = {
                    "name": destination.name,
                    "health_status": destination.health_status.value,
                    "utilization_percent": round(utilization, 2),
                    "success_rate": round(success_rate, 2),
                    "avg_response_time": round(destination.avg_response_time, 3),
                    "total_messages": destination.total_messages_routed,
                    "current_load": destination.current_load
                }
            
            # Calculate strategy usage
            strategy_stats = defaultdict(int)
            for decision in self.routing_history:
                strategy_stats[decision.strategy_used.value] += 1
            
            return {
                "global_metrics": {
                    "total_messages": self.routing_metrics.total_messages,
                    "successful_routes": self.routing_metrics.successful_routes,
                    "failed_routes": self.routing_metrics.failed_routes,
                    "success_rate": (
                        self.routing_metrics.successful_routes / 
                        max(self.routing_metrics.total_messages, 1)
                    ) * 100,
                    "avg_decision_time_ms": round(self.routing_metrics.avg_decision_time, 3)
                },
                "destinations": destination_stats,
                "strategy_usage": dict(strategy_stats),
                "active_rules": len([r for r in self.routing_rules.values() if r.is_active]),
                "health_distribution": self._get_health_distribution()
            }
            
        except Exception as e:
            logger.error(f"Error getting routing statistics: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_routing_configuration(self) -> Dict[str, Any]:
        """Analyze and optimize routing configuration"""
        try:
            optimization_results = {}
            
            # Analyze destination performance
            dest_analysis = await self._analyze_destination_performance()
            optimization_results["destination_analysis"] = dest_analysis
            
            # Analyze routing patterns
            pattern_analysis = await self._analyze_routing_patterns()
            optimization_results["pattern_analysis"] = pattern_analysis
            
            # Suggest configuration improvements
            suggestions = await self._generate_optimization_suggestions()
            optimization_results["suggestions"] = suggestions
            
            # Apply automatic optimizations
            auto_optimizations = await self._apply_automatic_optimizations()
            optimization_results["auto_optimizations"] = auto_optimizations
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing routing configuration: {str(e)}")
            return {"error": str(e)}
    
    # Core routing logic
    
    async def _find_applicable_rule(self, 
                                   message_type: str,
                                   message_content: Dict[str, Any],
                                   business_context: Dict[str, Any]) -> Optional[RoutingRule]:
        """Find the most applicable routing rule"""
        applicable_rules = []
        
        for rule in self.routing_rules.values():
            if not rule.is_active:
                continue
            
            # Check message type patterns
            if rule.message_type_patterns:
                if not any(pattern in message_type for pattern in rule.message_type_patterns):
                    continue
            
            # Check sender patterns
            if rule.sender_patterns:
                sender_id = business_context.get("sender_id", "")
                if not any(pattern in sender_id for pattern in rule.sender_patterns):
                    continue
            
            # Check business context requirements
            if rule.business_context_required:
                if not self._check_business_context_requirements(business_context, rule.business_context_required):
                    continue
            
            applicable_rules.append(rule)
        
        # Return highest priority rule
        if applicable_rules:
            return max(applicable_rules, key=lambda r: r.priority)
        
        return None
    
    async def _get_available_destinations(self, rule: RoutingRule) -> List[str]:
        """Get available destinations for a routing rule"""
        available = []
        
        for dest_id in rule.destination_pool:
            if dest_id not in self.destinations:
                continue
            
            destination = self.destinations[dest_id]
            
            # Check if destination is active and healthy
            if (destination.is_active and 
                destination.health_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]):
                
                # Check capacity
                if destination.current_load < destination.max_capacity:
                    available.append(dest_id)
        
        # If no primary destinations available, try fallbacks
        if not available and rule.fallback_destinations:
            for dest_id in rule.fallback_destinations:
                if dest_id in self.destinations:
                    destination = self.destinations[dest_id]
                    if (destination.is_active and 
                        destination.health_status != HealthStatus.UNHEALTHY):
                        available.append(dest_id)
        
        return available
    
    async def _select_destination(self,
                                rule: RoutingRule,
                                available_destinations: List[str],
                                message_content: Dict[str, Any],
                                business_context: Dict[str, Any]) -> str:
        """Select the best destination based on routing strategy"""
        
        if len(available_destinations) == 1:
            return available_destinations[0]
        
        strategy = rule.strategy
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._select_round_robin(rule.rule_id, available_destinations)
        
        elif strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._select_weighted_round_robin(available_destinations)
        
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return await self._select_least_connections(available_destinations)
        
        elif strategy == RoutingStrategy.LEAST_RESPONSE_TIME:
            return await self._select_least_response_time(available_destinations)
        
        elif strategy == RoutingStrategy.HASH_BASED:
            return await self._select_hash_based(message_content, available_destinations)
        
        elif strategy == RoutingStrategy.GEOGRAPHIC:
            return await self._select_geographic(business_context, available_destinations)
        
        elif strategy == RoutingStrategy.RESOURCE_BASED:
            return await self._select_resource_based(business_context, available_destinations)
        
        elif strategy == RoutingStrategy.INTELLIGENT:
            return await self._select_intelligent(rule, message_content, business_context, available_destinations)
        
        else:
            # Default to first available
            return available_destinations[0]
    
    async def _select_round_robin(self, rule_id: str, destinations: List[str]) -> str:
        """Round robin selection"""
        counter = self.round_robin_counters[rule_id]
        selected = destinations[counter % len(destinations)]
        self.round_robin_counters[rule_id] = counter + 1
        return selected
    
    async def _select_weighted_round_robin(self, destinations: List[str]) -> str:
        """Weighted round robin selection"""
        total_weight = sum(self.destinations[dest_id].weight for dest_id in destinations)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for dest_id in destinations:
            current_weight += self.destinations[dest_id].weight
            if random_value <= current_weight:
                return dest_id
        
        return destinations[0]  # Fallback
    
    async def _select_least_connections(self, destinations: List[str]) -> str:
        """Least connections selection"""
        return min(destinations, key=lambda dest_id: self.destination_connections[dest_id])
    
    async def _select_least_response_time(self, destinations: List[str]) -> str:
        """Least response time selection"""
        return min(destinations, key=lambda dest_id: self.destinations[dest_id].avg_response_time)
    
    async def _select_hash_based(self, message_content: Dict[str, Any], destinations: List[str]) -> str:
        """Hash-based consistent selection"""
        # Use message content hash for consistent routing
        content_hash = hashlib.md5(json.dumps(message_content, sort_keys=True).encode()).hexdigest()
        hash_value = int(content_hash, 16)
        return destinations[hash_value % len(destinations)]
    
    async def _select_geographic(self, business_context: Dict[str, Any], destinations: List[str]) -> str:
        """Geographic proximity selection"""
        user_region = business_context.get("user_region", "us-east")
        preferred_regions = AinflueBusiness.GEOGRAPHIC_PREFERENCES.get(user_region, ["us-east-1"])
        
        # Find destinations in preferred regions
        for region in preferred_regions:
            for dest_id in destinations:
                if self.destinations[dest_id].region == region:
                    return dest_id
        
        return destinations[0]  # Fallback
    
    async def _select_resource_based(self, business_context: Dict[str, Any], destinations: List[str]) -> str:
        """Resource requirement-based selection"""
        requires_gpu = business_context.get("requires_gpu", False)
        
        if requires_gpu:
            # Prefer GPU-enabled destinations
            gpu_destinations = [
                dest_id for dest_id in destinations
                if self.destinations[dest_id].resources.get("gpu_count", 0) > 0
            ]
            if gpu_destinations:
                return min(gpu_destinations, key=lambda dest_id: self.destinations[dest_id].current_load)
        
        # Default to least loaded
        return min(destinations, key=lambda dest_id: self.destinations[dest_id].current_load)
    
    async def _select_intelligent(self,
                                rule: RoutingRule,
                                message_content: Dict[str, Any],
                                business_context: Dict[str, Any],
                                destinations: List[str]) -> str:
        """Intelligent ML-based selection"""
        
        # Use custom routing function if specified
        if rule.custom_routing_function:
            custom_func = self.custom_routing_functions.get(rule.custom_routing_function)
            if custom_func:
                try:
                    result = custom_func({"business_context": business_context}, destinations)
                    if result in destinations:
                        return result
                except Exception as e:
                    logger.warning(f"Custom routing function failed: {str(e)}")
        
        # Fallback to weighted selection based on performance
        destination_scores = {}
        
        for dest_id in destinations:
            destination = self.destinations[dest_id]
            
            # Score based on multiple factors
            load_score = 1.0 - (destination.current_load / max(destination.max_capacity, 1))
            response_time_score = 1.0 / max(destination.avg_response_time, 0.001)
            success_rate = destination.successful_messages / max(destination.total_messages_routed, 1)
            
            # Health status modifier
            health_modifier = {
                HealthStatus.HEALTHY: 1.0,
                HealthStatus.DEGRADED: 0.7,
                HealthStatus.UNHEALTHY: 0.1,
                HealthStatus.UNKNOWN: 0.5
            }[destination.health_status]
            
            total_score = (load_score * 0.3 + response_time_score * 0.3 + 
                          success_rate * 0.2 + health_modifier * 0.2)
            
            destination_scores[dest_id] = total_score
        
        # Select destination with highest score
        return max(destination_scores.keys(), key=lambda dest_id: destination_scores[dest_id])
    
    # Helper methods
    
    async def _load_business_configuration(self) -> None:
        """Load Ainflue business routing configuration"""
        # Load destinations
        for service_type, destinations in AinflueBusiness.ROUTING_DESTINATIONS.items():
            for destination in destinations:
                await self.register_destination(destination)
        
        # Load routing rules
        for rule_name, rule in AinflueBusiness.ROUTING_RULES.items():
            await self.register_routing_rule(rule)
        
        # Load custom routing functions
        self.custom_routing_functions.update(AinflueBusiness.CUSTOM_ROUTING_FUNCTIONS)
        
        logger.info("Loaded business routing configuration")
    
    async def _get_default_rule(self) -> RoutingRule:
        """Get default routing rule"""
        return RoutingRule(
            rule_id="default",
            name="Default Routing Rule",
            strategy=RoutingStrategy.ROUND_ROBIN,
            destination_pool=list(self.destinations.keys())
        )
    
    def _check_business_context_requirements(self, 
                                           context: Dict[str, Any],
                                           requirements: Dict[str, Any]) -> bool:
        """Check if business context meets requirements"""
        for key, expected_type in requirements.items():
            if key not in context:
                return False
            
            value = context[key]
            if not isinstance(value, expected_type):
                return False
        
        return True
    
    async def _update_routing_state(self, destination_id -> None: str, decision -> None: RoutingDecision) -> None:
        """Update routing state after decision"""
        # Update connection count
        self.destination_connections[destination_id] += 1
        
        # Update destination load
        if destination_id in self.destinations:
            self.destinations[destination_id].current_load += 1
            self.destinations[destination_id].total_messages_routed += 1
    
    async def _update_routing_metrics(self, decision -> None: RoutingDecision) -> None:
        """Update routing metrics"""
        self.routing_metrics.total_messages += 1
        self.routing_metrics.successful_routes += 1
        
        # Update average decision time
        total_time = self.routing_metrics.avg_decision_time * (self.routing_metrics.total_messages - 1)
        total_time += decision.decision_duration_ms
        self.routing_metrics.avg_decision_time = total_time / self.routing_metrics.total_messages
        
        # Update strategy usage
        strategy = decision.strategy_used.value
        self.routing_metrics.strategy_usage[strategy] = self.routing_metrics.strategy_usage.get(strategy, 0) + 1
    
    async def _start_health_monitoring(self) -> None:
        """Start health monitoring for all destinations"""
        for dest_id in self.destinations.keys():
            await self._start_destination_health_monitoring(dest_id)
    
    async def _start_destination_health_monitoring(self, destination_id -> None: str) -> None:
        """Start health monitoring for a specific destination"""
        if destination_id in self.health_check_tasks:
            return  # Already monitoring
        
        task = asyncio.create_task(self._health_check_loop(destination_id))
        self.health_check_tasks[destination_id] = task
    
    async def _health_check_loop(self, destination_id -> None: str) -> None:
        """Health check loop for a destination"""
        while destination_id in self.destinations:
            try:
                # Perform health check
                health_status = await self._perform_health_check(destination_id)
                await self.update_destination_health(destination_id, health_status)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check for {destination_id}: {str(e)}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _perform_health_check(self, destination_id: str) -> HealthStatus:
        """Perform health check for a destination"""
        destination = self.destinations[destination_id]
        
        try:
            # This would perform actual health check
            # For now, simulate based on load and response time
            
            if destination.current_load > destination.max_capacity * 0.9:
                return HealthStatus.DEGRADED
            elif destination.avg_response_time > 5.0:  # 5 second threshold
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
                
        except Exception as e:
            logger.warning(f"Health check failed for {destination_id}: {str(e)}")
            return HealthStatus.UNHEALTHY
    
    async def _handle_health_status_change(self, 
                                         destination_id -> None: str,
                                         old_status -> None: HealthStatus,
                                         new_status -> None: HealthStatus) -> None:
        """Handle destination health status changes"""
        destination = self.destinations[destination_id]
        
        if new_status == HealthStatus.UNHEALTHY:
            destination.consecutive_failures += 1
            logger.warning(f"Destination {destination.name} is now unhealthy ({destination.consecutive_failures} consecutive failures)")
        
        elif new_status == HealthStatus.HEALTHY and old_status != HealthStatus.HEALTHY:
            destination.consecutive_failures = 0
            logger.info(f"Destination {destination.name} is now healthy")
    
    def _get_health_distribution(self) -> Dict[str, int]:
        """Get distribution of health statuses"""
        distribution = defaultdict(int)
        for destination in self.destinations.values():
            distribution[destination.health_status.value] += 1
        return dict(distribution)
    
    # Analysis and optimization methods
    
    async def _analyze_destination_performance(self) -> Dict[str, Any]:
        """Analyze destination performance"""
        analysis = {}
        
        for dest_id, destination in self.destinations.items():
            if destination.total_messages_routed == 0:
                continue
            
            success_rate = destination.successful_messages / destination.total_messages_routed
            utilization = destination.current_load / destination.max_capacity
            
            analysis[dest_id] = {
                "success_rate": round(success_rate * 100, 2),
                "utilization": round(utilization * 100, 2),
                "avg_response_time": round(destination.avg_response_time, 3),
                "health_status": destination.health_status.value,
                "recommendations": []
            }
            
            # Generate recommendations
            if success_rate < 0.9:
                analysis[dest_id]["recommendations"].append("Low success rate - investigate failures")
            
            if utilization > 0.8:
                analysis[dest_id]["recommendations"].append("High utilization - consider scaling")
            
            if destination.avg_response_time > 2.0:
                analysis[dest_id]["recommendations"].append("High response time - optimize performance")
        
        return analysis
    
    async def _analyze_routing_patterns(self) -> Dict[str, Any]:
        """Analyze routing patterns and effectiveness"""
        if len(self.routing_history) < 100:
            return {"status": "insufficient_data", "minimum_required": 100}
        
        # Analyze strategy effectiveness
        strategy_performance = defaultdict(list)
        
        for decision in self.routing_history:
            strategy_performance[decision.strategy_used.value].append(decision.decision_duration_ms)
        
        strategy_analysis = {}
        for strategy, times in strategy_performance.items():
            strategy_analysis[strategy] = {
                "avg_decision_time": round(sum(times) / len(times), 3),
                "usage_count": len(times),
                "usage_percentage": round((len(times) / len(self.routing_history)) * 100, 2)
            }
        
        return {
            "total_decisions": len(self.routing_history),
            "strategy_performance": strategy_analysis,
            "avg_decision_time": round(sum(d.decision_duration_ms for d in self.routing_history) / len(self.routing_history), 3)
        }
    
    async def _generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Analyze destination utilization
        high_utilization_destinations = [
            dest_id for dest_id, dest in self.destinations.items()
            if dest.current_load / dest.max_capacity > 0.8
        ]
        
        if high_utilization_destinations:
            suggestions.append(f"Consider scaling high utilization destinations: {', '.join(high_utilization_destinations)}")
        
        # Analyze strategy usage
        if len(self.routing_history) > 100:
            strategy_usage = defaultdict(int)
            for decision in self.routing_history:
                strategy_usage[decision.strategy_used.value] += 1
            
            most_used = max(strategy_usage.keys(), key=lambda k: strategy_usage[k])
            suggestions.append(f"Most used strategy: {most_used} - consider optimizing its configuration")
        
        # Check health status distribution
        unhealthy_count = sum(1 for dest in self.destinations.values() 
                            if dest.health_status == HealthStatus.UNHEALTHY)
        
        if unhealthy_count > 0:
            suggestions.append(f"{unhealthy_count} destinations are unhealthy - investigate and fix")
        
        return suggestions
    
    async def _apply_automatic_optimizations(self) -> List[str]:
        """Apply automatic optimizations"""
        optimizations = []
        
        # Adjust weights based on performance
        for dest_id, destination in self.destinations.items():
            if destination.total_messages_routed > 50:  # Enough data
                success_rate = destination.successful_messages / destination.total_messages_routed
                
                if success_rate > 0.95 and destination.health_status == HealthStatus.HEALTHY:
                    # Increase weight for high-performing destinations
                    old_weight = destination.weight
                    destination.weight = min(destination.weight * 1.1, 5.0)
                    
                    if destination.weight != old_weight:
                        optimizations.append(f"Increased weight for {destination.name} from {old_weight:.2f} to {destination.weight:.2f}")
                
                elif success_rate < 0.8:
                    # Decrease weight for poor-performing destinations
                    old_weight = destination.weight
                    destination.weight = max(destination.weight * 0.9, 0.1)
                    
                    if destination.weight != old_weight:
                        optimizations.append(f"Decreased weight for {destination.name} from {old_weight:.2f} to {destination.weight:.2f}")
        
        return optimizations


# Export for public API
__all__ = [
    "MessageRoutingIntelligence",
    "RoutingDestination",
    "RoutingRule",
    "RoutingDecision",
    "RoutingMetrics",
    "RoutingStrategy",
    "DestinationType",
    "HealthStatus",
    "AinflueBusiness"
]