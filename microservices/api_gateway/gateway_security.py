#!/usr/bin/env python3
"""
🔒 Gateway Security - Enterprise API Gateway Service
===================================================

Comprehensive security service for enterprise API gateway.
Provides threat detection, security policies, and protection mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import hmac
import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import ipaddress

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Security action enumeration."""
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    CAPTCHA = "captcha"
    LOG_ONLY = "log_only"


@dataclass
class SecurityThreat:
    """Security threat data structure."""
    id: str
    threat_type: str
    level: ThreatLevel
    source_ip: str
    timestamp: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False


@dataclass
class SecurityRule:
    """Security rule configuration."""
    name: str
    description: str
    pattern: str
    threat_type: str
    level: ThreatLevel
    action: SecurityAction
    enabled: bool = True
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)


class GatewaySecurity:
    """
    🔒 Enterprise Gateway Security Service
    
    Provides comprehensive security protection including threat detection,
    WAF capabilities, DDoS protection, and security policy enforcement.
    """

    def __init__(self):
        """Initialize the security service."""
        self.security_rules: Dict[str, SecurityRule] = {}
        self.threats: List[SecurityThreat] = []
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.security_stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'threats_detected': 0,
            'false_positives': 0
        }
        
        # Initialize security rules
        self._setup_default_rules()
        
        logger.info("🔒 Gateway Security Service initialized")

    async def start(self):
        """Start the security service."""
        logger.info("🚀 Starting Gateway Security Service")
        
        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Gateway Security Service started")

    async def stop(self):
        """Stop the security service."""
        logger.info("🛑 Stopping Gateway Security Service")
        
        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Gateway Security Service stopped")

    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for security threats."""
        self.security_stats['total_requests'] += 1
        
        client_ip = request_data.get('client_ip', '127.0.0.1')
        path = request_data.get('path', '/')
        headers = request_data.get('headers', {})
        user_agent = headers.get('user-agent', '')
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            self.security_stats['blocked_requests'] += 1
            return {
                'action': SecurityAction.BLOCK,
                'reason': 'IP address is blocked',
                'threat_level': ThreatLevel.HIGH
            }
        
        # Check rate limits
        rate_limit_result = await self._check_rate_limits(client_ip, request_data)
        if rate_limit_result['action'] != SecurityAction.ALLOW:
            return rate_limit_result
        
        # Run security rules
        for rule_name, rule in self.security_rules.items():
            if not rule.enabled:
                continue
            
            result = await self._apply_security_rule(rule, request_data)
            if result['action'] != SecurityAction.ALLOW:
                return result
        
        # Check for common attack patterns
        attack_result = await self._check_attack_patterns(request_data)
        if attack_result['action'] != SecurityAction.ALLOW:
            return attack_result
        
        # Validate request headers
        header_result = await self._validate_headers(headers)
        if header_result['action'] != SecurityAction.ALLOW:
            return header_result
        
        return {
            'action': SecurityAction.ALLOW,
            'reason': 'Request passed security checks',
            'threat_level': ThreatLevel.LOW
        }

    async def _check_rate_limits(self, client_ip: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limits for the client IP."""
        current_time = time.time()
        window_size = 60  # 1 minute window
        max_requests = 100  # Max requests per minute
        
        # Initialize rate limit data for IP
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = {
                'requests': [],
                'blocked_until': 0
            }
        
        ip_data = self.rate_limits[client_ip]
        
        # Check if IP is currently blocked
        if current_time < ip_data['blocked_until']:
            return {
                'action': SecurityAction.BLOCK,
                'reason': 'Rate limit exceeded',
                'threat_level': ThreatLevel.MEDIUM
            }
        
        # Clean old requests
        ip_data['requests'] = [
            req_time for req_time in ip_data['requests']
            if current_time - req_time < window_size
        ]
        
        # Add current request
        ip_data['requests'].append(current_time)
        
        # Check rate limit
        if len(ip_data['requests']) > max_requests:
            # Block IP for 5 minutes
            ip_data['blocked_until'] = current_time + 300
            
            await self._record_threat(
                ThreatLevel.MEDIUM,
                "rate_limit_exceeded",
                client_ip,
                f"Rate limit exceeded: {len(ip_data['requests'])} requests in {window_size} seconds"
            )
            
            return {
                'action': SecurityAction.BLOCK,
                'reason': 'Rate limit exceeded',
                'threat_level': ThreatLevel.MEDIUM
            }
        
        return {'action': SecurityAction.ALLOW}

    async def _apply_security_rule(self, rule: SecurityRule, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a security rule to the request."""
        client_ip = request_data.get('client_ip', '127.0.0.1')
        
        # Check whitelist
        if rule.whitelist_ips and client_ip in rule.whitelist_ips:
            return {'action': SecurityAction.ALLOW}
        
        # Check blacklist
        if rule.blacklist_ips and client_ip in rule.blacklist_ips:
            await self._record_threat(
                rule.level,
                rule.threat_type,
                client_ip,
                f"IP in blacklist: {rule.name}"
            )
            return {
                'action': rule.action,
                'reason': f'Blacklisted IP: {rule.name}',
                'threat_level': rule.level
            }
        
        # Check pattern matching
        if rule.pattern:
            request_text = json.dumps(request_data, default=str)
            if re.search(rule.pattern, request_text, re.IGNORECASE):
                await self._record_threat(
                    rule.level,
                    rule.threat_type,
                    client_ip,
                    f"Pattern match: {rule.name}"
                )
                return {
                    'action': rule.action,
                    'reason': f'Security rule triggered: {rule.name}',
                    'threat_level': rule.level
                }
        
        return {'action': SecurityAction.ALLOW}

    async def _check_attack_patterns(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for common attack patterns."""
        client_ip = request_data.get('client_ip', '127.0.0.1')
        path = request_data.get('path', '/')
        headers = request_data.get('headers', {})
        query_params = request_data.get('query_params', {})
        body = request_data.get('body', '')
        
        # SQL Injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
            r"(\bunion\s+select\b)",
            r"(\bor\s+1\s*=\s*1\b)",
            r"(\band\s+1\s*=\s*1\b)",
            r"'.*--",
            r"';.*--"
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        # Path traversal patterns
        traversal_patterns = [
            r"\.\.\/",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c"
        ]
        
        # Check all patterns
        all_patterns = [
            (sql_patterns, "sql_injection", ThreatLevel.HIGH),
            (xss_patterns, "xss_attack", ThreatLevel.HIGH),
            (traversal_patterns, "path_traversal", ThreatLevel.MEDIUM)
        ]
        
        request_content = f"{path} {str(query_params)} {str(headers)} {body}".lower()
        
        for patterns, threat_type, level in all_patterns:
            for pattern in patterns:
                if re.search(pattern, request_content, re.IGNORECASE):
                    await self._record_threat(
                        level,
                        threat_type,
                        client_ip,
                        f"Attack pattern detected: {pattern}"
                    )
                    return {
                        'action': SecurityAction.BLOCK,
                        'reason': f'Attack pattern detected: {threat_type}',
                        'threat_level': level
                    }
        
        return {'action': SecurityAction.ALLOW}

    async def _validate_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate request headers for security issues."""
        # Check for suspicious user agents
        user_agent = headers.get('user-agent', '').lower()
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'nessus', 'burpsuite',
            'dirb', 'dirbuster', 'gobuster', 'wfuzz'
        ]
        
        for agent in suspicious_agents:
            if agent in user_agent:
                return {
                    'action': SecurityAction.BLOCK,
                    'reason': f'Suspicious user agent: {agent}',
                    'threat_level': ThreatLevel.HIGH
                }
        
        # Check for missing security headers in response (placeholder)
        # This would be implemented for response validation
        
        return {'action': SecurityAction.ALLOW}

    async def _record_threat(self, level: ThreatLevel, threat_type: str, source_ip: str, description: str):
        """Record a security threat."""
        threat = SecurityThreat(
            id=f"threat_{int(time.time())}_{len(self.threats)}",
            threat_type=threat_type,
            level=level,
            source_ip=source_ip,
            timestamp=datetime.now(),
            description=description
        )
        
        self.threats.append(threat)
        self.security_stats['threats_detected'] += 1
        
        # Auto-block critical threats
        if level == ThreatLevel.CRITICAL:
            self.blocked_ips.add(source_ip)
            threat.blocked = True
            logger.error(f"🚨 Critical threat detected and blocked: {description}")
        elif level == ThreatLevel.HIGH:
            logger.warning(f"⚠️ High threat detected: {description}")
        
        # Keep only last 10000 threats
        if len(self.threats) > 10000:
            self.threats = self.threats[-10000:]

    def _setup_default_rules(self):
        """Setup default security rules."""
        default_rules = [
            SecurityRule(
                name="block_admin_paths",
                description="Block access to admin paths",
                pattern=r"/(admin|wp-admin|administrator|phpmyadmin)",
                threat_type="unauthorized_access",
                level=ThreatLevel.MEDIUM,
                action=SecurityAction.BLOCK
            ),
            SecurityRule(
                name="block_config_files",
                description="Block access to configuration files",
                pattern=r"\.(config|ini|conf|env|log)$",
                threat_type="information_disclosure",
                level=ThreatLevel.MEDIUM,
                action=SecurityAction.BLOCK
            ),
            SecurityRule(
                name="detect_scanner_user_agents",
                description="Detect security scanner user agents",
                pattern=r"(nikto|nmap|sqlmap|dirb|gobuster|wfuzz|burpsuite)",
                threat_type="security_scanning",
                level=ThreatLevel.HIGH,
                action=SecurityAction.BLOCK
            )
        ]
        
        for rule in default_rules:
            self.security_rules[rule.name] = rule

    def add_security_rule(self, rule: SecurityRule):
        """Add a new security rule."""
        self.security_rules[rule.name] = rule
        logger.info(f"➕ Added security rule: {rule.name}")

    def remove_security_rule(self, rule_name: str):
        """Remove a security rule."""
        if rule_name in self.security_rules:
            del self.security_rules[rule_name]
            logger.info(f"➖ Removed security rule: {rule_name}")

    def block_ip(self, ip_address: str, reason: str = "Manual block"):
        """Manually block an IP address."""
        self.blocked_ips.add(ip_address)
        logger.info(f"🚫 Blocked IP: {ip_address} - {reason}")

    def unblock_ip(self, ip_address: str):
        """Unblock an IP address."""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"✅ Unblocked IP: {ip_address}")

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status."""
        recent_threats = [
            threat for threat in self.threats
            if threat.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        threat_by_level = {}
        for level in ThreatLevel:
            threat_by_level[level.value] = len([
                t for t in recent_threats if t.level == level
            ])
        
        return {
            'stats': self.security_stats.copy(),
            'blocked_ips_count': len(self.blocked_ips),
            'active_rules_count': len([r for r in self.security_rules.values() if r.enabled]),
            'recent_threats': {
                'total': len(recent_threats),
                'by_level': threat_by_level,
                'by_type': self._group_threats_by_type(recent_threats)
            },
            'top_threat_sources': self._get_top_threat_sources(recent_threats, limit=10)
        }

    def get_recent_threats(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent threats."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_threats = [
            threat for threat in self.threats[-limit:]
            if threat.timestamp >= cutoff_time
        ]
        
        return [
            {
                'id': threat.id,
                'type': threat.threat_type,
                'level': threat.level.value,
                'source_ip': threat.source_ip,
                'timestamp': threat.timestamp.isoformat(),
                'description': threat.description,
                'blocked': threat.blocked
            }
            for threat in recent_threats
        ]

    def _group_threats_by_type(self, threats: List[SecurityThreat]) -> Dict[str, int]:
        """Group threats by type."""
        threat_types = {}
        for threat in threats:
            threat_types[threat.threat_type] = threat_types.get(threat.threat_type, 0) + 1
        return threat_types

    def _get_top_threat_sources(self, threats: List[SecurityThreat], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top threat source IPs."""
        source_counts = {}
        for threat in threats:
            source_counts[threat.source_ip] = source_counts.get(threat.source_ip, 0) + 1
        
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'ip': ip, 'threat_count': count}
            for ip, count in sorted_sources[:limit]
        ]

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Security cleanup error: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_data(self):
        """Clean up old security data."""
        # Clean old rate limit data
        current_time = time.time()
        for ip in list(self.rate_limits.keys()):
            ip_data = self.rate_limits[ip]
            # Remove old requests
            ip_data['requests'] = [
                req_time for req_time in ip_data['requests']
                if current_time - req_time < 3600  # Keep last hour
            ]
            # Remove empty entries
            if not ip_data['requests'] and ip_data['blocked_until'] < current_time:
                del self.rate_limits[ip]
        
        # Clean old threats (keep last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        self.threats = [
            threat for threat in self.threats
            if threat.timestamp >= cutoff_time
        ]
        
        logger.info("🧹 Security data cleanup completed")


async def main():
    """Example usage of the Gateway Security service."""
    print("🔒 Gateway Security Example")
    print("=" * 32)
    
    # Create security service
    security = GatewaySecurity()
    await security.start()
    
    # Test requests
    test_requests = [
        {
            'client_ip': '192.168.1.100',
            'path': '/api/users',
            'headers': {'user-agent': 'Mozilla/5.0'},
            'method': 'GET'
        },
        {
            'client_ip': '10.0.0.1',
            'path': '/admin/login',
            'headers': {'user-agent': 'nikto/2.1.6'},
            'method': 'GET'
        },
        {
            'client_ip': '172.16.0.1',
            'path': '/api/search',
            'query_params': {'q': "'; DROP TABLE users; --"},
            'headers': {'user-agent': 'Chrome/91.0'},
            'method': 'GET'
        }
    ]
    
    print("\n🔍 Analyzing requests...")
    for i, request in enumerate(test_requests):
        result = await security.analyze_request(request)
        status = "✅ ALLOWED" if result['action'] == SecurityAction.ALLOW else "🚫 BLOCKED"
        print(f"{status} Request {i+1}: {result['reason']} (Level: {result.get('threat_level', 'N/A')})")
    
    # Show security status
    status = security.get_security_status()
    print(f"\n📊 Security Status:")
    print(f"   Total requests: {status['stats']['total_requests']}")
    print(f"   Blocked requests: {status['stats']['blocked_requests']}")
    print(f"   Threats detected: {status['stats']['threats_detected']}")
    print(f"   Blocked IPs: {status['blocked_ips_count']}")
    
    # Show recent threats
    threats = security.get_recent_threats(limit=5)
    if threats:
        print(f"\n🚨 Recent Threats:")
        for threat in threats:
            print(f"   {threat['level'].upper()}: {threat['type']} from {threat['source_ip']}")
    
    await security.stop()
    print("\n🛑 Security service stopped")


if __name__ == "__main__":
    asyncio.run(main())