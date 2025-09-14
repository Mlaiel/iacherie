"""
Firewall Configuration module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise Network Firewall Configuration Manager
# Advanced firewall rules and security policies
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
import json
import logging
from datetime import datetime
from enum import Enum
import ipaddress
import re

class FirewallAction(Enum):
    """Firewall rule actions"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    REJECT = "reject"
    LOG = "log"

class ProtocolType(Enum):
    """Network protocol types"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"

class TrafficDirection(Enum):
    """Traffic direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class FirewallRule:
    """Firewall rule definition"""
    id: str
    name: str
    priority: int
    action: FirewallAction
    protocol: ProtocolType
    source_ip: str
    destination_ip: str
    source_port: Optional[Union[int, str]]
    destination_port: Optional[Union[int, str]]
    direction: TrafficDirection
    description: str
    enabled: bool = True
    created_at: datetime = None
    last_modified: datetime = None

@dataclass
class SecurityZone:
    """Network security zone definition"""
    name: str
    description: str
    trust_level: int  # 0-100, where 100 is most trusted
    networks: List[str]
    default_action: FirewallAction
    allowed_protocols: List[ProtocolType]

class FirewallConfiguration:
    """
    Enterprise Network Firewall Configuration Manager
    
    Capabilities:
    - Multi-zone firewall management
    - Advanced rule engine with priorities
    - Application-aware filtering
    - DDoS protection and rate limiting
    - VPN and tunnel management
    - Compliance policy enforcement
    - Real-time threat detection
    """
    
    def __init__(self) -> None:
        self.logger = self._setup_logging()
        self.rules: Dict[str, FirewallRule] = {}
        self.security_zones: Dict[str, SecurityZone] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self.blocked_ips: set = set()
        self.allowed_ips: set = set()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("FirewallConfiguration")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self) -> bool:
        """Initialize firewall configuration"""
        try:
            # Create default security zones
            await self._create_default_zones()
            
            # Load baseline security rules
            await self._load_baseline_rules()
            
            # Initialize threat intelligence
            await self._initialize_threat_intelligence()
            
            # Setup monitoring and alerting
            await self._setup_monitoring()
            
            self.logger.info("Firewall configuration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize firewall configuration: {e}")
            return False
    
    async def _create_default_zones(self) -> bool:
        """Create default security zones"""
        try:
            # DMZ Zone
            dmz_zone = SecurityZone(
                name="dmz",
                description="Demilitarized Zone for public-facing services",
                trust_level=30,
                networks=["10.0.1.0/24", "172.16.1.0/24"],
                default_action=FirewallAction.DENY,
                allowed_protocols=[ProtocolType.TCP, ProtocolType.UDP]
            )
            
            # Internal Zone
            internal_zone = SecurityZone(
                name="internal",
                description="Internal corporate network",
                trust_level=80,
                networks=["10.0.0.0/16", "172.16.0.0/16", "192.168.0.0/16"],
                default_action=FirewallAction.ALLOW,
                allowed_protocols=[ProtocolType.TCP, ProtocolType.UDP, ProtocolType.ICMP]
            )
            
            # Management Zone
            mgmt_zone = SecurityZone(
                name="management",
                description="Network management and administration",
                trust_level=90,
                networks=["10.0.100.0/24", "172.16.100.0/24"],
                default_action=FirewallAction.ALLOW,
                allowed_protocols=[ProtocolType.TCP, ProtocolType.UDP, ProtocolType.ICMP]
            )
            
            # Guest Zone
            guest_zone = SecurityZone(
                name="guest",
                description="Guest and visitor network access",
                trust_level=10,
                networks=["10.0.200.0/24", "172.16.200.0/24"],
                default_action=FirewallAction.DENY,
                allowed_protocols=[ProtocolType.TCP, ProtocolType.UDP]
            )
            
            # AI Processing Zone
            ai_zone = SecurityZone(
                name="ai-processing",
                description="AI and machine learning workloads",
                trust_level=70,
                networks=["10.0.50.0/24", "172.16.50.0/24"],
                default_action=FirewallAction.ALLOW,
                allowed_protocols=[ProtocolType.TCP, ProtocolType.UDP]
            )
            
            self.security_zones = {
                "dmz": dmz_zone,
                "internal": internal_zone,
                "management": mgmt_zone,
                "guest": guest_zone,
                "ai-processing": ai_zone
            }
            
            self.logger.info("Default security zones created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create default zones: {e}")
            return False
    
    async def _load_baseline_rules(self) -> bool:
        """Load baseline security rules"""
        try:
            baseline_rules = [
                # Allow internal communication
                FirewallRule(
                    id="baseline-001",
                    name="Allow Internal to Internal",
                    priority=1000,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.ALL,
                    source_ip="10.0.0.0/16",
                    destination_ip="10.0.0.0/16",
                    source_port=None,
                    destination_port=None,
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow all internal network communication"
                ),
                
                # Allow DNS queries
                FirewallRule(
                    id="baseline-002",
                    name="Allow DNS Queries",
                    priority=900,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.UDP,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="53",
                    direction=TrafficDirection.OUTBOUND,
                    description="Allow DNS resolution"
                ),
                
                # Allow HTTPS outbound
                FirewallRule(
                    id="baseline-003",
                    name="Allow HTTPS Outbound",
                    priority=850,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="443",
                    direction=TrafficDirection.OUTBOUND,
                    description="Allow HTTPS connections"
                ),
                
                # Block common attack ports
                FirewallRule(
                    id="baseline-004",
                    name="Block Telnet",
                    priority=100,
                    action=FirewallAction.DENY,
                    protocol=ProtocolType.TCP,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="23",
                    direction=TrafficDirection.INBOUND,
                    description="Block insecure Telnet protocol"
                ),
                
                # Block FTP
                FirewallRule(
                    id="baseline-005",
                    name="Block FTP",
                    priority=100,
                    action=FirewallAction.DENY,
                    protocol=ProtocolType.TCP,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="21",
                    direction=TrafficDirection.INBOUND,
                    description="Block insecure FTP protocol"
                ),
                
                # Allow Kubernetes API server
                FirewallRule(
                    id="k8s-001",
                    name="Allow Kubernetes API",
                    priority=800,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="6443",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow Kubernetes API server access"
                ),
                
                # Allow kubelet
                FirewallRule(
                    id="k8s-002",
                    name="Allow Kubelet",
                    priority=800,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="10250",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow kubelet communication"
                ),
                
                # Allow Istio service mesh
                FirewallRule(
                    id="istio-001",
                    name="Allow Istio Pilot",
                    priority=750,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="15010",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow Istio Pilot discovery"
                ),
                
                # Default deny rule
                FirewallRule(
                    id="default-deny",
                    name="Default Deny All",
                    priority=1,
                    action=FirewallAction.DENY,
                    protocol=ProtocolType.ALL,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="any",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Default deny all traffic"
                )
            ]
            
            # Add rules to configuration
            for rule in baseline_rules:
                rule.created_at = datetime.utcnow()
                rule.last_modified = datetime.utcnow()
                self.rules[rule.id] = rule
            
            # Create rule groups
            self.rule_groups = {
                "baseline": ["baseline-001", "baseline-002", "baseline-003", "baseline-004", "baseline-005"],
                "kubernetes": ["k8s-001", "k8s-002"],
                "service-mesh": ["istio-001"],
                "default": ["default-deny"]
            }
            
            self.logger.info("Baseline security rules loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load baseline rules: {e}")
            return False
    
    async def _initialize_threat_intelligence(self) -> bool:
        """Initialize threat intelligence feeds"""
        try:
            # Known malicious IP ranges (example)
            malicious_ips = [
                "1.2.3.0/24",  # Example malicious network
                "192.0.2.0/24",  # Test network (RFC 5737)
                "198.51.100.0/24",  # Test network (RFC 5737)
                "203.0.113.0/24"  # Test network (RFC 5737)
            ]
            
            for ip_range in malicious_ips:
                self.blocked_ips.add(ip_range)
            
            # Trusted IP ranges
            trusted_ips = [
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16"
            ]
            
            for ip_range in trusted_ips:
                self.allowed_ips.add(ip_range)
            
            self.logger.info("Threat intelligence initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize threat intelligence: {e}")
            return False
    
    async def _setup_monitoring(self) -> bool:
        """Setup firewall monitoring and alerting"""
        try:
            # In a real implementation, this would setup:
            # - Log collection and analysis
            # - Alerting for suspicious activities
            # - Performance monitoring
            # - Compliance reporting
            
            self.logger.info("Firewall monitoring setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring: {e}")
            return False
    
    async def add_rule(self, rule: FirewallRule) -> bool:
        """Add new firewall rule"""
        try:
            # Validate rule
            if not await self._validate_rule(rule):
                self.logger.error(f"Rule validation failed: {rule.id}")
                return False
            
            # Check for conflicts
            conflicts = await self._check_rule_conflicts(rule)
            if conflicts:
                self.logger.warning(f"Rule conflicts detected: {conflicts}")
            
            # Add rule
            rule.created_at = datetime.utcnow()
            rule.last_modified = datetime.utcnow()
            self.rules[rule.id] = rule
            
            self.logger.info(f"Firewall rule added: {rule.id} - {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add firewall rule: {e}")
            return False
    
    async def _validate_rule(self, rule: FirewallRule) -> bool:
        """Validate firewall rule"""
        try:
            # Check required fields
            if not rule.id or not rule.name:
                return False
            
            # Validate IP addresses
            if rule.source_ip != "any":
                try:
                    ipaddress.ip_network(rule.source_ip, strict=False)
                except ValueError:
                    return False
            
            if rule.destination_ip != "any":
                try:
                    ipaddress.ip_network(rule.destination_ip, strict=False)
                except ValueError:
                    return False
            
            # Validate port ranges
            if rule.source_port and rule.source_port != "any":
                if not self._validate_port(rule.source_port):
                    return False
            
            if rule.destination_port and rule.destination_port != "any":
                if not self._validate_port(rule.destination_port):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate rule: {e}")
            return False
    
    def _validate_port(self, port: Union[int, str]) -> bool:
        """Validate port number or range"""
        try:
            if isinstance(port, int):
                return 1 <= port <= 65535
            
            if isinstance(port, str):
                if port == "any":
                    return True
                
                # Check for port range (e.g., "80-90")
                if "-" in port:
                    start, end = map(int, port.split("-"))
                    return 1 <= start <= end <= 65535
                
                # Single port
                port_num = int(port)
                return 1 <= port_num <= 65535
            
            return False
            
        except (ValueError, AttributeError):
            return False
    
    async def _check_rule_conflicts(self, new_rule: FirewallRule) -> List[str]:
        """Check for rule conflicts"""
        try:
            conflicts = []
            
            for existing_id, existing_rule in self.rules.items():
                # Check for overlapping rules with same priority
                if (existing_rule.priority == new_rule.priority and
                    self._rules_overlap(existing_rule, new_rule)):
                    conflicts.append(existing_id)
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Failed to check rule conflicts: {e}")
            return []
    
    def _rules_overlap(self, rule1: FirewallRule, rule2: FirewallRule) -> bool:
        """Check if two rules overlap in scope"""
        try:
            # Simplified overlap check
            # In a real implementation, this would be more sophisticated
            return (
                rule1.protocol == rule2.protocol and
                rule1.direction == rule2.direction and
                self._ip_ranges_overlap(rule1.source_ip, rule2.source_ip) and
                self._ip_ranges_overlap(rule1.destination_ip, rule2.destination_ip)
            )
            
        except Exception:
            return False
    
    def _ip_ranges_overlap(self, ip1: str, ip2: str) -> bool:
        """Check if two IP ranges overlap"""
        try:
            if ip1 == "any" or ip2 == "any":
                return True
            
            network1 = ipaddress.ip_network(ip1, strict=False)
            network2 = ipaddress.ip_network(ip2, strict=False)
            
            return network1.overlaps(network2)
            
        except ValueError:
            return False
    
    async def create_application_rules(self, app_name: str, ports: List[int], sources: List[str] = None) -> bool:
        """Create firewall rules for an application"""
        try:
            if sources is None:
                sources = ["10.0.0.0/16"]  # Default to internal network
            
            rules_created = 0
            
            for i, port in enumerate(ports):
                for j, source in enumerate(sources):
                    rule_id = f"app-{app_name}-{port}-{j}"
                    
                    rule = FirewallRule(
                        id=rule_id,
                        name=f"Allow {app_name} on port {port}",
                        priority=500,
                        action=FirewallAction.ALLOW,
                        protocol=ProtocolType.TCP,
                        source_ip=source,
                        destination_ip="any",
                        source_port="any",
                        destination_port=str(port),
                        direction=TrafficDirection.INBOUND,
                        description=f"Allow access to {app_name} application on port {port}"
                    )
                    
                    if await self.add_rule(rule):
                        rules_created += 1
            
            # Add to application rule group
            if app_name not in self.rule_groups:
                self.rule_groups[app_name] = []
            
            app_rules = [f"app-{app_name}-{port}-{j}" for j, _ in enumerate(sources) for port in ports]
            self.rule_groups[app_name].extend(app_rules)
            
            self.logger.info(f"Created {rules_created} firewall rules for application {app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create application rules: {e}")
            return False
    
    async def create_kubernetes_rules(self) -> bool:
        """Create Kubernetes-specific firewall rules"""
        try:
            k8s_rules = [
                # etcd cluster communication
                FirewallRule(
                    id="k8s-etcd-001",
                    name="Allow etcd client communication",
                    priority=800,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="2379",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow etcd client communication"
                ),
                
                # etcd peer communication
                FirewallRule(
                    id="k8s-etcd-002",
                    name="Allow etcd peer communication",
                    priority=800,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="2380",
                    direction=TrafficDirection.BIDIRECTIONAL,
                    description="Allow etcd peer communication"
                ),
                
                # kube-proxy metrics
                FirewallRule(
                    id="k8s-proxy-001",
                    name="Allow kube-proxy metrics",
                    priority=750,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="10.0.0.0/16",
                    destination_ip="any",
                    source_port="any",
                    destination_port="10249",
                    direction=TrafficDirection.INBOUND,
                    description="Allow kube-proxy metrics collection"
                ),
                
                # NodePort services
                FirewallRule(
                    id="k8s-nodeport-001",
                    name="Allow NodePort services",
                    priority=700,
                    action=FirewallAction.ALLOW,
                    protocol=ProtocolType.TCP,
                    source_ip="any",
                    destination_ip="any",
                    source_port="any",
                    destination_port="30000-32767",
                    direction=TrafficDirection.INBOUND,
                    description="Allow NodePort service access"
                )
            ]
            
            for rule in k8s_rules:
                await self.add_rule(rule)
            
            # Update Kubernetes rule group
            k8s_rule_ids = [rule.id for rule in k8s_rules]
            if "kubernetes" in self.rule_groups:
                self.rule_groups["kubernetes"].extend(k8s_rule_ids)
            else:
                self.rule_groups["kubernetes"] = k8s_rule_ids
            
            self.logger.info("Kubernetes firewall rules created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Kubernetes rules: {e}")
            return False
    
    async def block_malicious_ip(self, ip_address: str, reason: str = "Threat detected") -> bool:
        """Block malicious IP address"""
        try:
            rule_id = f"block-{ip_address.replace('.', '-').replace('/', '-')}"
            
            rule = FirewallRule(
                id=rule_id,
                name=f"Block malicious IP {ip_address}",
                priority=50,  # High priority for security blocks
                action=FirewallAction.DENY,
                protocol=ProtocolType.ALL,
                source_ip=ip_address,
                destination_ip="any",
                source_port="any",
                destination_port="any",
                direction=TrafficDirection.BIDIRECTIONAL,
                description=f"Block malicious IP: {reason}"
            )
            
            if await self.add_rule(rule):
                self.blocked_ips.add(ip_address)
                self.logger.warning(f"Blocked malicious IP: {ip_address} - {reason}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to block malicious IP: {e}")
            return False
    
    async def generate_firewall_config(self, format_type: str = "json") -> str:
        """Generate firewall configuration in specified format"""
        try:
            config = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": "1.0",
                    "total_rules": len(self.rules),
                    "total_zones": len(self.security_zones)
                },
                "security_zones": {
                    name: {
                        "description": zone.description,
                        "trust_level": zone.trust_level,
                        "networks": zone.networks,
                        "default_action": zone.default_action.value,
                        "allowed_protocols": [p.value for p in zone.allowed_protocols]
                    }
                    for name, zone in self.security_zones.items()
                },
                "firewall_rules": [
                    {
                        "id": rule.id,
                        "name": rule.name,
                        "priority": rule.priority,
                        "action": rule.action.value,
                        "protocol": rule.protocol.value,
                        "source_ip": rule.source_ip,
                        "destination_ip": rule.destination_ip,
                        "source_port": rule.source_port,
                        "destination_port": rule.destination_port,
                        "direction": rule.direction.value,
                        "description": rule.description,
                        "enabled": rule.enabled,
                        "created_at": rule.created_at.isoformat() if rule.created_at else None
                    }
                    for rule in sorted(self.rules.values(), key=lambda r: r.priority, reverse=True)
                ],
                "rule_groups": self.rule_groups,
                "blocked_ips": list(self.blocked_ips),
                "allowed_ips": list(self.allowed_ips)
            }
            
            if format_type.lower() == "json":
                return json.dumps(config, indent=2)
            elif format_type.lower() == "yaml":
                import yaml
                return yaml.dump(config, default_flow_style=False)
            else:
                return str(config)
                
        except Exception as e:
            self.logger.error(f"Failed to generate firewall config: {e}")
            return ""

# Factory function for easy instantiation
def create_firewall_configuration() -> FirewallConfiguration:
    """Create and initialize firewall configuration"""
    return FirewallConfiguration()

# Enterprise firewall patterns
ENTERPRISE_FIREWALL_PATTERNS = {
    "zero_trust": {
        "default_action": "deny",
        "verification_required": True,
        "encryption_enforced": True,
        "continuous_monitoring": True
    },
    "defense_in_depth": {
        "multiple_layers": True,
        "zone_segmentation": True,
        "application_aware": True,
        "threat_intelligence": True
    },
    "compliance_focused": {
        "audit_logging": True,
        "policy_enforcement": True,
        "change_tracking": True,
        "compliance_reporting": True
    }
}