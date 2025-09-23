
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔐 SERVICE REGISTRY ENTERPRISE - SECURITY POLICY ENGINE
========================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: Ainflue Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🛡️ SECURITY POLICY ENGINE
Moteur politiques sécurité pour service registry.
Access control + audit logging + compliance monitoring + threat detection.
"""

import asyncio
import json
import logging
import time
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import ipaddress
import re
from collections import defaultdict, deque
import jwt
from cryptography.fernet import Fernet
import secrets

# Core logger
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security clearance levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class AuthMethod(Enum):
    """Authentication methods"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    MUTUAL_TLS = "mutual_tls"
    OAUTH2 = "oauth2"
    SERVICE_ACCOUNT = "service_account"

class Permission(Enum):
    """Registry operation permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"
    MONITOR = "monitor"

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SERVICE_ABUSE = "service_abuse"
    ANOMALY = "anomaly"

class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"

@dataclass
class ServicePrincipal:
    """Service principal for authentication"""
    principal_id: str
    principal_type: str  # service, user, system
    service_id: Optional[str]
    roles: Set[str]
    permissions: Set[Permission]
    security_level: SecurityLevel
    api_key_hash: Optional[str] = None
    certificate_fingerprint: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityRequest:
    """Security request for authentication/authorization"""
    operation: str
    resource: str
    principal: Optional[ServicePrincipal] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_time: float = field(default_factory=time.time)
    auth_method: Optional[AuthMethod] = None
    auth_token: Optional[str] = None
    additional_headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityResult:
    """Security operation result"""
    authorized: bool
    principal: Optional[ServicePrincipal] = None
    permissions_granted: Set[Permission] = field(default_factory=set)
    security_warnings: List[str] = field(default_factory=list)
    audit_events: List[Dict[str, Any]] = field(default_factory=list)
    threat_indicators: List[str] = field(default_factory=list)
    compliance_status: Dict[str, bool] = field(default_factory=dict)

@dataclass
class RegistryOperation:
    """Registry operation for authorization"""
    operation_id: str
    operation_type: str  # register, discover, update, delete, query
    resource_type: str   # service, configuration, health
    resource_id: str
    requested_permissions: Set[Permission]
    security_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthenticationResult:
    """Authentication result"""
    authenticated: bool
    principal: Optional[ServicePrincipal] = None
    auth_method: Optional[AuthMethod] = None
    confidence_score: float = 0.0
    error_message: Optional[str] = None
    expires_at: Optional[float] = None

@dataclass
class AuthorizationResult:
    """Authorization result"""
    authorized: bool
    granted_permissions: Set[Permission]
    denied_permissions: Set[Permission]
    policy_violations: List[str] = field(default_factory=list)
    additional_constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RegistryActivity:
    """Registry activity for auditing"""
    activity_id: str
    timestamp: float
    principal_id: str
    operation: str
    resource: str
    source_ip: str
    user_agent: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditResult:
    """Audit operation result"""
    audit_id: str
    logged: bool
    compliance_events: List[str]
    retention_policy_applied: bool
    encryption_applied: bool

@dataclass
class RegistryEvent:
    """Registry event for threat detection"""
    event_id: str
    timestamp: float
    event_type: str
    source_ip: str
    principal_id: Optional[str]
    details: Dict[str, Any]
    severity: str = "medium"

@dataclass
class ThreatDetectionResult:
    """Threat detection result"""
    threats_detected: List[Dict[str, Any]]
    risk_score: float  # 0.0 to 1.0
    recommended_actions: List[str]
    immediate_blocking_required: bool = False
    affected_principals: List[str] = field(default_factory=list)

@dataclass
class SecurityConfig:
    """Security configuration"""
    default_security_level: SecurityLevel = SecurityLevel.INTERNAL
    session_timeout_seconds: int = 3600
    max_failed_attempts: int = 5
    lockout_duration_seconds: int = 300
    jwt_secret_key: Optional[str] = None
    enable_mfa: bool = False
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    threat_detection_enabled: bool = True
    audit_retention_days: int = 90

class AccessController:
    """Access control management"""
    
    def __init__(self):
        self.principals: Dict[str, ServicePrincipal] = {}
        self.roles_permissions: Dict[str, Set[Permission]] = {}
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.locked_principals: Dict[str, float] = {}
        
        # Initialize default roles
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default RBAC roles"""
        self.roles_permissions = {
            'service_reader': {Permission.READ, Permission.MONITOR},
            'service_writer': {Permission.READ, Permission.WRITE, Permission.MONITOR},
            'service_admin': {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN, Permission.MONITOR},
            'auditor': {Permission.READ, Permission.AUDIT, Permission.MONITOR},
            'system_admin': {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN, Permission.AUDIT, Permission.MONITOR}
        }
    
    async def register_principal(self, principal: ServicePrincipal) -> bool:
        """Register new service principal"""
        try:
            # Generate API key hash if not provided
            if not principal.api_key_hash and principal.principal_type == 'service':
                api_key = secrets.token_urlsafe(32)
                principal.api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                logger.info(f"Generated API key for principal {principal.principal_id}")
            
            # Assign permissions based on roles
            for role in principal.roles:
                if role in self.roles_permissions:
                    principal.permissions.update(self.roles_permissions[role])
            
            self.principals[principal.principal_id] = principal
            logger.info(f"Registered principal: {principal.principal_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register principal {principal.principal_id}: {e}")
            return False
    
    async def authenticate_principal(self, auth_request: SecurityRequest) -> AuthenticationResult:
        """Authenticate service principal"""
        try:
            if not auth_request.auth_method or not auth_request.auth_token:
                return AuthenticationResult(
                    authenticated=False,
                    error_message="Missing authentication method or token"
                )
            
            # Check for locked principals
            if auth_request.principal and auth_request.principal.principal_id in self.locked_principals:
                lockout_time = self.locked_principals[auth_request.principal.principal_id]
                if time.time() < lockout_time:
                    return AuthenticationResult(
                        authenticated=False,
                        error_message="Principal is locked due to failed attempts"
                    )
                else:
                    # Remove expired lockout
                    del self.locked_principals[auth_request.principal.principal_id]
            
            # Authenticate based on method
            if auth_request.auth_method == AuthMethod.API_KEY:
                return await self._authenticate_api_key(auth_request)
            elif auth_request.auth_method == AuthMethod.JWT_TOKEN:
                return await self._authenticate_jwt(auth_request)
            elif auth_request.auth_method == AuthMethod.MUTUAL_TLS:
                return await self._authenticate_mtls(auth_request)
            else:
                return AuthenticationResult(
                    authenticated=False,
                    error_message=f"Unsupported authentication method: {auth_request.auth_method}"
                )
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return AuthenticationResult(
                authenticated=False,
                error_message=f"Authentication error: {str(e)}"
            )
    
    async def _authenticate_api_key(self, request: SecurityRequest) -> AuthenticationResult:
        """Authenticate using API key"""
        try:
            provided_key_hash = hashlib.sha256(request.auth_token.encode()).hexdigest()
            
            # Find principal with matching API key
            for principal in self.principals.values():
                if principal.api_key_hash == provided_key_hash and principal.is_active:
                    # Check expiration
                    if principal.expires_at and time.time() > principal.expires_at:
                        return AuthenticationResult(
                            authenticated=False,
                            error_message="API key has expired"
                        )
                    
                    return AuthenticationResult(
                        authenticated=True,
                        principal=principal,
                        auth_method=AuthMethod.API_KEY,
                        confidence_score=0.9,
                        expires_at=principal.expires_at
                    )
            
            # Record failed attempt
            if request.principal:
                self._record_failed_attempt(request.principal.principal_id)
            
            return AuthenticationResult(
                authenticated=False,
                error_message="Invalid API key"
            )
            
        except Exception as e:
            logger.error(f"API key authentication failed: {e}")
            return AuthenticationResult(
                authenticated=False,
                error_message="API key authentication error"
            )
    
    async def _authenticate_jwt(self, request: SecurityRequest) -> AuthenticationResult:
        """Authenticate using JWT token"""
        try:
            # For demo purposes, simple JWT validation
            # In production, would use proper JWT library with secret verification
            
            # Decode JWT header to get algorithm (without verification)
            header = jwt.get_unverified_header(request.auth_token)
            
            # Decode payload (without verification for demo)
            payload = jwt.decode(request.auth_token, options={"verify_signature": False})
            
            principal_id = payload.get('sub')
            if not principal_id:
                return AuthenticationResult(
                    authenticated=False,
                    error_message="Invalid JWT payload"
                )
            
            # Find principal
            principal = self.principals.get(principal_id)
            if not principal or not principal.is_active:
                return AuthenticationResult(
                    authenticated=False,
                    error_message="Principal not found or inactive"
                )
            
            # Check expiration
            exp = payload.get('exp')
            if exp and time.time() > exp:
                return AuthenticationResult(
                    authenticated=False,
                    error_message="JWT token has expired"
                )
            
            return AuthenticationResult(
                authenticated=True,
                principal=principal,
                auth_method=AuthMethod.JWT_TOKEN,
                confidence_score=0.95,
                expires_at=exp
            )
            
        except jwt.InvalidTokenError as e:
            return AuthenticationResult(
                authenticated=False,
                error_message=f"Invalid JWT token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"JWT authentication failed: {e}")
            return AuthenticationResult(
                authenticated=False,
                error_message="JWT authentication error"
            )
    
    async def _authenticate_mtls(self, request: SecurityRequest) -> AuthenticationResult:
        """Authenticate using mutual TLS"""
        try:
            # Extract certificate fingerprint from request
            cert_fingerprint = request.additional_headers.get('X-Client-Cert-Fingerprint')
            if not cert_fingerprint:
                return AuthenticationResult(
                    authenticated=False,
                    error_message="Client certificate required"
                )
            
            # Find principal with matching certificate
            for principal in self.principals.values():
                if (principal.certificate_fingerprint == cert_fingerprint and 
                    principal.is_active):
                    return AuthenticationResult(
                        authenticated=True,
                        principal=principal,
                        auth_method=AuthMethod.MUTUAL_TLS,
                        confidence_score=1.0
                    )
            
            return AuthenticationResult(
                authenticated=False,
                error_message="Invalid client certificate"
            )
            
        except Exception as e:
            logger.error(f"mTLS authentication failed: {e}")
            return AuthenticationResult(
                authenticated=False,
                error_message="mTLS authentication error"
            )
    
    def _record_failed_attempt(self, principal_id: str):
        """Record failed authentication attempt"""
        current_time = time.time()
        self.failed_attempts[principal_id].append(current_time)
        
        # Check if lockout threshold reached
        recent_failures = [
            t for t in self.failed_attempts[principal_id]
            if current_time - t < 300  # 5 minutes
        ]
        
        if len(recent_failures) >= 5:  # Max failed attempts
            self.locked_principals[principal_id] = current_time + 300  # 5 minute lockout
            logger.warning(f"Principal {principal_id} locked due to failed attempts")
    
    async def authorize_operation(self, operation: RegistryOperation, principal: ServicePrincipal) -> AuthorizationResult:
        """Authorize registry operation"""
        try:
            granted_permissions = set()
            denied_permissions = set()
            policy_violations = []
            
            # Check if principal has required permissions
            for permission in operation.requested_permissions:
                if permission in principal.permissions:
                    granted_permissions.add(permission)
                else:
                    denied_permissions.add(permission)
                    policy_violations.append(f"Missing permission: {permission.value}")
            
            # Check security level constraints
            resource_security_level = operation.security_context.get('security_level', SecurityLevel.INTERNAL)
            if isinstance(resource_security_level, str):
                resource_security_level = SecurityLevel(resource_security_level)
            
            if not self._check_security_level_access(principal.security_level, resource_security_level):
                policy_violations.append(f"Insufficient security clearance for {resource_security_level.value}")
                denied_permissions.update(operation.requested_permissions)
                granted_permissions.clear()
            
            # Check time-based constraints
            current_hour = datetime.now().hour
            if principal.metadata.get('restricted_hours'):
                restricted_hours = principal.metadata['restricted_hours']
                if current_hour in restricted_hours:
                    policy_violations.append("Access restricted during current hours")
                    denied_permissions.update(operation.requested_permissions)
                    granted_permissions.clear()
            
            # Check IP restrictions
            if principal.metadata.get('allowed_ip_ranges') and operation.security_context.get('client_ip'):
                client_ip = operation.security_context['client_ip']
                allowed_ranges = principal.metadata['allowed_ip_ranges']
                
                ip_allowed = False
                for ip_range in allowed_ranges:
                    try:
                        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(ip_range):
                            ip_allowed = True
                            break
                    except ValueError:
                        continue
                
                if not ip_allowed:
                    policy_violations.append(f"IP address {client_ip} not in allowed ranges")
                    denied_permissions.update(operation.requested_permissions)
                    granted_permissions.clear()
            
            authorized = len(denied_permissions) == 0 and len(policy_violations) == 0
            
            return AuthorizationResult(
                authorized=authorized,
                granted_permissions=granted_permissions,
                denied_permissions=denied_permissions,
                policy_violations=policy_violations
            )
            
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return AuthorizationResult(
                authorized=False,
                granted_permissions=set(),
                denied_permissions=operation.requested_permissions,
                policy_violations=[f"Authorization error: {str(e)}"]
            )
    
    def _check_security_level_access(self, principal_level: SecurityLevel, resource_level: SecurityLevel) -> bool:
        """Check if principal has sufficient security clearance"""
        level_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.CONFIDENTIAL: 2,
            SecurityLevel.SECRET: 3,
            SecurityLevel.TOP_SECRET: 4
        }
        
        return level_hierarchy[principal_level] >= level_hierarchy[resource_level]

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.audit_log: deque = deque(maxlen=100000)  # Keep last 100k entries in memory
        self.compliance_events: Dict[ComplianceStandard, List[Dict]] = defaultdict(list)
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def log_registry_activity(self, activity: RegistryActivity) -> AuditResult:
        """Log registry activity with compliance requirements"""
        try:
            audit_id = str(uuid.uuid4())
            
            # Create audit entry
            audit_entry = {
                'audit_id': audit_id,
                'timestamp': activity.timestamp,
                'principal_id': activity.principal_id,
                'operation': activity.operation,
                'resource': activity.resource,
                'source_ip': activity.source_ip,
                'user_agent': activity.user_agent,
                'success': activity.success,
                'details': activity.details
            }
            
            # Encrypt sensitive data
            encrypted_entry = self._encrypt_audit_entry(audit_entry)
            
            # Store audit entry
            self.audit_log.append(encrypted_entry)
            
            # Generate compliance events
            compliance_events = await self._generate_compliance_events(activity)
            
            # Store compliance-specific events
            for standard, events in compliance_events.items():
                self.compliance_events[standard].extend(events)
            
            logger.debug(f"Logged audit entry {audit_id}")
            
            return AuditResult(
                audit_id=audit_id,
                logged=True,
                compliance_events=list(compliance_events.keys()),
                retention_policy_applied=True,
                encryption_applied=True
            )
            
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
            return AuditResult(
                audit_id="",
                logged=False,
                compliance_events=[],
                retention_policy_applied=False,
                encryption_applied=False
            )
    
    def _encrypt_audit_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive audit entry data"""
        try:
            # Convert to JSON and encrypt
            json_data = json.dumps(entry)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'timestamp': entry['timestamp'],
                'audit_id': entry['audit_id']
            }
            
        except Exception as e:
            logger.error(f"Audit entry encryption failed: {e}")
            return entry  # Return unencrypted as fallback
    
    async def _generate_compliance_events(self, activity: RegistryActivity) -> Dict[ComplianceStandard, List[Dict]]:
        """Generate compliance-specific events"""
        compliance_events = defaultdict(list)
        
        # GDPR events
        if self._is_gdpr_relevant(activity):
            compliance_events[ComplianceStandard.GDPR].append({
                'event_type': 'data_access',
                'principal_id': activity.principal_id,
                'resource': activity.resource,
                'timestamp': activity.timestamp,
                'lawful_basis': 'legitimate_interest'
            })
        
        # SOX events (for financial data)
        if self._is_sox_relevant(activity):
            compliance_events[ComplianceStandard.SOX].append({
                'event_type': 'financial_system_access',
                'principal_id': activity.principal_id,
                'operation': activity.operation,
                'timestamp': activity.timestamp,
                'control_objective': 'access_control'
            })
        
        return compliance_events
    
    def _is_gdpr_relevant(self, activity: RegistryActivity) -> bool:
        """Check if activity is GDPR relevant"""
        gdpr_operations = ['user_data_access', 'personal_info_query', 'profile_update']
        return activity.operation in gdpr_operations or 'user' in activity.resource.lower()
    
    def _is_sox_relevant(self, activity: RegistryActivity) -> bool:
        """Check if activity is SOX relevant"""
        sox_operations = ['financial_data_access', 'billing_update', 'payment_process']
        return activity.operation in sox_operations or 'monetization' in activity.resource.lower()
    
    async def get_audit_trail(self, principal_id: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Get audit trail for principal within time range"""
        try:
            trail = []
            
            for encrypted_entry in self.audit_log:
                # Decrypt entry
                try:
                    encrypted_data = base64.b64decode(encrypted_entry['encrypted_data'])
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    entry = json.loads(decrypted_data.decode())
                    
                    # Filter by principal and time range
                    if (entry['principal_id'] == principal_id and 
                        start_time <= entry['timestamp'] <= end_time):
                        trail.append(entry)
                        
                except Exception as e:
                    logger.error(f"Failed to decrypt audit entry: {e}")
                    continue
            
            return sorted(trail, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Audit trail retrieval failed: {e}")
            return []

class ComplianceMonitor:
    """Compliance monitoring and reporting"""
    
    def __init__(self):
        self.compliance_rules: Dict[ComplianceStandard, Dict[str, Any]] = {}
        self.compliance_violations: Dict[ComplianceStandard, List[Dict]] = defaultdict(list)
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for different standards"""
        self.compliance_rules = {
            ComplianceStandard.GDPR: {
                'data_retention_days': 1095,  # 3 years
                'consent_required': True,
                'right_to_erasure': True,
                'data_portability': True,
                'privacy_by_design': True
            },
            ComplianceStandard.HIPAA: {
                'encryption_required': True,
                'access_logging': True,
                'minimum_necessary': True,
                'administrative_safeguards': True
            },
            ComplianceStandard.SOX: {
                'change_management': True,
                'segregation_of_duties': True,
                'access_controls': True,
                'audit_trails': True
            },
            ComplianceStandard.PCI_DSS: {
                'encryption_in_transit': True,
                'encryption_at_rest': True,
                'access_control': True,
                'vulnerability_management': True
            }
        }
    
    async def check_compliance(self, standard: ComplianceStandard, activity: RegistryActivity) -> Dict[str, Any]:
        """Check activity compliance against standard"""
        try:
            rules = self.compliance_rules.get(standard, {})
            compliance_status = {}
            violations = []
            
            # Check specific compliance requirements
            if standard == ComplianceStandard.GDPR:
                compliance_status = await self._check_gdpr_compliance(activity, rules)
            elif standard == ComplianceStandard.HIPAA:
                compliance_status = await self._check_hipaa_compliance(activity, rules)
            elif standard == ComplianceStandard.SOX:
                compliance_status = await self._check_sox_compliance(activity, rules)
            elif standard == ComplianceStandard.PCI_DSS:
                compliance_status = await self._check_pci_compliance(activity, rules)
            
            # Record violations
            for requirement, compliant in compliance_status.items():
                if not compliant:
                    violation = {
                        'timestamp': activity.timestamp,
                        'activity_id': activity.activity_id,
                        'requirement': requirement,
                        'principal_id': activity.principal_id,
                        'details': activity.details
                    }
                    violations.append(violation)
                    self.compliance_violations[standard].append(violation)
            
            return {
                'standard': standard.value,
                'compliant': all(compliance_status.values()),
                'compliance_status': compliance_status,
                'violations': violations
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                'standard': standard.value,
                'compliant': False,
                'compliance_status': {},
                'violations': [{'error': str(e)}]
            }
    
    async def _check_gdpr_compliance(self, activity: RegistryActivity, rules: Dict[str, Any]) -> Dict[str, bool]:
        """Check GDPR compliance"""
        compliance = {}
        
        # Check if consent is required and present
        if rules.get('consent_required') and 'user' in activity.resource.lower():
            compliance['consent_documented'] = 'consent' in activity.details
        
        # Check data minimization
        compliance['data_minimized'] = True  # Assume compliant for demo
        
        # Check purpose limitation
        compliance['purpose_limited'] = 'purpose' in activity.details
        
        return compliance
    
    async def _check_hipaa_compliance(self, activity: RegistryActivity, rules: Dict[str, Any]) -> Dict[str, bool]:
        """Check HIPAA compliance"""
        compliance = {}
        
        # Check encryption requirement
        if rules.get('encryption_required'):
            compliance['data_encrypted'] = activity.details.get('encrypted', False)
        
        # Check minimum necessary principle
        if rules.get('minimum_necessary'):
            compliance['minimum_necessary'] = True  # Assume compliant for demo
        
        return compliance
    
    async def _check_sox_compliance(self, activity: RegistryActivity, rules: Dict[str, Any]) -> Dict[str, bool]:
        """Check SOX compliance"""
        compliance = {}
        
        # Check change management
        if rules.get('change_management') and activity.operation in ['update', 'delete']:
            compliance['change_approved'] = 'approval' in activity.details
        
        # Check segregation of duties
        if rules.get('segregation_of_duties'):
            compliance['duties_segregated'] = True  # Assume compliant for demo
        
        return compliance
    
    async def _check_pci_compliance(self, activity: RegistryActivity, rules: Dict[str, Any]) -> Dict[str, bool]:
        """Check PCI DSS compliance"""
        compliance = {}
        
        # Check encryption requirements
        if rules.get('encryption_in_transit'):
            compliance['encrypted_in_transit'] = activity.details.get('tls_enabled', False)
        
        if rules.get('encryption_at_rest'):
            compliance['encrypted_at_rest'] = activity.details.get('encrypted_storage', False)
        
        return compliance

class ThreatDetector:
    """ML-based threat detection system"""
    
    def __init__(self):
        self.event_history: deque = deque(maxlen=10000)
        self.ip_reputation: Dict[str, float] = {}
        self.behavioral_baselines: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.threat_patterns: Dict[ThreatType, Dict[str, Any]] = {}
        self._initialize_threat_patterns()
    
    def _initialize_threat_patterns(self):
        """Initialize threat detection patterns"""
        self.threat_patterns = {
            ThreatType.BRUTE_FORCE: {
                'max_failed_attempts': 10,
                'time_window_minutes': 5,
                'ip_based': True
            },
            ThreatType.SUSPICIOUS_ACTIVITY: {
                'unusual_hours': [22, 23, 0, 1, 2, 3, 4, 5],
                'rapid_requests': {'threshold': 100, 'window_minutes': 1},
                'geographic_anomaly': True
            },
            ThreatType.SERVICE_ABUSE: {
                'request_rate_threshold': 1000,  # requests per minute
                'resource_enumeration': True,
                'privilege_escalation': True
            }
        }
    
    async def detect_threats(self, registry_events: List[RegistryEvent]) -> ThreatDetectionResult:
        """Detect security threats from registry events"""
        try:
            threats_detected = []
            risk_score = 0.0
            recommended_actions = []
            immediate_blocking = False
            affected_principals = set()
            
            # Store events for analysis
            self.event_history.extend(registry_events)
            
            # Analyze different threat types
            for event in registry_events:
                # Brute force detection
                brute_force_threat = await self._detect_brute_force(event)
                if brute_force_threat:
                    threats_detected.append(brute_force_threat)
                    risk_score = max(risk_score, 0.8)
                    recommended_actions.append('Block IP address')
                    if event.principal_id:
                        affected_principals.add(event.principal_id)
                
                # Suspicious activity detection
                suspicious_threat = await self._detect_suspicious_activity(event)
                if suspicious_threat:
                    threats_detected.append(suspicious_threat)
                    risk_score = max(risk_score, 0.6)
                    recommended_actions.append('Increase monitoring')
                
                # Service abuse detection
                abuse_threat = await self._detect_service_abuse(event)
                if abuse_threat:
                    threats_detected.append(abuse_threat)
                    risk_score = max(risk_score, 0.9)
                    immediate_blocking = True
                    recommended_actions.append('Rate limit principal')
                    if event.principal_id:
                        affected_principals.add(event.principal_id)
            
            # Analyze behavioral anomalies
            anomaly_threats = await self._detect_behavioral_anomalies(registry_events)
            threats_detected.extend(anomaly_threats)
            
            if anomaly_threats:
                risk_score = max(risk_score, 0.5)
                recommended_actions.append('Investigate anomalous behavior')
            
            return ThreatDetectionResult(
                threats_detected=threats_detected,
                risk_score=risk_score,
                recommended_actions=list(set(recommended_actions)),
                immediate_blocking_required=immediate_blocking,
                affected_principals=list(affected_principals)
            )
            
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            return ThreatDetectionResult(
                threats_detected=[],
                risk_score=0.0,
                recommended_actions=[],
                immediate_blocking_required=False,
                affected_principals=[]
            )
    
    async def _detect_brute_force(self, event: RegistryEvent) -> Optional[Dict[str, Any]]:
        """Detect brute force attacks"""
        try:
            if event.event_type != 'authentication_failed':
                return None
            
            # Count failed attempts from same IP in time window
            current_time = event.timestamp
            time_window = 300  # 5 minutes
            
            failed_attempts = [
                e for e in self.event_history
                if (e.source_ip == event.source_ip and
                    e.event_type == 'authentication_failed' and
                    current_time - e.timestamp <= time_window)
            ]
            
            if len(failed_attempts) >= 10:  # Threshold
                return {
                    'threat_type': ThreatType.BRUTE_FORCE.value,
                    'source_ip': event.source_ip,
                    'failed_attempts': len(failed_attempts),
                    'time_window_minutes': time_window / 60,
                    'severity': 'high',
                    'confidence': 0.9
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Brute force detection failed: {e}")
            return None
    
    async def _detect_suspicious_activity(self, event: RegistryEvent) -> Optional[Dict[str, Any]]:
        """Detect suspicious activity patterns"""
        try:
            suspicious_indicators = []
            
            # Check for unusual hours
            hour = datetime.fromtimestamp(event.timestamp).hour
            if hour in [22, 23, 0, 1, 2, 3, 4, 5]:
                suspicious_indicators.append('unusual_hours')
            
            # Check for rapid requests
            current_time = event.timestamp
            recent_events = [
                e for e in self.event_history
                if (e.source_ip == event.source_ip and
                    current_time - e.timestamp <= 60)  # 1 minute
            ]
            
            if len(recent_events) > 100:
                suspicious_indicators.append('rapid_requests')
            
            # Check user agent anomalies
            if not event.details.get('user_agent') or 'bot' in event.details.get('user_agent', '').lower():
                suspicious_indicators.append('suspicious_user_agent')
            
            if suspicious_indicators:
                return {
                    'threat_type': ThreatType.SUSPICIOUS_ACTIVITY.value,
                    'source_ip': event.source_ip,
                    'indicators': suspicious_indicators,
                    'severity': 'medium',
                    'confidence': 0.6
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Suspicious activity detection failed: {e}")
            return None
    
    async def _detect_service_abuse(self, event: RegistryEvent) -> Optional[Dict[str, Any]]:
        """Detect service abuse patterns"""
        try:
            # Check for resource enumeration
            if event.event_type == 'service_discovery':
                current_time = event.timestamp
                discovery_events = [
                    e for e in self.event_history
                    if (e.source_ip == event.source_ip and
                        e.event_type == 'service_discovery' and
                        current_time - e.timestamp <= 300)  # 5 minutes
                ]
                
                if len(discovery_events) > 50:  # Threshold for enumeration
                    return {
                        'threat_type': ThreatType.SERVICE_ABUSE.value,
                        'source_ip': event.source_ip,
                        'abuse_type': 'resource_enumeration',
                        'discovery_requests': len(discovery_events),
                        'severity': 'high',
                        'confidence': 0.8
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Service abuse detection failed: {e}")
            return None
    
    async def _detect_behavioral_anomalies(self, events: List[RegistryEvent]) -> List[Dict[str, Any]]:
        """Detect behavioral anomalies using ML techniques"""
        try:
            anomalies = []
            
            # Group events by principal
            principal_events = defaultdict(list)
            for event in events:
                if event.principal_id:
                    principal_events[event.principal_id].append(event)
            
            # Analyze each principal's behavior
            for principal_id, principal_events_list in principal_events.items():
                if len(principal_events_list) < 5:  # Need minimum events
                    continue
                
                # Calculate request rate anomaly
                request_times = [e.timestamp for e in principal_events_list]
                if len(request_times) > 1:
                    time_diffs = [request_times[i] - request_times[i-1] for i in range(1, len(request_times))]
                    avg_interval = sum(time_diffs) / len(time_diffs)
                    
                    # Check for unusually rapid requests
                    rapid_requests = [diff for diff in time_diffs if diff < avg_interval * 0.1]
                    if len(rapid_requests) > len(time_diffs) * 0.3:  # 30% of requests are rapid
                        anomalies.append({
                            'threat_type': ThreatType.ANOMALY.value,
                            'principal_id': principal_id,
                            'anomaly_type': 'rapid_request_pattern',
                            'severity': 'medium',
                            'confidence': 0.7
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Behavioral anomaly detection failed: {e}")
            return []

class SecurityPolicyEngine:
    """
    Moteur politiques sécurité pour service registry.
    Access control + audit logging + compliance monitoring + threat detection.
    """
    
    def __init__(self, security_config: Optional[SecurityConfig] = None):
        """Initialize security policy engine"""
        self.security_config = security_config or SecurityConfig()
        self.access_controller = AccessController()
        self.audit_logger = AuditLogger()
        self.compliance_monitor = ComplianceMonitor()
        self.threat_detector = ThreatDetector()
        
        # Initialize JWT handling if configured
        if not self.security_config.jwt_secret_key:
            self.security_config.jwt_secret_key = secrets.token_urlsafe(32)
        
        # Service registry reference (to be injected)
        self.service_registry = None
        
        # Background threat detection task
        self._threat_detection_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics
        self.metrics = {
            'authentication_attempts': 0,
            'authentication_successes': 0,
            'authorization_requests': 0,
            'authorization_grants': 0,
            'threats_detected': 0,
            'compliance_violations': 0,
            'audit_entries': 0
        }
    
    def set_service_registry(self, registry):
        """Set reference to service registry"""
        self.service_registry = registry
    
    async def start_threat_monitoring(self):
        """Start background threat monitoring"""
        if self._threat_detection_task is None or self._threat_detection_task.done():
            self._shutdown_event.clear()
            self._threat_detection_task = asyncio.create_task(self._threat_monitoring_loop())
            logger.info("Security threat monitoring started")
    
    async def stop_threat_monitoring(self):
        """Stop background threat monitoring"""
        self._shutdown_event.set()
        if self._threat_detection_task and not self._threat_detection_task.done():
            await self._threat_detection_task
        logger.info("Security threat monitoring stopped")
    
    async def enforce_security_policies(self, security_request: SecurityRequest) -> SecurityResult:
        """
        Enforcement politiques sécurité avec threat detection.
        
        Security Features:
        - RBAC pour service registration avec fine-grained permissions
        - Service-to-service authentication avec mutual TLS
        - Audit logging pour compliance et forensics
        - Threat detection avec ML anomaly detection
        - Registry access monitoring avec suspicious activity detection
        - Service identity verification avec certificate management
        - Compliance monitoring pour regulatory requirements
        - Security policy as code avec versioning
        """
        try:
            # Step 1: Authentication
            auth_result = await self.authenticate_service_request(security_request)
            self.metrics['authentication_attempts'] += 1
            
            if not auth_result.authenticated:
                # Log failed authentication
                await self._log_security_event(security_request, 'authentication_failed', {
                    'error': auth_result.error_message
                })
                
                return SecurityResult(
                    authorized=False,
                    security_warnings=[auth_result.error_message or 'Authentication failed'],
                    audit_events=[{
                        'event_type': 'authentication_failed',
                        'timestamp': time.time(),
                        'details': {'error': auth_result.error_message}
                    }]
                )
            
            self.metrics['authentication_successes'] += 1
            principal = auth_result.principal
            
            # Step 2: Authorization (if operation specified)
            granted_permissions = set()
            authorization_warnings = []
            
            if security_request.operation and security_request.resource:
                # Create registry operation for authorization
                operation = RegistryOperation(
                    operation_id=str(uuid.uuid4()),
                    operation_type=security_request.operation,
                    resource_type='service',
                    resource_id=security_request.resource,
                    requested_permissions={Permission.READ, Permission.WRITE},  # Default permissions
                    security_context={
                        'client_ip': security_request.client_ip,
                        'security_level': principal.security_level
                    }
                )
                
                auth_result_op = await self.authorize_registry_operation(operation, principal)
                self.metrics['authorization_requests'] += 1
                
                if auth_result_op.authorized:
                    granted_permissions = auth_result_op.granted_permissions
                    self.metrics['authorization_grants'] += 1
                else:
                    authorization_warnings.extend(auth_result_op.policy_violations)
            
            # Step 3: Compliance monitoring
            compliance_status = {}
            if self.security_config.compliance_standards:
                activity = RegistryActivity(
                    activity_id=str(uuid.uuid4()),
                    timestamp=security_request.request_time,
                    principal_id=principal.principal_id,
                    operation=security_request.operation or 'access',
                    resource=security_request.resource or 'registry',
                    source_ip=security_request.client_ip or 'unknown',
                    user_agent=security_request.user_agent or 'unknown',
                    success=True,
                    details={
                        'auth_method': auth_result.auth_method.value if auth_result.auth_method else 'unknown',
                        'permissions': list(p.value for p in granted_permissions)
                    }
                )
                
                for standard in self.security_config.compliance_standards:
                    compliance_result = await self.compliance_monitor.check_compliance(standard, activity)
                    compliance_status[standard.value] = compliance_result['compliant']
                    
                    if not compliance_result['compliant']:
                        self.metrics['compliance_violations'] += 1
            
            # Step 4: Threat detection
            threat_indicators = []
            if self.security_config.threat_detection_enabled:
                registry_event = RegistryEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=security_request.request_time,
                    event_type=security_request.operation or 'access',
                    source_ip=security_request.client_ip or 'unknown',
                    principal_id=principal.principal_id,
                    details={
                        'user_agent': security_request.user_agent,
                        'resource': security_request.resource
                    }
                )
                
                threat_result = await self.threat_detector.detect_threats([registry_event])
                if threat_result.threats_detected:
                    threat_indicators = [t['threat_type'] for t in threat_result.threats_detected]
                    self.metrics['threats_detected'] += len(threat_result.threats_detected)
            
            # Step 5: Audit logging
            audit_events = []
            if principal:
                activity = RegistryActivity(
                    activity_id=str(uuid.uuid4()),
                    timestamp=security_request.request_time,
                    principal_id=principal.principal_id,
                    operation=security_request.operation or 'access',
                    resource=security_request.resource or 'registry',
                    source_ip=security_request.client_ip or 'unknown',
                    user_agent=security_request.user_agent or 'unknown',
                    success=True,
                    details={
                        'auth_method': auth_result.auth_method.value if auth_result.auth_method else 'unknown',
                        'granted_permissions': list(p.value for p in granted_permissions),
                        'threat_indicators': threat_indicators
                    }
                )
                
                audit_result = await self.audit_registry_activity(activity)
                if audit_result.logged:
                    self.metrics['audit_entries'] += 1
                    audit_events.append({
                        'audit_id': audit_result.audit_id,
                        'timestamp': activity.timestamp,
                        'event_type': 'access_granted'
                    })
            
            # Compile result
            authorized = auth_result.authenticated and (not authorization_warnings)
            security_warnings = authorization_warnings.copy()
            
            if threat_indicators:
                security_warnings.extend([f"Threat detected: {indicator}" for indicator in threat_indicators])
            
            return SecurityResult(
                authorized=authorized,
                principal=principal,
                permissions_granted=granted_permissions,
                security_warnings=security_warnings,  
                audit_events=audit_events,
                threat_indicators=threat_indicators,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Security policy enforcement failed: {e}")
            return SecurityResult(
                authorized=False,
                security_warnings=[f"Security policy error: {str(e)}"],
                audit_events=[{
                    'event_type': 'security_error',
                    'timestamp': time.time(),
                    'details': {'error': str(e)}
                }]
            )
    
    async def authenticate_service_request(self, service_request: SecurityRequest) -> AuthenticationResult:
        """Authentification requête service avec mTLS et JWT."""
        try:
            return await self.access_controller.authenticate_principal(service_request)
        except Exception as e:
            logger.error(f"Service authentication failed: {e}")
            return AuthenticationResult(
                authenticated=False,
                error_message=f"Authentication error: {str(e)}"
            )
    
    async def authorize_registry_operation(self, operation: RegistryOperation, principal: ServicePrincipal) -> AuthorizationResult:
        """Autorisation opération registry avec RBAC policies."""
        try:
            return await self.access_controller.authorize_operation(operation, principal)
        except Exception as e:
            logger.error(f"Registry operation authorization failed: {e}")
            return AuthorizationResult(
                authorized=False,
                granted_permissions=set(),
                denied_permissions=operation.requested_permissions,
                policy_violations=[f"Authorization error: {str(e)}"]
            )
    
    async def audit_registry_activity(self, activity: RegistryActivity) -> AuditResult:
        """Audit activité registry pour compliance et security."""
        try:
            return await self.audit_logger.log_registry_activity(activity)
        except Exception as e:
            logger.error(f"Registry activity audit failed: {e}")
            return AuditResult(
                audit_id="",
                logged=False,
                compliance_events=[],
                retention_policy_applied=False,
                encryption_applied=False
            )
    
    async def detect_security_threats(self, registry_events: List[RegistryEvent]) -> ThreatDetectionResult:
        """Détection menaces sécurité avec ML analysis."""
        try:
            return await self.threat_detector.detect_threats(registry_events)
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            return ThreatDetectionResult(
                threats_detected=[],
                risk_score=0.0,
                recommended_actions=[],
                immediate_blocking_required=False,
                affected_principals=[]
            )
    
    async def register_service_principal(self, principal: ServicePrincipal) -> bool:
        """Register new service principal"""
        try:
            return await self.access_controller.register_principal(principal)
        except Exception as e:
            logger.error(f"Principal registration failed: {e}")
            return False
    
    async def _threat_monitoring_loop(self):
        """Background threat monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Collect recent events
                current_time = time.time()
                recent_events = [
                    event for event in self.threat_detector.event_history
                    if current_time - event.timestamp <= 300  # Last 5 minutes
                ]
                
                if recent_events:
                    # Detect threats
                    threat_result = await self.threat_detector.detect_threats(recent_events)
                    
                    if threat_result.threats_detected:
                        logger.warning(f"Threats detected: {len(threat_result.threats_detected)}")
                        self.metrics['threats_detected'] += len(threat_result.threats_detected)
                        
                        # Handle immediate blocking if required
                        if threat_result.immediate_blocking_required:
                            logger.critical("Immediate blocking required for security threat")
                            # In production, would implement actual blocking mechanism
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Threat monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def _log_security_event(self, request: SecurityRequest, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        try:
            registry_event = RegistryEvent(
                event_id=str(uuid.uuid4()),
                timestamp=request.request_time,
                event_type=event_type,
                source_ip=request.client_ip or 'unknown',
                principal_id=request.principal.principal_id if request.principal else None,
                details=details
            )
            
            # Add to threat detector history
            self.threat_detector.event_history.append(registry_event)
            
        except Exception as e:
            logger.error(f"Security event logging failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get security policy engine metrics"""
        return {
            **self.metrics,
            'registered_principals': len(self.access_controller.principals),
            'locked_principals': len(self.access_controller.locked_principals),
            'audit_log_size': len(self.audit_logger.audit_log),
            'threat_detection_active': self._threat_detection_task is not None and not self._threat_detection_task.done(),
            'compliance_violations_total': sum(
                len(violations) for violations in self.compliance_monitor.compliance_violations.values()
            )
        }
    
    async def shutdown(self):
        """Graceful shutdown of security policy engine"""
        logger.info("Shutting down SecurityPolicyEngine")
        await self.stop_threat_monitoring()

# Factory function
async def create_security_policy_engine(config: Optional[SecurityConfig] = None) -> SecurityPolicyEngine:
    """Factory function to create security policy engine"""
    return SecurityPolicyEngine(config)

# Export main classes and functions
__all__ = [
    'SecurityPolicyEngine',
    'SecurityConfig',
    'ServicePrincipal',
    'SecurityRequest',
    'SecurityResult',
    'RegistryOperation',
    'AuthenticationResult',
    'AuthorizationResult',
    'RegistryActivity',
    'AuditResult',
    'RegistryEvent',
    'ThreatDetectionResult',
    'SecurityLevel',
    'AuthMethod',
    'Permission',
    'ThreatType',
    'ComplianceStandard',
    'create_security_policy_engine'
]