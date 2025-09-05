"""Edge Firewall
=============

Advanced edge firewall with intelligent packet filtering and DPI.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import ipaddress

logger = logging.getLogger(__name__)

class RuleAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    LOG = "log"

class ProtocolType(str, Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ANY = "any"

@dataclass
class FirewallRule:
    rule_id: str
    name: str
    action: RuleAction
    protocol: ProtocolType
    source_ip: str = "any"
    dest_ip: str = "any"
    source_port: str = "any"
    dest_port: str = "any"
    enabled: bool = True
    priority: int = 100

class EdgeFirewall:
    def __init__(self):
        self.rules: Dict[str, FirewallRule] = {}
        self.blocked_ips: set = set()
        self.allowed_ips: set = set()
        self.packet_count = 0
        self.blocked_count = 0
        
    async def add_rule(self, rule: FirewallRule):
        self.rules[rule.rule_id] = rule
        logger.info(f"Added firewall rule: {rule.name}")
        
    async def remove_rule(self, rule_id: str):
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed firewall rule: {rule_id}")
            
    async def check_packet(self, src_ip: str, dest_ip: str, protocol: str, dest_port: int) -> bool:
        self.packet_count += 1
        
        # Quick blocked IP check
        if src_ip in self.blocked_ips:
            self.blocked_count += 1
            return False
            
        # Check rules in priority order
        sorted_rules = sorted(self.rules.values(), key=lambda r: r.priority)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
                
            if self._rule_matches(rule, src_ip, dest_ip, protocol, dest_port):
                if rule.action in [RuleAction.DENY, RuleAction.DROP]:
                    self.blocked_count += 1
                    return False
                elif rule.action == RuleAction.ALLOW:
                    return True
                    
        # Default deny
        self.blocked_count += 1
        return False
        
    def _rule_matches(self, rule: FirewallRule, src_ip: str, dest_ip: str, protocol: str, dest_port: int) -> bool:
        # Simplified rule matching
        if rule.protocol != ProtocolType.ANY and rule.protocol.value != protocol.lower():
            return False
            
        if rule.source_ip != "any" and not self._ip_matches(src_ip, rule.source_ip):
            return False
            
        if rule.dest_ip != "any" and not self._ip_matches(dest_ip, rule.dest_ip):
            return False
            
        if rule.dest_port != "any" and str(dest_port) != rule.dest_port:
            return False
            
        return True
        
    def _ip_matches(self, ip: str, pattern: str) -> bool:
        try:
            if "/" in pattern:
                # CIDR notation
                network = ipaddress.ip_network(pattern, strict=False)
                return ipaddress.ip_address(ip) in network
            else:
                return ip == pattern
        except:
            return False
            
    async def get_statistics(self) -> Dict[str, Any]:
        return {
            'total_packets': self.packet_count,
            'blocked_packets': self.blocked_count,
            'allowed_packets': self.packet_count - self.blocked_count,
            'block_rate': (self.blocked_count / self.packet_count * 100) if self.packet_count > 0 else 0,
            'active_rules': len([r for r in self.rules.values() if r.enabled]),
            'blocked_ips': len(self.blocked_ips)
        }

def create_edge_firewall() -> EdgeFirewall:
    return EdgeFirewall()