"""
IA Influencer Agent - Firewall Network Manager
Enterprise firewall configuration and security rules for content protection platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

  AVERTISSEMENT SÉVÈRE 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""

import asyncio
import logging
import ipaddress
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml
import re

from kubernetes import client, config
from prometheus_client import Counter, Histogram, Gauge
import iptables
import nftables
from scapy.all import sniff, IP, TCP, UDP
import geoip2.database
import maxminddb

# Metrics
firewall_rules_total = Counter('firewall_rules_total', 'Total firewall rules', ['action', 'protocol'])
blocked_requests_total = Counter('firewall_blocked_requests_total', 'Blocked requests', ['reason', 'source'])
firewall_latency = Histogram('firewall_processing_latency_seconds', 'Firewall processing latency')
active_connections_by_country = Gauge('firewall_connections_by_country', 'Active connections by country', ['country'])

logger = logging.getLogger(__name__)


class FirewallAction(Enum):
    """Firewall actions"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    REJECT = "reject"
    LOG = "log"
    RATE_LIMIT = "rate_limit"


class ProtocolType(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    WEBSOCKET = "ws"
    ALL = "all"


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IPRange:
    """IP address range specification"""
    network: str
    description: str = ""
    country: Optional[str] = None
    organization: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.LOW
    
    def __post_init__(self):
        # Validate IP network
        try:
            self.network_obj = ipaddress.ip_network(self.network, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid IP network: {self.network} - {e}")


@dataclass
class FirewallRule:
    """Firewall rule configuration"""
    name: str
    priority: int
    action: FirewallAction
    protocol: ProtocolType
    source_ips: List[IPRange] = field(default_factory=list)
    destination_ips: List[IPRange] = field(default_factory=list)
    source_ports: List[int] = field(default_factory=list)
    destination_ports: List[int] = field(default_factory=list)
    enabled: bool = True
    rate_limit: Optional[int] = None  # requests per minute
    countries_allowed: List[str] = field(default_factory=list)
    countries_blocked: List[str] = field(default_factory=list)
    user_agents_blocked: List[str] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    rules: List[FirewallRule]
    default_action: FirewallAction = FirewallAction.DENY
    log_level: str = "INFO"
    intrusion_detection: bool = True
    ddos_protection: bool = True
    geo_blocking: bool = True
    rate_limiting: bool = True
    bot_protection: bool = True
    content_filtering: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    ip_address: str
    threat_type: str
    threat_level: ThreatLevel
    description: str
    source: str
    first_seen: datetime
    last_seen: datetime
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class FirewallManager:
    """
    Enterprise firewall manager for IA Influencer Agent Platform
    Provides advanced security, DDoS protection, geo-blocking, and threat intelligence
    """
    
    def __init__(
        self,
        config_path: str = "/etc/firewall/config.yaml",
        geoip_database_path: str = "/var/lib/GeoLite2/GeoLite2-City.mmdb",
        threat_feeds: Optional[List[str]] = None
    ):
        self.config_path = config_path
        self.geoip_database_path = geoip_database_path
        self.threat_feeds = threat_feeds or []
        
        # Configuration storage
        self.rules: Dict[str, FirewallRule] = {}
        self.policies: Dict[str, SecurityPolicy] = {}
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.blocked_ips: Set[str] = set()
        self.rate_limit_cache: Dict[str, Dict] = {}
        
        # GeoIP database
        self.geoip_reader = None
        
        # Network interfaces
        self.iptables_manager = None
        self.nftables_manager = None
        
        # Kubernetes integration
        self.k8s_client = None
        
        self._initialize_components()
    
    async def initialize(self) -> None:
        """Initialize firewall manager"""



        try:
            logger.info("Initializing Firewall Manager...")
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize GeoIP database
            await self._initialize_geoip()
            
            # Initialize threat intelligence
            await self._initialize_threat_intelligence()
            
            # Setup firewall backends
            await self._setup_firewall_backends()
            
            # Apply default security policies
            await self._apply_default_policies()
            
            # Start monitoring
            await self._start_monitoring()
            
            # Start threat feed updates
            await self._start_threat_feed_updates()
            
            logger.info("Firewall Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firewall Manager: {e}")
            raise
    
    async def add_firewall_rule(self, rule: FirewallRule) -> bool:
        """Add new firewall rule"""



        try:
            logger.info(f"Adding firewall rule: {rule.name}")
            
            # Validate rule
            if not await self._validate_rule(rule):
                return False
            
            # Check for conflicts
            if await self._check_rule_conflicts(rule):
                logger.warning(f"Rule conflicts detected for: {rule.name}")
                return False
            
            # Add rule
            self.rules[rule.name] = rule
            
            # Apply to firewall backends
            await self._apply_rule_to_backends(rule)
            
            # Update Kubernetes network policies if applicable
            await self._update_kubernetes_network_policy(rule)
            
            # Update metrics
            firewall_rules_total.labels(
                action=rule.action.value,
                protocol=rule.protocol.value
            ).inc()
            
            logger.info(f"Firewall rule added successfully: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add firewall rule: {e}")
            return False
    
    async def remove_firewall_rule(self, rule_name: str) -> bool:
        """Remove firewall rule"""



        try:
            if rule_name not in self.rules:
                logger.warning(f"Firewall rule not found: {rule_name}")
                return False
            
            rule = self.rules[rule_name]
            
            # Remove from backends
            await self._remove_rule_from_backends(rule)
            
            # Remove from configuration
            del self.rules[rule_name]
            
            logger.info(f"Firewall rule removed: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove firewall rule: {e}")
            return False
    
    async def apply_security_policy(self, policy: SecurityPolicy) -> bool:
        """Apply comprehensive security policy"""



        try:
            logger.info(f"Applying security policy: {policy.name}")
            
            # Validate policy
            if not await self._validate_policy(policy):
                return False
            
            # Store policy
            self.policies[policy.name] = policy
            
            # Apply all rules in policy
            for rule in policy.rules:
                if not await self.add_firewall_rule(rule):
                    logger.error(f"Failed to apply rule in policy: {rule.name}")
                    return False
            
            # Configure policy-specific settings
            await self._configure_policy_settings(policy)
            
            logger.info(f"Security policy applied successfully: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply security policy: {e}")
            return False
    
    async def block_ip_address(
        self,
        ip_address: str,
        reason: str = "Manual block",
        duration: Optional[timedelta] = None
    ) -> bool:
        """Block specific IP address"""



        try:
            logger.info(f"Blocking IP address: {ip_address} - {reason}")
            
            # Validate IP address
            try:
                ipaddress.ip_address(ip_address)
            except ValueError:
                logger.error(f"Invalid IP address: {ip_address}")
                return False
            
            # Add to blocked IPs
            self.blocked_ips.add(ip_address)
            
            # Create temporary rule
            rule = FirewallRule(
                name=f"block_{ip_address}_{int(datetime.now().timestamp())}",
                priority=1000,
                action=FirewallAction.DROP,
                protocol=ProtocolType.ALL,
                source_ips=[IPRange(network=f"{ip_address}/32", description=reason)],
                description=f"Blocked IP: {reason}",
                expires_at=datetime.now() + duration if duration else None
            )
            
            # Apply rule
            await self.add_firewall_rule(rule)
            
            # Update metrics
            blocked_requests_total.labels(reason=reason, source=ip_address).inc()
            
            # Schedule auto-removal if duration specified
            if duration:
                asyncio.create_task(self._schedule_ip_unblock(ip_address, duration))
            
            logger.info(f"IP address blocked successfully: {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to block IP address: {e}")
            return False
    
    async def unblock_ip_address(self, ip_address: str) -> bool:
        """Unblock specific IP address"""



        try:
            if ip_address not in self.blocked_ips:
                logger.warning(f"IP address not blocked: {ip_address}")
                return False
            
            # Remove from blocked IPs
            self.blocked_ips.discard(ip_address)
            
            # Find and remove blocking rules
            rules_to_remove = []
            for rule_name, rule in self.rules.items():
                for ip_range in rule.source_ips:
                    if ip_range.network == f"{ip_address}/32":
                        rules_to_remove.append(rule_name)
            
            for rule_name in rules_to_remove:
                await self.remove_firewall_rule(rule_name)
            
            logger.info(f"IP address unblocked: {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unblock IP address: {e}")
            return False
    
    async def enable_geo_blocking(
        self,
        blocked_countries: List[str],
        allowed_countries: Optional[List[str]] = None
    ) -> bool:
        """Enable geographic blocking"""



        try:
            logger.info(f"Enabling geo-blocking for countries: {blocked_countries}")
            
            # Create geo-blocking rule
            rule = FirewallRule(
                name="geo_blocking_rule",
                priority=500,
                action=FirewallAction.DROP,
                protocol=ProtocolType.ALL,
                countries_blocked=blocked_countries,
                countries_allowed=allowed_countries or [],
                description="Geographic blocking rule"
            )
            
            # Apply rule
            await self.add_firewall_rule(rule)
            
            logger.info("Geo-blocking enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable geo-blocking: {e}")
            return False
    
    async def enable_ddos_protection(
        self,
        threshold: int = 1000,  # requests per minute
        action: FirewallAction = FirewallAction.RATE_LIMIT
    ) -> bool:
        """Enable DDoS protection"""



        try:
            logger.info(f"Enabling DDoS protection with threshold: {threshold}")
            
            # Create DDoS protection rule
            rule = FirewallRule(
                name="ddos_protection_rule",
                priority=100,
                action=action,
                protocol=ProtocolType.ALL,
                rate_limit=threshold,
                description="DDoS protection rule"
            )
            
            # Apply rule
            await self.add_firewall_rule(rule)
            
            # Start DDoS monitoring
            asyncio.create_task(self._ddos_monitoring_loop())
            
            logger.info("DDoS protection enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable DDoS protection: {e}")
            return False
    
    async def update_threat_intelligence(self, threat_data: ThreatIntelligence) -> bool:
        """Update threat intelligence data"""



        try:
            logger.info(f"Updating threat intelligence for IP: {threat_data.ip_address}")
            
            # Store threat data
            self.threat_intelligence[threat_data.ip_address] = threat_data
            
            # Auto-block high-threat IPs
            if threat_data.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self.block_ip_address(
                    threat_data.ip_address,
                    f"Threat intelligence: {threat_data.threat_type}",
                    timedelta(hours=24)
                )
            
            logger.info(f"Threat intelligence updated: {threat_data.ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update threat intelligence: {e}")
            return False
    
    async def get_firewall_status(self) -> Dict[str, Any]:
        """Get comprehensive firewall status"""



        try:
            status = {
                'total_rules': len(self.rules),
                'active_policies': len(self.policies),
                'blocked_ips': len(self.blocked_ips),
                'threat_ips': len(self.threat_intelligence),
                'rules': {},
                'policies': list(self.policies.keys()),
                'blocked_ips_list': list(self.blocked_ips),
                'recent_blocks': [],
                'connection_stats': {},
                'performance_metrics': {}
            }
            
            # Rule details
            for rule_name, rule in self.rules.items():
                status['rules'][rule_name] = {
                    'priority': rule.priority,
                    'action': rule.action.value,
                    'protocol': rule.protocol.value,
                    'enabled': rule.enabled,
                    'source_ips_count': len(rule.source_ips),
                    'destination_ports': rule.destination_ports,
                    'rate_limit': rule.rate_limit,
                    'expires_at': rule.expires_at.isoformat() if rule.expires_at else None
                }
            
            # Connection statistics by country
            connection_stats = await self._get_connection_statistics()
            status['connection_stats'] = connection_stats
            
            # Performance metrics
            status['performance_metrics'] = {
                'total_blocked_requests': blocked_requests_total._value.sum(),
                'average_processing_latency': firewall_latency._sum.get() / max(firewall_latency._count.get(), 1)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get firewall status: {e}")
            return {}
    
    # Private methods
    
    def _initialize_components(self) -> None:
        """Initialize firewall components"""



        try:
            # Initialize iptables if available
            try:
                import iptc
                self.iptables_manager = iptc
            except ImportError:
                logger.warning("iptables not available")
            
            # Initialize nftables if available
            try:
                import nftables
                self.nftables_manager = nftables.Nftables()
            except ImportError:
                logger.warning("nftables not available")
            
            # Initialize Kubernetes client
            try:
                config.load_incluster_config()
                self.k8s_client = client.NetworkingV1Api()
            except Exception:
                logger.warning("Kubernetes client not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
    
    async def _load_configuration(self) -> None:
        """Load firewall configuration"""



        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Load rules
            if 'rules' in config_data:
                for rule_data in config_data['rules']:
                    rule = FirewallRule(**rule_data)
                    self.rules[rule.name] = rule
            
            # Load policies
            if 'policies' in config_data:
                for policy_data in config_data['policies']:
                    policy = SecurityPolicy(**policy_data)
                    self.policies[policy.name] = policy
            
            # Load blocked IPs
            if 'blocked_ips' in config_data:
                self.blocked_ips = set(config_data['blocked_ips'])
                
        except FileNotFoundError:
            logger.info("Configuration file not found, starting with default configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def _initialize_geoip(self) -> None:
        """Initialize GeoIP database"""



        try:
            import geoip2.database
            self.geoip_reader = geoip2.database.Reader(self.geoip_database_path)
            logger.info("GeoIP database initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize GeoIP database: {e}")
    
    async def _initialize_threat_intelligence(self) -> None:
        """Initialize threat intelligence feeds"""



        try:
            # Load existing threat data
            for feed_url in self.threat_feeds:
                await self._update_threat_feed(feed_url)
            
            logger.info("Threat intelligence initialized")
        except Exception as e:
            logger.error(f"Failed to initialize threat intelligence: {e}")
    
    async def _setup_firewall_backends(self) -> None:
        """Setup firewall backend systems"""



        try:
            # Configure iptables rules
            if self.iptables_manager:
                await self._configure_iptables()
            
            # Configure nftables rules
            if self.nftables_manager:
                await self._configure_nftables()
            
            logger.info("Firewall backends configured")
        except Exception as e:
            logger.error(f"Failed to setup firewall backends: {e}")
    
    async def _apply_default_policies(self) -> None:
        """Apply default security policies"""



        try:
            # Create default policy for IA platform protection
            default_policy = SecurityPolicy(
                name="ia_platform_default",
                rules=[
                    # Block common attack ports
                    FirewallRule(
                        name="block_attack_ports",
                        priority=900,
                        action=FirewallAction.DROP,
                        protocol=ProtocolType.TCP,
                        destination_ports=[23, 135, 139, 445, 1433, 3389],
                        description="Block common attack ports"
                    ),
                    # Rate limit API endpoints
                    FirewallRule(
                        name="api_rate_limit",
                        priority=800,
                        action=FirewallAction.RATE_LIMIT,
                        protocol=ProtocolType.HTTP,
                        destination_ports=[80, 443],
                        rate_limit=1000,
                        description="API rate limiting"
                    )
                ]
            )
            
            await self.apply_security_policy(default_policy)
            
        except Exception as e:
            logger.error(f"Failed to apply default policies: {e}")
    
    async def _validate_rule(self, rule: FirewallRule) -> bool:
        """Validate firewall rule"""
        if not rule.name:
            logger.error("Rule name is required")
            return False
        
        if rule.priority < 0 or rule.priority > 10000:
            logger.error("Rule priority must be between 0 and 10000")
            return False
        
        # Validate IP ranges
        for ip_range in rule.source_ips + rule.destination_ips:
            try:
                ipaddress.ip_network(ip_range.network, strict=False)
            except ValueError:
                logger.error(f"Invalid IP network: {ip_range.network}")
                return False
        
        # Validate ports
        for port in rule.source_ports + rule.destination_ports:
            if port < 1 or port > 65535:
                logger.error(f"Invalid port number: {port}")
                return False
        
        return True
    
    async def _check_rule_conflicts(self, rule: FirewallRule) -> bool:
        """Check for rule conflicts"""
        # Check for duplicate names
        if rule.name in self.rules:
            return True
        
        # Check for conflicting priorities
        for existing_rule in self.rules.values():
            if existing_rule.priority == rule.priority:
                return True
        
        return False
    
    async def _start_monitoring(self) -> None:
        """Start firewall monitoring"""
        asyncio.create_task(self._monitoring_loop())
    
    async def _start_threat_feed_updates(self) -> None:
        """Start threat feed updates"""
        asyncio.create_task(self._threat_feed_update_loop())
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                # Check rule expiration
                await self._check_rule_expiration()
                
                # Update connection statistics
                await self._update_connection_statistics()
                
                # Clean up rate limit cache
                await self._cleanup_rate_limit_cache()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _threat_feed_update_loop(self) -> None:
        """Threat feed update loop"""
        while True:
            try:
                for feed_url in self.threat_feeds:
                    await self._update_threat_feed(feed_url)
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Threat feed update error: {e}")
                await asyncio.sleep(3600)
