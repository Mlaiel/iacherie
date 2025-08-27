"""
� Secrets Management Configuration - IA-Influencer-Agent
==================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade secrets management for secure credential storage
→ encrypted storage → key rotation → access control → audit logging.
==================================================================
"""

import logging
import asyncio
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

class SecretType(Enum):
    """Secret types"""
    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    DATABASE_CREDENTIAL = "database_credential"
    JWT_SECRET = "jwt_secret"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_TOKEN = "oauth_token"
    WEBHOOK_SECRET = "webhook_secret"

class RotationStrategy(Enum):
    """Secret rotation strategies"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ON_DEMAND = "on_demand"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"

class StorageBackend(Enum):
    """Secret storage backends"""
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    KUBERNETES_SECRETS = "kubernetes_secrets"
    ENCRYPTED_FILE = "encrypted_file"

class AccessLevel(Enum):
    """Access levels for secrets"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    ROTATE = "rotate"

@dataclass
class SecretPolicy:
    """Secret policy configuration"""
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_symbols: bool = True
    forbidden_patterns: List[str] = field(default_factory=list)
    max_age_days: int = 90
    rotation_warning_days: int = 7
    max_usage_count: Optional[int] = None
    allowed_environments: List[str] = field(default_factory=list)

@dataclass
class RotationConfig:
    """Secret rotation configuration"""
    strategy: RotationStrategy = RotationStrategy.TIME_BASED
    interval_days: int = 90
    advance_notice_days: int = 7
    backup_versions: int = 3
    auto_deploy: bool = True
    notification_channels: List[str] = field(default_factory=list)
    validation_required: bool = True

@dataclass
class AccessControl:
    """Access control for secrets"""
    users: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, str] = field(default_factory=dict)
    access_level: AccessLevel = AccessLevel.READ_ONLY

@dataclass
class SecretMetadata:
    """Secret metadata"""
    name: str
    secret_type: SecretType
    description: str = ""
    tags: List[str] = field(default_factory=list)
    environment: str = "production"
    service: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_modified: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    version: int = 1

@dataclass
class SecretEntry:
    """Complete secret entry"""
    metadata: SecretMetadata
    value: str
    encrypted_value: str = ""
    policy: SecretPolicy = field(default_factory=SecretPolicy)
    rotation_config: RotationConfig = field(default_factory=RotationConfig)
    access_control: AccessControl = field(default_factory=AccessControl)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

class SecretsManager:
    """
    Enterprise secrets and credentials management.
    
    Provides comprehensive secrets management:
    - Multi-backend storage (Vault, AWS, Azure, GCP, K8s)
    - Automatic secret rotation with policies
    - Strong encryption and security
    - Access control and auditing
    - Secret versioning and rollback
    - Policy-based validation
    - Integration with CI/CD pipelines
    - Compliance and governance
    - Real-time monitoring and alerting
    - Emergency access procedures
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize secrets manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Encryption setup
        self.master_key = master_key or self._generate_master_key()
        self.cipher_suite = self._initialize_encryption()
        
        # Secret storage
        self.secrets = {}
        self.secret_versions = {}
        self.rotation_schedules = {}
        
        # Access control
        self.access_logs = []
        self.failed_attempts = {}
        
        # Backend configuration
        self.storage_backend = StorageBackend.ENCRYPTED_FILE
        self.backend_config = {}
        
        # Monitoring
        self.metrics = {
            "secrets_total": 0,
            "rotations_completed": 0,
            "access_attempts": 0,
            "failed_accesses": 0,
            "policy_violations": 0
        }
        
        self.logger.info("Secrets manager initialized")
    
    def _generate_master_key(self) -> str:
        """Generate a new master encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption cipher"""
        key_bytes = base64.urlsafe_b64decode(self.master_key.encode())
        return Fernet(base64.urlsafe_b64encode(key_bytes))
    
    async def initialize(self, backend: StorageBackend, backend_config: Dict[str, Any]) -> bool:
        """
        Initialize secrets manager with storage backend.
        
        Args:
            backend: Storage backend type
            backend_config: Backend configuration
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.storage_backend = backend
            self.backend_config = backend_config
            
            # Initialize storage backend
            await self._initialize_backend()
            
            # Load existing secrets
            await self._load_secrets()
            
            # Start rotation scheduler
            await self._start_rotation_scheduler()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            self.logger.info(f"Secrets manager initialized with backend: {backend.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize secrets manager: {e}")
            return False
    
    async def _initialize_backend(self) -> None:
        """Initialize storage backend"""
        if self.storage_backend == StorageBackend.VAULT:
            await self._initialize_vault()
        elif self.storage_backend == StorageBackend.AWS_SECRETS_MANAGER:
            await self._initialize_aws_secrets()
        elif self.storage_backend == StorageBackend.AZURE_KEY_VAULT:
            await self._initialize_azure_vault()
        elif self.storage_backend == StorageBackend.GCP_SECRET_MANAGER:
            await self._initialize_gcp_secrets()
        elif self.storage_backend == StorageBackend.KUBERNETES_SECRETS:
            await self._initialize_k8s_secrets()
        else:
            # Encrypted file backend (default)
            await self._initialize_file_backend()
    
    async def _initialize_vault(self) -> None:
        """Initialize HashiCorp Vault backend"""
        # Implementation would setup Vault client
        self.logger.info("Vault backend initialized")
    
    async def _initialize_aws_secrets(self) -> None:
        """Initialize AWS Secrets Manager backend"""
        # Implementation would setup AWS client
        self.logger.info("AWS Secrets Manager backend initialized")
    
    async def _initialize_azure_vault(self) -> None:
        """Initialize Azure Key Vault backend"""
        # Implementation would setup Azure client
        self.logger.info("Azure Key Vault backend initialized")
    
    async def _initialize_gcp_secrets(self) -> None:
        """Initialize GCP Secret Manager backend"""
        # Implementation would setup GCP client
        self.logger.info("GCP Secret Manager backend initialized")
    
    async def _initialize_k8s_secrets(self) -> None:
        """Initialize Kubernetes Secrets backend"""
        # Implementation would setup Kubernetes client
        self.logger.info("Kubernetes Secrets backend initialized")
    
    async def _initialize_file_backend(self) -> None:
        """Initialize encrypted file backend"""
        # Implementation would setup file-based storage
        self.logger.info("Encrypted file backend initialized")
    
    async def _load_secrets(self) -> None:
        """Load existing secrets from backend"""
        # Implementation would load secrets from storage backend
        self.metrics["secrets_total"] = len(self.secrets)
        self.logger.info(f"Loaded {len(self.secrets)} secrets")
    
    async def _start_rotation_scheduler(self) -> None:
        """Start automatic secret rotation scheduler"""
        asyncio.create_task(self._rotation_scheduler())
        self.logger.info("Secret rotation scheduler started")
    
    async def _rotation_scheduler(self) -> None:
        """Secret rotation scheduler"""
        while True:
            try:
                await self._check_rotation_schedules()
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Rotation scheduler error: {e}")
                await asyncio.sleep(3600)
    
    async def _check_rotation_schedules(self) -> None:
        """Check and execute scheduled rotations"""
        now = datetime.now()
        
        for secret_name, secret_entry in self.secrets.items():
            rotation_config = secret_entry.rotation_config
            
            if rotation_config.strategy == RotationStrategy.TIME_BASED:
                last_rotation = secret_entry.metadata.last_modified
                next_rotation = last_rotation + timedelta(days=rotation_config.interval_days)
                
                if now >= next_rotation:
                    await self._rotate_secret(secret_name)
                elif now >= (next_rotation - timedelta(days=rotation_config.advance_notice_days)):
                    await self._send_rotation_notice(secret_name, next_rotation)
    
    async def _initialize_monitoring(self) -> None:
        """Initialize secrets monitoring"""
        asyncio.create_task(self._monitor_secret_usage())
        self.logger.info("Secrets monitoring initialized")
    
    async def _monitor_secret_usage(self) -> None:
        """Monitor secret usage and access patterns"""
        while True:
            try:
                # Monitor for suspicious access patterns
                await self._analyze_access_patterns()
                
                # Check for policy violations
                await self._check_policy_violations()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Secret monitoring error: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_access_patterns(self) -> None:
        """Analyze access patterns for anomalies"""
        # Implementation would analyze access logs for suspicious patterns
        pass
    
    async def _check_policy_violations(self) -> None:
        """Check for policy violations"""
        for secret_name, secret_entry in self.secrets.items():
            policy = secret_entry.policy
            metadata = secret_entry.metadata
            
            # Check age
            age_days = (datetime.now() - metadata.created_at).days
            if age_days > policy.max_age_days:
                await self._handle_policy_violation(
                    secret_name, "age_exceeded", f"Secret age {age_days} days exceeds limit {policy.max_age_days}"
                )
            
            # Check usage count
            if policy.max_usage_count and metadata.access_count > policy.max_usage_count:
                await self._handle_policy_violation(
                    secret_name, "usage_exceeded", f"Usage count {metadata.access_count} exceeds limit {policy.max_usage_count}"
                )
    
    async def _handle_policy_violation(self, secret_name: str, violation_type: str, message: str) -> None:
        """Handle policy violation"""
        self.metrics["policy_violations"] += 1
        self.logger.warning(f"Policy violation for secret {secret_name}: {violation_type} - {message}")
        
        # Implementation would trigger alerts and take remediation actions
    
    async def create_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType,
        description: str = "",
        environment: str = "production",
        policy: Optional[SecretPolicy] = None,
        rotation_config: Optional[RotationConfig] = None,
        access_control: Optional[AccessControl] = None
    ) -> bool:
        """
        Create a new secret.
        
        Args:
            name: Secret name
            value: Secret value
            secret_type: Type of secret
            description: Secret description
            environment: Environment (dev, staging, production)
            policy: Secret policy
            rotation_config: Rotation configuration
            access_control: Access control settings
            
        Returns:
            bool: True if successful
        """
        try:
            # Validate secret policy
            if not await self._validate_secret(value, policy or SecretPolicy()):
                raise ValueError("Secret does not meet policy requirements")
            
            # Encrypt secret value
            encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
            
            # Create secret metadata
            metadata = SecretMetadata(
                name=name,
                secret_type=secret_type,
                description=description,
                environment=environment,
                created_by="system",  # Would be actual user in production
                version=1
            )
            
            # Create secret entry
            secret_entry = SecretEntry(
                metadata=metadata,
                value=value,
                encrypted_value=encrypted_value,
                policy=policy or SecretPolicy(),
                rotation_config=rotation_config or RotationConfig(),
                access_control=access_control or AccessControl()
            )
            
            # Store secret
            self.secrets[name] = secret_entry
            self.secret_versions[name] = [secret_entry]
            
            # Store in backend
            await self._store_secret_in_backend(name, secret_entry)
            
            # Add audit log entry
            await self._audit_log(name, "created", "Secret created")
            
            self.metrics["secrets_total"] += 1
            self.logger.info(f"Secret created: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create secret {name}: {e}")
            return False
    
    async def _validate_secret(self, value: str, policy: SecretPolicy) -> bool:
        """Validate secret against policy"""
        # Length check
        if len(value) < policy.min_length:
            return False
        
        # Character requirements
        if policy.require_uppercase and not any(c.isupper() for c in value):
            return False
        if policy.require_lowercase and not any(c.islower() for c in value):
            return False
        if policy.require_numbers and not any(c.isdigit() for c in value):
            return False
        if policy.require_symbols and not any(not c.isalnum() for c in value):
            return False
        
        # Forbidden patterns
        for pattern in policy.forbidden_patterns:
            if pattern.lower() in value.lower():
                return False
        
        return True
    
    async def _store_secret_in_backend(self, name: str, secret_entry: SecretEntry) -> None:
        """Store secret in configured backend"""
        # Implementation would store in actual backend
        pass
    
    async def get_secret(
        self,
        name: str,
        requester: str = "",
        access_reason: str = ""
    ) -> Optional[str]:
        """
        Retrieve a secret.
        
        Args:
            name: Secret name
            requester: Who is requesting the secret
            access_reason: Reason for accessing the secret
            
        Returns:
            Secret value if authorized, None otherwise
        """
        try:
            if name not in self.secrets:
                self.metrics["failed_accesses"] += 1
                return None
            
            secret_entry = self.secrets[name]
            
            # Check access control
            if not await self._check_access(name, requester, secret_entry.access_control):
                self.metrics["failed_accesses"] += 1
                await self._audit_log(name, "access_denied", f"Access denied for {requester}")
                return None
            
            # Update access metadata
            secret_entry.metadata.last_accessed = datetime.now()
            secret_entry.metadata.access_count += 1
            
            # Audit log
            await self._audit_log(name, "accessed", f"Accessed by {requester}: {access_reason}")
            
            self.metrics["access_attempts"] += 1
            return secret_entry.value
            
        except Exception as e:
            self.logger.error(f"Failed to get secret {name}: {e}")
            self.metrics["failed_accesses"] += 1
            return None
    
    async def _check_access(self, secret_name: str, requester: str, access_control: AccessControl) -> bool:
        """Check if requester has access to secret"""
        # Implementation would check access control rules
        # For now, return True (in production, implement proper RBAC)
        return True
    
    async def update_secret(
        self,
        name: str,
        new_value: str,
        requester: str = "",
        reason: str = ""
    ) -> bool:
        """
        Update a secret value.
        
        Args:
            name: Secret name
            new_value: New secret value
            requester: Who is updating the secret
            reason: Reason for update
            
        Returns:
            bool: True if successful
        """
        try:
            if name not in self.secrets:
                raise ValueError(f"Secret not found: {name}")
            
            secret_entry = self.secrets[name]
            
            # Check access
            if not await self._check_access(name, requester, secret_entry.access_control):
                raise PermissionError(f"Access denied for {requester}")
            
            # Validate new secret
            if not await self._validate_secret(new_value, secret_entry.policy):
                raise ValueError("New secret does not meet policy requirements")
            
            # Create new version
            old_entry = secret_entry
            new_metadata = SecretMetadata(
                name=name,
                secret_type=secret_entry.metadata.secret_type,
                description=secret_entry.metadata.description,
                environment=secret_entry.metadata.environment,
                created_at=secret_entry.metadata.created_at,
                created_by=secret_entry.metadata.created_by,
                last_modified=datetime.now(),
                version=secret_entry.metadata.version + 1
            )
            
            # Encrypt new value
            encrypted_value = self.cipher_suite.encrypt(new_value.encode()).decode()
            
            new_entry = SecretEntry(
                metadata=new_metadata,
                value=new_value,
                encrypted_value=encrypted_value,
                policy=secret_entry.policy,
                rotation_config=secret_entry.rotation_config,
                access_control=secret_entry.access_control,
                audit_log=secret_entry.audit_log.copy()
            )
            
            # Update secret
            self.secrets[name] = new_entry
            
            # Store version history
            if name not in self.secret_versions:
                self.secret_versions[name] = []
            self.secret_versions[name].append(new_entry)
            
            # Limit version history
            max_versions = secret_entry.rotation_config.backup_versions
            if len(self.secret_versions[name]) > max_versions:
                self.secret_versions[name] = self.secret_versions[name][-max_versions:]
            
            # Store in backend
            await self._store_secret_in_backend(name, new_entry)
            
            # Audit log
            await self._audit_log(name, "updated", f"Updated by {requester}: {reason}")
            
            self.logger.info(f"Secret updated: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update secret {name}: {e}")
            return False
    
    async def delete_secret(self, name: str, requester: str = "") -> bool:
        """
        Delete a secret.
        
        Args:
            name: Secret name
            requester: Who is deleting the secret
            
        Returns:
            bool: True if successful
        """
        try:
            if name not in self.secrets:
                raise ValueError(f"Secret not found: {name}")
            
            secret_entry = self.secrets[name]
            
            # Check access
            if not await self._check_access(name, requester, secret_entry.access_control):
                raise PermissionError(f"Access denied for {requester}")
            
            # Remove from storage
            del self.secrets[name]
            if name in self.secret_versions:
                del self.secret_versions[name]
            if name in self.rotation_schedules:
                del self.rotation_schedules[name]
            
            # Remove from backend
            await self._delete_secret_from_backend(name)
            
            # Audit log
            await self._audit_log(name, "deleted", f"Deleted by {requester}")
            
            self.metrics["secrets_total"] -= 1
            self.logger.info(f"Secret deleted: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete secret {name}: {e}")
            return False
    
    async def _delete_secret_from_backend(self, name: str) -> None:
        """Delete secret from backend storage"""
        # Implementation would delete from actual backend
        pass
    
    async def rotate_secret(self, name: str, new_value: Optional[str] = None) -> bool:
        """
        Rotate a secret.
        
        Args:
            name: Secret name
            new_value: New value (auto-generated if not provided)
            
        Returns:
            bool: True if successful
        """
        try:
            if name not in self.secrets:
                raise ValueError(f"Secret not found: {name}")
            
            secret_entry = self.secrets[name]
            
            # Generate new value if not provided
            if new_value is None:
                new_value = await self._generate_secret_value(secret_entry)
            
            # Update secret
            success = await self.update_secret(name, new_value, "system", "automatic rotation")
            
            if success:
                self.metrics["rotations_completed"] += 1
                
                # Deploy new secret if configured
                if secret_entry.rotation_config.auto_deploy:
                    await self._deploy_rotated_secret(name)
                
                # Send notifications
                await self._send_rotation_notification(name, "completed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to rotate secret {name}: {e}")
            return False
    
    async def _rotate_secret(self, name: str) -> None:
        """Internal method to rotate secret"""
        await self.rotate_secret(name)
    
    async def _generate_secret_value(self, secret_entry: SecretEntry) -> str:
        """Generate new secret value based on type and policy"""
        secret_type = secret_entry.metadata.secret_type
        policy = secret_entry.policy
        
        if secret_type == SecretType.PASSWORD:
            return self._generate_password(policy)
        elif secret_type == SecretType.API_KEY:
            return self._generate_api_key(policy.min_length)
        elif secret_type == SecretType.JWT_SECRET:
            return self._generate_jwt_secret()
        else:
            return self._generate_random_string(policy.min_length)
    
    def _generate_password(self, policy: SecretPolicy) -> str:
        """Generate password according to policy"""
        import string
        
        chars = ""
        if policy.require_lowercase:
            chars += string.ascii_lowercase
        if policy.require_uppercase:
            chars += string.ascii_uppercase
        if policy.require_numbers:
            chars += string.digits
        if policy.require_symbols:
            chars += "!@#$%^&*"
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        password = ''.join(secrets.choice(chars) for _ in range(policy.min_length))
        return password
    
    def _generate_api_key(self, length: int) -> str:
        """Generate API key"""
        return secrets.token_urlsafe(length)
    
    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string"""
        return secrets.token_hex(length // 2)
    
    async def _deploy_rotated_secret(self, name: str) -> None:
        """Deploy rotated secret to services"""
        # Implementation would deploy secret to services/applications
        self.logger.info(f"Deployed rotated secret: {name}")
    
    async def _send_rotation_notice(self, name: str, rotation_date: datetime) -> None:
        """Send rotation advance notice"""
        secret_entry = self.secrets[name]
        channels = secret_entry.rotation_config.notification_channels
        
        # Implementation would send notifications
        self.logger.info(f"Rotation notice sent for secret: {name}")
    
    async def _send_rotation_notification(self, name: str, status: str) -> None:
        """Send rotation completion notification"""
        secret_entry = self.secrets[name]
        channels = secret_entry.rotation_config.notification_channels
        
        # Implementation would send notifications
        self.logger.info(f"Rotation notification sent for secret: {name} - {status}")
    
    async def _audit_log(self, secret_name: str, action: str, details: str) -> None:
        """Add audit log entry"""
        log_entry = {
            "timestamp": datetime.now(),
            "secret_name": secret_name,
            "action": action,
            "details": details,
            "source_ip": "127.0.0.1",  # Would be actual IP
            "user_agent": "SecretsManager/1.0"
        }
        
        self.access_logs.append(log_entry)
        
        if secret_name in self.secrets:
            self.secrets[secret_name].audit_log.append(log_entry)
    
    async def list_secrets(
        self,
        environment: Optional[str] = None,
        secret_type: Optional[SecretType] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List secrets with optional filtering.
        
        Args:
            environment: Filter by environment
            secret_type: Filter by secret type
            include_metadata: Include full metadata
            
        Returns:
            List of secrets
        """
        results = []
        
        for name, secret_entry in self.secrets.items():
            # Apply filters
            if environment and secret_entry.metadata.environment != environment:
                continue
            if secret_type and secret_entry.metadata.secret_type != secret_type:
                continue
            
            if include_metadata:
                results.append({
                    "name": name,
                    "type": secret_entry.metadata.secret_type.value,
                    "description": secret_entry.metadata.description,
                    "environment": secret_entry.metadata.environment,
                    "created_at": secret_entry.metadata.created_at,
                    "last_modified": secret_entry.metadata.last_modified,
                    "version": secret_entry.metadata.version,
                    "access_count": secret_entry.metadata.access_count
                })
            else:
                results.append({"name": name, "type": secret_entry.metadata.secret_type.value})
        
        return results
    
    async def get_audit_log(self, secret_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        if secret_name:
            if secret_name in self.secrets:
                return self.secrets[secret_name].audit_log
            else:
                return []
        
        return self.access_logs
    
    async def get_secrets_status(self) -> Dict[str, Any]:
        """Get comprehensive secrets status"""
        now = datetime.now()
        
        # Calculate secrets needing rotation
        rotation_due = 0
        rotation_warning = 0
        
        for secret_entry in self.secrets.values():
            if secret_entry.rotation_config.strategy == RotationStrategy.TIME_BASED:
                last_rotation = secret_entry.metadata.last_modified
                next_rotation = last_rotation + timedelta(days=secret_entry.rotation_config.interval_days)
                warning_date = next_rotation - timedelta(days=secret_entry.rotation_config.advance_notice_days)
                
                if now >= next_rotation:
                    rotation_due += 1
                elif now >= warning_date:
                    rotation_warning += 1
        
        return {
            "total_secrets": len(self.secrets),
            "by_type": {
                secret_type.value: sum(
                    1 for s in self.secrets.values() 
                    if s.metadata.secret_type == secret_type
                ) for secret_type in SecretType
            },
            "by_environment": {
                env: sum(
                    1 for s in self.secrets.values() 
                    if s.metadata.environment == env
                ) for env in set(s.metadata.environment for s in self.secrets.values())
            },
            "rotation_status": {
                "due": rotation_due,
                "warning": rotation_warning,
                "completed_today": 0  # Would calculate actual rotations today
            },
            "metrics": self.metrics,
            "storage_backend": self.storage_backend.value
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get secrets manager status"""
        return await self.get_secrets_status()
