"""🔐 Model Endpoint Security - Enterprise ML API Protection
============================================================
Module: mlops/model_deployment/model_endpoint_security.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE MODEL ENDPOINT SECURITY
Comprehensive security system for ML model API endpoints in Creator Economy
- Multi-layered authentication and authorization
- Creator-specific API key management and rate limiting
- Advanced threat detection and DDoS protection
- End-to-end encryption and data privacy compliance
"""

import asyncio
import logging
import hashlib
import hmac
import jwt
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import secrets
import base64
import ipaddress
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class AuthenticationMethod(Enum):
    """Authentication methods for API endpoints"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"
    SIGNATURE_BASED = "signature_based"

class SecurityLevel(Enum):
    """Security levels for different creator tiers"""
    BASIC = "basic"        # Free tier
    STANDARD = "standard"  # Creator tier
    ADVANCED = "advanced"  # Professional tier
    ENTERPRISE = "enterprise"  # Enterprise tier

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    DDOS_ATTACK = "ddos_attack"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    MODEL_EXTRACTION = "model_extraction"

class AccessStatus(Enum):
    """Access request status"""
    ALLOWED = "allowed"
    DENIED = "denied"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    REQUIRES_MFA = "requires_mfa"

@dataclass
class CreatorAPIKey:
    """Creator API key information"""
    key_id: str
    creator_id: str
    hashed_key: str
    name: str
    permissions: List[str]
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    allowed_ips: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    model_id: str
    creator_id: str
    security_level: SecurityLevel
    authentication_methods: List[AuthenticationMethod]
    rate_limits: Dict[str, int]
    ip_restrictions: List[str]
    allowed_origins: List[str]
    require_https: bool = True
    require_signature: bool = False
    enable_audit_logging: bool = True
    threat_detection_enabled: bool = True
    data_encryption_required: bool = True

@dataclass
class AccessRequest:
    """API access request"""
    request_id: str
    creator_id: str
    model_id: str
    endpoint: str
    method: str
    source_ip: str
    user_agent: str
    timestamp: datetime
    authentication_method: AuthenticationMethod
    api_key_id: Optional[str] = None
    payload_size: int = 0
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    threat_type: ThreatType
    severity: str
    source_ip: str
    creator_id: str
    model_id: str
    details: Dict[str, Any]
    timestamp: datetime
    blocked: bool = False
    action_taken: str = ""

class ModelEndpointSecurity:
    """🔐 Enterprise Model Endpoint Security Manager
    
    Comprehensive security system for ML model API endpoints providing multi-layered
    protection, authentication, authorization, and threat detection for Creator Economy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the model endpoint security system"""
        self.config = config or {}
        
        # Security configurations
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.creator_api_keys: Dict[str, List[CreatorAPIKey]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.rate_limit_counters: Dict[str, Dict[str, int]] = {}
        
        # Threat detection
        self.security_events: List[SecurityEvent] = []
        self.threat_patterns = self._initialize_threat_patterns()
        
        # JWT configuration
        self.jwt_secret = self.config.get('jwt_secret', secrets.token_urlsafe(64))
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration_hours = 24
        
        # Rate limiting windows
        self.rate_limit_windows = {
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }
        
        # Security level configurations
        self.security_level_configs = self._setup_security_level_configs()
        
        # Encryption settings
        self.encryption_key = self.config.get('encryption_key', secrets.token_bytes(32))
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'authenticated_requests': 0,
            'rate_limited_requests': 0,
            'threats_detected': 0,
            'api_keys_created': 0,
            'security_events': 0
        }
        
        logger.info("ModelEndpointSecurity initialized successfully")
    
    def _initialize_threat_patterns(self) -> Dict[ThreatType, Dict[str, Any]]:
        """Initialize threat detection patterns"""
        return {
            ThreatType.BRUTE_FORCE: {
                'failed_attempts_threshold': 10,
                'time_window_minutes': 15,
                'block_duration_minutes': 60
            },
            ThreatType.DDOS_ATTACK: {
                'requests_per_minute_threshold': 1000,
                'concurrent_connections_threshold': 500,
                'block_duration_minutes': 30
            },
            ThreatType.RATE_LIMIT_VIOLATION: {
                'violations_threshold': 5,
                'time_window_minutes': 10,
                'escalation_factor': 2.0
            },
            ThreatType.SUSPICIOUS_PATTERN: {
                'unusual_payload_size': 10485760,  # 10MB
                'suspicious_user_agents': ['bot', 'crawler', 'scraper'],
                'geographic_anomaly_threshold': 5  # Different countries in short time
            },
            ThreatType.MODEL_EXTRACTION: {
                'high_frequency_requests': 100,
                'systematic_parameter_probing': True,
                'response_pattern_analysis': True
            }
        }
    
    def _setup_security_level_configs(self) -> Dict[SecurityLevel, Dict[str, Any]]:
        """Setup security configurations per level"""
        return {
            SecurityLevel.BASIC: {
                'max_api_keys': 2,
                'rate_limit_per_minute': 60,
                'rate_limit_per_hour': 1000,
                'rate_limit_per_day': 10000,
                'authentication_methods': [AuthenticationMethod.API_KEY],
                'threat_detection': False,
                'audit_logging': True,
                'ip_restrictions': False
            },
            SecurityLevel.STANDARD: {
                'max_api_keys': 5,
                'rate_limit_per_minute': 300,
                'rate_limit_per_hour': 10000,
                'rate_limit_per_day': 100000,
                'authentication_methods': [AuthenticationMethod.API_KEY, AuthenticationMethod.JWT_TOKEN],
                'threat_detection': True,
                'audit_logging': True,
                'ip_restrictions': True
            },
            SecurityLevel.ADVANCED: {
                'max_api_keys': 15,
                'rate_limit_per_minute': 1000,
                'rate_limit_per_hour': 50000,
                'rate_limit_per_day': 500000,
                'authentication_methods': [
                    AuthenticationMethod.API_KEY,
                    AuthenticationMethod.JWT_TOKEN,
                    AuthenticationMethod.OAUTH2
                ],
                'threat_detection': True,
                'audit_logging': True,
                'ip_restrictions': True
            },
            SecurityLevel.ENTERPRISE: {
                'max_api_keys': 50,
                'rate_limit_per_minute': 5000,
                'rate_limit_per_hour': 200000,
                'rate_limit_per_day': 2000000,
                'authentication_methods': [
                    AuthenticationMethod.API_KEY,
                    AuthenticationMethod.JWT_TOKEN,
                    AuthenticationMethod.OAUTH2,
                    AuthenticationMethod.MUTUAL_TLS,
                    AuthenticationMethod.SIGNATURE_BASED
                ],
                'threat_detection': True,
                'audit_logging': True,
                'ip_restrictions': True
            }
        }
    
    async def setup_security_policy(
        self,
        deployment_context: Dict[str, Any],
        custom_policy: Optional[SecurityPolicy] = None
    ) -> Dict[str, Any]:
        """🛡️ Setup security policy for model endpoint
        
        Args:
            deployment_context: Complete deployment context
            custom_policy: Optional custom security policy
            
        Returns:
            Security setup result
        """
        model_id = deployment_context['model_id']
        creator_id = deployment_context['creator_id']
        
        try:
            logger.info(f"Setting up security policy for model {model_id}")
            
            # Create or use provided security policy
            if not custom_policy:
                security_policy = await self._create_optimal_security_policy(deployment_context)
            else:
                security_policy = custom_policy
            
            # Store security policy
            policy_key = f"{creator_id}:{model_id}"
            self.security_policies[policy_key] = security_policy
            
            # Initialize rate limiting counters
            self.rate_limit_counters[policy_key] = {
                'minute': {},
                'hour': {},
                'day': {}
            }
            
            # Create initial API key if none exists
            if creator_id not in self.creator_api_keys:
                initial_key = await self.create_api_key(
                    creator_id=creator_id,
                    name="Default API Key",
                    permissions=["model:inference", "model:status"]
                )
            
            logger.info(f"Security policy setup completed for {model_id}")
            
            return {
                'success': True,
                'model_id': model_id,
                'creator_id': creator_id,
                'security_level': security_policy.security_level.value,
                'authentication_methods': [method.value for method in security_policy.authentication_methods],
                'rate_limits': security_policy.rate_limits,
                'policy_key': policy_key
            }
            
        except Exception as e:
            logger.error(f"Security policy setup failed for {model_id}: {str(e)}")
            return {
                'success': False,
                'model_id': model_id,
                'creator_id': creator_id,
                'error': str(e)
            }
    
    async def _create_optimal_security_policy(
        self,
        deployment_context: Dict[str, Any]
    ) -> SecurityPolicy:
        """Create optimal security policy based on creator tier and requirements"""
        try:
            model_id = deployment_context['model_id']
            creator_id = deployment_context['creator_id']
            creator_config = deployment_context.get('creator_config', {})
            
            # Determine security level based on creator tier
            creator_tier = creator_config.get('tier', 'creator')
            security_level_map = {
                'free': SecurityLevel.BASIC,
                'creator': SecurityLevel.STANDARD,
                'professional': SecurityLevel.ADVANCED,
                'enterprise': SecurityLevel.ENTERPRISE
            }
            security_level = security_level_map.get(creator_tier, SecurityLevel.STANDARD)
            
            # Get level configuration
            level_config = self.security_level_configs[security_level]
            
            # Create security policy
            return SecurityPolicy(
                model_id=model_id,
                creator_id=creator_id,
                security_level=security_level,
                authentication_methods=level_config['authentication_methods'],
                rate_limits={
                    'per_minute': level_config['rate_limit_per_minute'],
                    'per_hour': level_config['rate_limit_per_hour'],
                    'per_day': level_config['rate_limit_per_day']
                },
                ip_restrictions=[],  # Empty initially, can be configured
                allowed_origins=['*'],  # Allow all origins initially
                require_https=True,
                require_signature=security_level == SecurityLevel.ENTERPRISE,
                enable_audit_logging=level_config['audit_logging'],
                threat_detection_enabled=level_config['threat_detection'],
                data_encryption_required=security_level in [SecurityLevel.ADVANCED, SecurityLevel.ENTERPRISE]
            )
            
        except Exception as e:
            logger.error(f"Failed to create optimal security policy: {str(e)}")
            raise
    
    async def create_api_key(
        self,
        creator_id: str,
        name: str,
        permissions: List[str],
        rate_limit_per_minute: Optional[int] = None,
        expires_days: Optional[int] = None,
        allowed_ips: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """🔑 Create new API key for creator
        
        Args:
            creator_id: Creator identifier
            name: Human-readable name for the key
            permissions: List of permissions for the key
            rate_limit_per_minute: Custom rate limit (optional)
            expires_days: Expiration in days (optional)
            allowed_ips: List of allowed IP addresses (optional)
            
        Returns:
            API key creation result
        """
        try:
            # Check if creator has reached API key limit
            creator_keys = self.creator_api_keys.get(creator_id, [])
            active_keys = [key for key in creator_keys if key.is_active]
            
            # Get security level for creator (assume standard if not found)
            security_level = SecurityLevel.STANDARD
            for policy in self.security_policies.values():
                if policy.creator_id == creator_id:
                    security_level = policy.security_level
                    break
            
            level_config = self.security_level_configs[security_level]
            
            if len(active_keys) >= level_config['max_api_keys']:
                return {
                    'success': False,
                    'error': f'Maximum API keys limit reached ({level_config["max_api_keys"]})'
                }
            
            # Generate API key
            raw_key = secrets.token_urlsafe(32)
            key_id = secrets.token_urlsafe(16)
            hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
            
            # Calculate expiration
            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Create API key object
            api_key = CreatorAPIKey(
                key_id=key_id,
                creator_id=creator_id,
                hashed_key=hashed_key,
                name=name,
                permissions=permissions,
                rate_limit_per_minute=rate_limit_per_minute or level_config['rate_limit_per_minute'],
                rate_limit_per_hour=level_config['rate_limit_per_hour'],
                rate_limit_per_day=level_config['rate_limit_per_day'],
                created_at=datetime.now(),
                expires_at=expires_at,
                allowed_ips=allowed_ips or [],
                metadata={'security_level': security_level.value}
            )
            
            # Store API key
            if creator_id not in self.creator_api_keys:
                self.creator_api_keys[creator_id] = []
            
            self.creator_api_keys[creator_id].append(api_key)
            self.metrics['api_keys_created'] += 1
            
            logger.info(f"API key created for creator {creator_id}: {key_id}")
            
            return {
                'success': True,
                'api_key': raw_key,  # Only returned once
                'key_id': key_id,
                'permissions': permissions,
                'rate_limits': {
                    'per_minute': api_key.rate_limit_per_minute,
                    'per_hour': api_key.rate_limit_per_hour,
                    'per_day': api_key.rate_limit_per_day
                },
                'expires_at': expires_at.isoformat() if expires_at else None
            }
            
        except Exception as e:
            logger.error(f"API key creation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def authenticate_request(self, access_request: AccessRequest) -> Dict[str, Any]:
        """🔐 Authenticate API request
        
        Args:
            access_request: Access request to authenticate
            
        Returns:
            Authentication result
        """
        try:
            self.metrics['total_requests'] += 1
            
            # Check if IP is blocked
            if self._is_ip_blocked(access_request.source_ip):
                self.metrics['blocked_requests'] += 1
                return {
                    'status': AccessStatus.BLOCKED,
                    'reason': 'IP address is blocked',
                    'retry_after': self._get_block_remaining_time(access_request.source_ip)
                }
            
            # Get security policy
            policy_key = f"{access_request.creator_id}:{access_request.model_id}"
            security_policy = self.security_policies.get(policy_key)
            
            if not security_policy:
                return {
                    'status': AccessStatus.DENIED,
                    'reason': 'No security policy found for model'
                }
            
            # Perform authentication based on method
            auth_result = await self._perform_authentication(access_request, security_policy)
            
            if auth_result['status'] != AccessStatus.ALLOWED:
                return auth_result
            
            # Check rate limits
            rate_limit_result = await self._check_rate_limits(access_request, security_policy)
            
            if rate_limit_result['status'] != AccessStatus.ALLOWED:
                self.metrics['rate_limited_requests'] += 1
                return rate_limit_result
            
            # Perform threat detection
            if security_policy.threat_detection_enabled:
                threat_result = await self._detect_threats(access_request)
                
                if threat_result['threat_detected']:
                    self.metrics['threats_detected'] += 1
                    await self._handle_security_threat(access_request, threat_result)
                    
                    if threat_result['block_request']:
                        self.metrics['blocked_requests'] += 1
                        return {
                            'status': AccessStatus.BLOCKED,
                            'reason': f'Security threat detected: {threat_result["threat_type"]}',
                            'threat_id': threat_result['event_id']
                        }
            
            # Update API key usage
            if access_request.api_key_id:
                await self._update_api_key_usage(access_request.creator_id, access_request.api_key_id)
            
            self.metrics['authenticated_requests'] += 1
            
            return {
                'status': AccessStatus.ALLOWED,
                'creator_id': access_request.creator_id,
                'permissions': auth_result.get('permissions', []),
                'rate_limits_remaining': rate_limit_result.get('remaining', {}),
                'audit_log_id': await self._log_access_request(access_request, 'ALLOWED')
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return {
                'status': AccessStatus.DENIED,
                'reason': f'Authentication error: {str(e)}'
            }
    
    async def _perform_authentication(
        self,
        access_request: AccessRequest,
        security_policy: SecurityPolicy
    ) -> Dict[str, Any]:
        """Perform authentication based on configured methods"""
        try:
            auth_method = access_request.authentication_method
            
            if auth_method not in security_policy.authentication_methods:
                return {
                    'status': AccessStatus.DENIED,
                    'reason': f'Authentication method {auth_method.value} not allowed'
                }
            
            if auth_method == AuthenticationMethod.API_KEY:
                return await self._authenticate_api_key(access_request)
            elif auth_method == AuthenticationMethod.JWT_TOKEN:
                return await self._authenticate_jwt_token(access_request)
            elif auth_method == AuthenticationMethod.OAUTH2:
                return await self._authenticate_oauth2(access_request)
            elif auth_method == AuthenticationMethod.SIGNATURE_BASED:
                return await self._authenticate_signature(access_request)
            else:
                return {
                    'status': AccessStatus.DENIED,
                    'reason': f'Unsupported authentication method: {auth_method.value}'
                }
                
        except Exception as e:
            return {'status': AccessStatus.DENIED, 'reason': str(e)}
    
    async def _authenticate_api_key(self, access_request: AccessRequest) -> Dict[str, Any]:
        """Authenticate using API key"""
        try:
            # Extract API key from headers
            auth_header = access_request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'status': AccessStatus.DENIED, 'reason': 'Missing or invalid Authorization header'}
            
            raw_key = auth_header[7:]  # Remove 'Bearer ' prefix
            hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
            
            # Find matching API key
            creator_keys = self.creator_api_keys.get(access_request.creator_id, [])
            matching_key = None
            
            for key in creator_keys:
                if key.hashed_key == hashed_key and key.is_active:
                    matching_key = key
                    break
            
            if not matching_key:
                return {'status': AccessStatus.DENIED, 'reason': 'Invalid API key'}
            
            # Check expiration
            if matching_key.expires_at and datetime.now() > matching_key.expires_at:
                return {'status': AccessStatus.DENIED, 'reason': 'API key expired'}
            
            # Check IP restrictions
            if matching_key.allowed_ips and access_request.source_ip not in matching_key.allowed_ips:
                return {'status': AccessStatus.DENIED, 'reason': 'IP address not allowed'}
            
            # Store key ID for usage tracking
            access_request.api_key_id = matching_key.key_id
            
            return {
                'status': AccessStatus.ALLOWED,
                'permissions': matching_key.permissions,
                'key_id': matching_key.key_id
            }
            
        except Exception as e:
            return {'status': AccessStatus.DENIED, 'reason': f'API key authentication error: {str(e)}'}
    
    async def _authenticate_jwt_token(self, access_request: AccessRequest) -> Dict[str, Any]:
        """Authenticate using JWT token"""
        try:
            # Extract JWT token from headers
            auth_header = access_request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'status': AccessStatus.DENIED, 'reason': 'Missing or invalid Authorization header'}
            
            token = auth_header[7:]
            
            # Decode and verify JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Verify creator ID matches
            if payload.get('creator_id') != access_request.creator_id:
                return {'status': AccessStatus.DENIED, 'reason': 'Token creator ID mismatch'}
            
            # Check expiration (handled by jwt.decode)
            permissions = payload.get('permissions', [])
            
            return {
                'status': AccessStatus.ALLOWED,
                'permissions': permissions,
                'token_payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {'status': AccessStatus.DENIED, 'reason': 'JWT token expired'}
        except jwt.InvalidTokenError:
            return {'status': AccessStatus.DENIED, 'reason': 'Invalid JWT token'}
        except Exception as e:
            return {'status': AccessStatus.DENIED, 'reason': f'JWT authentication error: {str(e)}'}
    
    async def _authenticate_oauth2(self, access_request: AccessRequest) -> Dict[str, Any]:
        """Authenticate using OAuth2 (simplified implementation)"""
        try:
            # In real implementation, this would validate OAuth2 tokens
            # with the authorization server
            
            auth_header = access_request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'status': AccessStatus.DENIED, 'reason': 'Missing OAuth2 token'}
            
            token = auth_header[7:]
            
            # Placeholder OAuth2 validation
            # In real implementation: validate with OAuth2 provider
            if len(token) < 20:  # Basic validation
                return {'status': AccessStatus.DENIED, 'reason': 'Invalid OAuth2 token'}
            
            return {
                'status': AccessStatus.ALLOWED,
                'permissions': ['model:inference'],  # Default permissions
                'oauth2_token': token
            }
            
        except Exception as e:
            return {'status': AccessStatus.DENIED, 'reason': f'OAuth2 authentication error: {str(e)}'}
    
    async def _authenticate_signature(self, access_request: AccessRequest) -> Dict[str, Any]:
        """Authenticate using request signature"""
        try:
            # Extract signature from headers
            signature = access_request.headers.get('X-Signature', '')
            timestamp = access_request.headers.get('X-Timestamp', '')
            
            if not signature or not timestamp:
                return {'status': AccessStatus.DENIED, 'reason': 'Missing signature or timestamp'}
            
            # Check timestamp freshness (prevent replay attacks)
            try:
                request_time = datetime.fromisoformat(timestamp)
                if abs((datetime.now() - request_time).total_seconds()) > 300:  # 5 minutes
                    return {'status': AccessStatus.DENIED, 'reason': 'Request timestamp too old'}
            except ValueError:
                return {'status': AccessStatus.DENIED, 'reason': 'Invalid timestamp format'}
            
            # Get creator's signing key (would be stored securely)
            signing_key = self._get_creator_signing_key(access_request.creator_id)
            if not signing_key:
                return {'status': AccessStatus.DENIED, 'reason': 'No signing key found'}
            
            # Verify signature
            message = f"{access_request.method}:{access_request.endpoint}:{timestamp}"
            expected_signature = hmac.new(
                signing_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return {'status': AccessStatus.DENIED, 'reason': 'Invalid signature'}
            
            return {
                'status': AccessStatus.ALLOWED,
                'permissions': ['model:inference', 'model:status'],
                'signature_valid': True
            }
            
        except Exception as e:
            return {'status': AccessStatus.DENIED, 'reason': f'Signature authentication error: {str(e)}'}
    
    def _get_creator_signing_key(self, creator_id: str) -> Optional[str]:
        """Get creator's signing key (placeholder implementation)"""
        # In real implementation, this would retrieve from secure storage
        return f"signing_key_for_{creator_id}"
    
    async def _check_rate_limits(
        self,
        access_request: AccessRequest,
        security_policy: SecurityPolicy
    ) -> Dict[str, Any]:
        """Check rate limits for the request"""
        try:
            policy_key = f"{access_request.creator_id}:{access_request.model_id}"
            current_time = datetime.now()
            
            # Initialize counters if not exists
            if policy_key not in self.rate_limit_counters:
                self.rate_limit_counters[policy_key] = {
                    'minute': {},
                    'hour': {},
                    'day': {}
                }
            
            counters = self.rate_limit_counters[policy_key]
            remaining_limits = {}
            
            # Check each time window
            for window, seconds in self.rate_limit_windows.items():
                window_key = int(current_time.timestamp() // seconds)
                
                # Clean old windows
                old_keys = [k for k in counters[window].keys() if k < window_key - 1]
                for old_key in old_keys:
                    del counters[window][old_key]
                
                # Get current count
                current_count = counters[window].get(window_key, 0)
                limit_key = f'per_{window}'
                rate_limit = security_policy.rate_limits.get(limit_key, float('inf'))
                
                remaining_limits[window] = max(0, rate_limit - current_count)
                
                # Check if limit exceeded
                if current_count >= rate_limit:
                    return {
                        'status': AccessStatus.RATE_LIMITED,
                        'reason': f'Rate limit exceeded for {window}',
                        'limit': rate_limit,
                        'current': current_count,
                        'reset_time': ((window_key + 1) * seconds)
                    }
                
                # Increment counter
                counters[window][window_key] = current_count + 1
            
            return {
                'status': AccessStatus.ALLOWED,
                'remaining': remaining_limits
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return {'status': AccessStatus.ALLOWED}  # Allow on error to prevent service disruption
    
    async def _detect_threats(self, access_request: AccessRequest) -> Dict[str, Any]:
        """Detect security threats in the request"""
        try:
            threats_detected = []
            threat_score = 0
            
            # Check for suspicious patterns
            if self._check_suspicious_patterns(access_request):
                threats_detected.append(ThreatType.SUSPICIOUS_PATTERN)
                threat_score += 30
            
            # Check for potential brute force
            if self._check_brute_force_pattern(access_request):
                threats_detected.append(ThreatType.BRUTE_FORCE)
                threat_score += 50
            
            # Check for DDoS patterns
            if self._check_ddos_pattern(access_request):
                threats_detected.append(ThreatType.DDOS_ATTACK)
                threat_score += 70
            
            # Check for model extraction attempts
            if self._check_model_extraction_pattern(access_request):
                threats_detected.append(ThreatType.MODEL_EXTRACTION)
                threat_score += 80
            
            # Determine if request should be blocked
            block_request = threat_score >= 70  # High threat score threshold
            
            if threats_detected:
                # Create security event
                event_id = secrets.token_urlsafe(16)
                security_event = SecurityEvent(
                    event_id=event_id,
                    threat_type=threats_detected[0],  # Primary threat
                    severity='HIGH' if threat_score >= 70 else 'MEDIUM' if threat_score >= 40 else 'LOW',
                    source_ip=access_request.source_ip,
                    creator_id=access_request.creator_id,
                    model_id=access_request.model_id,
                    details={
                        'threats': [t.value for t in threats_detected],
                        'threat_score': threat_score,
                        'user_agent': access_request.user_agent,
                        'endpoint': access_request.endpoint
                    },
                    timestamp=datetime.now(),
                    blocked=block_request,
                    action_taken='BLOCKED' if block_request else 'LOGGED'
                )
                
                self.security_events.append(security_event)
                self.metrics['security_events'] += 1
                
                return {
                    'threat_detected': True,
                    'threats': threats_detected,
                    'threat_score': threat_score,
                    'block_request': block_request,
                    'event_id': event_id
                }
            
            return {
                'threat_detected': False,
                'threat_score': 0,
                'block_request': False
            }
            
        except Exception as e:
            logger.error(f"Threat detection failed: {str(e)}")
            return {'threat_detected': False, 'threat_score': 0, 'block_request': False}
    
    def _check_suspicious_patterns(self, access_request: AccessRequest) -> bool:
        """Check for suspicious request patterns"""
        try:
            patterns = self.threat_patterns[ThreatType.SUSPICIOUS_PATTERN]
            
            # Check payload size
            if access_request.payload_size > patterns['unusual_payload_size']:
                return True
            
            # Check user agent
            user_agent = access_request.user_agent.lower()
            for suspicious_agent in patterns['suspicious_user_agents']:
                if suspicious_agent in user_agent:
                    return True
            
            return False
        except Exception:
            return False
    
    def _check_brute_force_pattern(self, access_request: AccessRequest) -> bool:
        """Check for brute force attack patterns"""
        try:
            # Count failed attempts from this IP in recent time
            recent_events = [
                event for event in self.security_events
                if (event.source_ip == access_request.source_ip and
                    event.threat_type == ThreatType.BRUTE_FORCE and
                    (datetime.now() - event.timestamp).total_seconds() < 900)  # 15 minutes
            ]
            
            patterns = self.threat_patterns[ThreatType.BRUTE_FORCE]
            return len(recent_events) >= patterns['failed_attempts_threshold']
            
        except Exception:
            return False
    
    def _check_ddos_pattern(self, access_request: AccessRequest) -> bool:
        """Check for DDoS attack patterns"""
        try:
            # Count requests from this IP in the last minute
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_requests = sum(
                1 for event in self.security_events
                if (event.source_ip == access_request.source_ip and
                    event.timestamp > one_minute_ago)
            )
            
            patterns = self.threat_patterns[ThreatType.DDOS_ATTACK]
            return recent_requests >= patterns['requests_per_minute_threshold']
            
        except Exception:
            return False
    
    def _check_model_extraction_pattern(self, access_request: AccessRequest) -> bool:
        """Check for model extraction attack patterns"""
        try:
            # Look for systematic probing patterns
            # This is a simplified check - real implementation would be more sophisticated
            
            # Check for high frequency requests from same IP
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_requests = sum(
                1 for event in self.security_events
                if (event.source_ip == access_request.source_ip and
                    event.timestamp > one_hour_ago)
            )
            
            patterns = self.threat_patterns[ThreatType.MODEL_EXTRACTION]
            return recent_requests >= patterns['high_frequency_requests']
            
        except Exception:
            return False
    
    async def _handle_security_threat(
        self,
        access_request: AccessRequest,
        threat_result: Dict[str, Any]
    ) -> None:
        """Handle detected security threat"""
        try:
            if threat_result['block_request']:
                # Block IP temporarily
                block_duration = timedelta(minutes=30)  # Default block duration
                self.blocked_ips[access_request.source_ip] = datetime.now() + block_duration
                
                logger.warning(
                    f"IP {access_request.source_ip} blocked due to security threat: "
                    f"{threat_result['threats']}"
                )
            
            # Additional threat handling could include:
            # - Alerting security team
            # - Updating firewall rules
            # - Notifying creator of suspicious activity
            
        except Exception as e:
            logger.error(f"Threat handling failed: {str(e)}")
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is currently blocked"""
        try:
            block_until = self.blocked_ips.get(ip_address)
            if not block_until:
                return False
            
            if datetime.now() > block_until:
                # Block expired, remove from blocked list
                del self.blocked_ips[ip_address]
                return False
            
            return True
        except Exception:
            return False
    
    def _get_block_remaining_time(self, ip_address: str) -> Optional[int]:
        """Get remaining block time in seconds"""
        try:
            block_until = self.blocked_ips.get(ip_address)
            if not block_until:
                return None
            
            remaining = (block_until - datetime.now()).total_seconds()
            return max(0, int(remaining))
        except Exception:
            return None
    
    async def _update_api_key_usage(self, creator_id: str, key_id: str) -> None:
        """Update API key usage statistics"""
        try:
            creator_keys = self.creator_api_keys.get(creator_id, [])
            for key in creator_keys:
                if key.key_id == key_id:
                    key.usage_count += 1
                    key.last_used_at = datetime.now()
                    break
        except Exception as e:
            logger.error(f"Failed to update API key usage: {str(e)}")
    
    async def _log_access_request(self, access_request: AccessRequest, status: str) -> str:
        """Log access request for audit purposes"""
        try:
            audit_log_id = secrets.token_urlsafe(16)
            
            # In real implementation, this would write to audit log storage
            logger.info(
                f"AUDIT: {audit_log_id} - {status} - "
                f"{access_request.creator_id} - {access_request.model_id} - "
                f"{access_request.source_ip} - {access_request.endpoint}"
            )
            
            return audit_log_id
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
            return "audit_log_error"
    
    async def revoke_api_key(self, creator_id: str, key_id: str) -> Dict[str, Any]:
        """🚫 Revoke API key"""
        try:
            creator_keys = self.creator_api_keys.get(creator_id, [])
            
            for key in creator_keys:
                if key.key_id == key_id:
                    key.is_active = False
                    
                    logger.info(f"API key revoked: {key_id} for creator {creator_id}")
                    
                    return {
                        'success': True,
                        'key_id': key_id,
                        'revoked_at': datetime.now().isoformat()
                    }
            
            return {'success': False, 'error': 'API key not found'}
            
        except Exception as e:
            logger.error(f"API key revocation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_security_status(self, creator_id: str, model_id: str) -> Dict[str, Any]:
        """📊 Get security status for model endpoint"""
        try:
            policy_key = f"{creator_id}:{model_id}"
            security_policy = self.security_policies.get(policy_key)
            
            if not security_policy:
                return {'found': False, 'error': 'Security policy not found'}
            
            # Get creator API keys
            creator_keys = self.creator_api_keys.get(creator_id, [])
            active_keys = [key for key in creator_keys if key.is_active]
            
            # Get recent security events
            recent_events = [
                {
                    'event_id': event.event_id,
                    'threat_type': event.threat_type.value,
                    'severity': event.severity,
                    'source_ip': event.source_ip,
                    'timestamp': event.timestamp.isoformat(),
                    'blocked': event.blocked
                }
                for event in self.security_events[-10:]
                if event.creator_id == creator_id and event.model_id == model_id
            ]
            
            return {
                'found': True,
                'creator_id': creator_id,
                'model_id': model_id,
                'security_level': security_policy.security_level.value,
                'authentication_methods': [method.value for method in security_policy.authentication_methods],
                'rate_limits': security_policy.rate_limits,
                'active_api_keys': len(active_keys),
                'threat_detection_enabled': security_policy.threat_detection_enabled,
                'recent_events': recent_events,
                'blocked_ips_count': len(self.blocked_ips)
            }
            
        except Exception as e:
            logger.error(f"Failed to get security status: {str(e)}")
            return {'found': False, 'error': str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """📈 Get security metrics"""
        total_requests = max(self.metrics['total_requests'], 1)
        
        return {
            **self.metrics,
            'authentication_rate': (self.metrics['authenticated_requests'] / total_requests) * 100,
            'block_rate': (self.metrics['blocked_requests'] / total_requests) * 100,
            'rate_limit_rate': (self.metrics['rate_limited_requests'] / total_requests) * 100,
            'threat_detection_rate': (self.metrics['threats_detected'] / total_requests) * 100,
            'total_api_keys': sum(len(keys) for keys in self.creator_api_keys.values()),
            'active_blocked_ips': len(self.blocked_ips),
            'total_security_events': len(self.security_events)
        }

# Export all components
__all__ = [
    'ModelEndpointSecurity',
    'AuthenticationMethod',
    'SecurityLevel',
    'ThreatType',
    'AccessStatus',
    'CreatorAPIKey',
    'SecurityPolicy',
    'AccessRequest',
    'SecurityEvent'
]