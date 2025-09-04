"""Security Service - Consolidated Security Management Services
================================================================

Comprehensive security system providing authentication, authorization,
encryption, and threat detection for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import secrets

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(str, Enum):
    LOGIN_ATTEMPT = "login_attempt"
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALWARE_DETECTED = "malware_detected"


@dataclass
class SecurityEvent:
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


class AuthenticationService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session_timeout = self.config.get('session_timeout', 3600)
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.lockout_duration = self.config.get('lockout_duration', 900)  # 15 minutes
        self.failed_attempts = {}
        self.active_sessions = {}
        
    async def authenticate(self, username: str, password: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Check for account lockout
            if await self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to multiple failed attempts'
                }
            
            # Verify credentials (simplified)
            if await self._verify_credentials(username, password):
                # Reset failed attempts on successful login
                self.failed_attempts.pop(username, None)
                
                # Create session
                session_token = self._generate_session_token()
                session_data = {
                    'username': username,
                    'ip_address': ip_address,
                    'created_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(seconds=self.session_timeout)
                }
                
                self.active_sessions[session_token] = session_data
                
                return {
                    'success': True,
                    'session_token': session_token,
                    'expires_at': session_data['expires_at']
                }
            else:
                # Track failed attempt
                await self._track_failed_attempt(username, ip_address)
                
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'error': 'Authentication service error'
            }
    
    async def _verify_credentials(self, username: str, password: str) -> bool:
        # Implementation would verify against database
        # For demo, accept any non-empty credentials
        return bool(username and password)
    
    async def _is_account_locked(self, username: str) -> bool:
        failed_data = self.failed_attempts.get(username)
        if not failed_data:
            return False
        
        if failed_data['count'] >= self.max_login_attempts:
            time_elapsed = (datetime.utcnow() - failed_data['last_attempt']).total_seconds()
            return time_elapsed < self.lockout_duration
        
        return False
    
    async def _track_failed_attempt(self, username: str, ip_address: Optional[str] = None):
        current_time = datetime.utcnow()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                'count': 0,
                'first_attempt': current_time,
                'last_attempt': current_time,
                'ip_addresses': set()
            }
        
        failed_data = self.failed_attempts[username]
        failed_data['count'] += 1
        failed_data['last_attempt'] = current_time
        
        if ip_address:
            failed_data['ip_addresses'].add(ip_address)
    
    def _generate_session_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    async def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        try:
            session_data = self.active_sessions.get(session_token)
            if not session_data:
                return None
            
            # Check if session has expired
            if datetime.utcnow() > session_data['expires_at']:
                del self.active_sessions[session_token]
                return None
            
            return session_data
            
        except Exception as e:
            logger.error(f"Session validation error: {str(e)}")
            return None
    
    async def logout(self, session_token: str) -> bool:
        try:
            if session_token in self.active_sessions:
                del self.active_sessions[session_token]
                return True
            return False
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False


class EncryptionService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.encryption_key = self.config.get('encryption_key', 'default_key')
        
    async def encrypt_data(self, data: str) -> str:
        try:
            # Implementation would use proper encryption algorithm (AES, etc.)
            # For demo, use simple hash
            return hashlib.sha256(f"{data}{self.encryption_key}".encode()).hexdigest()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        try:
            # Implementation would decrypt the data
            # For demo, return placeholder
            return "decrypted_data"
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
    
    async def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        try:
            if not salt:
                salt = secrets.token_hex(16)
            
            # Use a proper password hashing algorithm (bcrypt, scrypt, etc.)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            
            return {
                'hash': password_hash.hex(),
                'salt': salt
            }
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise
    
    async def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        try:
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == stored_hash
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False


class ThreatDetectionService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.security_events = []
        self.threat_patterns = {
            'brute_force': {'threshold': 10, 'window': 300},  # 10 attempts in 5 minutes
            'suspicious_locations': {'enabled': True},
            'unusual_activity': {'enabled': True}
        }
        
    async def detect_threats(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        try:
            # Analyze event for threats
            threat_level = await self._analyze_threat_level(event_data)
            
            if threat_level != ThreatLevel.LOW:
                security_event = SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=SecurityEventType(event_data.get('event_type', 'suspicious_activity')),
                    threat_level=threat_level,
                    user_id=event_data.get('user_id'),
                    ip_address=event_data.get('ip_address'),
                    user_agent=event_data.get('user_agent'),
                    description=event_data.get('description', ''),
                    metadata=event_data.get('metadata', {})
                )
                
                self.security_events.append(security_event)
                await self._handle_threat(security_event)
                
                return security_event
            
            return None
            
        except Exception as e:
            logger.error(f"Threat detection error: {str(e)}")
            return None
    
    async def _analyze_threat_level(self, event_data: Dict[str, Any]) -> ThreatLevel:
        # Simplified threat analysis
        event_type = event_data.get('event_type')
        
        if event_type == SecurityEventType.DATA_BREACH_ATTEMPT.value:
            return ThreatLevel.CRITICAL
        elif event_type == SecurityEventType.MALWARE_DETECTED.value:
            return ThreatLevel.HIGH
        elif event_type == SecurityEventType.FAILED_LOGIN.value:
            # Check for brute force
            return await self._check_brute_force(event_data)
        else:
            return ThreatLevel.LOW
    
    async def _check_brute_force(self, event_data: Dict[str, Any]) -> ThreatLevel:
        # Check for multiple failed logins from same IP
        ip_address = event_data.get('ip_address')
        if not ip_address:
            return ThreatLevel.LOW
        
        # Count recent failed logins from this IP
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self.threat_patterns['brute_force']['window'])
        
        failed_count = sum(1 for event in self.security_events
                          if event.event_type == SecurityEventType.FAILED_LOGIN
                          and event.ip_address == ip_address
                          and event.timestamp >= window_start)
        
        if failed_count >= self.threat_patterns['brute_force']['threshold']:
            return ThreatLevel.HIGH
        elif failed_count >= self.threat_patterns['brute_force']['threshold'] // 2:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _handle_threat(self, security_event: SecurityEvent):
        try:
            if security_event.threat_level == ThreatLevel.CRITICAL:
                # Immediate action required
                logger.critical(f"CRITICAL THREAT DETECTED: {security_event.event_id}")
                await self._block_ip(security_event.ip_address)
                await self._alert_administrators(security_event)
            elif security_event.threat_level == ThreatLevel.HIGH:
                # High priority threat
                logger.error(f"HIGH THREAT DETECTED: {security_event.event_id}")
                await self._rate_limit_ip(security_event.ip_address)
                await self._alert_administrators(security_event)
            elif security_event.threat_level == ThreatLevel.MEDIUM:
                # Monitor closely
                logger.warning(f"MEDIUM THREAT DETECTED: {security_event.event_id}")
                await self._increase_monitoring(security_event.ip_address)
                
        except Exception as e:
            logger.error(f"Threat handling error: {str(e)}")
    
    async def _block_ip(self, ip_address: Optional[str]):
        if ip_address:
            # Implementation would block IP at firewall/load balancer level
            logger.info(f"Blocking IP: {ip_address}")
    
    async def _rate_limit_ip(self, ip_address: Optional[str]):
        if ip_address:
            # Implementation would apply rate limiting
            logger.info(f"Rate limiting IP: {ip_address}")
    
    async def _increase_monitoring(self, ip_address: Optional[str]):
        if ip_address:
            # Implementation would increase monitoring for this IP
            logger.info(f"Increased monitoring for IP: {ip_address}")
    
    async def _alert_administrators(self, security_event: SecurityEvent):
        # Implementation would send alerts to administrators
        logger.info(f"Alert sent for security event: {security_event.event_id}")


class AuditService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.audit_logs = []
        
    async def log_event(self, event_type: str, user_id: Optional[str], details: Dict[str, Any]) -> None:
        try:
            audit_log = {
                'log_id': str(uuid.uuid4()),
                'event_type': event_type,
                'user_id': user_id,
                'details': details,
                'timestamp': datetime.utcnow(),
                'ip_address': details.get('ip_address'),
                'user_agent': details.get('user_agent')
            }
            
            self.audit_logs.append(audit_log)
            logger.info(f"Audit log created: {audit_log['log_id']}")
            
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
    
    async def get_audit_trail(self, user_id: Optional[str] = None, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        try:
            filtered_logs = self.audit_logs
            
            if user_id:
                filtered_logs = [log for log in filtered_logs if log['user_id'] == user_id]
            
            if start_date:
                filtered_logs = [log for log in filtered_logs if log['timestamp'] >= start_date]
            
            if end_date:
                filtered_logs = [log for log in filtered_logs if log['timestamp'] <= end_date]
            
            return filtered_logs
            
        except Exception as e:
            logger.error(f"Audit trail retrieval error: {str(e)}")
            return []


class SecurityService:
    """
    Unified Security Service that orchestrates all security-related services
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.auth_service = AuthenticationService(self.config.get('auth', {}))
        self.encryption_service = EncryptionService(self.config.get('encryption', {}))
        self.threat_detection_service = ThreatDetectionService(self.config.get('threat_detection', {}))
        self.audit_service = AuditService(self.config.get('audit', {}))
        
        logger.info("🔒 Security Service initialized")
    
    async def initialize(self):
        logger.info("🚀 Initializing Security Service")
    
    async def shutdown(self):
        logger.info("🛑 Shutting down Security Service")
    
    # Authentication methods
    async def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user"""
        result = await self.auth_service.authenticate(username, password, ip_address)
        
        # Log authentication attempt
        await self.audit_service.log_event('authentication_attempt', username, {
            'success': result['success'],
            'ip_address': ip_address,
            'error': result.get('error')
        })
        
        # Check for threats on failed login
        if not result['success']:
            await self.threat_detection_service.detect_threats({
                'event_type': 'failed_login',
                'user_id': username,
                'ip_address': ip_address,
                'description': 'Failed login attempt'
            })
        
        return result
    
    async def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session"""
        return await self.auth_service.validate_session(session_token)
    
    async def logout_user(self, session_token: str) -> bool:
        """Logout user"""
        return await self.auth_service.logout(session_token)
    
    # Encryption methods
    async def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        return await self.encryption_service.encrypt_data(data)
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        return await self.encryption_service.decrypt_data(encrypted_data)
    
    async def hash_password(self, password: str) -> Dict[str, str]:
        """Hash password"""
        return await self.encryption_service.hash_password(password)
    
    async def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password"""
        return await self.encryption_service.verify_password(password, stored_hash, salt)
    
    # Threat detection methods
    async def detect_threat(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect security threats"""
        return await self.threat_detection_service.detect_threats(event_data)
    
    # Audit methods
    async def log_security_event(self, event_type: str, user_id: Optional[str], details: Dict[str, Any]) -> None:
        """Log security event"""
        await self.audit_service.log_event(event_type, user_id, details)
    
    async def get_audit_trail(self, user_id: Optional[str] = None, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit trail"""
        return await self.audit_service.get_audit_trail(user_id, start_date, end_date)


__all__ = [
    "ThreatLevel", "SecurityEventType", "SecurityEvent",
    "AuthenticationService", "EncryptionService", 
    "ThreatDetectionService", "AuditService",
    "SecurityService"
]

logger.info(f"🔒 Security Service v{__version__} loaded")