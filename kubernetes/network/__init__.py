"""IA Influencer Agent - Network Deployment Module
Enterprise network configuration and security for content protection platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT SÉVÈRE ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Core network managers
from .ingress_manager import (
    IngressManager,
    IngressRule,
    IngressProtocol,
    LoadBalancingMethod,
    BackendService,
    SSLCertificate
)

from .firewall_manager import (
    FirewallManager,
    FirewallRule,
    FirewallAction,
    ProtocolType,
    ThreatLevel,
    SecurityPolicy,
    ThreatIntelligence,
    IPRange
)

from .vpc_manager import (
    VPCManager,
    VPCConfiguration,
    Subnet,
    SubnetType,
    VPCPeering,
    NATGateway,
    VPCEndpoint,
    CloudProvider,
    NetworkTier
)

from .dns_manager import (
    DNSManager,
    DNSZone,
    DNSRecord,
    DNSRecordType,
    DNSProvider,
    HealthCheck,
    HealthCheckType,
    DNSFailoverConfiguration,
    GeoDNSConfiguration
)

# Content delivery and analytics
from .content_delivery_manager import (
    ContentDeliveryManager,
    ContentType,
    CacheStrategy,
    CDNProvider,
    GeographicRegion as CDNGeographicRegion,
    ContentMetadata,
    CDNConfiguration,
    EdgeCache,
    AudioCDNManager,
    VideoCDNManager,
    FingerprintCDNManager
)

from .traffic_analytics_manager import (
    TrafficAnalyticsManager,
    TrafficType,
    AnalyticsMetric,
    TrafficPattern,
    TrafficData,
    ContentAnalytics,
    UserBehaviorMetrics
)

from .geo_distribution_manager import (
    GeographicDistributionManager,
    GeographicRegion,
    ContentDistributionStrategy,
    RegionPriority,
    GeographicPoint,
    RegionMetrics,
    ContentGeoDistribution,
    GeoOptimizationRule
)

from .performance_monitor import (
    NetworkPerformanceMonitor,
    PerformanceMetric,
    NetworkOptimization,
    PerformanceThreshold
)

# Advanced enterprise modules
from .security_compliance_manager import (
    NetworkSecurityComplianceManager,
    SecurityThreat,
    ComplianceViolation,
    SecurityPolicy,
    ComplianceFramework,
    SecurityThreatLevel,
    SecurityScanType
)

from .revenue_monetization_manager import (
    NetworkRevenueMonetizationManager,
    RevenueRecord,
    MonetizationMetrics,
    UserRevenueProfile,
    RevenueSource,
    PaymentProvider,
    RevenueStatus,
    PayoutFrequency
)

# Enterprise monitoring and alerting
from .metrics_dashboard import (
    NetworkMetricsDashboard
)

from .alert_manager import (
    NetworkAlertManager,
    AlertSeverity,
    AlertChannel,
    AlertRule,
    Alert
)

# Network orchestrator
from .index import (
    NetworkOrchestrator,
    NetworkConfiguration,
    NetworkDeploymentStatus
)

__all__ = [
    # Core Managers
    "IngressManager",
    "FirewallManager", 
    "VPCManager",
    "DNSManager",
    
    # Content Delivery & Analytics
    "ContentDeliveryManager",
    "TrafficAnalyticsManager",
    "GeographicDistributionManager",
    "NetworkPerformanceMonitor",
    
    # Advanced Enterprise Modules
    "NetworkSecurityComplianceManager",
    "NetworkRevenueMonetizationManager",
    
    # Enterprise Monitoring
    "NetworkMetricsDashboard",
    "NetworkAlertManager",
    
    # Orchestrator
    "NetworkOrchestrator",
    "NetworkConfiguration",
    "NetworkDeploymentStatus",
    
    # Ingress Components
    "IngressRule",
    "IngressProtocol",
    "LoadBalancingMethod",
    "BackendService",
    "SSLCertificate",
    
    # Firewall Components
    "FirewallRule",
    "FirewallAction",
    "ProtocolType",
    "ThreatLevel", 
    "SecurityPolicy",
    "ThreatIntelligence",
    "IPRange",
    
    # VPC Components
    "VPCConfiguration",
    "Subnet",
    "SubnetType",
    "VPCPeering",
    "NATGateway",
    "VPCEndpoint",
    "CloudProvider",
    "NetworkTier",
    
    # DNS Components
    "DNSZone",
    "DNSRecord",
    "DNSRecordType",
    "DNSProvider",
    "HealthCheck",
    "HealthCheckType",
    "DNSFailoverConfiguration",
    "GeoDNSConfiguration",
    
    # Content Delivery Components
    "ContentType",
    "CacheStrategy",
    "CDNProvider",
    "CDNGeographicRegion",
    "ContentMetadata",
    "CDNConfiguration",
    "EdgeCache",
    "AudioCDNManager",
    "VideoCDNManager",
    "FingerprintCDNManager",
    
    # Traffic Analytics Components
    "TrafficType",
    "AnalyticsMetric",
    "TrafficPattern",
    "TrafficData",
    "ContentAnalytics",
    "UserBehaviorMetrics",
    
    # Geographic Distribution Components
    "GeographicRegion",
    "ContentDistributionStrategy",
    "RegionPriority",
    "GeographicPoint",
    "RegionMetrics",
    "ContentGeoDistribution",
    "GeoOptimizationRule",
    
    # Performance Monitoring Components
    "PerformanceMetric",
    "NetworkOptimization",
    "PerformanceThreshold",
    
    # Security & Compliance Components
    "SecurityThreat",
    "ComplianceViolation",
    "ComplianceFramework",
    "SecurityThreatLevel",
    "SecurityScanType",
    
    # Revenue & Monetization Components
    "RevenueRecord",
    "MonetizationMetrics",
    "UserRevenueProfile",
    "RevenueSource",
    "PaymentProvider",
    "RevenueStatus",
    "PayoutFrequency",
    
    # Alert Management Components
    "AlertSeverity",
    "AlertChannel",
    "AlertRule",
    "Alert"
]
