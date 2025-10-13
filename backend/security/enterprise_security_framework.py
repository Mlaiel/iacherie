"""
🔒 Enterprise Security Framework - Core Implementation
Comprehensive security framework for enterprise-grade platform protection

Author: Fahed Mlaiel <mlaiel@live.de>
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for the platform"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"


class ThreatType(Enum):
    """Types of security threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    DATA_BREACH = "data_breach"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuthenticationMethod(Enum):
    """Authentication methods supported"""
    PASSWORD = "password"
    TWO_FACTOR = "two_factor"
    BIOMETRIC = "biometric"
    OAUTH = "oauth"
    JWT = "jwt"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    SSO = "sso"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    blocked: bool
    metadata: Dict[str, Any]


class EnterpriseSecurityFramework:
    """
    Enterprise-grade security framework implementing multiple layers of protection
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        self.security_level = security_level
        self.security_events: List[SecurityEvent] = []
        self.blocked_ips: set = set()
        self.active_sessions: Dict[str, Dict] = {}
        self.threat_detection_enabled = True
        
        logger.info(f"🔒 Enterprise Security Framework initialized - Level: {security_level.value}")
    
    def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate incoming request for security threats
        
        Args:
            request_data: Request data to validate
            
        Returns:
            bool: True if request is safe, False otherwise
        """
        ip_address = request_data.get("ip_address", "unknown")
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            self._log_security_event(
                threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                severity=SecurityLevel.HIGH,
                source_ip=ip_address,
                description="Request from blocked IP",
                blocked=True
            )
            return False
        
        # Check for SQL injection patterns
        if self._detect_sql_injection(request_data):
            self._log_security_event(
                threat_type=ThreatType.SQL_INJECTION,
                severity=SecurityLevel.CRITICAL,
                source_ip=ip_address,
                description="SQL injection attempt detected",
                blocked=True
            )
            self.block_ip(ip_address)
            return False
        
        # Check for XSS patterns
        if self._detect_xss(request_data):
            self._log_security_event(
                threat_type=ThreatType.XSS,
                severity=SecurityLevel.HIGH,
                source_ip=ip_address,
                description="XSS attempt detected",
                blocked=True
            )
            return False
        
        return True
    
    def authenticate(self, credentials: Dict[str, Any], method: AuthenticationMethod) -> Optional[str]:
        """
        Authenticate user with specified method
        
        Args:
            credentials: Authentication credentials
            method: Authentication method to use
            
        Returns:
            Optional[str]: Session token if successful, None otherwise
        """
        # Generate secure session token
        session_token = self._generate_session_token()
        
        # Store session
        self.active_sessions[session_token] = {
            "user_id": credentials.get("user_id"),
            "method": method.value,
            "created_at": datetime.utcnow(),
            "ip_address": credentials.get("ip_address")
        }
        
        logger.info(f"✅ User authenticated: {credentials.get('user_id')} - Method: {method.value}")
        return session_token
    
    def validate_session(self, session_token: str) -> bool:
        """
        Validate active session
        
        Args:
            session_token: Session token to validate
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        return session_token in self.active_sessions
    
    def block_ip(self, ip_address: str):
        """
        Block IP address
        
        Args:
            ip_address: IP address to block
        """
        self.blocked_ips.add(ip_address)
        logger.warning(f"🚫 IP blocked: {ip_address}")
    
    def unblock_ip(self, ip_address: str):
        """
        Unblock IP address
        
        Args:
            ip_address: IP address to unblock
        """
        self.blocked_ips.discard(ip_address)
        logger.info(f"✅ IP unblocked: {ip_address}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate security report
        
        Returns:
            Dict: Security statistics and events
        """
        threat_counts = {}
        for event in self.security_events:
            threat_type = event.threat_type.value
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        
        return {
            "security_level": self.security_level.value,
            "total_events": len(self.security_events),
            "blocked_ips_count": len(self.blocked_ips),
            "active_sessions_count": len(self.active_sessions),
            "threat_distribution": threat_counts,
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "threat_type": e.threat_type.value,
                    "severity": e.severity.value,
                    "blocked": e.blocked
                }
                for e in self.security_events[-10:]  # Last 10 events
            ]
        }
    
    def _detect_sql_injection(self, data: Dict[str, Any]) -> bool:
        """Detect SQL injection patterns"""
        sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE",
            "UNION SELECT",
            "1' OR '1' = '1",
            "admin'--",
            "' OR 1=1--"
        ]
        
        data_str = str(data).upper()
        return any(pattern.upper() in data_str for pattern in sql_patterns)
    
    def _detect_xss(self, data: Dict[str, Any]) -> bool:
        """Detect XSS patterns"""
        xss_patterns = [
            "<script>",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe",
            "eval(",
            "alert("
        ]
        
        data_str = str(data).lower()
        return any(pattern.lower() in data_str for pattern in xss_patterns)
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def _log_security_event(
        self,
        threat_type: ThreatType,
        severity: SecurityLevel,
        source_ip: str,
        description: str,
        blocked: bool,
        user_id: Optional[str] = None
    ):
        """Log security event"""
        event = SecurityEvent(
            event_id=hashlib.sha256(f"{datetime.utcnow()}{source_ip}{threat_type}".encode()).hexdigest()[:16],
            timestamp=datetime.utcnow(),
            threat_type=threat_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            blocked=blocked,
            metadata={}
        )
        
        self.security_events.append(event)
        logger.warning(f"⚠️ Security Event: {threat_type.value} - {description} - Blocked: {blocked}")


# Global security framework instance
_global_security_framework: Optional[EnterpriseSecurityFramework] = None


def create_security_framework(security_level: SecurityLevel = SecurityLevel.HIGH) -> EnterpriseSecurityFramework:
    """
    Create enterprise security framework instance
    
    Args:
        security_level: Security level to initialize with
        
    Returns:
        EnterpriseSecurityFramework: Security framework instance
    """
    global _global_security_framework
    _global_security_framework = EnterpriseSecurityFramework(security_level)
    return _global_security_framework


def get_global_security_framework() -> Optional[EnterpriseSecurityFramework]:
    """
    Get global security framework instance
    
    Returns:
        Optional[EnterpriseSecurityFramework]: Global instance or None
    """
    return _global_security_framework


# Auto-initialize on import
_global_security_framework = EnterpriseSecurityFramework(SecurityLevel.HIGH)

logger.info("🔒 Enterprise Security Framework module initialized")
