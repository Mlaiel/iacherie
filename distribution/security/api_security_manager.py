"""
API Security Manager for Ainflue Distribution Platform

This module provides comprehensive API security management including
authentication, authorization, rate limiting, and threat detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import hmac
import jwt
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import ipaddress
import re

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Security actions to take"""
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    LOG_ONLY = "log_only"


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    policy_id: str
    name: str
    enabled: bool
    rules: List[Dict[str, Any]]
    actions: List[SecurityAction]
    threshold_settings: Dict[str, float]
    whitelist_ips: List[str]
    blacklist_ips: List[str]
    rate_limits: Dict[str, int]
    created_at: datetime
    updated_at: datetime


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    threat_level: ThreatLevel
    incident_type: str
    source_ip: str
    user_agent: str
    request_path: str
    request_method: str
    threat_indicators: List[str]
    action_taken: SecurityAction
    timestamp: datetime
    resolved: bool
    resolution_notes: Optional[str]


@dataclass
class APIRequest:
    """API request context for security analysis"""
    request_id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[str]
    client_ip: str
    user_agent: str
    timestamp: datetime
    user_id: Optional[str]
    api_key: Optional[str]


class APISecurityManager:
    """
    Comprehensive API security manager for distribution platform
    
    Features:
    - JWT token validation and management
    - Rate limiting with sliding windows
    - IP-based access control
    - Request signature verification
    - Threat detection and response
    - Security policy enforcement
    """

    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.security_policies = {}
        self.active_incidents = {}
        self.rate_limit_cache = {}
        self.blocked_ips = set()
        self.whitelisted_ips = set()
        self.jwt_secret = config.get('jwt_secret', 'default_secret')
        self.api_keys = {}
        self.request_signatures = {}
        
        # Initialize default security policies
        self._initialize_default_policies()

    def _initialize_default_policies(self) -> None:
        """Initialize default security policies"""
        
        # Basic rate limiting policy
        self.security_policies['rate_limiting'] = SecurityPolicy(
            policy_id='rate_limiting',
            name='API Rate Limiting',
            enabled=True,
            rules=[
                {'type': 'rate_limit', 'window': 60, 'max_requests': 100},
                {'type': 'burst_limit', 'window': 1, 'max_requests': 10}
            ],
            actions=[SecurityAction.RATE_LIMIT, SecurityAction.LOG_ONLY],
            threshold_settings={'burst_threshold': 0.8, 'sustained_threshold': 0.9},
            whitelist_ips=[],
            blacklist_ips=[],
            rate_limits={'default': 100, 'premium': 1000, 'enterprise': 10000},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Threat detection policy
        self.security_policies['threat_detection'] = SecurityPolicy(
            policy_id='threat_detection',
            name='Threat Detection and Response',
            enabled=True,
            rules=[
                {'type': 'sql_injection', 'pattern': r'(union|select|insert|delete|drop|update)\s'},
                {'type': 'xss_attempt', 'pattern': r'<script|javascript:|onload=|onerror='},
                {'type': 'path_traversal', 'pattern': r'\.\./|\.\.\\'}, 
                {'type': 'suspicious_user_agent', 'pattern': r'(bot|spider|crawler)'}
            ],
            actions=[SecurityAction.BLOCK, SecurityAction.LOG_ONLY],
            threshold_settings={'detection_threshold': 0.7},
            whitelist_ips=[],
            blacklist_ips=[],
            rate_limits={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def validate_request(self, request: APIRequest) -> Tuple[bool, SecurityAction, Optional[str]]:
        """
        Validate API request against security policies
        
        Args:
            request: API request to validate
            
        Returns:
            Tuple of (is_valid, action_to_take, reason)
        """
        try:
            # Check IP whitelist/blacklist
            ip_check = await self._check_ip_access(request.client_ip)
            if not ip_check[0]:
                return False, SecurityAction.BLOCK, ip_check[1]
            
            # Check rate limits
            rate_check = await self._check_rate_limits(request)
            if not rate_check[0]:
                return False, SecurityAction.RATE_LIMIT, rate_check[1]
            
            # Validate authentication
            auth_check = await self._validate_authentication(request)
            if not auth_check[0]:
                return False, SecurityAction.BLOCK, auth_check[1]
            
            # Check for threats
            threat_check = await self._detect_threats(request)
            if not threat_check[0]:
                return False, SecurityAction.BLOCK, threat_check[1]
            
            # Validate request signature if present
            if request.headers.get('X-Signature'):
                sig_check = await self._validate_signature(request)
                if not sig_check[0]:
                    return False, SecurityAction.BLOCK, sig_check[1]
            
            return True, SecurityAction.ALLOW, "Request validation passed"
            
        except Exception as e:
            logger.error(f"Error validating request: {e}")
            return False, SecurityAction.BLOCK, f"Validation error: {str(e)}"

    async def _check_ip_access(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """Check IP-based access control"""
        
        try:
            ip_addr = ipaddress.ip_address(client_ip)
            
            # Check blacklist
            if client_ip in self.blocked_ips:
                return False, f"IP {client_ip} is blacklisted"
            
            # Check whitelist (if configured)
            if self.whitelisted_ips and client_ip not in self.whitelisted_ips:
                # Check if IP is in whitelisted networks
                for whitelisted in self.whitelisted_ips:
                    try:
                        if '/' in whitelisted:  # CIDR notation
                            network = ipaddress.ip_network(whitelisted, strict=False)
                            if ip_addr in network:
                                return True, None
                        elif ip_addr == ipaddress.ip_address(whitelisted):
                            return True, None
                    except:
                        continue
                
                return False, f"IP {client_ip} not in whitelist"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking IP access: {e}")
            return False, f"IP validation error: {str(e)}"

    async def _check_rate_limits(self, request: APIRequest) -> Tuple[bool, Optional[str]]:
        """Check rate limits for the request"""
        
        try:
            # Determine rate limit tier
            tier = self._get_user_tier(request.user_id, request.api_key)
            rate_limit = self.security_policies['rate_limiting'].rate_limits.get(tier, 100)
            
            # Create rate limit key
            rate_key = f"{request.client_ip}:{request.user_id or 'anonymous'}"
            
            current_time = time.time()
            window_size = 60  # 1 minute window
            
            # Get current request count
            if rate_key not in self.rate_limit_cache:
                self.rate_limit_cache[rate_key] = []
            
            # Clean old entries
            self.rate_limit_cache[rate_key] = [
                timestamp for timestamp in self.rate_limit_cache[rate_key]
                if current_time - timestamp < window_size
            ]
            
            # Check if over limit
            current_count = len(self.rate_limit_cache[rate_key])
            if current_count >= rate_limit:
                return False, f"Rate limit exceeded: {current_count}/{rate_limit} requests per minute"
            
            # Add current request
            self.rate_limit_cache[rate_key].append(current_time)
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return False, f"Rate limit check error: {str(e)}"

    async def _validate_authentication(self, request: APIRequest) -> Tuple[bool, Optional[str]]:
        """Validate request authentication"""
        
        try:
            # Check for JWT token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                jwt_check = await self._validate_jwt_token(token)
                if jwt_check[0]:
                    return True, None
                else:
                    return False, jwt_check[1]
            
            # Check for API key
            api_key = request.headers.get('X-API-Key') or request.query_params.get('api_key')
            if api_key:
                api_check = await self._validate_api_key(api_key)
                if api_check[0]:
                    return True, None
                else:
                    return False, api_check[1]
            
            # Check if authentication is required
            if self._requires_authentication(request.path):
                return False, "Authentication required"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating authentication: {e}")
            return False, f"Authentication validation error: {str(e)}"

    async def _validate_jwt_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Validate JWT token"""
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check expiration
            if 'exp' in payload and payload['exp'] < time.time():
                return False, "Token expired"
            
            # Check issuer
            if 'iss' in payload and payload['iss'] != 'ainflue-distribution':
                return False, "Invalid token issuer"
            
            return True, None
            
        except jwt.ExpiredSignatureError:
            return False, "Token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid token"
        except Exception as e:
            return False, f"Token validation error: {str(e)}"

    async def _validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate API key"""
        
        try:
            # Hash the API key for comparison
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check if key exists and is active
            if key_hash in self.api_keys:
                key_info = self.api_keys[key_hash]
                if key_info.get('active', False):
                    # Check expiration
                    if 'expires_at' in key_info:
                        if datetime.utcnow() > key_info['expires_at']:
                            return False, "API key expired"
                    
                    return True, None
                else:
                    return False, "API key disabled"
            
            return False, "Invalid API key"
            
        except Exception as e:
            return False, f"API key validation error: {str(e)}"

    async def _detect_threats(self, request: APIRequest) -> Tuple[bool, Optional[str]]:
        """Detect security threats in request"""
        
        try:
            threats_detected = []
            
            threat_policy = self.security_policies.get('threat_detection')
            if not threat_policy or not threat_policy.enabled:
                return True, None
            
            # Check request path for threats
            for rule in threat_policy.rules:
                pattern = rule.get('pattern', '')
                threat_type = rule.get('type', 'unknown')
                
                # Check path
                if re.search(pattern, request.path, re.IGNORECASE):
                    threats_detected.append(f"{threat_type} in path")
                
                # Check query parameters
                for param, value in request.query_params.items():
                    if re.search(pattern, str(value), re.IGNORECASE):
                        threats_detected.append(f"{threat_type} in query parameter {param}")
                
                # Check headers
                for header, value in request.headers.items():
                    if re.search(pattern, str(value), re.IGNORECASE):
                        threats_detected.append(f"{threat_type} in header {header}")
                
                # Check body if present
                if request.body:
                    if re.search(pattern, request.body, re.IGNORECASE):
                        threats_detected.append(f"{threat_type} in request body")
            
            if threats_detected:
                # Log security incident
                await self._log_security_incident(request, threats_detected)
                return False, f"Security threats detected: {', '.join(threats_detected)}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error detecting threats: {e}")
            return False, f"Threat detection error: {str(e)}"

    async def _validate_signature(self, request: APIRequest) -> Tuple[bool, Optional[str]]:
        """Validate request signature"""
        
        try:
            signature = request.headers.get('X-Signature', '')
            timestamp = request.headers.get('X-Timestamp', '')
            
            if not signature or not timestamp:
                return False, "Missing signature or timestamp"
            
            # Check timestamp freshness (5 minute window)
            try:
                request_time = datetime.fromisoformat(timestamp)
                time_diff = abs((datetime.utcnow() - request_time).total_seconds())
                if time_diff > 300:  # 5 minutes
                    return False, "Request timestamp too old"
            except:
                return False, "Invalid timestamp format"
            
            # Create expected signature
            api_key = request.headers.get('X-API-Key', '')
            if not api_key:
                return False, "API key required for signed requests"
            
            # Get secret for API key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            if key_hash not in self.api_keys:
                return False, "Invalid API key for signature"
            
            secret = self.api_keys[key_hash].get('secret', '')
            
            # Create signature payload
            payload = f"{request.method}{request.path}{timestamp}{request.body or ''}"
            
            # Calculate expected signature
            expected_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid request signature"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating signature: {e}")
            return False, f"Signature validation error: {str(e)}"

    async def _log_security_incident(self, request -> None: APIRequest, threats -> None: List[str]) -> None:
        """Log security incident"""
        
        try:
            incident = SecurityIncident(
                incident_id=f"inc_{int(time.time())}_{hash(request.request_id) % 10000}",
                threat_level=self._assess_threat_level(threats),
                incident_type="threat_detection",
                source_ip=request.client_ip,
                user_agent=request.user_agent,
                request_path=request.path,
                request_method=request.method,
                threat_indicators=threats,
                action_taken=SecurityAction.BLOCK,
                timestamp=datetime.utcnow(),
                resolved=False,
                resolution_notes=None
            )
            
            self.active_incidents[incident.incident_id] = incident
            
            # Log to security system
            logger.warning(f"Security incident: {incident.incident_id} - {threats}")
            
            # If critical, could trigger alerts
            if incident.threat_level == ThreatLevel.CRITICAL:
                await self._trigger_security_alert(incident)
                
        except Exception as e:
            logger.error(f"Error logging security incident: {e}")

    def _assess_threat_level(self, threats: List[str]) -> ThreatLevel:
        """Assess threat level based on detected threats"""
        
        critical_threats = ['sql_injection', 'command_injection', 'path_traversal']
        high_threats = ['xss_attempt', 'csrf_attempt']
        medium_threats = ['suspicious_user_agent', 'rate_limit_violation']
        
        for threat in threats:
            if any(critical in threat.lower() for critical in critical_threats):
                return ThreatLevel.CRITICAL
            elif any(high in threat.lower() for high in high_threats):
                return ThreatLevel.HIGH
            elif any(medium in threat.lower() for medium in medium_threats):
                return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW

    async def _trigger_security_alert(self, incident -> None: SecurityIncident) -> None:
        """Trigger security alert for critical incidents"""
        
        # This would integrate with alerting systems
        logger.critical(f"SECURITY ALERT: {incident.incident_id} - {incident.threat_indicators}")
        
        # Could send notifications, emails, etc.
        # await self.notification_service.send_security_alert(incident)

    def _get_user_tier(self, user_id: Optional[str], api_key: Optional[str]) -> str:
        """Get user tier for rate limiting"""
        
        if api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            if key_hash in self.api_keys:
                return self.api_keys[key_hash].get('tier', 'default')
        
        # Default tier
        return 'default'

    def _requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication"""
        
        # Public endpoints that don't require auth
        public_paths = [
            '/health',
            '/status',
            '/docs',
            '/openapi.json'
        ]
        
        return not any(path.startswith(public) for public in public_paths)

    async def create_jwt_token(self, user_id: str, permissions: List[str], expires_in: int = 3600) -> str:
        """Create JWT token for user"""
        
        try:
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'iss': 'ainflue-distribution',
                'iat': time.time(),
                'exp': time.time() + expires_in
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise

    async def create_api_key(self, user_id: str, tier: str = 'default', expires_in_days: int = 365) -> Tuple[str, str]:
        """Create new API key for user"""
        
        try:
            import secrets
            
            # Generate random API key
            api_key = secrets.token_urlsafe(32)
            secret = secrets.token_urlsafe(32)
            
            # Hash for storage
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Store key info
            self.api_keys[key_hash] = {
                'user_id': user_id,
                'tier': tier,
                'secret': secret,
                'active': True,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=expires_in_days)
            }
            
            return api_key, secret
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            raise

    async def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            if key_hash in self.api_keys:
                self.api_keys[key_hash]['active'] = False
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False

    async def block_ip(self, ip_address -> None: str, reason -> None: str = "Security violation") -> None:
        """Block IP address"""
        
        try:
            self.blocked_ips.add(ip_address)
            logger.warning(f"Blocked IP {ip_address}: {reason}")
            
        except Exception as e:
            logger.error(f"Error blocking IP: {e}")

    async def unblock_ip(self, ip_address -> None: str) -> None:
        """Unblock IP address"""
        
        try:
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)
                logger.info(f"Unblocked IP {ip_address}")
                
        except Exception as e:
            logger.error(f"Error unblocking IP: {e}")

    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and statistics"""
        
        try:
            current_time = datetime.utcnow()
            last_24h = current_time - timedelta(hours=24)
            
            # Count incidents by type and level
            incidents_24h = [
                incident for incident in self.active_incidents.values()
                if incident.timestamp >= last_24h
            ]
            
            metrics = {
                'total_incidents': len(self.active_incidents),
                'incidents_24h': len(incidents_24h),
                'threat_levels': {
                    'critical': len([i for i in incidents_24h if i.threat_level == ThreatLevel.CRITICAL]),
                    'high': len([i for i in incidents_24h if i.threat_level == ThreatLevel.HIGH]),
                    'medium': len([i for i in incidents_24h if i.threat_level == ThreatLevel.MEDIUM]),
                    'low': len([i for i in incidents_24h if i.threat_level == ThreatLevel.LOW])
                },
                'blocked_ips': len(self.blocked_ips),
                'active_api_keys': len([k for k in self.api_keys.values() if k.get('active', False)]),
                'rate_limit_violations': len([
                    i for i in incidents_24h 
                    if 'rate_limit' in ' '.join(i.threat_indicators).lower()
                ])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {}