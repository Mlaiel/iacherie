#!/usr/bin/env python3
"""
🛡️ Security Monitoring Service - Security Services Module
========================================================

Advanced security monitoring and threat detection service for enterprise.

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Security Module
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "auth_failure"
    SUSPICIOUS_ACCESS = "suspicious_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALWARE_DETECTED = "malware_detected"
    DDOS_ATTACK = "ddos_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    description: str
    affected_resource: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None

class SecurityMonitoringService:
    """Enterprise Security Monitoring Service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_enabled = True
        self.events_buffer = []
        self.threat_patterns = {}
        self.blocked_ips = set()
        self.security_rules = []
        
        # Initialize security monitoring
        self._initialize_security_monitoring()
        
        self.logger.info("✅ SecurityMonitoringService initialized")
        
    def _initialize_security_monitoring(self):
        """Initialize security monitoring system"""
        try:
            # Load default security rules
            self.security_rules = [
                {
                    "name": "Brute Force Detection",
                    "pattern": "multiple_auth_failures",
                    "threshold": 5,
                    "window": 300,  # 5 minutes
                    "action": "block_ip"
                },
                {
                    "name": "Suspicious User Agent",
                    "pattern": "malicious_user_agent",
                    "threshold": 1,
                    "window": 60,
                    "action": "alert"
                },
                {
                    "name": "Unusual Access Patterns",
                    "pattern": "abnormal_access",
                    "threshold": 10,
                    "window": 600,  # 10 minutes
                    "action": "monitor"
                }
            ]
            
            # Initialize threat detection patterns
            self.threat_patterns = {
                "sql_injection": [
                    "' OR '1'='1",
                    "UNION SELECT",
                    "DROP TABLE",
                    "INSERT INTO"
                ],
                "xss": [
                    "<script>",
                    "javascript:",
                    "onerror=",
                    "onclick="
                ],
                "malicious_user_agents": [
                    "sqlmap",
                    "nikto",
                    "nmap",
                    "masscan"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security monitoring: {e}")
            
    def detect_threat(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect potential security threats in request data"""
        try:
            source_ip = request_data.get("ip", "unknown")
            user_agent = request_data.get("user_agent", "")
            path = request_data.get("path", "")
            method = request_data.get("method", "GET")
            
            # Check for malicious user agents
            for malicious_agent in self.threat_patterns.get("malicious_user_agents", []):
                if malicious_agent.lower() in user_agent.lower():
                    return SecurityEvent(
                        event_id=f"threat_{int(time.time())}",
                        event_type=SecurityEventType.SUSPICIOUS_ACCESS,
                        threat_level=ThreatLevel.HIGH,
                        timestamp=datetime.now(timezone.utc),
                        source_ip=source_ip,
                        description=f"Malicious user agent detected: {malicious_agent}",
                        affected_resource=path,
                        metadata={"user_agent": user_agent, "method": method}
                    )
            
            # Check for SQL injection patterns
            for param_value in request_data.get("params", {}).values():
                if isinstance(param_value, str):
                    for pattern in self.threat_patterns.get("sql_injection", []):
                        if pattern.lower() in param_value.lower():
                            return SecurityEvent(
                                event_id=f"sqli_{int(time.time())}",
                                event_type=SecurityEventType.DATA_BREACH_ATTEMPT,
                                threat_level=ThreatLevel.CRITICAL,
                                timestamp=datetime.now(timezone.utc),
                                source_ip=source_ip,
                                description=f"SQL injection attempt detected: {pattern}",
                                affected_resource=path,
                                metadata={"pattern": pattern, "value": param_value}
                            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Threat detection failed: {e}")
            return None
    
    def log_security_event(self, event: SecurityEvent):
        """Log security event to monitoring system"""
        try:
            self.events_buffer.append(event)
            
            # Log based on threat level
            if event.threat_level == ThreatLevel.CRITICAL:
                self.logger.critical(f"CRITICAL SECURITY EVENT: {event.description}")
            elif event.threat_level == ThreatLevel.HIGH:
                self.logger.error(f"HIGH THREAT: {event.description}")
            elif event.threat_level == ThreatLevel.MEDIUM:
                self.logger.warning(f"MEDIUM THREAT: {event.description}")
            else:
                self.logger.info(f"Security event: {event.description}")
            
            # Take automatic action if needed
            if event.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                self._handle_high_threat(event)
                
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def _handle_high_threat(self, event: SecurityEvent):
        """Handle high-level security threats automatically"""
        try:
            if event.source_ip and event.source_ip != "unknown":
                # Block suspicious IP
                self.blocked_ips.add(event.source_ip)
                self.logger.warning(f"Blocked IP {event.source_ip} due to {event.event_type.value}")
            
            # Send alert to security team
            self._send_security_alert(event)
            
        except Exception as e:
            self.logger.error(f"Failed to handle high threat: {e}")
    
    def _send_security_alert(self, event: SecurityEvent):
        """Send security alert to administrators"""
        try:
            alert_data = {
                "event_id": event.event_id,
                "threat_level": event.threat_level.value,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "source_ip": event.source_ip,
                "description": event.description,
                "affected_resource": event.affected_resource
            }
            
            # In a real implementation, this would send to alerting system
            self.logger.info(f"Security alert sent: {alert_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to send security alert: {e}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security monitoring metrics"""
        try:
            recent_events = [e for e in self.events_buffer if (datetime.now(timezone.utc) - e.timestamp).seconds < 3600]
            
            return {
                "total_events": len(self.events_buffer),
                "recent_events": len(recent_events),
                "blocked_ips": len(self.blocked_ips),
                "threat_levels": {
                    "critical": len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL]),
                    "high": len([e for e in recent_events if e.threat_level == ThreatLevel.HIGH]),
                    "medium": len([e for e in recent_events if e.threat_level == ThreatLevel.MEDIUM]),
                    "low": len([e for e in recent_events if e.threat_level == ThreatLevel.LOW])
                },
                "monitoring_enabled": self.monitoring_enabled,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {e}")
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get security monitoring service health status"""
        try:
            return {
                "status": "healthy",
                "service": "SecurityMonitoringService",
                "version": "1.0.0",
                "monitoring_enabled": self.monitoring_enabled,
                "events_processed": len(self.events_buffer),
                "blocked_ips": len(self.blocked_ips),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "service": "SecurityMonitoringService"
            }
    
    async def start_monitoring(self):
        """Start continuous security monitoring"""
        try:
            self.logger.info("Starting security monitoring...")
            
            while self.monitoring_enabled:
                try:
                    # Clean old events (keep last 24 hours)
                    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                    self.events_buffer = [e for e in self.events_buffer if e.timestamp > cutoff_time]
                    
                    # Monitor system resources
                    await self._monitor_system_resources()
                    
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Error in security monitoring loop: {e}")
                    await asyncio.sleep(30)
                    
        except Exception as e:
            self.logger.error(f"Failed to start security monitoring: {e}")
    
    async def _monitor_system_resources(self):
        """Monitor system resources for anomalies"""
        try:
            # This would monitor CPU, memory, network, etc.
            # For now, just a placeholder
            pass
            
        except Exception as e:
            self.logger.error(f"System resource monitoring failed: {e}")

# Create default instance
security_monitoring_service = SecurityMonitoringService()

__all__ = [
    'SecurityMonitoringService', 
    'SecurityEvent', 
    'ThreatLevel', 
    'SecurityEventType',
    'security_monitoring_service'
]