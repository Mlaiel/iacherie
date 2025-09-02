"""Advanced Traffic Shaping Engine for IA Influencer Agent Platform

Provides intelligent traffic shaping, bandwidth management, and QoS
for content protection, fingerprinting, and monetization services
with priority-based resource allocation and adaptive throttling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import math
import statistics
from collections import defaultdict, deque
import redis
from prometheus_client import Counter, Histogram, Gauge
import psutil
import aiofiles
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

# Prometheus metrics for traffic shaping
TRAFFIC_SHAPED_BYTES = Counter('traffic_shaped_bytes_total', 'Total bytes shaped', ['service', 'priority', 'action'])
TRAFFIC_SHAPING_LATENCY = Histogram('traffic_shaping_latency_seconds', 'Traffic shaping processing latency')
BANDWIDTH_UTILIZATION = Gauge('bandwidth_utilization_ratio', 'Bandwidth utilization ratio', ['service', 'direction'])
QOS_VIOLATIONS = Counter('qos_violations_total', 'QoS policy violations', ['service', 'policy'])
TRAFFIC_PRIORITY_DISTRIBUTION = Gauge('traffic_priority_distribution', 'Traffic distribution by priority', ['priority'])


class TrafficPriority(Enum):
    """
Traffic priority levels for QoS management"""

    CRITICAL = 1      # Real-time AI agent responses, payment processing
    HIGH = 2          # Fingerprinting uploads, protection alerts
    MEDIUM = 3        # Content analysis, routine API calls
    LOW = 4           # Background crawling, batch processing
    BULK = 5          # Data migrations, backups


class TrafficAction(Enum):
    """
Traffic shaping actions"""

    ALLOW = "allow"
    THROTTLE = "throttle"
    DELAY = "delay"
    DROP = "drop"
    PRIORITIZE = "prioritize"
    QUEUE = "queue"


class BandwidthDirection(Enum):
    """Bandwidth direction"""

    INGRESS = "ingress"
    EGRESS = "egress"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class TrafficClass:
    """Traffic classification configuration"""
    name: str
    priority: TrafficPriority
    bandwidth_limit_mbps: Optional[float] = None
    bandwidth_guarantee_mbps: Optional[float] = None
    max_burst_size_mb: Optional[float] = None
    max_latency_ms: Optional[int] = None
    jitter_tolerance_ms: Optional[int] = None
    packet_loss_threshold: Optional[float] = None
    connection_limit: Optional[int] = None
    rate_limit_per_second: Optional[int] = None
    
    # Advanced QoS parameters
    weight: int = 1
    ceiling_mbps: Optional[float] = None
    floor_mbps: Optional[float] = None
    congestion_algorithm: str = "cubic"
    buffer_size_kb: int = 256
    
    # Platform-specific settings
    service_type: str = "general"
    tenant_isolation: bool = False
    geographic_restrictions: List[str] = field(default_factory=list)


@dataclass
class TrafficFlow:
    """Individual traffic flow tracking"""
    flow_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    service_type: str
    traffic_class: str
    
    # Flow statistics
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # QoS metrics
    current_bandwidth_mbps: float = 0.0
    average_latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_rate: float = 0.0
    
    # Shaping state
    is_throttled: bool = False
    throttle_rate_mbps: Optional[float] = None
    queue_depth: int = 0
    priority_boost: bool = False


@dataclass
class BandwidthPool:
    """
Bandwidth resource pool for traffic classes"""
    name: str
    total_bandwidth_mbps: float
    allocated_bandwidth_mbps: float = 0.0
    available_bandwidth_mbps: float = 0.0
    peak_usage_mbps: float = 0.0
    utilization_threshold: float = 0.8
    
    # Pool members
    traffic_classes: List[str] = field(default_factory=list)
    active_flows: Dict[str, TrafficFlow] = field(default_factory=dict)
    
    # Borrowing configuration
    can_borrow: bool = True
    can_lend: bool = True
    borrowing_ratio: float = 0.2
    lending_ratio: float = 0.3
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
@dataclass
class ShapingPolicy:
    """
Traffic shaping policy configuration"""
    name: str
    description: str
    enabled: bool = True
    
    # Matching criteria
    source_networks: List[str] = field(default_factory=list)
    destination_networks: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    service_types: List[str] = field(default_factory=list)
    
    # Shaping actions
    traffic_class: str = "medium"
    bandwidth_limit_mbps: Optional[float] = None
    priority_adjustment: int = 0
    delay_ms: Optional[int] = None
    
    # Advanced policies
    time_based_rules: Dict[str, Any] = field(default_factory=dict)
    geographic_rules: Dict[str, Any] = field(default_factory=dict)
    adaptive_throttling: bool = False
    burst_allowance: bool = True


class TrafficShapingEngine:
    """
    Advanced Traffic Shaping Engine for IA Influencer Agent Platform
    
    Provides intelligent traffic management with:
    - Priority-based QoS for real-time AI agent responses
    - Bandwidth allocation for content protection services
    - Adaptive throttling for fingerprinting workloads
    - Multi-tenant traffic isolation
    - Geographic traffic optimization
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        redis_client: Optional[redis.Redis] = None,
        enable_metrics: bool = True
    ):
        self.config_file = config_file
        self.redis_client = redis_client
        self.enable_metrics = enable_metrics
        
        # Traffic management components
        self.traffic_classes: Dict[str, TrafficClass] = {}
        self.bandwidth_pools: Dict[str, BandwidthPool] = {}
        self.shaping_policies: Dict[str, ShapingPolicy] = {}
        self.active_flows: Dict[str, TrafficFlow] = {}
        
        # Performance tracking
        self.flow_statistics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.bandwidth_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=300))  # 5 min at 1s intervals
        self.latency_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configuration
        self.config = {
            "total_bandwidth_mbps": 1000,
            "monitoring_interval": 1,
            "flow_timeout_minutes": 5,
            "adaptive_shaping": True,
            "congestion_threshold": 0.85,
            "burst_detection_threshold": 2.0,
            "packet_inspection_enabled": True,
            "geographic_shaping": True
        }
        
        # Runtime state
        self._monitoring_active = False
        self._shaping_active = False
        self._last_stats_update = datetime.now()
        
        logger.info("Traffic Shaping Engine initialized for IA Influencer Agent platform")
    
    async def initialize(self) -> bool:
        """Initialize traffic shaping engine with platform configuration"""
        try:
            # Load configuration
            await self._load_configuration()
            
            # Configure platform traffic classes
            await self._configure_platform_traffic_classes()
            
            # Setup bandwidth pools
            await self._configure_bandwidth_pools()
            
            # Configure shaping policies
            await self._configure_shaping_policies()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Start traffic shaping
            await self._start_traffic_shaping()
            
            logger.info("Traffic shaping engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize traffic shaping engine: {e}")
            return False
    
    async def _load_configuration(self) -> None:
        """Load traffic shaping configuration"""
        try:
            if self.config_file and Path(self.config_file).exists():
                async with aiofiles.open(self.config_file, 'r') as f:
                    content = await f.read()
                    file_config = yaml.safe_load(content)
                    self.config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("Using default traffic shaping configuration")
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")
    
    async def _configure_platform_traffic_classes(self) -> None:
        """Configure traffic classes for IA Influencer Agent platform services"""
        try:
            # Critical priority - Real-time AI agent and payments
            critical_class = TrafficClass(
                name="critical",
                priority=TrafficPriority.CRITICAL,
                bandwidth_guarantee_mbps=100.0,
                max_latency_ms=50,
                jitter_tolerance_ms=10,
                packet_loss_threshold=0.001,
                connection_limit=1000,
                rate_limit_per_second=10000,
                weight=10,
                floor_mbps=50.0,
                service_type="ai_agent,payments",
                tenant_isolation=True
            )
            
            # High priority - Content protection and fingerprinting
            high_class = TrafficClass(
                name="high",
                priority=TrafficPriority.HIGH,
                bandwidth_guarantee_mbps=200.0,
                max_latency_ms=100,
                jitter_tolerance_ms=20,
                packet_loss_threshold=0.01,
                connection_limit=2000,
                rate_limit_per_second=5000,
                weight=8,
                floor_mbps=100.0,
                service_type="fingerprinting,protection",
                tenant_isolation=True
            )
            
            # Medium priority - Content analysis and APIs
            medium_class = TrafficClass(
                name="medium",
                priority=TrafficPriority.MEDIUM,
                bandwidth_guarantee_mbps=150.0,
                max_latency_ms=200,
                jitter_tolerance_ms=50,
                packet_loss_threshold=0.05,
                connection_limit=5000,
                rate_limit_per_second=2000,
                weight=5,
                floor_mbps=50.0,
                service_type="analysis,api",
                tenant_isolation=False
            )
            
            # Low priority - Background crawling and processing
            low_class = TrafficClass(
                name="low",
                priority=TrafficPriority.LOW,
                bandwidth_guarantee_mbps=50.0,
                max_latency_ms=500,
                jitter_tolerance_ms=100,
                packet_loss_threshold=0.1,
                connection_limit=1000,
                rate_limit_per_second=500,
                weight=3,
                floor_mbps=10.0,
                service_type="crawlers,background",
                tenant_isolation=False
            )
            
            # Bulk priority - Data migrations and backups
            bulk_class = TrafficClass(
                name="bulk",
                priority=TrafficPriority.BULK,
                bandwidth_guarantee_mbps=25.0,
                max_latency_ms=1000,
                jitter_tolerance_ms=200,
                packet_loss_threshold=0.2,
                connection_limit=100,
                rate_limit_per_second=100,
                weight=1,
                floor_mbps=5.0,
                service_type="backup,migration",
                tenant_isolation=False
            )
            
            self.traffic_classes = {
                "critical": critical_class,
                "high": high_class,
                "medium": medium_class,
                "low": low_class,
                "bulk": bulk_class
            }
            
            logger.info("Platform traffic classes configured")
            
        except Exception as e:
            logger.error(f"Failed to configure traffic classes: {e}")
            raise
    
    async def _configure_bandwidth_pools(self) -> None:
        """Configure bandwidth pools for different service categories"""
        try:
            total_bandwidth = self.config["total_bandwidth_mbps"]
            
            # AI Agent and Real-time Services Pool (30%)
            realtime_pool = BandwidthPool(
                name="realtime",
                total_bandwidth_mbps=total_bandwidth * 0.30,
                utilization_threshold=0.9,
                traffic_classes=["critical"],
                can_borrow=True,
                can_lend=False,  # Don't lend critical bandwidth
                borrowing_ratio=0.1
            )
            
            # Content Protection Pool (40%)
            protection_pool = BandwidthPool(
                name="protection",
                total_bandwidth_mbps=total_bandwidth * 0.40,
                utilization_threshold=0.85,
                traffic_classes=["high", "medium"],
                can_borrow=True,
                can_lend=True,
                borrowing_ratio=0.2,
                lending_ratio=0.3
            )
            
            # Background Services Pool (30%)
            background_pool = BandwidthPool(
                name="background",
                total_bandwidth_mbps=total_bandwidth * 0.30,
                utilization_threshold=0.7,
                traffic_classes=["low", "bulk"],
                can_borrow=True,
                can_lend=True,
                borrowing_ratio=0.5,
                lending_ratio=0.8
            )
            
            self.bandwidth_pools = {
                "realtime": realtime_pool,
                "protection": protection_pool,
                "background": background_pool
            }
            
            logger.info("Bandwidth pools configured")
            
        except Exception as e:
            logger.error(f"Failed to configure bandwidth pools: {e}")
            raise
    
    async def _configure_shaping_policies(self) -> None:
        """Configure traffic shaping policies for platform services"""
        try:
            # AI Agent API priority policy
            ai_agent_policy = ShapingPolicy(
                name="ai_agent_priority",
                description="Prioritize AI agent API requests",
                service_types=["ai_agent", "spotify_integration"],
                ports=[8004, 443],
                traffic_class="critical",
                priority_adjustment=2,
                adaptive_throttling=True,
                burst_allowance=True
            )
            
            # Fingerprinting upload policy
            fingerprinting_policy = ShapingPolicy(
                name="fingerprinting_uploads",
                description="Shape fingerprinting content uploads",
                service_types=["fingerprinting"],
                ports=[8001],
                traffic_class="high",
                bandwidth_limit_mbps=100.0,
                burst_allowance=True,
                time_based_rules={
                    "peak_hours": {"start": "09:00", "end": "18:00", "multiplier": 1.5},
                    "off_hours": {"start": "22:00", "end": "06:00", "multiplier": 0.5}
                }
            )
            
            # Payment processing policy
            payment_policy = ShapingPolicy(
                name="payment_processing",
                description="Guarantee payment processing bandwidth",
                service_types=["monetization", "payments"],
                ports=[8003],
                traffic_class="critical",
                bandwidth_limit_mbps=50.0,
                priority_adjustment=3,
                delay_ms=0  # No delay for payments
            )
            
            # Crawler throttling policy
            crawler_policy = ShapingPolicy(
                name="crawler_throttling",
                description="Throttle background crawling",
                service_types=["crawlers"],
                ports=[8005],
                traffic_class="low",
                bandwidth_limit_mbps=20.0,
                adaptive_throttling=True,
                time_based_rules={
                    "business_hours": {"start": "08:00", "end": "20:00", "multiplier": 0.3},
                    "night_hours": {"start": "20:00", "end": "08:00", "multiplier": 2.0}
                }
            )
            
            # Geographic content protection policy
            geo_protection_policy = ShapingPolicy(
                name="geographic_protection",
                description="Geographic-aware content protection",
                service_types=["protection", "monitoring"],
                ports=[8002],
                traffic_class="high",
                geographic_rules={
                    "europe": {"bandwidth_multiplier": 1.2, "latency_priority": True},
                    "north_america": {"bandwidth_multiplier": 1.0, "latency_priority": True},
                    "asia_pacific": {"bandwidth_multiplier": 0.8, "latency_priority": False}
                }
            )
            
            self.shaping_policies = {
                "ai_agent_priority": ai_agent_policy,
                "fingerprinting_uploads": fingerprinting_policy,
                "payment_processing": payment_policy,
                "crawler_throttling": crawler_policy,
                "geographic_protection": geo_protection_policy
            }
            
            logger.info("Traffic shaping policies configured")
            
        except Exception as e:
            logger.error(f"Failed to configure shaping policies: {e}")
            raise
    
    async def classify_traffic(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        payload_size: int,
        service_type: Optional[str] = None
    ) -> Tuple[str, TrafficClass]:
        """
        Classify traffic into appropriate traffic class
        Returns: (traffic_class_name, traffic_class_config)
        """
        try:
            # Service-based classification (highest priority)
            if service_type:
                for class_name, traffic_class in self.traffic_classes.items():
                    if service_type in traffic_class.service_type:
                        return class_name, traffic_class
            
            # Port-based classification
            if destination_port in [8004, 443]:  # AI Agent, HTTPS
                return "critical", self.traffic_classes["critical"]
            elif destination_port in [8001, 8002]:  # Fingerprinting, Protection
                return "high", self.traffic_classes["high"]
            elif destination_port in [8003]:  # Monetization
                return "critical", self.traffic_classes["critical"]
            elif destination_port in [8005]:  # Crawlers
                return "low", self.traffic_classes["low"]
            elif destination_port in [80, 8080]:  # Regular HTTP
                return "medium", self.traffic_classes["medium"]
            
            # Protocol-based classification
            if protocol.upper() == "UDP":
                return "high", self.traffic_classes["high"]  # Assume real-time
            
            # Payload size-based classification
            if payload_size > 10 * 1024 * 1024:  # > 10MB
                return "bulk", self.traffic_classes["bulk"]
            elif payload_size > 1024 * 1024:  # > 1MB
                return "low", self.traffic_classes["low"]
            
            # Default classification
            return "medium", self.traffic_classes["medium"]
            
        except Exception as e:
            logger.error(f"Failed to classify traffic: {e}")
            return "medium", self.traffic_classes["medium"]
    
    async def shape_traffic_flow(
        self,
        flow: TrafficFlow,
        current_bandwidth_mbps: float
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """
        Apply traffic shaping to a flow
        Returns: (action, parameters)
        """
        try:
            traffic_class = self.traffic_classes.get(flow.traffic_class)
            if not traffic_class:
                return TrafficAction.ALLOW, {}
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(flow)
            
            # Check bandwidth limits
            bandwidth_action = await self._check_bandwidth_limits(flow, current_bandwidth_mbps, traffic_class)
            if bandwidth_action[0] != TrafficAction.ALLOW:
                return bandwidth_action
            
            # Check connection limits
            connection_action = await self._check_connection_limits(flow, traffic_class)
            if connection_action[0] != TrafficAction.ALLOW:
                return connection_action
            
            # Check rate limits
            rate_action = await self._check_rate_limits(flow, traffic_class)
            if rate_action[0] != TrafficAction.ALLOW:
                return rate_action
            
            # Apply adaptive shaping
            if self.config["adaptive_shaping"]:
                adaptive_action = await self._apply_adaptive_shaping(flow, traffic_class)
                if adaptive_action[0] != TrafficAction.ALLOW:
                    return adaptive_action
            
            # Apply priority-based shaping
            priority_action = await self._apply_priority_shaping(flow, traffic_class)
            
            # Update metrics
            if self.enable_metrics:
                TRAFFIC_SHAPED_BYTES.labels(
                    service=flow.service_type,
                    priority=traffic_class.priority.name,
                    action=priority_action[0].value
                ).inc(flow.bytes_sent + flow.bytes_received)
            
            return priority_action
            
        except Exception as e:
            logger.error(f"Failed to shape traffic flow: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _get_applicable_policies(self, flow: TrafficFlow) -> List[ShapingPolicy]:
        """Get applicable shaping policies for a flow"""
        try:
            applicable = []
            
            for policy in self.shaping_policies.values():
                if not policy.enabled:
                    continue
                
                # Check service type
                if policy.service_types and flow.service_type not in policy.service_types:
                    continue
                
                # Check ports
                if policy.ports and flow.destination_port not in policy.ports:
                    continue
                
                # Check protocols
                if policy.protocols and flow.protocol not in policy.protocols:
                    continue
                
                applicable.append(policy)
            
            return applicable
            
        except Exception as e:
            logger.error(f"Failed to get applicable policies: {e}")
            return []
    
    async def _check_bandwidth_limits(
        self,
        flow: TrafficFlow,
        current_bandwidth_mbps: float,
        traffic_class: TrafficClass
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """Check bandwidth limits for traffic class"""
        try:
            # Check class bandwidth limit
            if traffic_class.bandwidth_limit_mbps:
                if current_bandwidth_mbps > traffic_class.bandwidth_limit_mbps:
                    throttle_rate = traffic_class.bandwidth_limit_mbps * 0.9
                    return TrafficAction.THROTTLE, {
                        "rate_mbps": throttle_rate,
                        "reason": "bandwidth_limit_exceeded"
                    }
            
            # Check bandwidth pool utilization
            pool = await self._get_flow_bandwidth_pool(flow)
            if pool:
                utilization = pool.allocated_bandwidth_mbps / pool.total_bandwidth_mbps
                if utilization > pool.utilization_threshold:
                    # Try borrowing from other pools
                    borrowed = await self._try_borrow_bandwidth(pool, current_bandwidth_mbps)
                    if not borrowed:
                        return TrafficAction.THROTTLE, {
                            "rate_mbps": traffic_class.floor_mbps or 1.0,
                            "reason": "pool_congestion"
                        }
            
            return TrafficAction.ALLOW, {}
            
        except Exception as e:
            logger.error(f"Failed to check bandwidth limits: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _check_connection_limits(
        self,
        flow: TrafficFlow,
        traffic_class: TrafficClass
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """Check connection limits for traffic class"""
        try:
            if not traffic_class.connection_limit:
                return TrafficAction.ALLOW, {}
            
            # Count active connections for this traffic class
            active_connections = sum(
                1 for f in self.active_flows.values()
                if f.traffic_class == flow.traffic_class
            )
            
            if active_connections >= traffic_class.connection_limit:
                return TrafficAction.DROP, {
                    "reason": "connection_limit_exceeded",
                    "limit": traffic_class.connection_limit,
                    "current": active_connections
                }
            
            return TrafficAction.ALLOW, {}
            
        except Exception as e:
            logger.error(f"Failed to check connection limits: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _check_rate_limits(
        self,
        flow: TrafficFlow,
        traffic_class: TrafficClass
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """Check rate limits for traffic class"""
        try:
            if not traffic_class.rate_limit_per_second:
                return TrafficAction.ALLOW, {}
            
            # Check if we have rate limiting data
            current_time = time.time()
            rate_key = f"rate:{flow.traffic_class}:{int(current_time)}"
            
            if self.redis_client:
                try:
                    current_rate = self.redis_client.incr(rate_key)
                    self.redis_client.expire(rate_key, 1)  # 1 second TTL
                    
                    if current_rate > traffic_class.rate_limit_per_second:
                        delay_ms = min(1000, current_rate - traffic_class.rate_limit_per_second)
                        return TrafficAction.DELAY, {
                            "delay_ms": delay_ms,
                            "reason": "rate_limit_exceeded"
                        }
                except Exception as e:
                    logger.warning(f"Redis rate limiting error: {e}")
            
            return TrafficAction.ALLOW, {}
            
        except Exception as e:
            logger.error(f"Failed to check rate limits: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _apply_adaptive_shaping(
        self,
        flow: TrafficFlow,
        traffic_class: TrafficClass
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """Apply adaptive traffic shaping based on network conditions"""
        try:
            # Check for congestion
            network_utilization = await self._get_network_utilization()
            
            if network_utilization > self.config["congestion_threshold"]:
                # Network is congested, apply adaptive measures
                
                if traffic_class.priority in [TrafficPriority.LOW, TrafficPriority.BULK]:
                    # Throttle low priority traffic more aggressively
                    throttle_factor = min(0.8, (network_utilization - 0.5) * 2)
                    base_rate = traffic_class.bandwidth_guarantee_mbps or 10.0
                    throttle_rate = base_rate * (1 - throttle_factor)
                    
                    return TrafficAction.THROTTLE, {
                        "rate_mbps": throttle_rate,
                        "reason": "adaptive_congestion_control",
                        "network_utilization": network_utilization
                    }
                
                elif traffic_class.priority == TrafficPriority.MEDIUM:
                    # Moderate throttling for medium priority
                    throttle_factor = min(0.3, (network_utilization - 0.7) * 3)
                    base_rate = traffic_class.bandwidth_guarantee_mbps or 20.0
                    throttle_rate = base_rate * (1 - throttle_factor)
                    
                    return TrafficAction.THROTTLE, {
                        "rate_mbps": throttle_rate,
                        "reason": "adaptive_congestion_control"
                    }
            
            # Check for burst detection
            if await self._detect_traffic_burst(flow):
                if traffic_class.max_burst_size_mb:
                    return TrafficAction.QUEUE, {
                        "queue_size_mb": traffic_class.max_burst_size_mb,
                        "reason": "burst_smoothing"
                    }
            
            return TrafficAction.ALLOW, {}
            
        except Exception as e:
            logger.error(f"Failed to apply adaptive shaping: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _apply_priority_shaping(
        self,
        flow: TrafficFlow,
        traffic_class: TrafficClass
    ) -> Tuple[TrafficAction, Dict[str, Any]]:
        """Apply priority-based traffic shaping"""
        try:
            # Critical and high priority traffic gets prioritized
            if traffic_class.priority in [TrafficPriority.CRITICAL, TrafficPriority.HIGH]:
                return TrafficAction.PRIORITIZE, {
                    "priority_level": traffic_class.priority.value,
                    "weight": traffic_class.weight,
                    "guaranteed_bandwidth": traffic_class.bandwidth_guarantee_mbps
                }
            
            # Medium priority gets standard treatment
            elif traffic_class.priority == TrafficPriority.MEDIUM:
                return TrafficAction.ALLOW, {
                    "weight": traffic_class.weight
                }
            
            # Low and bulk priority may be queued during congestion
            else:
                network_utilization = await self._get_network_utilization()
                if network_utilization > 0.7:
                    return TrafficAction.QUEUE, {
                        "priority_level": traffic_class.priority.value,
                        "weight": traffic_class.weight
                    }
                else:
                    return TrafficAction.ALLOW, {
                        "weight": traffic_class.weight
                    }
                    
        except Exception as e:
            logger.error(f"Failed to apply priority shaping: {e}")
            return TrafficAction.ALLOW, {}
    
    async def _get_flow_bandwidth_pool(self, flow: TrafficFlow) -> Optional[BandwidthPool]:
        """Get bandwidth pool for a flow"""
        try:
            for pool in self.bandwidth_pools.values():
                if flow.traffic_class in pool.traffic_classes:
                    return pool
            return None
            
        except Exception as e:
            logger.error(f"Failed to get flow bandwidth pool: {e}")
            return None
    
    async def _try_borrow_bandwidth(self, pool: BandwidthPool, required_mbps: float) -> bool:
        """Try to borrow bandwidth from other pools"""
        try:
            if not pool.can_borrow:
                return False
            
            max_borrowable = pool.total_bandwidth_mbps * pool.borrowing_ratio
            
            for other_pool in self.bandwidth_pools.values():
                if other_pool == pool or not other_pool.can_lend:
                    continue
                
                available_to_lend = other_pool.total_bandwidth_mbps * other_pool.lending_ratio
                current_utilization = other_pool.allocated_bandwidth_mbps / other_pool.total_bandwidth_mbps
                
                if current_utilization < 0.5:  # Only lend if low utilization
                    lendable = min(available_to_lend, required_mbps, max_borrowable)
                    if lendable > 0:
                        # Temporarily increase pool capacity
                        pool.total_bandwidth_mbps += lendable
                        other_pool.total_bandwidth_mbps -= lendable
                        logger.debug(f"Borrowed {lendable} Mbps from {other_pool.name} to {pool.name}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to borrow bandwidth: {e}")
            return False
    
    async def _get_network_utilization(self) -> float:
        """Get current network utilization"""
        try:
            # Calculate total allocated bandwidth across all pools
            total_allocated = sum(pool.allocated_bandwidth_mbps for pool in self.bandwidth_pools.values())
            total_capacity = sum(pool.total_bandwidth_mbps for pool in self.bandwidth_pools.values())
            
            if total_capacity > 0:
                return total_allocated / total_capacity
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get network utilization: {e}")
            return 0.0
    
    async def _detect_traffic_burst(self, flow: TrafficFlow) -> bool:
        """Detect if traffic flow is experiencing a burst"""
        try:
            # Get recent bandwidth history for this flow
            flow_history = self.bandwidth_history.get(flow.flow_id, deque(maxlen=10))
            
            if len(flow_history) < 5:
                return False  # Not enough data
            
            recent_avg = statistics.mean(list(flow_history)[-5:])
            overall_avg = statistics.mean(flow_history)
            
            # Burst detected if recent average is significantly higher
            burst_ratio = recent_avg / overall_avg if overall_avg > 0 else 1.0
            
            return burst_ratio > self.config["burst_detection_threshold"]
            
        except Exception as e:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "monitor_traffic",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric monitor_traffic collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection monitor_traffic failed: {e}")
                    return None
        except Exception as e:
            logger.error(f"Failed to detect traffic burst: {e}")
            return False
    
    async def _initialize_monitoring(self) -> None:
        """Initialize traffic monitoring"""
        try:
            self._monitoring_active = True
            
            async def monitor_traffic():
                while self._monitoring_active:
                    try:
                        await self._update_traffic_statistics()
                        await self._update_bandwidth_pools()
                        await self._update_metrics()
                        await asyncio.sleep(self.config["monitoring_interval"])
                        
                    except Exception as e:
                        logger.error(f"Error in traffic monitoring: {e}")
                        await asyncio.sleep(10)
            
            asyncio.create_task(monitor_traffic())
            logger.info("Traffic monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
    
    async def _start_traffic_shaping(self) -> None:
        """Start traffic shaping engine"""
        try:
            self._shaping_active = True
            logger.info("Traffic shaping engine started")
            
        except Exception as e:
            logger.error(f"Failed to start traffic shaping: {e}")
    
    async def _update_traffic_statistics(self) -> None:
        """Update traffic flow statistics"""
        try:
            current_time = datetime.now()
            
            for flow_id, flow in list(self.active_flows.items()):
                # Check for expired flows
                if (current_time - flow.last_activity).total_seconds() > self.config["flow_timeout_minutes"] * 60:
                    del self.active_flows[flow_id]
                    continue
                
                # Update flow statistics
                self.flow_statistics[flow_id].update({
                    "last_update": current_time.isoformat(),
                    "duration_seconds": (current_time - flow.start_time).total_seconds(),
                    "bytes_per_second": flow.bytes_sent / max(1, (current_time - flow.start_time).total_seconds()),
                    "packets_per_second": flow.packets_sent / max(1, (current_time - flow.start_time).total_seconds())
                })
                
                # Update bandwidth history
                bandwidth_mbps = (flow.bytes_sent * 8) / (1024 * 1024)  # Convert to Mbps
                self.bandwidth_history[flow_id].append(bandwidth_mbps)
            
            self._last_stats_update = current_time
            
        except Exception as e:
            logger.error(f"Failed to update traffic statistics: {e}")
    
    async def _update_bandwidth_pools(self) -> None:
        """Update bandwidth pool allocations"""
        try:
            for pool in self.bandwidth_pools.values():
                # Calculate current allocation
                allocated = sum(
                    flow.current_bandwidth_mbps
                    for flow in self.active_flows.values()
                    if flow.traffic_class in pool.traffic_classes
                )
                
                pool.allocated_bandwidth_mbps = allocated
                pool.available_bandwidth_mbps = pool.total_bandwidth_mbps - allocated
                pool.peak_usage_mbps = max(pool.peak_usage_mbps, allocated)
                
        except Exception as e:
            logger.error(f"Failed to update bandwidth pools: {e}")
    
    async def _update_metrics(self) -> None:
        """Update Prometheus metrics"""
        try:
            if not self.enable_metrics:
                return
            
            # Update bandwidth utilization metrics
            for pool_name, pool in self.bandwidth_pools.values():
                utilization = pool.allocated_bandwidth_mbps / pool.total_bandwidth_mbps if pool.total_bandwidth_mbps > 0 else 0
                BANDWIDTH_UTILIZATION.labels(service=pool_name, direction="bidirectional").set(utilization)
            
            # Update traffic priority distribution
            priority_counts = defaultdict(int)
            for flow in self.active_flows.values():
                if flow.traffic_class in self.traffic_classes:
                    priority = self.traffic_classes[flow.traffic_class].priority.name
                    priority_counts[priority] += 1
            
            for priority, count in priority_counts.items():
                TRAFFIC_PRIORITY_DISTRIBUTION.labels(priority=priority).set(count)
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    async def register_flow(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        service_type: str = "general"
    ) -> str:
        """Register a new traffic flow"""
        try:
            flow_id = f"{source_ip}:{source_port}-{destination_ip}:{destination_port}-{protocol}"
            
            # Classify traffic
            traffic_class_name, traffic_class = await self.classify_traffic(
                source_ip, destination_ip, source_port, destination_port, protocol, 0, service_type
            )
            
            # Create flow
            flow = TrafficFlow(
                flow_id=flow_id,
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_port=source_port,
                destination_port=destination_port,
                protocol=protocol,
                service_type=service_type,
                traffic_class=traffic_class_name
            )
            
            self.active_flows[flow_id] = flow
            
            logger.debug(f"Registered new flow: {flow_id} -> {traffic_class_name}")
            return flow_id
            
        except Exception as e:
            logger.error(f"Failed to register flow: {e}")
            return ""
    
    async def update_flow_stats(
        self,
        flow_id: str,
        bytes_sent: int = 0,
        bytes_received: int = 0,
        packets_sent: int = 0,
        packets_received: int = 0
    ) -> None:
        """Update statistics for a traffic flow"""
        try:
            if flow_id not in self.active_flows:
                return
            
            flow = self.active_flows[flow_id]
            flow.bytes_sent += bytes_sent
            flow.bytes_received += bytes_received
            flow.packets_sent += packets_sent
            flow.packets_received += packets_received
            flow.last_activity = datetime.now()
            
            # Calculate current bandwidth
            duration = (flow.last_activity - flow.start_time).total_seconds()
            if duration > 0:
                total_bytes = flow.bytes_sent + flow.bytes_received
                flow.current_bandwidth_mbps = (total_bytes * 8) / (duration * 1024 * 1024)
                
        except Exception as e:
            logger.error(f"Failed to update flow stats: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of traffic shaping engine"""
        try:
            # Flow statistics
            total_flows = len(self.active_flows)
            flows_by_class = defaultdict(int)
            for flow in self.active_flows.values():
                flows_by_class[flow.traffic_class] += 1
            
            # Bandwidth statistics
            total_bandwidth = sum(pool.total_bandwidth_mbps for pool in self.bandwidth_pools.values())
            allocated_bandwidth = sum(pool.allocated_bandwidth_mbps for pool in self.bandwidth_pools.values())
            
            # Pool status
            pool_status = {}
            for name, pool in self.bandwidth_pools.items():
                pool_status[name] = {
                    "total_mbps": pool.total_bandwidth_mbps,
                    "allocated_mbps": pool.allocated_bandwidth_mbps,
                    "available_mbps": pool.available_bandwidth_mbps,
                    "utilization": pool.allocated_bandwidth_mbps / pool.total_bandwidth_mbps if pool.total_bandwidth_mbps > 0 else 0,
                    "peak_usage_mbps": pool.peak_usage_mbps,
                    "active_flows": len(pool.active_flows)
                }
            
            return {
                "active": self._shaping_active,
                "monitoring_active": self._monitoring_active,
                "total_flows": total_flows,
                "flows_by_class": dict(flows_by_class),
                "total_bandwidth_mbps": total_bandwidth,
                "allocated_bandwidth_mbps": allocated_bandwidth,
                "overall_utilization": allocated_bandwidth / total_bandwidth if total_bandwidth > 0 else 0,
                "traffic_classes_configured": len(self.traffic_classes),
                "shaping_policies_configured": len(self.shaping_policies),
                "bandwidth_pools": pool_status,
                "last_stats_update": self._last_stats_update.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def shutdown(self) -> None:
        """Shutdown traffic shaping engine"""
        try:
            logger.info("Shutting down Traffic Shaping Engine...")
            
            self._monitoring_active = False
            self._shaping_active = False
            
            # Clear active flows
            self.active_flows.clear()
            
            logger.info("Traffic Shaping Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Platform-specific traffic shaping functions
async def shape_fingerprinting_traffic(
    shaping_engine: TrafficShapingEngine,
    client_ip: str,
    content_size_mb: float,
    content_type: str = "audio"
) -> Dict[str, Any]:
    """Apply traffic shaping for fingerprinting uploads"""
    try:
        # Register flow for fingerprinting service
        flow_id = await shaping_engine.register_flow(
            source_ip=client_ip,
            destination_ip="0.0.0.0",  # Placeholder
            source_port=0,
            destination_port=8001,
            protocol="HTTPS",
            service_type="fingerprinting"
        )
        
        # Get flow and apply shaping
        flow = shaping_engine.active_flows.get(flow_id)
        if flow:
            action, params = await shaping_engine.shape_traffic_flow(flow, content_size_mb)
            return {
                "flow_id": flow_id,
                "action": action.value,
                "parameters": params,
                "traffic_class": flow.traffic_class
            }
        
        return {"error": "Failed to create flow"}
        
    except Exception as e:
        logger.error(f"Failed to shape fingerprinting traffic: {e}")
        return {"error": str(e)}


async def shape_ai_agent_traffic(
    shaping_engine: TrafficShapingEngine,
    client_ip: str,
    request_type: str = "recommendation"
) -> Dict[str, Any]:
    """Apply traffic shaping for AI agent requests with priority"""
    try:
        # Register flow for AI agent service
        flow_id = await shaping_engine.register_flow(
            source_ip=client_ip,
            destination_ip="0.0.0.0",
            source_port=0,
            destination_port=8004,
            protocol="HTTPS",
            service_type="ai_agent"
        )
        
        # Get flow and apply shaping
        flow = shaping_engine.active_flows.get(flow_id)
        if flow:
            # AI agent gets priority treatment
            action, params = await shaping_engine.shape_traffic_flow(flow, 0.1)  # Small request size
            return {
                "flow_id": flow_id,
                "action": action.value,
                "parameters": params,
                "traffic_class": flow.traffic_class,
                "priority": "critical"
            }
        
        return {"error": "Failed to create flow"}
        
    except Exception as e:
        logger.error(f"Failed to shape AI agent traffic: {e}")
        return {"error": str(e)}
