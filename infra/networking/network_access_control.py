# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Network Access Control

Enterprise network access control system for advanced traffic filtering and monitoring.
Provides comprehensive network security and access management capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import json
import re


class AccessControlAction(Enum):
    """Access control actions"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    LOG = "log"
    RATE_LIMIT = "rate_limit"


class AccessControlCondition(Enum):
    """Access control conditions"""
    SOURCE_IP = "source_ip"
    DESTINATION_IP = "destination_ip"
    SOURCE_PORT = "source_port"
    DESTINATION_PORT = "destination_port"
    PROTOCOL = "protocol"
    USER_AGENT = "user_agent"
    GEOLOCATION = "geolocation"
    TIME_OF_DAY = "time_of_day"
    BANDWIDTH_USAGE = "bandwidth_usage"
    CONNECTION_COUNT = "connection_count"


class AccessControlScope(Enum):
    """Access control scope"""
    GLOBAL = "global"
    VPC = "vpc"
    SUBNET = "subnet"
    INSTANCE = "instance"
    APPLICATION = "application"


@dataclass
class AccessControlRule:
    """Network access control rule"""
    id: str
    name: str
    description: str
    scope: AccessControlScope
    scope_target: str  # VPC ID, subnet ID, instance ID, etc.
    conditions: Dict[AccessControlCondition, Any]
    action: AccessControlAction
    priority: int = 1000
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Rate limiting parameters
    rate_limit_requests: Optional[int] = None
    rate_limit_window: Optional[int] = None  # seconds
    
    # Logging parameters
    log_level: str = "info"
    log_details: bool = True


@dataclass
class AccessControlMetrics:
    """Access control metrics"""
    rule_id: str
    matches_count: int = 0
    blocks_count: int = 0
    allows_count: int = 0
    rate_limits_count: int = 0
    last_match: Optional[datetime] = None
    total_bytes: int = 0
    unique_sources: Set[str] = field(default_factory=set)


@dataclass
class AccessControlEvent:
    """Access control event log"""
    timestamp: datetime
    rule_id: str
    action: AccessControlAction
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    bytes_transferred: int = 0
    user_agent: Optional[str] = None
    geolocation: Optional[str] = None
    blocked: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


class NetworkAccessControl:
    """
    Enterprise network access control system
    
    Provides comprehensive network security and access management including:
    - Advanced traffic filtering and inspection
    - Geolocation-based access control
    - Rate limiting and DDoS protection
    - Application-layer security
    - Real-time monitoring and alerting
    - Compliance reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Access control rules storage
        self.rules: Dict[str, AccessControlRule] = {}
        self.metrics: Dict[str, AccessControlMetrics] = {}
        self.events: List[AccessControlEvent] = []
        
        # Rate limiting tracking
        self.rate_limit_buckets: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_events = self.config.get('max_events', 10000)
        self.geolocation_enabled = self.config.get('geolocation_enabled', False)
        self.deep_packet_inspection = self.config.get('deep_packet_inspection', False)
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default access control rules"""
        
        # Anti-DDoS rule
        ddos_protection_rule = AccessControlRule(
            id="ddos_protection",
            name="DDoS Protection",
            description="Rate limit connections per source IP",
            scope=AccessControlScope.GLOBAL,
            scope_target="*",
            conditions={
                AccessControlCondition.CONNECTION_COUNT: {"threshold": 100, "window": 60}
            },
            action=AccessControlAction.RATE_LIMIT,
            priority=100,
            rate_limit_requests=100,
            rate_limit_window=60
        )
        
        # Block known malicious IPs
        malicious_ip_rule = AccessControlRule(
            id="block_malicious_ips",
            name="Block Malicious IPs",
            description="Block traffic from known malicious IP addresses",
            scope=AccessControlScope.GLOBAL,
            scope_target="*",
            conditions={
                AccessControlCondition.SOURCE_IP: {
                    "blacklist": [
                        "192.168.100.0/24",  # Example malicious range
                        "10.0.100.0/24"      # Example malicious range
                    ]
                }
            },
            action=AccessControlAction.DENY,
            priority=50
        )
        
        # Admin access restriction
        admin_access_rule = AccessControlRule(
            id="restrict_admin_access",
            name="Restrict Admin Access",
            description="Restrict SSH/RDP access to admin networks only",
            scope=AccessControlScope.GLOBAL,
            scope_target="*",
            conditions={
                AccessControlCondition.DESTINATION_PORT: [22, 3389],
                AccessControlCondition.SOURCE_IP: {
                    "whitelist": [
                        "10.0.0.0/16",        # Internal network
                        "192.168.1.0/24"     # Admin network
                    ]
                }
            },
            action=AccessControlAction.ALLOW,
            priority=200
        )
        
        # Default deny for admin ports from external
        admin_deny_rule = AccessControlRule(
            id="deny_external_admin",
            name="Deny External Admin Access",
            description="Deny SSH/RDP access from external networks",
            scope=AccessControlScope.GLOBAL,
            scope_target="*",
            conditions={
                AccessControlCondition.DESTINATION_PORT: [22, 3389],
                AccessControlCondition.SOURCE_IP: {
                    "exclude_private": True
                }
            },
            action=AccessControlAction.DENY,
            priority=300
        )
        
        # Geolocation blocking (if enabled)
        if self.geolocation_enabled:
            geo_blocking_rule = AccessControlRule(
                id="geo_blocking",
                name="Geographic Blocking",
                description="Block traffic from high-risk countries",
                scope=AccessControlScope.GLOBAL,
                scope_target="*",
                conditions={
                    AccessControlCondition.GEOLOCATION: {
                        "blocked_countries": ["CN", "RU", "KP"]  # Example blocked countries
                    }
                },
                action=AccessControlAction.DENY,
                priority=150
            )
            self.add_rule(geo_blocking_rule)
        
        # Add default rules
        self.add_rule(ddos_protection_rule)
        self.add_rule(malicious_ip_rule)
        self.add_rule(admin_access_rule)
        self.add_rule(admin_deny_rule)
    
    def add_rule(self, rule: AccessControlRule):
        """Add an access control rule"""
        
        # Validate rule
        self._validate_rule(rule)
        
        # Store rule
        self.rules[rule.id] = rule
        
        # Initialize metrics
        self.metrics[rule.id] = AccessControlMetrics(rule_id=rule.id)
        
        self.logger.info(f"Added access control rule: {rule.name} ({rule.id})")
    
    def _validate_rule(self, rule: AccessControlRule):
        """Validate access control rule"""
        
        # Validate priority
        if not (1 <= rule.priority <= 10000):
            raise ValueError("Rule priority must be between 1 and 10000")
        
        # Validate conditions
        for condition, value in rule.conditions.items():
            if condition == AccessControlCondition.SOURCE_IP or condition == AccessControlCondition.DESTINATION_IP:
                if isinstance(value, dict):
                    # Validate IP lists
                    for ip_list in ['whitelist', 'blacklist']:
                        if ip_list in value:
                            for ip in value[ip_list]:
                                try:
                                    ipaddress.ip_network(ip, strict=False)
                                except ValueError:
                                    raise ValueError(f"Invalid IP/CIDR in {ip_list}: {ip}")
                else:
                    # Single IP/CIDR
                    try:
                        ipaddress.ip_network(value, strict=False)
                    except ValueError:
                        raise ValueError(f"Invalid IP/CIDR: {value}")
            
            elif condition in [AccessControlCondition.SOURCE_PORT, AccessControlCondition.DESTINATION_PORT]:
                if isinstance(value, list):
                    for port in value:
                        if not (1 <= port <= 65535):
                            raise ValueError(f"Invalid port: {port}")
                elif isinstance(value, int):
                    if not (1 <= value <= 65535):
                        raise ValueError(f"Invalid port: {value}")
        
        # Validate rate limiting parameters
        if rule.action == AccessControlAction.RATE_LIMIT:
            if not rule.rate_limit_requests or not rule.rate_limit_window:
                raise ValueError("Rate limiting action requires rate_limit_requests and rate_limit_window")
    
    def remove_rule(self, rule_id: str):
        """Remove an access control rule"""
        
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
        
        rule_name = self.rules[rule_id].name
        del self.rules[rule_id]
        
        # Clean up metrics
        if rule_id in self.metrics:
            del self.metrics[rule_id]
        
        # Clean up rate limit buckets
        self.rate_limit_buckets = {
            k: v for k, v in self.rate_limit_buckets.items() 
            if not k.startswith(f"{rule_id}:")
        }
        
        self.logger.info(f"Removed access control rule: {rule_name} ({rule_id})")
    
    def enable_rule(self, rule_id: str):
        """Enable an access control rule"""
        
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
        
        self.rules[rule_id].enabled = True
        self.rules[rule_id].last_modified = datetime.utcnow()
        
        self.logger.info(f"Enabled access control rule: {rule_id}")
    
    def disable_rule(self, rule_id: str):
        """Disable an access control rule"""
        
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
        
        self.rules[rule_id].enabled = False
        self.rules[rule_id].last_modified = datetime.utcnow()
        
        self.logger.info(f"Disabled access control rule: {rule_id}")
    
    async def evaluate_access(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: Optional[int] = None,
        destination_port: Optional[int] = None,
        protocol: Optional[str] = None,
        user_agent: Optional[str] = None,
        scope: AccessControlScope = AccessControlScope.GLOBAL,
        scope_target: str = "*"
    ) -> Dict[str, Any]:
        """
        Evaluate network access based on configured rules
        
        Returns decision and matching rules
        """
        evaluation_result = {
            'decision': AccessControlAction.ALLOW,
            'matched_rules': [],
            'blocked': False,
            'rate_limited': False,
            'should_log': False,
            'details': {}
        }
        
        # Get applicable rules sorted by priority
        applicable_rules = self._get_applicable_rules(scope, scope_target)
        applicable_rules.sort(key=lambda r: r.priority)
        
        # Get geolocation if enabled
        geolocation = None
        if self.geolocation_enabled:
            geolocation = await self._get_geolocation(source_ip)
        
        # Evaluate each rule
        for rule in applicable_rules:
            if not rule.enabled:
                continue
            
            # Check if rule conditions match
            if self._rule_matches(rule, source_ip, destination_ip, source_port, 
                                destination_port, protocol, user_agent, geolocation):
                
                evaluation_result['matched_rules'].append(rule.id)
                
                # Update metrics
                metrics = self.metrics[rule.id]
                metrics.matches_count += 1
                metrics.last_match = datetime.utcnow()
                metrics.unique_sources.add(source_ip)
                
                # Apply rule action
                if rule.action == AccessControlAction.DENY or rule.action == AccessControlAction.DROP:
                    evaluation_result['decision'] = rule.action
                    evaluation_result['blocked'] = True
                    metrics.blocks_count += 1
                    break  # Deny/drop rules are terminal
                
                elif rule.action == AccessControlAction.RATE_LIMIT:
                    # Check rate limit
                    if self._check_rate_limit(rule, source_ip):
                        evaluation_result['decision'] = AccessControlAction.DENY
                        evaluation_result['rate_limited'] = True
                        evaluation_result['blocked'] = True
                        metrics.rate_limits_count += 1
                        break
                
                elif rule.action == AccessControlAction.ALLOW:
                    evaluation_result['decision'] = AccessControlAction.ALLOW
                    metrics.allows_count += 1
                    # Allow rules don't break the loop, lower priority rules can still deny
                
                elif rule.action == AccessControlAction.LOG:
                    evaluation_result['should_log'] = True
                    # Log rules don't change the decision
        
        # Log event if needed
        if evaluation_result['should_log'] or evaluation_result['blocked']:
            await self._log_access_event(
                evaluation_result['matched_rules'],
                evaluation_result['decision'],
                source_ip, destination_ip, source_port, destination_port,
                protocol, user_agent, geolocation, evaluation_result['blocked']
            )
        
        return evaluation_result
    
    def _get_applicable_rules(self, scope: AccessControlScope, scope_target: str) -> List[AccessControlRule]:
        """Get rules applicable to the given scope"""
        
        applicable_rules = []
        
        for rule in self.rules.values():
            # Global rules apply everywhere
            if rule.scope == AccessControlScope.GLOBAL:
                applicable_rules.append(rule)
            
            # Scope-specific rules
            elif rule.scope == scope and (rule.scope_target == scope_target or rule.scope_target == "*"):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _rule_matches(
        self,
        rule: AccessControlRule,
        source_ip: str,
        destination_ip: str,
        source_port: Optional[int],
        destination_port: Optional[int],
        protocol: Optional[str],
        user_agent: Optional[str],
        geolocation: Optional[str]
    ) -> bool:
        """Check if a rule matches the given conditions"""
        
        for condition, value in rule.conditions.items():
            if condition == AccessControlCondition.SOURCE_IP:
                if not self._ip_matches(source_ip, value):
                    return False
            
            elif condition == AccessControlCondition.DESTINATION_IP:
                if not self._ip_matches(destination_ip, value):
                    return False
            
            elif condition == AccessControlCondition.SOURCE_PORT:
                if source_port is None:
                    return False
                if isinstance(value, list):
                    if source_port not in value:
                        return False
                elif source_port != value:
                    return False
            
            elif condition == AccessControlCondition.DESTINATION_PORT:
                if destination_port is None:
                    return False
                if isinstance(value, list):
                    if destination_port not in value:
                        return False
                elif destination_port != value:
                    return False
            
            elif condition == AccessControlCondition.PROTOCOL:
                if protocol is None or protocol.lower() != value.lower():
                    return False
            
            elif condition == AccessControlCondition.USER_AGENT:
                if user_agent is None:
                    return False
                if isinstance(value, str):
                    if value.lower() not in user_agent.lower():
                        return False
                elif isinstance(value, dict) and 'regex' in value:
                    if not re.search(value['regex'], user_agent, re.IGNORECASE):
                        return False
            
            elif condition == AccessControlCondition.GEOLOCATION:
                if geolocation is None:
                    return False
                if 'blocked_countries' in value:
                    if geolocation in value['blocked_countries']:
                        return True  # Match for blocking
                if 'allowed_countries' in value:
                    if geolocation not in value['allowed_countries']:
                        return True  # Match for blocking
            
            elif condition == AccessControlCondition.TIME_OF_DAY:
                current_time = datetime.utcnow().time()
                if 'start_time' in value and 'end_time' in value:
                    start_time = datetime.strptime(value['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(value['end_time'], '%H:%M').time()
                    if not (start_time <= current_time <= end_time):
                        return False
        
        return True
    
    def _ip_matches(self, ip: str, condition: Any) -> bool:
        """Check if an IP matches the condition"""
        
        try:
            ip_addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        
        if isinstance(condition, str):
            # Single IP or CIDR
            try:
                network = ipaddress.ip_network(condition, strict=False)
                return ip_addr in network
            except ValueError:
                return False
        
        elif isinstance(condition, dict):
            # Whitelist/blacklist or special conditions
            if 'whitelist' in condition:
                for allowed_ip in condition['whitelist']:
                    try:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if ip_addr in network:
                            return True
                    except ValueError:
                        continue
                return False
            
            if 'blacklist' in condition:
                for blocked_ip in condition['blacklist']:
                    try:
                        network = ipaddress.ip_network(blocked_ip, strict=False)
                        if ip_addr in network:
                            return True
                    except ValueError:
                        continue
                return False
            
            if 'exclude_private' in condition and condition['exclude_private']:
                return not ip_addr.is_private
        
        return False
    
    def _check_rate_limit(self, rule: AccessControlRule, source_ip: str) -> bool:
        """Check if source IP has exceeded rate limit for the rule"""
        
        bucket_key = f"{rule.id}:{source_ip}"
        current_time = datetime.utcnow()
        
        if bucket_key not in self.rate_limit_buckets:
            self.rate_limit_buckets[bucket_key] = {
                'count': 1,
                'window_start': current_time
            }
            return False
        
        bucket = self.rate_limit_buckets[bucket_key]
        window_elapsed = (current_time - bucket['window_start']).total_seconds()
        
        # Reset window if expired
        if window_elapsed >= rule.rate_limit_window:
            bucket['count'] = 1
            bucket['window_start'] = current_time
            return False
        
        # Increment count
        bucket['count'] += 1
        
        # Check if limit exceeded
        return bucket['count'] > rule.rate_limit_requests
    
    async def _get_geolocation(self, ip: str) -> Optional[str]:
        """Get geolocation country code for IP address"""
        
        # This would integrate with a geolocation service
        # For now, return a placeholder
        
        try:
            # Mock geolocation lookup
            ip_addr = ipaddress.ip_address(ip)
            
            # Return mock country codes based on IP range
            if ip_addr.is_private:
                return "US"  # Assume private IPs are local
            
            # Mock some country assignments
            first_octet = int(str(ip_addr).split('.')[0])
            if first_octet < 64:
                return "US"
            elif first_octet < 128:
                return "EU"
            elif first_octet < 192:
                return "CN"
            else:
                return "RU"
        
        except Exception:
            return None
    
    async def _log_access_event(
        self,
        matched_rules: List[str],
        decision: AccessControlAction,
        source_ip: str,
        destination_ip: str,
        source_port: Optional[int],
        destination_port: Optional[int],
        protocol: Optional[str],
        user_agent: Optional[str],
        geolocation: Optional[str],
        blocked: bool
    ):
        """Log access control event"""
        
        event = AccessControlEvent(
            timestamp=datetime.utcnow(),
            rule_id=matched_rules[0] if matched_rules else "no_match",
            action=decision,
            source_ip=source_ip,
            destination_ip=destination_ip,
            source_port=source_port,
            destination_port=destination_port,
            protocol=protocol,
            user_agent=user_agent,
            geolocation=geolocation,
            blocked=blocked,
            details={'matched_rules': matched_rules}
        )
        
        self.events.append(event)
        
        # Maintain event limit
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Log to system logger
        log_level = logging.WARNING if blocked else logging.INFO
        self.logger.log(
            log_level,
            f"Access {'BLOCKED' if blocked else 'ALLOWED'}: {source_ip} -> "
            f"{destination_ip}:{destination_port} ({protocol}) - Rules: {matched_rules}"
        )
    
    def get_rules(self, scope: Optional[AccessControlScope] = None) -> List[AccessControlRule]:
        """Get access control rules"""
        
        rules = list(self.rules.values())
        
        if scope:
            rules = [rule for rule in rules if rule.scope == scope]
        
        return rules
    
    def get_rule(self, rule_id: str) -> Optional[AccessControlRule]:
        """Get specific access control rule"""
        return self.rules.get(rule_id)
    
    def get_metrics(self, rule_id: Optional[str] = None) -> Union[AccessControlMetrics, Dict[str, AccessControlMetrics]]:
        """Get access control metrics"""
        
        if rule_id:
            return self.metrics.get(rule_id)
        
        return self.metrics.copy()
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        rule_id: Optional[str] = None,
        blocked_only: bool = False,
        limit: int = 1000
    ) -> List[AccessControlEvent]:
        """Get access control events with filters"""
        
        events = self.events.copy()
        
        # Apply filters
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        if rule_id:
            events = [e for e in events if e.rule_id == rule_id]
        
        if blocked_only:
            events = [e for e in events if e.blocked]
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    def get_top_blocked_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top blocked IP addresses"""
        
        blocked_ips = {}
        
        for event in self.events:
            if event.blocked:
                ip = event.source_ip
                if ip not in blocked_ips:
                    blocked_ips[ip] = {
                        'ip': ip,
                        'block_count': 0,
                        'first_seen': event.timestamp,
                        'last_seen': event.timestamp,
                        'geolocation': event.geolocation
                    }
                
                blocked_ips[ip]['block_count'] += 1
                if event.timestamp < blocked_ips[ip]['first_seen']:
                    blocked_ips[ip]['first_seen'] = event.timestamp
                if event.timestamp > blocked_ips[ip]['last_seen']:
                    blocked_ips[ip]['last_seen'] = event.timestamp
        
        # Sort by block count
        top_blocked = sorted(blocked_ips.values(), key=lambda x: x['block_count'], reverse=True)
        
        return top_blocked[:limit]
    
    def get_access_summary(self) -> Dict[str, Any]:
        """Get access control summary statistics"""
        
        total_events = len(self.events)
        blocked_events = len([e for e in self.events if e.blocked])
        allowed_events = total_events - blocked_events
        
        # Rule statistics
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        
        # Top blocked IPs
        top_blocked_ips = self.get_top_blocked_ips(5)
        
        # Recent activity (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_events = [e for e in self.events if e.timestamp >= one_hour_ago]
        recent_blocked = len([e for e in recent_events if e.blocked])
        
        # Top matched rules
        rule_matches = {}
        for rule_id, metrics in self.metrics.items():
            if metrics.matches_count > 0:
                rule_matches[rule_id] = {
                    'rule_name': self.rules[rule_id].name,
                    'matches': metrics.matches_count,
                    'blocks': metrics.blocks_count,
                    'allows': metrics.allows_count
                }
        
        top_rules = sorted(rule_matches.values(), key=lambda x: x['matches'], reverse=True)[:5]
        
        return {
            'total_events': total_events,
            'blocked_events': blocked_events,
            'allowed_events': allowed_events,
            'block_rate': (blocked_events / total_events * 100) if total_events > 0 else 0,
            'total_rules': total_rules,
            'enabled_rules': enabled_rules,
            'recent_activity': {
                'total_events_last_hour': len(recent_events),
                'blocked_events_last_hour': recent_blocked
            },
            'top_blocked_ips': top_blocked_ips,
            'top_matched_rules': top_rules,
            'rate_limit_buckets_active': len(self.rate_limit_buckets)
        }
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old events and rate limit buckets"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean up old events
        old_event_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
        new_event_count = len(self.events)
        
        # Clean up old rate limit buckets
        old_bucket_count = len(self.rate_limit_buckets)
        buckets_to_remove = []
        
        for bucket_key, bucket_data in self.rate_limit_buckets.items():
            if bucket_data['window_start'] < cutoff_time:
                buckets_to_remove.append(bucket_key)
        
        for bucket_key in buckets_to_remove:
            del self.rate_limit_buckets[bucket_key]
        
        new_bucket_count = len(self.rate_limit_buckets)
        
        self.logger.info(
            f"Cleanup completed - Events: {old_event_count} -> {new_event_count}, "
            f"Rate limit buckets: {old_bucket_count} -> {new_bucket_count}"
        )


# Export main classes
__all__ = ['NetworkAccessControl', 'AccessControlRule', 'AccessControlMetrics', 'AccessControlEvent', 'AccessControlAction', 'AccessControlCondition', 'AccessControlScope']