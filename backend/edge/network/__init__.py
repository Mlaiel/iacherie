"""Edge Network Services Module
=============================

Network services infrastructure for edge computing nodes,
providing CDN edge, DNS resolution, load balancing, and network optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# CDN edge integration
from .cdn_edge import (
    EdgeCDN,
    CDNStrategy,
    CachePolicy,
    ContentOrigin,
    CDNConfig,
    create_edge_cdn
)

# DNS edge resolver
from .dns_resolver import (
    EdgeDNSResolver,
    DNSRecordType,
    DNSQuery,
    DNSResponse,
    create_dns_resolver
)

# Load balancer
from .load_balancer import (
    EdgeLoadBalancer,
    LoadBalancingAlgorithm,
    HealthCheckConfig,
    BackendServer,
    create_load_balancer
)

# Traffic shaping
from .traffic_shaper import (
    TrafficShaper,
    TrafficPolicy,
    QoSClass,
    BandwidthLimit,
    create_traffic_shaper
)

# Bandwidth optimizer
from .bandwidth_optimizer import (
    BandwidthOptimizer,
    OptimizationMode,
    CompressionAlgorithm,
    create_bandwidth_optimizer
)

# Latency optimizer
from .latency_optimizer import (
    LatencyOptimizer,
    LatencyTarget,
    OptimizationTechnique,
    create_latency_optimizer
)

# QoS manager
from .qos_manager import (
    QoSManager,
    ServiceClass,
    QoSPolicy,
    QoSMetrics,
    create_qos_manager
)

__all__ = [
    # CDN edge
    "EdgeCDN",
    "CDNStrategy",
    "CachePolicy", 
    "ContentOrigin",
    "CDNConfig",
    "create_edge_cdn",
    
    # DNS resolver
    "EdgeDNSResolver",
    "DNSRecordType",
    "DNSQuery",
    "DNSResponse",
    "create_dns_resolver",
    
    # Load balancer
    "EdgeLoadBalancer",
    "LoadBalancingAlgorithm",
    "HealthCheckConfig",
    "BackendServer",
    "create_load_balancer",
    
    # Traffic shaping
    "TrafficShaper",
    "TrafficPolicy",
    "QoSClass",
    "BandwidthLimit",
    "create_traffic_shaper",
    
    # Bandwidth optimization
    "BandwidthOptimizer",
    "OptimizationMode",
    "CompressionAlgorithm",
    "create_bandwidth_optimizer",
    
    # Latency optimization
    "LatencyOptimizer",
    "LatencyTarget",
    "OptimizationTechnique",
    "create_latency_optimizer",
    
    # QoS management
    "QoSManager",
    "ServiceClass",
    "QoSPolicy",
    "QoSMetrics",
    "create_qos_manager"
]