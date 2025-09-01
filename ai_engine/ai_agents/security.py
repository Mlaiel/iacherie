"""AI Agents Security System

Advanced security management system for AI agents with access control and threat detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import hashlib
import hmac
import time
import secrets
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import jwt

# Configure logging
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """
Security access levels."""

    PUBLIC = 1
    RESTRICTED = 2
    CONFIDENTIAL = 3
    SECRET = 4
    TOP_SECRET = 5


class ThreatLevel(Enum):
    """
Security threat levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecurityEvent:
    """
Security event record."""
    event_id: str
    timestamp: datetime
    event_type: str
    agent_id: str
    user_id: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.LOW
    description: str = ""
    source_ip: Optional[str] = None
    resolved: bool = False


@dataclass
class AccessControl:
    """Access control entry."""
    resource_id: str
    agent_id: str
    permissions: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class AgentSecurityManager:
    """
Advanced security manager for AI agents."""
    
    def __init__(self, secret_key: str = None):
        """
Initialize security manager."""
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.security_events: List[SecurityEvent] = []
        self.access_controls: Dict[str, AccessControl] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.threat_patterns: Dict[str, Any] = {}
        
        # Security configuration
        self.max_login_attempts = 5
        self.session_timeout = timedelta(hours=8)
        self.token_expiry = timedelta(hours=24)
        
        logger.info("Agent security manager initialized")
    
    def authenticate_agent(self, 
                          agent_id: str,
                          credentials: Dict[str, Any]) -> Optional[str]:
        """Authenticate an AI agent."""
        try:
            # Basic credential validation
            if not self._validate_credentials(agent_id, credentials):
                self._log_security_event(
                    "authentication_failed",
                    agent_id,
                    ThreatLevel.MEDIUM,
                    "Invalid credentials"
                )
                return None
            
            # Generate session token
            session_token = self._generate_session_token(agent_id)
            
            # Store active session
            self.active_sessions[session_token] = {
                'agent_id': agent_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'permissions': self._get_agent_permissions(agent_id)
            }
            
            self._log_security_event(
                "authentication_success",
                agent_id,
                ThreatLevel.LOW,
                "Agent authenticated successfully"
            )
            
            return session_token
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def _validate_credentials(self, agent_id: str, credentials: Dict) -> bool:
        """Validate agent credentials with comprehensive security checks."""
        try:
            # Validate required credential fields
            required_fields = ['api_key', 'timestamp', 'signature']
            for field in required_fields:
                if field not in credentials:
                    logger.warning(f"Missing required credential field: {field}")
                    return False
            
            # Validate API key format and existence
            api_key = credentials.get('api_key', '')
            if not api_key or len(api_key) < 32:
                logger.warning(f"Invalid API key format for agent {agent_id}")
                return False
            
            # Validate timestamp (prevent replay attacks)
            timestamp = credentials.get('timestamp', 0)
            current_time = datetime.utcnow().timestamp()
            if abs(current_time - timestamp) > 300:  # 5 minutes tolerance
                logger.warning(f"Timestamp validation failed for agent {agent_id}")
                return False
            
            # Validate signature
            expected_signature = self._calculate_signature(agent_id, credentials)
            if credentials.get('signature') != expected_signature:
                logger.warning(f"Signature validation failed for agent {agent_id}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Credential validation error for agent {agent_id}: {e}")
            return False
    
    def _calculate_signature(self, agent_id: str, credentials: Dict) -> str:
        """Calculate expected signature for credential validation."""
        import hashlib, hmac
        
        message = f"{agent_id}:{credentials.get('api_key')}:{credentials.get('timestamp')}"
        secret_key = os.getenv('SECURITY_SECRET_KEY', 'default-secret-key').encode()
        signature = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def _generate_session_token(self, agent_id: str) -> str:
        """Generate secure session token."""
        try:
            payload = {
                'agent_id': agent_id,
                'issued_at': datetime.utcnow().timestamp(),
                'expires_at': (datetime.utcnow() + self.token_expiry).timestamp()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return secrets.token_urlsafe(32)
    
    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token."""
        try:
            if token not in self.active_sessions:
                return None
            
            session = self.active_sessions[token]
            
            # Check session timeout
            if datetime.now() - session['last_activity'] > self.session_timeout:
                del self.active_sessions[token]
                return None
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
            return session['agent_id']
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def check_permission(self, 
                        agent_id: str,
                        resource_id: str,
                        permission: str) -> bool:
        """Check if agent has permission for resource."""
        try:
            access_key = f"{agent_id}:{resource_id}"
            
            if access_key not in self.access_controls:
                return False
            
            access_control = self.access_controls[access_key]
            
            # Check expiry
            if access_control.expires_at and datetime.now() > access_control.expires_at:
                return False
            
            # Check permission
            return permission in access_control.permissions
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    def grant_permission(self,
                        agent_id: str,
                        resource_id: str,
                        permissions: List[str],
                        security_level: SecurityLevel = SecurityLevel.PUBLIC,
                        expires_at: Optional[datetime] = None):
        """Grant permissions to agent."""
        try:
            access_key = f"{agent_id}:{resource_id}"
            
            access_control = AccessControl(
                resource_id=resource_id,
                agent_id=agent_id,
                permissions=permissions,
                security_level=security_level,
                expires_at=expires_at
            )
            
            self.access_controls[access_key] = access_control
            
            self._log_security_event(
                "permission_granted",
                agent_id,
                ThreatLevel.LOW,
                f"Granted permissions: {permissions} for resource: {resource_id}"
            )
            
        except Exception as e:
            logger.error(f"Grant permission error: {e}")
    
    def revoke_permission(self, agent_id: str, resource_id: str):
        """Revoke agent permissions."""
        try:
            access_key = f"{agent_id}:{resource_id}"
            
            if access_key in self.access_controls:
                del self.access_controls[access_key]
                
                self._log_security_event(
                    "permission_revoked",
                    agent_id,
                    ThreatLevel.LOW,
                    f"Revoked permissions for resource: {resource_id}"
                )
                
        except Exception as e:
            logger.error(f"Revoke permission error: {e}")
    
    def detect_threats(self, agent_id: str, activity_data: Dict) -> List[Dict]:
        """Detect potential security threats."""
        try:
            threats = []
            
            # Check for suspicious patterns
            if self._is_suspicious_activity(agent_id, activity_data):
                threats.append({
                    'type': 'suspicious_activity',
                    'threat_level': ThreatLevel.MEDIUM,
                    'description': 'Unusual activity pattern detected'
                })
            
            # Check for rate limiting violations
            if self._check_rate_limit(agent_id, activity_data):
                threats.append({
                    'type': 'rate_limit_violation',
                    'threat_level': ThreatLevel.HIGH,
                    'description': 'Rate limit exceeded'
                })
            
            # Log threats
            for threat in threats:
                self._log_security_event(
                    f"threat_detected_{threat['type']}",
                    agent_id,
                    threat['threat_level'],
                    threat['description']
                )
            
            return threats
            
        except Exception as e:
            logger.error(f"Threat detection error: {e}")
            return []
    
    def _is_suspicious_activity(self, agent_id: str, activity_data: Dict) -> bool:
        """Check for suspicious activity patterns using advanced analytics."""
        try:
            suspicious_indicators = 0
            
            # Check for unusual request patterns
            request_frequency = activity_data.get('requests_per_minute', 0)
            if request_frequency > self._get_agent_rate_limit(agent_id) * 1.5:
                suspicious_indicators += 1
            
            # Check for unusual access patterns
            accessed_resources = activity_data.get('accessed_resources', [])
            if len(set(accessed_resources)) > 20:  # Too many different resources
                suspicious_indicators += 1
            
            # Check for unusual time patterns
            request_time = activity_data.get('timestamp', 0)
            if self._is_unusual_time_pattern(agent_id, request_time):
                suspicious_indicators += 1
            
            # Check for geographical anomalies
            source_ip = activity_data.get('source_ip', '')
            if self._is_suspicious_ip(agent_id, source_ip):
                suspicious_indicators += 1
            
            # Check for failed authentication attempts
            failed_auths = activity_data.get('failed_auth_attempts', 0)
            if failed_auths > 3:
                suspicious_indicators += 2  # Weight this higher
            
            return suspicious_indicators >= 2
            
        except Exception as e:
            logger.error(f"Suspicious activity detection error: {e}")
            return False
    
    def _check_rate_limit(self, agent_id: str, activity_data: Dict) -> bool:
        """Check if agent is violating rate limits with adaptive thresholds."""
        try:
            current_requests = activity_data.get('requests_per_minute', 0)
            base_limit = self._get_agent_rate_limit(agent_id)
            
            # Adaptive rate limiting based on agent type and current load
            agent_type = activity_data.get('agent_type', 'standard')
            multiplier = {
                'premium': 2.0,
                'enterprise': 5.0,
                'standard': 1.0,
                'limited': 0.5
            }.get(agent_type, 1.0)
            
            adjusted_limit = int(base_limit * multiplier)
            
            # Consider burst allowance (short-term spikes)
            burst_allowance = adjusted_limit * 1.2
            consecutive_high_usage = activity_data.get('consecutive_high_usage_minutes', 0)
            
            if current_requests > burst_allowance and consecutive_high_usage > 2:
                logger.warning(f"Agent {agent_id} exceeding burst rate limit: {current_requests}/{burst_allowance}")
                return True
            
            return current_requests > adjusted_limit
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return False
    
    def _get_agent_rate_limit(self, agent_id: str) -> int:
        """Get the rate limit for a specific agent."""
        # Default rate limits per agent type
        default_limits = {
            'music_producer': 120,
            'content_optimizer': 100,
            'trend_analyzer': 150,
            'brand_manager': 80,
            'scheduling_agent': 60,
            'creative_director': 90
        }
        
        agent_type = agent_id.split('_')[0] if '_' in agent_id else 'standard'
        return default_limits.get(agent_type, 100)
    
    def _is_unusual_time_pattern(self, agent_id: str, timestamp: float) -> bool:
        """
Check if the request time is unusual for this agent."""
        import time
        from datetime import datetime
        
        try:
            request_time = datetime.fromtimestamp(timestamp)
            hour = request_time.hour
            
            # Most agents should not be active during maintenance windows
            if 2 <= hour <= 4:  # 2 AM - 4 AM maintenance window
                return True
            
            # Check against historical patterns (simplified)
            # In production, this would analyze historical data
            weekend = request_time.weekday() >= 5
            if weekend and hour < 8:  # Early weekend activity might be suspicious
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Time pattern analysis error: {e}")
            return False
    
    def _is_suspicious_ip(self, agent_id: str, source_ip: str) -> bool:
        """Check if the source IP is suspicious for this agent."""
        if not source_ip:
            return True  # Missing IP is suspicious
        
        # Check against known malicious IP ranges (simplified)
        suspicious_ranges = ['10.0.0.0/8', '192.168.0.0/16']  # Internal ranges in production
        
        # In production, this would check against threat intelligence feeds
        known_bad_ips = ['0.0.0.0', '127.0.0.1']  # Placeholder
        
        return source_ip in known_bad_ips
    
    def _get_agent_permissions(self, agent_id: str) -> List[str]:
        """
Get all permissions for an agent."""
        permissions = []
        
        for access_control in self.access_controls.values():
            if access_control.agent_id == agent_id:
                permissions.extend(access_control.permissions)
        
        return list(set(permissions))
    
    def _log_security_event(self,
                           event_type: str,
                           agent_id: str,
                           threat_level: ThreatLevel,
                           description: str):
        """
Log security event."""
        try:
            event = SecurityEvent(
                event_id=secrets.token_hex(16),
                timestamp=datetime.now(),
                event_type=event_type,
                agent_id=agent_id,
                threat_level=threat_level,
                description=description
            )
            
            self.security_events.append(event)
            
            # Log based on threat level
            if threat_level == ThreatLevel.CRITICAL:
                logger.critical(f"CRITICAL SECURITY EVENT: {description}")
            elif threat_level == ThreatLevel.HIGH:
                logger.warning(f"HIGH SECURITY EVENT: {description}")
            else:
                logger.info(f"Security event: {description}")
                
        except Exception as e:
            logger.error(f"Security event logging error: {e}")
    
    def get_security_events(self, 
                           agent_id: Optional[str] = None,
                           threat_level: Optional[ThreatLevel] = None,
                           limit: int = 100) -> List[SecurityEvent]:
        """Get security events."""
        try:
            events = self.security_events
            
            # Filter by agent
            if agent_id:
                events = [e for e in events if e.agent_id == agent_id]
            
            # Filter by threat level
            if threat_level:
                events = [e for e in events if e.threat_level == threat_level]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda e: e.timestamp, reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Get security events error: {e}")
            return []
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security system summary."""
        try:
            total_events = len(self.security_events)
            active_sessions_count = len(self.active_sessions)
            access_controls_count = len(self.access_controls)
            
            # Count events by threat level
            threat_counts = {}
            for level in ThreatLevel:
                threat_counts[level.name] = len([
                    e for e in self.security_events 
                    if e.threat_level == level
                ])
            
            # Recent critical events
            critical_events = [
                e for e in self.security_events 
                if e.threat_level == ThreatLevel.CRITICAL
            ][-5:]
            
            return {
                'total_events': total_events,
                'active_sessions': active_sessions_count,
                'access_controls': access_controls_count,
                'threat_level_counts': threat_counts,
                'recent_critical_events': len(critical_events),
                'system_status': 'healthy' if len(critical_events) == 0 else 'alert'
            }
            
        except Exception as e:
            logger.error(f"Security summary error: {e}")
            return {'error': str(e)}
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            # Simple encryption using HMAC
            key = self.secret_key.encode()
            message = data.encode()
            signature = hmac.new(key, message, hashlib.sha256).hexdigest()
            return f"{data}:{signature}"
            
        except Exception as e:
            logger.error(f"Data encryption error: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data."""
        try:
            if ':' not in encrypted_data:
                return encrypted_data
            
            data, signature = encrypted_data.rsplit(':', 1)
            key = self.secret_key.encode()
            message = data.encode()
            expected_signature = hmac.new(key, message, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Data decryption error: {e}")
            return None


# Module initialization
logger.info("AI agents security system module loaded successfully")
