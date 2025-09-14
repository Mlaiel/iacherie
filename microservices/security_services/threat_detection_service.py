"""
Threat Detection Service for Ainflue Microservices
Real-time threat detection and security monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json
import re
import ipaddress
from dataclasses import dataclass
from collections import defaultdict, deque
import time
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ThreatEvent:
    """Threat event information"""
    event_id: str
    threat_type: str
    severity: str  # low, medium, high, critical
    source_ip: str
    target: str
    description: str
    timestamp: datetime
    evidence: Dict[str, Any] = None
    mitigated: bool = False
    false_positive: bool = False


@dataclass
class SecurityRule:
    """Security detection rule"""
    rule_id: str
    name: str
    description: str
    threat_type: str
    pattern: str
    severity: str
    enabled: bool = True
    threshold: int = 1
    time_window: int = 60  # seconds
    action: str = "alert"  # alert, block, quarantine


@dataclass
class IPReputation:
    """IP address reputation information"""
    ip_address: str
    reputation_score: int  # 0-100, 0 is malicious
    threat_types: List[str]
    last_seen: datetime
    source: str
    is_whitelisted: bool = False
    is_blacklisted: bool = False


class ThreatDetectionService:
    """Enterprise threat detection service"""

    def __init__(self):
        self.threat_events = deque(maxlen=100000)  # Keep last 100k events
        self.security_rules = {}
        self.ip_reputation_db = {}
        self.blocked_ips = set()
        self.whitelisted_ips = set()
        self.request_counters = defaultdict(lambda: defaultdict(int))
        self.failed_login_attempts = defaultdict(list)
        self.suspicious_patterns = defaultdict(int)
        
        # Initialize default rules
        self._initialize_default_rules()
        
        # Initialize IP reputation
        self._initialize_ip_reputation()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())

    def _initialize_default_rules(self):
        """Initialize default security rules"""
        default_rules = [
            SecurityRule(
                rule_id="sql_injection_01",
                name="SQL Injection Detection",
                description="Detects SQL injection attempts",
                threat_type="sql_injection",
                pattern=r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table|'.*or.*'=')",
                severity="high",
                threshold=1,
                action="block"
            ),
            SecurityRule(
                rule_id="xss_01",
                name="XSS Attack Detection",
                description="Detects cross-site scripting attempts",
                threat_type="xss",
                pattern=r"(?i)(<script|javascript:|onload=|onerror=|onclick=)",
                severity="medium",
                threshold=1,
                action="block"
            ),
            SecurityRule(
                rule_id="brute_force_01",
                name="Brute Force Login Detection",
                description="Detects brute force login attempts",
                threat_type="brute_force",
                pattern="failed_login",
                severity="high",
                threshold=5,
                time_window=300,  # 5 minutes
                action="block"
            ),
            SecurityRule(
                rule_id="suspicious_ua_01",
                name="Suspicious User Agent",
                description="Detects suspicious user agents",
                threat_type="suspicious_activity",
                pattern=r"(?i)(bot|crawler|scanner|nikto|sqlmap|nmap|masscan)",
                severity="medium",
                threshold=1,
                action="alert"
            ),
            SecurityRule(
                rule_id="path_traversal_01",
                name="Path Traversal Detection",
                description="Detects directory traversal attempts",
                threat_type="path_traversal",
                pattern=r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow|\.\.%2f|\.\.%5c)",
                severity="high",
                threshold=1,
                action="block"
            ),
            SecurityRule(
                rule_id="command_injection_01",
                name="Command Injection Detection",
                description="Detects command injection attempts",
                threat_type="command_injection",
                pattern=r"(;|\|&|&&|\|\||`|\$\(|\${|<%|%>)",
                severity="high",
                threshold=1,
                action="block"
            ),
            SecurityRule(
                rule_id="dos_01",
                name="DoS Attack Detection",
                description="Detects denial of service attempts",
                threat_type="dos",
                pattern="high_request_rate",
                severity="critical",
                threshold=100,
                time_window=60,
                action="block"
            ),
            SecurityRule(
                rule_id="malware_upload_01",
                name="Malware Upload Detection",
                description="Detects potential malware uploads",
                threat_type="malware",
                pattern=r"(?i)\.(exe|bat|cmd|com|pif|scr|vbs|js|jar|php|asp|jsp)",
                severity="high",
                threshold=1,
                action="quarantine"
            )
        ]
        
        for rule in default_rules:
            self.security_rules[rule.rule_id] = rule

    def _initialize_ip_reputation(self):
        """Initialize IP reputation database with known threats"""
        # Sample known malicious IPs (in production, would integrate with threat feeds)
        known_malicious_ips = [
            "127.0.0.1",  # Example - never actually block localhost
            "192.168.1.100",  # Example internal IP
        ]
        
        for ip in known_malicious_ips:
            self.ip_reputation_db[ip] = IPReputation(
                ip_address=ip,
                reputation_score=0,
                threat_types=["botnet", "scanner"],
                last_seen=datetime.utcnow(),
                source="threat_feed",
                is_blacklisted=True
            )

    async def _cleanup_old_data(self):
        """Cleanup old data periodically"""
        while True:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Clean old failed login attempts
                for ip in list(self.failed_login_attempts.keys()):
                    self.failed_login_attempts[ip] = [
                        attempt for attempt in self.failed_login_attempts[ip]
                        if attempt > cutoff_time
                    ]
                    if not self.failed_login_attempts[ip]:
                        del self.failed_login_attempts[ip]
                
                # Clean old request counters
                current_time = int(time.time())
                for ip in list(self.request_counters.keys()):
                    for timestamp in list(self.request_counters[ip].keys()):
                        if current_time - timestamp > 3600:  # 1 hour
                            del self.request_counters[ip][timestamp]
                    
                    if not self.request_counters[ip]:
                        del self.request_counters[ip]
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)

    async def analyze_request(
        self, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze incoming request for threats"""
        try:
            source_ip = request_data.get("source_ip", "unknown")
            user_agent = request_data.get("user_agent", "")
            url = request_data.get("url", "")
            method = request_data.get("method", "GET")
            headers = request_data.get("headers", {})
            body = request_data.get("body", "")
            
            threats_detected = []
            
            # Check IP reputation
            ip_threat = await self._check_ip_reputation(source_ip)
            if ip_threat:
                threats_detected.append(ip_threat)
            
            # Check request rate
            rate_threat = await self._check_request_rate(source_ip)
            if rate_threat:
                threats_detected.append(rate_threat)
            
            # Check patterns in URL and body
            content_to_check = f"{url} {body}"
            for rule_id, rule in self.security_rules.items():
                if not rule.enabled:
                    continue
                
                if rule.pattern == "failed_login":
                    continue  # Handled separately
                elif rule.pattern == "high_request_rate":
                    continue  # Already checked
                
                if re.search(rule.pattern, content_to_check):
                    threat = await self._create_threat_event(
                        threat_type=rule.threat_type,
                        severity=rule.severity,
                        source_ip=source_ip,
                        target=url,
                        description=f"{rule.name}: Pattern matched",
                        evidence={
                            "rule_id": rule_id,
                            "pattern": rule.pattern,
                            "matched_content": content_to_check[:200],
                            "user_agent": user_agent,
                            "method": method
                        }
                    )
                    threats_detected.append(threat)
            
            # Check user agent patterns
            for rule_id, rule in self.security_rules.items():
                if rule.threat_type == "suspicious_activity" and rule.enabled:
                    if re.search(rule.pattern, user_agent):
                        threat = await self._create_threat_event(
                            threat_type=rule.threat_type,
                            severity=rule.severity,
                            source_ip=source_ip,
                            target=url,
                            description=f"Suspicious user agent detected",
                            evidence={
                                "rule_id": rule_id,
                                "user_agent": user_agent,
                                "pattern": rule.pattern
                            }
                        )
                        threats_detected.append(threat)
            
            # Determine overall risk level
            risk_level = "low"
            if any(t.severity == "critical" for t in threats_detected):
                risk_level = "critical"
            elif any(t.severity == "high" for t in threats_detected):
                risk_level = "high"
            elif any(t.severity == "medium" for t in threats_detected):
                risk_level = "medium"
            
            # Determine recommended action
            recommended_action = "allow"
            for threat in threats_detected:
                rule = self.security_rules.get(threat.evidence.get("rule_id") if threat.evidence else None)
                if rule and rule.action in ["block", "quarantine"]:
                    recommended_action = rule.action
                    break
            
            return {
                "risk_level": risk_level,
                "threats_detected": [t.__dict__ for t in threats_detected],
                "recommended_action": recommended_action,
                "source_ip": source_ip,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing request: {str(e)}")
            return {
                "risk_level": "unknown",
                "threats_detected": [],
                "recommended_action": "allow",
                "error": str(e)
            }

    async def _check_ip_reputation(self, ip_address: str) -> Optional[ThreatEvent]:
        """Check IP address reputation"""
        try:
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                return await self._create_threat_event(
                    threat_type="blocked_ip",
                    severity="high",
                    source_ip=ip_address,
                    target="system",
                    description="Request from blocked IP address",
                    evidence={"reason": "previously_blocked"}
                )
            
            # Check IP reputation database
            if ip_address in self.ip_reputation_db:
                rep = self.ip_reputation_db[ip_address]
                if rep.is_blacklisted or rep.reputation_score < 30:
                    return await self._create_threat_event(
                        threat_type="malicious_ip",
                        severity="high",
                        source_ip=ip_address,
                        target="system",
                        description=f"Request from malicious IP (score: {rep.reputation_score})",
                        evidence={
                            "reputation_score": rep.reputation_score,
                            "threat_types": rep.threat_types,
                            "source": rep.source
                        }
                    )
            
            # Check if IP is from suspicious range
            if await self._is_suspicious_ip_range(ip_address):
                return await self._create_threat_event(
                    threat_type="suspicious_ip_range",
                    severity="medium",
                    source_ip=ip_address,
                    target="system",
                    description="Request from suspicious IP range",
                    evidence={"ip_range_check": True}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking IP reputation: {str(e)}")
            return None

    async def _is_suspicious_ip_range(self, ip_address: str) -> bool:
        """Check if IP is from suspicious range"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for known suspicious ranges
            suspicious_ranges = [
                ipaddress.ip_network("10.0.0.0/8"),  # Example: certain internal ranges
                ipaddress.ip_network("172.16.0.0/12"),
                # Add more suspicious ranges as needed
            ]
            
            for network in suspicious_ranges:
                if ip in network:
                    return True
            
            return False
            
        except Exception:
            return False

    async def _check_request_rate(self, ip_address: str) -> Optional[ThreatEvent]:
        """Check request rate for potential DoS"""
        try:
            current_time = int(time.time())
            minute_window = current_time // 60  # Group by minute
            
            # Count requests in current minute
            self.request_counters[ip_address][minute_window] += 1
            current_minute_requests = self.request_counters[ip_address][minute_window]
            
            # Check if threshold exceeded
            dos_rule = next(
                (rule for rule in self.security_rules.values() 
                 if rule.threat_type == "dos" and rule.enabled),
                None
            )
            
            if dos_rule and current_minute_requests > dos_rule.threshold:
                return await self._create_threat_event(
                    threat_type="dos",
                    severity="critical",
                    source_ip=ip_address,
                    target="system",
                    description=f"High request rate detected: {current_minute_requests} requests/minute",
                    evidence={
                        "requests_per_minute": current_minute_requests,
                        "threshold": dos_rule.threshold,
                        "time_window": "1 minute"
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking request rate: {str(e)}")
            return None

    async def _create_threat_event(
        self,
        threat_type: str,
        severity: str,
        source_ip: str,
        target: str,
        description: str,
        evidence: Dict[str, Any] = None
    ) -> ThreatEvent:
        """Create threat event"""
        event_id = f"threat_{int(time.time())}_{hashlib.md5(f'{source_ip}{threat_type}'.encode()).hexdigest()[:8]}"
        
        threat_event = ThreatEvent(
            event_id=event_id,
            threat_type=threat_type,
            severity=severity,
            source_ip=source_ip,
            target=target,
            description=description,
            timestamp=datetime.utcnow(),
            evidence=evidence or {}
        )
        
        self.threat_events.append(threat_event)
        
        logger.warning(
            f"Threat detected: {threat_type} from {source_ip} - {description}"
        )
        
        return threat_event

    async def report_failed_login(self, ip_address: str, username: str = None) -> Dict[str, Any]:
        """Report failed login attempt"""
        try:
            current_time = datetime.utcnow()
            self.failed_login_attempts[ip_address].append(current_time)
            
            # Check brute force rule
            brute_force_rule = next(
                (rule for rule in self.security_rules.values() 
                 if rule.threat_type == "brute_force" and rule.enabled),
                None
            )
            
            if brute_force_rule:
                window_start = current_time - timedelta(seconds=brute_force_rule.time_window)
                recent_attempts = [
                    attempt for attempt in self.failed_login_attempts[ip_address]
                    if attempt > window_start
                ]
                
                if len(recent_attempts) >= brute_force_rule.threshold:
                    threat = await self._create_threat_event(
                        threat_type="brute_force",
                        severity="high",
                        source_ip=ip_address,
                        target="authentication",
                        description=f"Brute force attack detected: {len(recent_attempts)} failed attempts",
                        evidence={
                            "failed_attempts": len(recent_attempts),
                            "threshold": brute_force_rule.threshold,
                            "time_window": brute_force_rule.time_window,
                            "username": username
                        }
                    )
                    
                    # Auto-block IP after brute force detection
                    await self.block_ip(ip_address, "brute_force_auto_block")
                    
                    return {
                        "threat_detected": True,
                        "threat_event": threat.__dict__,
                        "action_taken": "ip_blocked"
                    }
            
            return {
                "threat_detected": False,
                "failed_attempts": len(self.failed_login_attempts[ip_address])
            }
            
        except Exception as e:
            logger.error(f"Error reporting failed login: {str(e)}")
            return {"error": str(e)}

    async def block_ip(self, ip_address: str, reason: str) -> bool:
        """Block IP address"""
        try:
            self.blocked_ips.add(ip_address)
            
            # Create threat event for blocking
            await self._create_threat_event(
                threat_type="ip_blocked",
                severity="high",
                source_ip=ip_address,
                target="system",
                description=f"IP address blocked: {reason}",
                evidence={"block_reason": reason}
            )
            
            logger.info(f"Blocked IP address: {ip_address} (reason: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {str(e)}")
            return False

    async def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address"""
        try:
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)
                logger.info(f"Unblocked IP address: {ip_address}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {str(e)}")
            return False

    async def get_threat_events(
        self, 
        limit: int = 100,
        severity: str = None,
        threat_type: str = None,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get threat events with filtering"""
        try:
            events = list(self.threat_events)
            
            # Apply filters
            if severity:
                events = [e for e in events if e.severity == severity]
            
            if threat_type:
                events = [e for e in events if e.threat_type == threat_type]
            
            if since:
                events = [e for e in events if e.timestamp > since]
            
            # Sort by timestamp (newest first) and limit
            events.sort(key=lambda x: x.timestamp, reverse=True)
            events = events[:limit]
            
            return [e.__dict__ for e in events]
            
        except Exception as e:
            logger.error(f"Error getting threat events: {str(e)}")
            return []

    async def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        try:
            events = list(self.threat_events)
            total_events = len(events)
            
            # Count by severity
            severity_counts = defaultdict(int)
            for event in events:
                severity_counts[event.severity] += 1
            
            # Count by threat type
            threat_type_counts = defaultdict(int)
            for event in events:
                threat_type_counts[event.threat_type] += 1
            
            # Get recent events (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_events = [e for e in events if e.timestamp > recent_cutoff]
            
            # Top source IPs
            source_ip_counts = defaultdict(int)
            for event in recent_events:
                source_ip_counts[event.source_ip] += 1
            
            top_source_ips = sorted(
                source_ip_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            return {
                "total_events": total_events,
                "recent_events_24h": len(recent_events),
                "severity_distribution": dict(severity_counts),
                "threat_type_distribution": dict(threat_type_counts),
                "top_source_ips": [{"ip": ip, "count": count} for ip, count in top_source_ips],
                "blocked_ips_count": len(self.blocked_ips),
                "active_rules_count": len([r for r in self.security_rules.values() if r.enabled]),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting threat statistics: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Threat detection service health check"""
        try:
            return {
                "status": "healthy",
                "total_threat_events": len(self.threat_events),
                "active_rules": len([r for r in self.security_rules.values() if r.enabled]),
                "blocked_ips": len(self.blocked_ips),
                "monitored_ips": len(self.ip_reputation_db),
                "failed_login_tracking": len(self.failed_login_attempts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Threat detection health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global threat detection service instance
threat_detection_service = ThreatDetectionService()


async def analyze_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze request for threats"""
    return await threat_detection_service.analyze_request(request_data)


async def report_failed_login(ip_address: str, username: str = None) -> Dict[str, Any]:
    """Report failed login attempt"""
    return await threat_detection_service.report_failed_login(ip_address, username)


async def block_ip(ip_address: str, reason: str) -> bool:
    """Block IP address"""
    return await threat_detection_service.block_ip(ip_address, reason)


if __name__ == "__main__":
    async def test_threat_detection():
        """Test threat detection service"""
        print("Testing Threat Detection Service...")
        
        # Test request analysis
        test_request = {
            "source_ip": "192.168.1.100",
            "user_agent": "sqlmap/1.0",
            "url": "/api/users?id=1' OR '1'='1",
            "method": "GET",
            "headers": {},
            "body": ""
        }
        
        analysis = await analyze_request(test_request)
        print(f"Analysis result: {json.dumps(analysis, indent=2)}")
        
        # Test failed login
        login_result = await report_failed_login("192.168.1.101", "admin")
        print(f"Failed login result: {login_result}")
        
        # Get statistics
        stats = await threat_detection_service.get_threat_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
        
        # Health check
        health = await threat_detection_service.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_threat_detection())