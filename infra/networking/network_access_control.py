"""
Network Access Control module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Network Access Control for Multi-Cloud Infrastructure
# Advanced network access management with zero-trust architecture
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from google.cloud import compute_v1
import ipaddress
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessAction(Enum):
    """Network access actions."""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    ALERT = "alert"

class AccessDirection(Enum):
    """Network access direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

class AccessLevel(Enum):
    """Access level classification."""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"

class ThreatLevel(Enum):
    """Threat level assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AccessRule:
    """Network access control rule."""
    id: str
    name: str
    description: str
    source: str  # IP, CIDR, or resource identifier
    destination: str  # IP, CIDR, or resource identifier
    protocol: str
    port_range: Tuple[int, int]
    action: AccessAction
    direction: AccessDirection
    priority: int
    access_level: AccessLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class AccessAttempt:
    """Network access attempt record."""
    id: str
    source_ip: str
    destination_ip: str
    protocol: str
    port: int
    action_taken: AccessAction
    rule_matched: Optional[str]
    timestamp: datetime
    user_agent: Optional[str] = None
    geo_location: Optional[Dict[str, str]] = None
    threat_indicators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThreatIntelligence:
    """Threat intelligence data."""
    ip_address: str
    threat_level: ThreatLevel
    threat_types: List[str]
    reputation_score: float  # 0-100
    last_seen: datetime
    sources: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessPolicy:
    """Network access policy."""
    id: str
    name: str
    description: str
    rules: List[AccessRule]
    default_action: AccessAction
    applies_to: List[str]  # Resource identifiers
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class NetworkAccessController:
    """
    Enterprise-grade network access control system.
    
    Implements zero-trust network architecture with comprehensive
    access control, threat intelligence, and compliance monitoring.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize network access controller."""
        self.config = config
        self.access_rules = {}
        self.access_policies = {}
        self.access_attempts = []
        self.threat_intelligence = {}
        self.blocked_ips = set()
        
        # Cloud clients
        self.aws_clients = {}
        self.azure_clients = {}
        self.gcp_clients = {}
        
        self._initialize_cloud_clients()
        self._load_threat_intelligence()
        self._initialize_default_policies()
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS clients
            if self.config.get('aws', {}).get('enabled', False):
                session = boto3.Session(
                    aws_access_key_id=self.config['aws'].get('access_key'),
                    aws_secret_access_key=self.config['aws'].get('secret_key'),
                    region_name=self.config['aws'].get('region', 'us-east-1')
                )
                
                self.aws_clients = {
                    'ec2': session.client('ec2'),
                    'waf': session.client('wafv2'),
                    'cloudfront': session.client('cloudfront'),
                    'shield': session.client('shield'),
                    'guardduty': session.client('guardduty')
                }
            
            # Azure clients
            if self.config.get('azure', {}).get('enabled', False):
                credential = DefaultAzureCredential()
                subscription_id = self.config['azure']['subscription_id']
                
                self.azure_clients = {
                    'network': NetworkManagementClient(credential, subscription_id)
                }
            
            # GCP clients
            if self.config.get('gcp', {}).get('enabled', False):
                self.gcp_clients = {
                    'compute': compute_v1.FirewallsClient(),
                    'security': compute_v1.SecurityPoliciesClient()
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud clients: {e}")
    
    def _load_threat_intelligence(self) -> None:
        """Load threat intelligence data."""
        try:
            # Load known threat IPs and indicators
            threat_feeds = self.config.get('threat_feeds', [])
            
            # Example threat intelligence (in production, this would come from feeds)
            known_threats = [
                {
                    "ip": "192.168.1.100",
                    "threat_level": ThreatLevel.HIGH,
                    "threat_types": ["malware", "botnet"],
                    "reputation_score": 15.0,
                    "sources": ["internal_detection"]
                },
                {
                    "ip": "10.0.0.50",
                    "threat_level": ThreatLevel.MEDIUM,
                    "threat_types": ["suspicious_activity"],
                    "reputation_score": 45.0,
                    "sources": ["behavioral_analysis"]
                }
            ]
            
            for threat in known_threats:
                threat_intel = ThreatIntelligence(
                    ip_address=threat["ip"],
                    threat_level=threat["threat_level"],
                    threat_types=threat["threat_types"],
                    reputation_score=threat["reputation_score"],
                    last_seen=datetime.utcnow(),
                    sources=threat["sources"]
                )
                self.threat_intelligence[threat["ip"]] = threat_intel
            
            logger.info(f"Loaded {len(self.threat_intelligence)} threat intelligence entries")
            
        except Exception as e:
            logger.error(f"Failed to load threat intelligence: {e}")
    
    def _initialize_default_policies(self) -> None:
        """Initialize default access policies."""
        try:
            # Default deny policy
            default_deny_policy = AccessPolicy(
                id="default-deny",
                name="Default Deny All",
                description="Default policy to deny all traffic not explicitly allowed",
                rules=[],
                default_action=AccessAction.DENY,
                applies_to=["*"]
            )
            
            # Web traffic policy
            web_policy_rules = [
                AccessRule(
                    id="allow-http",
                    name="Allow HTTP",
                    description="Allow HTTP traffic",
                    source="0.0.0.0/0",
                    destination="web-servers",
                    protocol="tcp",
                    port_range=(80, 80),
                    action=AccessAction.ALLOW,
                    direction=AccessDirection.INBOUND,
                    priority=100,
                    access_level=AccessLevel.PUBLIC
                ),
                AccessRule(
                    id="allow-https",
                    name="Allow HTTPS",
                    description="Allow HTTPS traffic",
                    source="0.0.0.0/0",
                    destination="web-servers",
                    protocol="tcp",
                    port_range=(443, 443),
                    action=AccessAction.ALLOW,
                    direction=AccessDirection.INBOUND,
                    priority=100,
                    access_level=AccessLevel.PUBLIC
                )
            ]
            
            web_policy = AccessPolicy(
                id="web-traffic",
                name="Web Traffic Policy",
                description="Policy for web server access",
                rules=web_policy_rules,
                default_action=AccessAction.DENY,
                applies_to=["web-servers"]
            )
            
            # Management policy
            mgmt_policy_rules = [
                AccessRule(
                    id="allow-ssh-admin",
                    name="Allow SSH from Admin",
                    description="Allow SSH from admin networks",
                    source="10.0.0.0/8",
                    destination="management-servers",
                    protocol="tcp",
                    port_range=(22, 22),
                    action=AccessAction.ALLOW,
                    direction=AccessDirection.INBOUND,
                    priority=200,
                    access_level=AccessLevel.RESTRICTED
                )
            ]
            
            mgmt_policy = AccessPolicy(
                id="management",
                name="Management Access Policy",
                description="Policy for management server access",
                rules=mgmt_policy_rules,
                default_action=AccessAction.DENY,
                applies_to=["management-servers"]
            )
            
            # Store policies
            self.access_policies = {
                "default-deny": default_deny_policy,
                "web-traffic": web_policy,
                "management": mgmt_policy
            }
            
            # Index rules
            for policy in self.access_policies.values():
                for rule in policy.rules:
                    self.access_rules[rule.id] = rule
            
            logger.info(f"Initialized {len(self.access_policies)} default policies")
            
        except Exception as e:
            logger.error(f"Failed to initialize default policies: {e}")
    
    async def evaluate_access_request(self,
                                    source_ip: str,
                                    destination_ip: str,
                                    protocol: str,
                                    port: int,
                                    context: Optional[Dict[str, Any]] = None) -> AccessAttempt:
        """Evaluate network access request against policies."""
        try:
            attempt_id = hashlib.md5(
                f"{source_ip}:{destination_ip}:{protocol}:{port}:{datetime.utcnow()}".encode()
            ).hexdigest()
            
            # Check threat intelligence
            threat_indicators = []
            if source_ip in self.threat_intelligence:
                threat_intel = self.threat_intelligence[source_ip]
                threat_indicators.extend(threat_intel.threat_types)
                
                # Block high-risk IPs immediately
                if threat_intel.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    attempt = AccessAttempt(
                        id=attempt_id,
                        source_ip=source_ip,
                        destination_ip=destination_ip,
                        protocol=protocol,
                        port=port,
                        action_taken=AccessAction.DENY,
                        rule_matched="threat-intelligence",
                        timestamp=datetime.utcnow(),
                        threat_indicators=threat_indicators
                    )
                    self.access_attempts.append(attempt)
                    await self._log_access_attempt(attempt)
                    return attempt
            
            # Check if IP is in blocked list
            if source_ip in self.blocked_ips:
                attempt = AccessAttempt(
                    id=attempt_id,
                    source_ip=source_ip,
                    destination_ip=destination_ip,
                    protocol=protocol,
                    port=port,
                    action_taken=AccessAction.DENY,
                    rule_matched="blocked-ip",
                    timestamp=datetime.utcnow(),
                    threat_indicators=["blocked_ip"]
                )
                self.access_attempts.append(attempt)
                await self._log_access_attempt(attempt)
                return attempt
            
            # Evaluate against policies
            matched_rule = None
            action_taken = AccessAction.DENY
            
            # Sort policies by specificity (more specific first)
            sorted_policies = sorted(
                self.access_policies.values(),
                key=lambda p: len(p.applies_to) if "*" not in p.applies_to else 999
            )
            
            for policy in sorted_policies:
                if not policy.enabled:
                    continue
                
                # Check if policy applies to this destination
                if not self._policy_applies(policy, destination_ip, context):
                    continue
                
                # Sort rules by priority
                sorted_rules = sorted(policy.rules, key=lambda r: r.priority)
                
                for rule in sorted_rules:
                    if self._rule_matches(rule, source_ip, destination_ip, protocol, port):
                        matched_rule = rule.id
                        action_taken = rule.action
                        break
                
                if matched_rule:
                    break
            
            # If no rule matched, use default action
            if not matched_rule:
                # Use default deny policy
                action_taken = AccessAction.DENY
                matched_rule = "default-deny"
            
            # Create access attempt record
            attempt = AccessAttempt(
                id=attempt_id,
                source_ip=source_ip,
                destination_ip=destination_ip,
                protocol=protocol,
                port=port,
                action_taken=action_taken,
                rule_matched=matched_rule,
                timestamp=datetime.utcnow(),
                threat_indicators=threat_indicators,
                metadata=context or {}
            )
            
            self.access_attempts.append(attempt)
            await self._log_access_attempt(attempt)
            
            # Take additional actions based on result
            if action_taken == AccessAction.DENY:
                await self._handle_denied_access(attempt)
            elif action_taken == AccessAction.ALERT:
                await self._handle_alert(attempt)
            
            return attempt
            
        except Exception as e:
            logger.error(f"Failed to evaluate access request: {e}")
            raise
    
    def _policy_applies(self,
                       policy: AccessPolicy,
                       destination_ip: str,
                       context: Optional[Dict[str, Any]]) -> bool:
        """Check if policy applies to the destination."""
        try:
            # Check if policy applies to all resources
            if "*" in policy.applies_to:
                return True
            
            # Check specific resource identifiers
            for resource in policy.applies_to:
                if resource == destination_ip:
                    return True
                
                # Check if resource is a network range
                try:
                    network = ipaddress.ip_network(resource, strict=False)
                    if ipaddress.ip_address(destination_ip) in network:
                        return True
                except:
                    pass
                
                # Check resource tags or groups from context
                if context and context.get('resource_tags'):
                    if resource in context['resource_tags']:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check policy applicability: {e}")
            return False
    
    def _rule_matches(self,
                     rule: AccessRule,
                     source_ip: str,
                     destination_ip: str,
                     protocol: str,
                     port: int) -> bool:
        """Check if access rule matches the request."""
        try:
            # Check protocol
            if rule.protocol.lower() != protocol.lower() and rule.protocol != "*":
                return False
            
            # Check port range
            if rule.port_range[0] != -1:
                if not (rule.port_range[0] <= port <= rule.port_range[1]):
                    return False
            
            # Check source
            if not self._ip_matches(source_ip, rule.source):
                return False
            
            # Check destination
            if not self._ip_matches(destination_ip, rule.destination):
                return False
            
            # Check additional conditions
            if rule.conditions:
                # Implementation would check additional conditions
                pass
            
            # Check if rule has expired
            if rule.expires_at and rule.expires_at < datetime.utcnow():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to match rule: {e}")
            return False
    
    def _ip_matches(self, ip: str, pattern: str) -> bool:
        """Check if IP matches pattern."""
        try:
            # Exact match
            if ip == pattern:
                return True
            
            # Wildcard
            if pattern == "*" or pattern == "any":
                return True
            
            # CIDR range
            try:
                network = ipaddress.ip_network(pattern, strict=False)
                return ipaddress.ip_address(ip) in network
            except:
                pass
            
            # Resource identifier (would be resolved in real implementation)
            if not pattern.count('.') == 3:  # Not an IP address
                return True  # Simplified for this example
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to match IP: {e}")
            return False
    
    async def _log_access_attempt(self, attempt -> None: AccessAttempt) -> None:
        """Log access attempt for audit and analysis."""
        try:
            log_entry = {
                "id": attempt.id,
                "timestamp": attempt.timestamp.isoformat(),
                "source_ip": attempt.source_ip,
                "destination_ip": attempt.destination_ip,
                "protocol": attempt.protocol,
                "port": attempt.port,
                "action": attempt.action_taken.value,
                "rule_matched": attempt.rule_matched,
                "threat_indicators": attempt.threat_indicators
            }
            
            # In production, this would write to centralized logging
            logger.info(f"Access attempt: {json.dumps(log_entry)}")
            
            # Store in cloud-specific logging services
            if self.aws_clients.get('cloudtrail'):
                await self._log_to_aws_cloudtrail(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log access attempt: {e}")
    
    async def _handle_denied_access(self, attempt -> None: AccessAttempt) -> None:
        """Handle denied access attempts."""
        try:
            # Increment failed attempt counter for source IP
            source_ip = attempt.source_ip
            
            # Count recent failed attempts from this IP
            recent_attempts = [
                a for a in self.access_attempts[-1000:]  # Last 1000 attempts
                if (a.source_ip == source_ip and 
                    a.action_taken == AccessAction.DENY and
                    a.timestamp > datetime.utcnow() - timedelta(minutes=15))
            ]
            
            # If too many failed attempts, block the IP
            if len(recent_attempts) >= self.config.get('max_failed_attempts', 10):
                await self.block_ip(source_ip, f"Too many failed attempts: {len(recent_attempts)}")
            
            # Alert on suspicious patterns
            if len(recent_attempts) >= 5:
                await self._send_security_alert(
                    f"Suspicious activity from {source_ip}: {len(recent_attempts)} failed attempts"
                )
            
        except Exception as e:
            logger.error(f"Failed to handle denied access: {e}")
    
    async def _handle_alert(self, attempt -> None: AccessAttempt) -> None:
        """Handle access attempts that trigger alerts."""
        try:
            alert_message = (
                f"Network access alert: {attempt.source_ip} -> "
                f"{attempt.destination_ip}:{attempt.port} ({attempt.protocol})"
            )
            
            await self._send_security_alert(alert_message)
            
        except Exception as e:
            logger.error(f"Failed to handle alert: {e}")
    
    async def _send_security_alert(self, message -> None: str) -> None:
        """Send security alert to configured channels."""
        try:
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "warning",
                "message": message,
                "source": "network_access_controller"
            }
            
            # In production, this would send to alerting systems
            logger.warning(f"Security Alert: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")
    
    async def block_ip(self, ip_address -> None: str, reason -> None: str) -> None:
        """Block IP address across all network access points."""
        try:
            self.blocked_ips.add(ip_address)
            
            # Update threat intelligence
            if ip_address not in self.threat_intelligence:
                self.threat_intelligence[ip_address] = ThreatIntelligence(
                    ip_address=ip_address,
                    threat_level=ThreatLevel.HIGH,
                    threat_types=["blocked_ip"],
                    reputation_score=10.0,
                    last_seen=datetime.utcnow(),
                    sources=["access_controller"],
                    metadata={"block_reason": reason}
                )
            
            # Block in cloud providers
            if self.aws_clients.get('waf'):
                await self._block_ip_aws_waf(ip_address)
            
            if self.azure_clients.get('network'):
                await self._block_ip_azure_nsg(ip_address)
            
            if self.gcp_clients.get('compute'):
                await self._block_ip_gcp_firewall(ip_address)
            
            logger.info(f"Blocked IP address {ip_address}: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to block IP: {e}")
    
    async def _block_ip_aws_waf(self, ip_address -> None: str) -> None:
        """Block IP in AWS WAF."""
        try:
            waf_client = self.aws_clients['waf']
            
            # Create IP set for blocked IPs
            ip_set_name = "blocked-ips"
            
            # In production, this would manage IP sets properly
            logger.info(f"Would block {ip_address} in AWS WAF")
            
        except Exception as e:
            logger.error(f"Failed to block IP in AWS WAF: {e}")
    
    async def _block_ip_azure_nsg(self, ip_address -> None: str) -> None:
        """Block IP in Azure Network Security Group."""
        try:
            # Implementation would add deny rule to NSG
            logger.info(f"Would block {ip_address} in Azure NSG")
            
        except Exception as e:
            logger.error(f"Failed to block IP in Azure NSG: {e}")
    
    async def _block_ip_gcp_firewall(self, ip_address -> None: str) -> None:
        """Block IP in GCP Firewall."""
        try:
            # Implementation would create deny firewall rule
            logger.info(f"Would block {ip_address} in GCP Firewall")
            
        except Exception as e:
            logger.error(f"Failed to block IP in GCP Firewall: {e}")
    
    async def unblock_ip(self, ip_address -> None: str) -> None:
        """Unblock IP address."""
        try:
            self.blocked_ips.discard(ip_address)
            
            # Remove from threat intelligence if it was only blocked
            if (ip_address in self.threat_intelligence and 
                self.threat_intelligence[ip_address].threat_types == ["blocked_ip"]):
                del self.threat_intelligence[ip_address]
            
            # Remove from cloud providers
            # Implementation would remove blocking rules
            
            logger.info(f"Unblocked IP address {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to unblock IP: {e}")
    
    async def create_access_rule(self, rule: AccessRule) -> str:
        """Create new access rule."""
        try:
            self.access_rules[rule.id] = rule
            
            # Add to appropriate policy
            # In this example, add to web-traffic policy if it's for web servers
            if "web" in rule.destination:
                self.access_policies["web-traffic"].rules.append(rule)
            else:
                # Add to default policy
                if "default" not in self.access_policies:
                    self.access_policies["default"] = AccessPolicy(
                        id="default",
                        name="Default Policy",
                        description="Default access policy",
                        rules=[],
                        default_action=AccessAction.DENY,
                        applies_to=["*"]
                    )
                self.access_policies["default"].rules.append(rule)
            
            logger.info(f"Created access rule: {rule.name}")
            return rule.id
            
        except Exception as e:
            logger.error(f"Failed to create access rule: {e}")
            raise
    
    async def update_access_rule(self, rule_id: str, updates: Dict[str, Any]) -> AccessRule:
        """Update existing access rule."""
        try:
            if rule_id not in self.access_rules:
                raise ValueError(f"Access rule not found: {rule_id}")
            
            rule = self.access_rules[rule_id]
            
            # Update rule attributes
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            logger.info(f"Updated access rule: {rule_id}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to update access rule: {e}")
            raise
    
    async def delete_access_rule(self, rule_id: str) -> bool:
        """Delete access rule."""
        try:
            if rule_id not in self.access_rules:
                raise ValueError(f"Access rule not found: {rule_id}")
            
            # Remove from access rules
            del self.access_rules[rule_id]
            
            # Remove from policies
            for policy in self.access_policies.values():
                policy.rules = [r for r in policy.rules if r.id != rule_id]
            
            logger.info(f"Deleted access rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete access rule: {e}")
            return False
    
    async def get_access_statistics(self, 
                                  hours: int = 24) -> Dict[str, Any]:
        """Get access statistics for the specified time period."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_attempts = [
                a for a in self.access_attempts
                if a.timestamp > cutoff_time
            ]
            
            stats = {
                "period_hours": hours,
                "total_attempts": len(recent_attempts),
                "allowed_attempts": len([a for a in recent_attempts if a.action_taken == AccessAction.ALLOW]),
                "denied_attempts": len([a for a in recent_attempts if a.action_taken == AccessAction.DENY]),
                "alert_attempts": len([a for a in recent_attempts if a.action_taken == AccessAction.ALERT]),
                "unique_source_ips": len(set(a.source_ip for a in recent_attempts)),
                "blocked_ips": len(self.blocked_ips),
                "threat_ips": len([ip for ip, intel in self.threat_intelligence.items() 
                                 if intel.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]),
                "top_denied_ips": {},
                "top_ports": {},
                "threat_distribution": {}
            }
            
            # Top denied IPs
            denied_attempts = [a for a in recent_attempts if a.action_taken == AccessAction.DENY]
            ip_counts = {}
            for attempt in denied_attempts:
                ip_counts[attempt.source_ip] = ip_counts.get(attempt.source_ip, 0) + 1
            
            stats["top_denied_ips"] = dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Top ports
            port_counts = {}
            for attempt in recent_attempts:
                port_counts[attempt.port] = port_counts.get(attempt.port, 0) + 1
            
            stats["top_ports"] = dict(sorted(port_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Threat distribution
            threat_counts = {}
            for attempt in recent_attempts:
                for threat in attempt.threat_indicators:
                    threat_counts[threat] = threat_counts.get(threat, 0) + 1
            
            stats["threat_distribution"] = threat_counts
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get access statistics: {e}")
            raise
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report for network access controls."""
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "access_control_summary": {
                    "total_policies": len(self.access_policies),
                    "total_rules": len(self.access_rules),
                    "enabled_policies": len([p for p in self.access_policies.values() if p.enabled]),
                    "blocked_ips": len(self.blocked_ips)
                },
                "security_posture": {},
                "policy_analysis": {},
                "recommendations": []
            }
            
            # Analyze security posture
            deny_rules = len([r for r in self.access_rules.values() if r.action == AccessAction.DENY])
            allow_rules = len([r for r in self.access_rules.values() if r.action == AccessAction.ALLOW])
            
            report["security_posture"] = {
                "default_deny_ratio": deny_rules / len(self.access_rules) if self.access_rules else 0,
                "explicit_allow_rules": allow_rules,
                "zero_trust_compliance": deny_rules > allow_rules,
                "threat_intelligence_coverage": len(self.threat_intelligence),
                "access_level_distribution": {}
            }
            
            # Access level distribution
            level_counts = {}
            for rule in self.access_rules.values():
                level = rule.access_level.value
                level_counts[level] = level_counts.get(level, 0) + 1
            
            report["security_posture"]["access_level_distribution"] = level_counts
            
            # Policy analysis
            for policy_id, policy in self.access_policies.items():
                policy_analysis = {
                    "enabled": policy.enabled,
                    "rule_count": len(policy.rules),
                    "default_action": policy.default_action.value,
                    "coverage": len(policy.applies_to),
                    "last_updated": policy.updated_at.isoformat()
                }
                report["policy_analysis"][policy_id] = policy_analysis
            
            # Recommendations
            recommendations = []
            
            if allow_rules > deny_rules:
                recommendations.append("Consider implementing more explicit deny rules for zero-trust architecture")
            
            if len(self.access_policies) < 3:
                recommendations.append("Consider creating more granular access policies for different resource types")
            
            if not any(p.default_action == AccessAction.DENY for p in self.access_policies.values()):
                recommendations.append("Implement default-deny policies for enhanced security")
            
            if len(self.threat_intelligence) < 10:
                recommendations.append("Integrate additional threat intelligence feeds")
            
            if recommendations:
                report["recommendations"] = recommendations
            else:
                report["recommendations"] = ["Network access controls follow security best practices"]
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "aws": {
            "enabled": True,
            "region": "us-east-1"
        },
        "azure": {
            "enabled": True,
            "subscription_id": "your-subscription-id"
        },
        "gcp": {
            "enabled": True,
            "project_id": "your-project-id"
        },
        "max_failed_attempts": 10,
        "threat_feeds": ["internal", "commercial"]
    }
    
    async def main() -> None:
        # Initialize network access controller
        controller = NetworkAccessController(config)
        
        # Create custom access rule
        custom_rule = AccessRule(
            id="allow-api-access",
            name="Allow API Access",
            description="Allow access to API servers from web tier",
            source="10.0.1.0/24",
            destination="10.0.2.0/24",
            protocol="tcp",
            port_range=(8080, 8080),
            action=AccessAction.ALLOW,
            direction=AccessDirection.INBOUND,
            priority=150,
            access_level=AccessLevel.PRIVATE
        )
        
        await controller.create_access_rule(custom_rule)
        
        # Simulate access requests
        access_requests = [
            ("203.0.113.1", "10.0.2.5", "tcp", 8080),  # Should be allowed
            ("198.51.100.1", "10.0.2.5", "tcp", 22),   # Should be denied
            ("192.168.1.100", "10.0.2.5", "tcp", 80),  # Threat IP - should be blocked
        ]
        
        for source, dest, protocol, port in access_requests:
            attempt = await controller.evaluate_access_request(source, dest, protocol, port)
            print(f"Access from {source} to {dest}:{port} - {attempt.action_taken.value}")
        
        # Get statistics
        stats = await controller.get_access_statistics(24)
        print(f"Total attempts in last 24h: {stats['total_attempts']}")
        print(f"Denied attempts: {stats['denied_attempts']}")
        
        # Generate compliance report
        report = await controller.generate_compliance_report()
        print(f"Zero-trust compliance: {report['security_posture']['zero_trust_compliance']}")
    
    # Run the example
    asyncio.run(main())