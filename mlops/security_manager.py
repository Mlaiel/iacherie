"""
Enterprise Security Manager for MLOps
Sécurité + Lead Dev IA implementation with comprehensive security framework
"""

import asyncio
import logging
import hashlib
import secrets
import hmac
import base64
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import jwt
import bcrypt
from pathlib import Path
import re
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import warnings

# Optional security libraries
try:
    import cryptography
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    warnings.warn("cryptography not available. Some security features will be limited.")

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    warnings.warn("paramiko not available. SSH key management will be limited.")

logger = logging.getLogger(__name__)


class SecurityThreat(Enum):
    """Types of security threats"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MODEL_POISONING = "model_poisoning"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INJECTION_ATTACK = "injection_attack"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    MALWARE = "malware"
    PHISHING = "phishing"


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class UserRole(Enum):
    """User roles for RBAC"""
    GUEST = "guest"
    USER = "user"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ML_ENGINEER = "ml_engineer"
    DATA_SCIENTIST = "data_scientist"
    SECURITY_OFFICER = "security_officer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class PermissionType(Enum):
    """Types of permissions"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    AUDIT = "audit"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: SecurityThreat
    severity: str  # low, medium, high, critical
    source_ip: str
    user_id: Optional[str]
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class AccessLog:
    """Access log entry"""
    log_id: str
    user_id: str
    resource: str
    action: str
    permission_granted: bool
    timestamp: datetime = field(default_factory=datetime.now)
    source_ip: str = ""
    user_agent: str = ""
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"


@dataclass
class UserProfile:
    """User security profile"""
    user_id: str
    username: str
    email: str
    roles: List[UserRole]
    permissions: List[str]
    password_hash: str
    salt: str
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    session_tokens: List[str] = field(default_factory=list)
    api_keys: List[str] = field(default_factory=list)


class EnterpriseSecurityManager:
    """
    Comprehensive Enterprise Security Manager for MLOps
    Sécurité + Lead Dev IA implementation
    """
    
    def __init__(
        self,
        organization_name -> None: str,
        encryption_key -> None: Optional[str] = None,
        jwt_secret -> None: Optional[str] = None,
        session_timeout_minutes -> None: int = 480,  # 8 hours
        max_failed_attempts -> None: int = 5
    ) -> None:
        """Initialize Enterprise Security Manager
        
        Args:
            organization_name: Name of the organization
            encryption_key: Master encryption key (generated if None)
            jwt_secret: JWT signing secret (generated if None)
            session_timeout_minutes: Session timeout in minutes
            max_failed_attempts: Max failed login attempts before lockout
        """
        self.organization_name = organization_name
        self.session_timeout_minutes = session_timeout_minutes
        self.max_failed_attempts = max_failed_attempts
        
        # Encryption setup
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        
        # JWT setup
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(64)
        
        # Security storage
        self.users: Dict[str, UserProfile] = {}
        self.security_events: List[SecurityEvent] = []
        self.access_logs: List[AccessLog] = []
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.active_sessions: Dict[str, Dict] = {}
        
        # Threat detection
        self.threat_patterns: Dict[str, List[str]] = {}
        self.ip_whitelist: set = set()
        self.ip_blacklist: set = set()
        
        # Audit trail
        self.audit_enabled = True
        self.audit_logs: List[Dict] = []
        
        # Role-based access control
        self.rbac_rules: Dict[UserRole, List[PermissionType]] = {}
        
        logger.info(f"Initialized Enterprise Security Manager for {organization_name}")
        
        # Setup default configurations
        self._setup_default_security_policies()
        self._setup_default_rbac_rules()
        self._setup_threat_detection_patterns()

    def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key"""
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def _setup_default_security_policies(self) -> None:
        """Setup default security policies"""
        
        # Password policy
        password_policy = SecurityPolicy(
            policy_id="password_policy",
            name="Password Security Policy",
            description="Enforces strong password requirements",
            rules=[
                {"min_length": 12},
                {"require_uppercase": True},
                {"require_lowercase": True},
                {"require_numbers": True},
                {"require_special_chars": True},
                {"password_history": 10},
                {"max_age_days": 90}
            ]
        )
        self.security_policies[password_policy.policy_id] = password_policy
        
        # Session policy
        session_policy = SecurityPolicy(
            policy_id="session_policy",
            name="Session Management Policy",
            description="Manages user session security",
            rules=[
                {"session_timeout_minutes": self.session_timeout_minutes},
                {"max_concurrent_sessions": 3},
                {"require_mfa_for_admin": True},
                {"session_encryption": True}
            ]
        )
        self.security_policies[session_policy.policy_id] = session_policy
        
        # Data classification policy
        data_policy = SecurityPolicy(
            policy_id="data_classification_policy",
            name="Data Classification Policy",
            description="Defines data classification and handling rules",
            rules=[
                {"encrypt_confidential_data": True},
                {"audit_all_access": True},
                {"retention_period_days": 2555},  # 7 years
                {"backup_encryption": True}
            ]
        )
        self.security_policies[data_policy.policy_id] = data_policy
        
        # Model security policy
        model_policy = SecurityPolicy(
            policy_id="model_security_policy",
            name="ML Model Security Policy",
            description="Security rules for ML models and data",
            rules=[
                {"encrypt_model_artifacts": True},
                {"validate_training_data": True},
                {"monitor_model_drift": True},
                {"audit_model_access": True},
                {"adversarial_testing": True}
            ]
        )
        self.security_policies[model_policy.policy_id] = model_policy

    def _setup_default_rbac_rules(self) -> None:
        """Setup default Role-Based Access Control rules"""
        
        self.rbac_rules = {
            UserRole.GUEST: [PermissionType.READ],
            UserRole.USER: [PermissionType.READ, PermissionType.WRITE],
            UserRole.CREATOR: [
                PermissionType.READ, PermissionType.WRITE, 
                PermissionType.EXECUTE, PermissionType.MONITOR
            ],
            UserRole.MODERATOR: [
                PermissionType.READ, PermissionType.WRITE, 
                PermissionType.EXECUTE, PermissionType.DELETE, PermissionType.MONITOR
            ],
            UserRole.ML_ENGINEER: [
                PermissionType.READ, PermissionType.WRITE, 
                PermissionType.EXECUTE, PermissionType.DEPLOY, PermissionType.MONITOR
            ],
            UserRole.DATA_SCIENTIST: [
                PermissionType.READ, PermissionType.WRITE, 
                PermissionType.EXECUTE, PermissionType.MONITOR
            ],
            UserRole.SECURITY_OFFICER: [
                PermissionType.READ, PermissionType.AUDIT, 
                PermissionType.MONITOR, PermissionType.ADMIN
            ],
            UserRole.ADMIN: [
                PermissionType.READ, PermissionType.WRITE, PermissionType.EXECUTE,
                PermissionType.DELETE, PermissionType.DEPLOY, PermissionType.MONITOR,
                PermissionType.AUDIT, PermissionType.ADMIN
            ],
            UserRole.SUPER_ADMIN: list(PermissionType)  # All permissions
        }

    def _setup_threat_detection_patterns(self) -> None:
        """Setup threat detection patterns"""
        
        self.threat_patterns = {
            'sql_injection': [
                r"union\s+select", r"drop\s+table", r"insert\s+into",
                r"delete\s+from", r"exec\s*\(", r"script\s*:"
            ],
            'xss_attack': [
                r"<script", r"javascript:", r"onload\s*=", 
                r"onerror\s*=", r"<iframe", r"eval\s*\("
            ],
            'command_injection': [
                r";\s*rm\s", r";\s*wget\s", r";\s*curl\s",
                r"&&\s*rm\s", r"\|\s*nc\s", r">\s*/dev/null"
            ],
            'path_traversal': [
                r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%2e%2e%5c"
            ],
            'brute_force': [
                r"multiple failed login attempts",
                r"rapid successive requests",
                r"dictionary attack pattern"
            ]
        }

    # User Management Methods
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: List[UserRole],
        creator_info: Optional[Dict] = None
    ) -> str:
        """Create a new user with security validation
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            roles: List of user roles
            creator_info: Optional creator-specific information
            
        Returns:
            User ID
        """
        try:
            # Validate inputs
            if not self._validate_password(password):
                raise ValueError("Password does not meet security requirements")
            
            if not self._validate_email(email):
                raise ValueError("Invalid email format")
            
            if username in [user.username for user in self.users.values()]:
                raise ValueError("Username already exists")
            
            # Generate user ID and salt
            user_id = str(uuid.uuid4())
            salt = secrets.token_hex(16)
            
            # Hash password
            password_hash = self._hash_password(password, salt)
            
            # Create user profile
            user_profile = UserProfile(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles,
                permissions=self._calculate_permissions(roles),
                password_hash=password_hash,
                salt=salt
            )
            
            self.users[user_id] = user_profile
            
            # Log user creation
            await self._log_security_event(
                SecurityThreat.UNAUTHORIZED_ACCESS,
                "low",
                "system",
                user_id,
                "user_management",
                f"User {username} created",
                {"roles": [role.value for role in roles]}
            )
            
            # Audit log
            if self.audit_enabled:
                await self._audit_log("create_user", {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "roles": [role.value for role in roles],
                    "creator_info": creator_info
                })
            
            logger.info(f"Created user {username} with ID {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            raise

    async def authenticate_user(
        self,
        username: str,
        password: str,
        source_ip: str = "",
        user_agent: str = ""
    ) -> Optional[Dict]:
        """Authenticate user and create session
        
        Args:
            username: Username
            password: Password
            source_ip: Source IP address
            user_agent: User agent string
            
        Returns:
            Authentication result with session token or None
        """
        try:
            # Find user
            user = None
            for user_profile in self.users.values():
                if user_profile.username == username:
                    user = user_profile
                    break
            
            if not user:
                await self._log_security_event(
                    SecurityThreat.UNAUTHORIZED_ACCESS,
                    "medium",
                    source_ip,
                    None,
                    "authentication",
                    f"Failed login attempt for unknown user: {username}"
                )
                return None
            
            # Check if user is locked
            if user.locked_until and user.locked_until > datetime.now():
                await self._log_security_event(
                    SecurityThreat.UNAUTHORIZED_ACCESS,
                    "high",
                    source_ip,
                    user.user_id,
                    "authentication",
                    f"Login attempt for locked user: {username}"
                )
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash, user.salt):
                user.failed_login_attempts += 1
                
                # Lock user if max attempts reached
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now() + timedelta(hours=1)
                    await self._log_security_event(
                        SecurityThreat.UNAUTHORIZED_ACCESS,
                        "high",
                        source_ip,
                        user.user_id,
                        "authentication",
                        f"User {username} locked due to failed attempts"
                    )
                
                await self._log_security_event(
                    SecurityThreat.UNAUTHORIZED_ACCESS,
                    "medium",
                    source_ip,
                    user.user_id,
                    "authentication",
                    f"Failed login attempt for user: {username}"
                )
                return None
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            # Create session
            session_token = await self._create_session(user, source_ip, user_agent)
            
            # Log successful authentication
            await self._log_access(
                user.user_id,
                "authentication",
                "login",
                True,
                source_ip,
                user_agent,
                session_token
            )
            
            logger.info(f"User {username} authenticated successfully")
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "roles": [role.value for role in user.roles],
                "permissions": user.permissions,
                "session_token": session_token,
                "session_expires": (datetime.now() + timedelta(minutes=self.session_timeout_minutes)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            return None

    async def _create_session(
        self,
        user: UserProfile,
        source_ip: str,
        user_agent: str
    ) -> str:
        """Create a new user session"""
        try:
            session_id = secrets.token_urlsafe(32)
            
            # Create JWT token
            payload = {
                "user_id": user.user_id,
                "username": user.username,
                "roles": [role.value for role in user.roles],
                "session_id": session_id,
                "iat": datetime.now().timestamp(),
                "exp": (datetime.now() + timedelta(minutes=self.session_timeout_minutes)).timestamp()
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            
            # Store session
            self.active_sessions[session_id] = {
                "user_id": user.user_id,
                "token": token,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=self.session_timeout_minutes),
                "source_ip": source_ip,
                "user_agent": user_agent,
                "last_activity": datetime.now()
            }
            
            # Add to user's session tokens
            user.session_tokens.append(session_id)
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user.username}: {e}")
            raise

    async def validate_session(self, token: str) -> Optional[Dict]:
        """Validate session token
        
        Args:
            token: JWT session token
            
        Returns:
            User session information or None if invalid
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            session_id = payload.get("session_id")
            
            if not session_id or session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Check expiration
            if session["expires_at"] < datetime.now():
                await self._end_session(session_id)
                return None
            
            # Update last activity
            session["last_activity"] = datetime.now()
            
            return {
                "user_id": payload["user_id"],
                "username": payload["username"],
                "roles": payload["roles"],
                "session_id": session_id,
                "source_ip": session["source_ip"]
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None

    async def _end_session(self, session_id: str) -> None:
        """End a user session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                user_id = session["user_id"]
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                
                # Remove from user's session tokens
                if user_id in self.users:
                    user = self.users[user_id]
                    if session_id in user.session_tokens:
                        user.session_tokens.remove(session_id)
                
                logger.info(f"Ended session {session_id}")
                
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")

    # Access Control Methods
    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        permission_type: PermissionType,
        context: Optional[Dict] = None
    ) -> bool:
        """Check if user has permission for action
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            permission_type: Type of permission required
            context: Additional context for permission check
            
        Returns:
            True if permission granted, False otherwise
        """
        try:
            if user_id not in self.users:
                await self._log_access(user_id, resource, action, False)
                return False
            
            user = self.users[user_id]
            
            # Check role-based permissions
            user_permissions = set()
            for role in user.roles:
                user_permissions.update(self.rbac_rules.get(role, []))
            
            has_permission = permission_type in user_permissions
            
            # Additional context-based checks
            if context:
                has_permission = has_permission and await self._check_contextual_permissions(
                    user, resource, action, permission_type, context
                )
            
            # Log access attempt
            await self._log_access(user_id, resource, action, has_permission)
            
            if not has_permission:
                await self._log_security_event(
                    SecurityThreat.UNAUTHORIZED_ACCESS,
                    "medium",
                    "",
                    user_id,
                    resource,
                    f"Permission denied: {action} on {resource}",
                    {"permission_type": permission_type.value, "context": context}
                )
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Permission check error for user {user_id}: {e}")
            return False

    async def _check_contextual_permissions(
        self,
        user: UserProfile,
        resource: str,
        action: str,
        permission_type: PermissionType,
        context: Dict
    ) -> bool:
        """Check contextual permissions based on business rules"""
        try:
            # Creator-specific access controls for Ainflue platform
            if "creator_type" in context:
                creator_type = context["creator_type"]
                
                # Musicians can only access audio-related resources
                if creator_type == "musician" and not any(
                    keyword in resource.lower() 
                    for keyword in ["audio", "music", "song", "album", "streaming"]
                ):
                    if permission_type in [PermissionType.WRITE, PermissionType.DELETE]:
                        return False
                
                # Bloggers can only access text-related resources
                elif creator_type == "blogger" and not any(
                    keyword in resource.lower()
                    for keyword in ["article", "blog", "text", "content", "seo"]
                ):
                    if permission_type in [PermissionType.WRITE, PermissionType.DELETE]:
                        return False
                
                # Similar checks for other creator types...
            
            # Time-based access controls
            if "time_restriction" in context:
                current_hour = datetime.now().hour
                allowed_hours = context["time_restriction"]
                if current_hour not in allowed_hours:
                    return False
            
            # Location-based access controls
            if "location_restriction" in context:
                # Implementation would check user's location
                pass
            
            # Data sensitivity checks
            if "classification" in context:
                classification = SecurityLevel(context["classification"])
                
                # Only certain roles can access restricted data
                if classification in [SecurityLevel.RESTRICTED, SecurityLevel.TOP_SECRET]:
                    if not any(role in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.SECURITY_OFFICER] 
                              for role in user.roles):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Contextual permission check error: {e}")
            return False

    # Encryption and Data Protection
    def encrypt_data(self, data: Union[str, bytes], additional_context: Optional[str] = None) -> str:
        """Encrypt sensitive data
        
        Args:
            data: Data to encrypt
            additional_context: Additional context for encryption
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Add context if provided
            if additional_context:
                data = f"{additional_context}:{data.decode('utf-8')}".encode('utf-8')
            
            encrypted_data = self.cipher_suite.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt_data(self, encrypted_data: str, additional_context: Optional[str] = None) -> str:
        """Decrypt sensitive data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            additional_context: Additional context for decryption
            
        Returns:
            Decrypted data
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Remove context if provided
            if additional_context:
                data_str = decrypted_data.decode('utf-8')
                if data_str.startswith(f"{additional_context}:"):
                    return data_str[len(f"{additional_context}:"):]
                else:
                    raise ValueError("Context mismatch in decryption")
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    # Threat Detection and Response
    async def detect_threats(self, request_data: Dict) -> List[SecurityThreat]:
        """Detect potential security threats in request data
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            List of detected threats
        """
        try:
            detected_threats = []
            
            # Extract relevant fields for analysis
            content = str(request_data.get("content", ""))
            user_input = str(request_data.get("user_input", ""))
            headers = request_data.get("headers", {})
            
            # Check for injection attacks
            for attack_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE) or \
                       re.search(pattern, user_input, re.IGNORECASE):
                        
                        if "injection" in attack_type:
                            detected_threats.append(SecurityThreat.INJECTION_ATTACK)
                        elif "xss" in attack_type:
                            detected_threats.append(SecurityThreat.ADVERSARIAL_ATTACK)
                        
                        await self._log_security_event(
                            detected_threats[-1],
                            "high",
                            request_data.get("source_ip", ""),
                            request_data.get("user_id"),
                            "threat_detection",
                            f"Detected {attack_type} pattern: {pattern}",
                            {"content": content[:100], "pattern": pattern}
                        )
            
            # Check for suspicious behavior patterns
            source_ip = request_data.get("source_ip", "")
            if source_ip in self.ip_blacklist:
                detected_threats.append(SecurityThreat.UNAUTHORIZED_ACCESS)
            
            # Check for unusual request patterns
            user_agent = headers.get("User-Agent", "")
            if self._is_suspicious_user_agent(user_agent):
                detected_threats.append(SecurityThreat.MALWARE)
            
            # Check for model-specific threats
            if "model_input" in request_data:
                model_threats = await self._detect_model_threats(request_data["model_input"])
                detected_threats.extend(model_threats)
            
            return list(set(detected_threats))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Threat detection error: {e}")
            return []

    async def _detect_model_threats(self, model_input: Any) -> List[SecurityThreat]:
        """Detect ML model-specific threats"""
        try:
            threats = []
            
            # Check for adversarial examples
            if await self._is_adversarial_input(model_input):
                threats.append(SecurityThreat.ADVERSARIAL_ATTACK)
            
            # Check for model poisoning attempts
            if await self._is_poisoning_attempt(model_input):
                threats.append(SecurityThreat.MODEL_POISONING)
            
            return threats
            
        except Exception as e:
            logger.error(f"Model threat detection error: {e}")
            return []

    async def _is_adversarial_input(self, model_input: Any) -> bool:
        """Check if input appears to be adversarial"""
        # Implementation would use actual adversarial detection algorithms
        # For now, return a simple heuristic
        return False

    async def _is_poisoning_attempt(self, model_input: Any) -> bool:
        """Check if input appears to be a poisoning attempt"""
        # Implementation would analyze input for poisoning patterns
        return False

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent appears suspicious"""
        suspicious_patterns = [
            r"bot", r"crawler", r"spider", r"scraper",
            r"automated", r"python-requests", r"curl"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent.lower()):
                return True
        
        return False

    # Security Monitoring and Auditing
    async def _log_security_event(
        self,
        event_type: SecurityThreat,
        severity: str,
        source_ip: str,
        user_id: Optional[str],
        resource: str,
        action: str,
        details: Optional[Dict] = None
    ) -> None:
        """Log security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=severity,
                source_ip=source_ip,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details or {}
            )
            
            self.security_events.append(event)
            
            # Auto-response for critical events
            if severity == "critical":
                await self._auto_respond_to_threat(event)
            
            logger.warning(f"Security event: {event_type.value} - {action}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")

    async def _log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        permission_granted: bool,
        source_ip: str = "",
        user_agent: str = "",
        session_id: Optional[str] = None
    ) -> None:
        """Log access attempt"""
        try:
            access_log = AccessLog(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                resource=resource,
                action=action,
                permission_granted=permission_granted,
                source_ip=source_ip,
                user_agent=user_agent,
                session_id=session_id
            )
            
            self.access_logs.append(access_log)
            
        except Exception as e:
            logger.error(f"Error logging access: {e}")

    async def _audit_log(self, action: str, details: Dict) -> None:
        """Create audit log entry"""
        try:
            if not self.audit_enabled:
                return
            
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
                "organization": self.organization_name
            }
            
            self.audit_logs.append(audit_entry)
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")

    async def _auto_respond_to_threat(self, event: SecurityEvent) -> None:
        """Automatically respond to security threats"""
        try:
            if event.event_type == SecurityThreat.UNAUTHORIZED_ACCESS:
                # Block IP address
                if event.source_ip:
                    self.ip_blacklist.add(event.source_ip)
                    logger.warning(f"Auto-blocked IP {event.source_ip} due to security event")
            
            elif event.event_type == SecurityThreat.ADVERSARIAL_ATTACK:
                # Increase monitoring for user
                if event.user_id:
                    # Implementation would increase monitoring
                    pass
            
            elif event.event_type == SecurityThreat.MODEL_POISONING:
                # Alert security team immediately
                logger.critical(f"Model poisoning detected: {event.details}")
                # Implementation would send immediate alerts
            
        except Exception as e:
            logger.error(f"Auto-response error: {e}")

    # Compliance and Reporting
    def generate_security_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter events and logs within time period
            recent_events = [
                event for event in self.security_events
                if event.timestamp > cutoff_date
            ]
            
            recent_access_logs = [
                log for log in self.access_logs
                if log.timestamp > cutoff_date
            ]
            
            # Calculate statistics
            total_events = len(recent_events)
            events_by_type = {}
            events_by_severity = {}
            
            for event in recent_events:
                event_type = event.event_type.value
                severity = event.severity
                
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
            
            # Access statistics
            total_access_attempts = len(recent_access_logs)
            successful_access = sum(1 for log in recent_access_logs if log.permission_granted)
            failed_access = total_access_attempts - successful_access
            
            # Top threats
            top_threats = sorted(
                events_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # User activity
            user_activity = {}
            for log in recent_access_logs:
                user_id = log.user_id
                user_activity[user_id] = user_activity.get(user_id, 0) + 1
            
            most_active_users = sorted(
                user_activity.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            report = {
                "report_period_days": days,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_security_events": total_events,
                    "total_access_attempts": total_access_attempts,
                    "successful_access_rate": (successful_access / total_access_attempts * 100) if total_access_attempts > 0 else 0,
                    "active_users": len(user_activity),
                    "blocked_ips": len(self.ip_blacklist)
                },
                "events_by_type": events_by_type,
                "events_by_severity": events_by_severity,
                "top_threats": top_threats,
                "most_active_users": most_active_users,
                "security_policies": {
                    policy_id: {
                        "name": policy.name,
                        "enabled": policy.enabled,
                        "version": policy.version
                    }
                    for policy_id, policy in self.security_policies.items()
                },
                "compliance_status": {
                    "audit_enabled": self.audit_enabled,
                    "encryption_enabled": True,
                    "mfa_enforcement": self._check_mfa_enforcement(),
                    "password_policy_compliant": self._check_password_policy_compliance()
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {}

    def _check_mfa_enforcement(self) -> bool:
        """Check if MFA is properly enforced"""
        admin_users = [
            user for user in self.users.values()
            if any(role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] for role in user.roles)
        ]
        
        if not admin_users:
            return True
        
        return all(user.mfa_enabled for user in admin_users)

    def _check_password_policy_compliance(self) -> bool:
        """Check password policy compliance"""
        # Implementation would check if all users comply with password policy
        return True

    # Utility Methods
    def _validate_password(self, password: str) -> bool:
        """Validate password against security policy"""
        policy = self.security_policies.get("password_policy")
        if not policy:
            return True
        
        rules = {rule.get("min_length", 8): len(password) >= rule.get("min_length", 8) for rule in policy.rules}
        
        # Check minimum length
        if len(password) < 12:
            return False
        
        # Check character requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return bcrypt.hashpw(
            (password + salt).encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                (password + salt).encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False

    def _calculate_permissions(self, roles: List[UserRole]) -> List[str]:
        """Calculate user permissions based on roles"""
        permissions = set()
        for role in roles:
            permissions.update([perm.value for perm in self.rbac_rules.get(role, [])])
        return list(permissions)

    # API Methods for security management
    def add_security_policy(self, policy: SecurityPolicy) -> None:
        """Add or update security policy"""
        self.security_policies[policy.policy_id] = policy
        logger.info(f"Added security policy: {policy.name}")

    def get_security_events(self, hours: int = 24) -> List[Dict]:
        """Get recent security events"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            {
                "event_id": event.event_id,
                "type": event.event_type.value,
                "severity": event.severity,
                "timestamp": event.timestamp.isoformat(),
                "source_ip": event.source_ip,
                "user_id": event.user_id,
                "resource": event.resource,
                "action": event.action,
                "resolved": event.resolved
            }
            for event in self.security_events
            if event.timestamp > cutoff_time
        ]

    def add_ip_to_whitelist(self, ip_address: str) -> None:
        """Add IP address to whitelist"""
        self.ip_whitelist.add(ip_address)
        logger.info(f"Added IP {ip_address} to whitelist")

    def add_ip_to_blacklist(self, ip_address: str) -> None:
        """Add IP address to blacklist"""
        self.ip_blacklist.add(ip_address)
        logger.info(f"Added IP {ip_address} to blacklist")

    def remove_ip_from_blacklist(self, ip_address: str) -> None:
        """Remove IP address from blacklist"""
        self.ip_blacklist.discard(ip_address)
        logger.info(f"Removed IP {ip_address} from blacklist")

    async def force_logout_user(self, user_id: str) -> bool:
        """Force logout user by ending all sessions"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            sessions_to_end = user.session_tokens.copy()
            
            for session_id in sessions_to_end:
                await self._end_session(session_id)
            
            await self._log_security_event(
                SecurityThreat.UNAUTHORIZED_ACCESS,
                "medium",
                "system",
                user_id,
                "session_management",
                f"Force logout user {user.username}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error forcing logout for user {user_id}: {e}")
            return False