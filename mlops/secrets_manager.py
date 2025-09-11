"""
Enterprise Secrets Manager for MLOps
Security + DevOps implementation with encrypted storage and access control
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import tempfile

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets"""
    API_KEY = "api_key"
    DATABASE_PASSWORD = "database_password"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    ACCESS_TOKEN = "access_token"
    ENCRYPTION_KEY = "encryption_key"
    CONNECTION_STRING = "connection_string"
    SERVICE_ACCOUNT = "service_account"
    WEBHOOK_SECRET = "webhook_secret"
    LICENSE_KEY = "license_key"


class AccessLevel(Enum):
    """Access levels for secrets"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


class RotationStatus(Enum):
    """Secret rotation status"""
    ACTIVE = "active"
    PENDING_ROTATION = "pending_rotation"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


@dataclass
class SecretMetadata:
    """Metadata for secrets"""
    secret_id: str
    name: str
    secret_type: SecretType
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None
    last_rotated: Optional[datetime] = None
    rotation_status: RotationStatus = RotationStatus.ACTIVE
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    environment: str = "production"
    service: str = ""
    owner: str = ""


@dataclass
class AccessPolicy:
    """Access policy for secrets"""
    policy_id: str
    name: str
    description: str
    principals: List[str]  # Users, services, or roles
    secret_patterns: List[str]  # Patterns of secret names/IDs
    access_level: AccessLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    ip_whitelist: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class AccessAuditLog:
    """Audit log entry for secret access"""
    log_id: str
    secret_id: str
    principal: str
    action: str  # read, write, delete, rotate
    success: bool
    timestamp: datetime
    ip_address: str = ""
    user_agent: str = ""
    request_id: str = ""
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionManager:
    """Handles encryption and decryption of secrets"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        if master_key:
            self.master_key = master_key
        else:
            self.master_key = self._generate_master_key()
        
        self.encryption_cache = {}
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master encryption key"""
        password = os.environ.get("AINFLUE_SECRET_KEY", "default-secret-key").encode()
        salt = os.environ.get("AINFLUE_SECRET_SALT", "default-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_secret(self, secret_value: str, secret_id: str) -> str:
        """Encrypt a secret value"""
        try:
            # Create encryption key derived from master key and secret ID
            derived_key = self._derive_key_for_secret(secret_id)
            fernet = Fernet(derived_key)
            
            # Encrypt the secret
            encrypted_value = fernet.encrypt(secret_value.encode())
            
            # Encode as base64 for storage
            return base64.b64encode(encrypted_value).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt secret {secret_id}: {e}")
            raise
    
    def decrypt_secret(self, encrypted_value: str, secret_id: str) -> str:
        """Decrypt a secret value"""
        try:
            # Create encryption key derived from master key and secret ID
            derived_key = self._derive_key_for_secret(secret_id)
            fernet = Fernet(derived_key)
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            
            # Decrypt the secret
            decrypted_value = fernet.decrypt(encrypted_bytes)
            
            return decrypted_value.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt secret {secret_id}: {e}")
            raise
    
    def _derive_key_for_secret(self, secret_id: str) -> bytes:
        """Derive encryption key for specific secret"""
        if secret_id in self.encryption_cache:
            return self.encryption_cache[secret_id]
        
        # Create unique salt for this secret
        secret_salt = hashlib.sha256(secret_id.encode()).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=secret_salt,
            iterations=50000,
        )
        
        derived_key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        
        # Cache the derived key
        self.encryption_cache[secret_id] = derived_key
        
        return derived_key
    
    def rotate_master_key(self, new_master_key: bytes) -> Dict[str, Any]:
        """Rotate the master encryption key"""
        try:
            old_master_key = self.master_key
            self.master_key = new_master_key
            
            # Clear encryption cache
            self.encryption_cache.clear()
            
            logger.info("Master key rotated successfully")
            
            return {
                "status": "success",
                "rotated_at": datetime.now().isoformat(),
                "requires_secret_re_encryption": True
            }
            
        except Exception as e:
            logger.error(f"Failed to rotate master key: {e}")
            raise


class AccessController:
    """Controls access to secrets based on policies"""
    
    def __init__(self):
        self.policies = {}
        self.audit_logs = []
    
    def add_policy(self, policy: AccessPolicy):
        """Add an access policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Added access policy: {policy.name}")
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove an access policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Removed access policy: {policy_id}")
            return True
        return False
    
    async def check_access(self, principal: str, secret_id: str, 
                          action: str, context: Dict[str, Any] = None) -> bool:
        """Check if principal has access to perform action on secret"""
        try:
            applicable_policies = self._find_applicable_policies(principal, secret_id)
            
            if not applicable_policies:
                logger.warning(f"No applicable policies found for {principal} accessing {secret_id}")
                return False
            
            for policy in applicable_policies:
                if await self._evaluate_policy(policy, principal, secret_id, action, context):
                    await self._log_access(secret_id, principal, action, True, context)
                    return True
            
            await self._log_access(secret_id, principal, action, False, context, "Access denied by policy")
            return False
            
        except Exception as e:
            logger.error(f"Access check failed for {principal} accessing {secret_id}: {e}")
            await self._log_access(secret_id, principal, action, False, context, str(e))
            return False
    
    def _find_applicable_policies(self, principal: str, secret_id: str) -> List[AccessPolicy]:
        """Find policies applicable to principal and secret"""
        applicable_policies = []
        
        for policy in self.policies.values():
            # Check if policy is currently valid
            now = datetime.now()
            if policy.valid_until and now > policy.valid_until:
                continue
            if now < policy.valid_from:
                continue
            
            # Check if principal matches
            principal_matches = any(
                self._matches_pattern(principal, pattern) 
                for pattern in policy.principals
            )
            
            if not principal_matches:
                continue
            
            # Check if secret matches
            secret_matches = any(
                self._matches_pattern(secret_id, pattern)
                for pattern in policy.secret_patterns
            )
            
            if secret_matches:
                applicable_policies.append(policy)
        
        return applicable_policies
    
    async def _evaluate_policy(self, policy: AccessPolicy, principal: str, 
                             secret_id: str, action: str, context: Dict[str, Any] = None) -> bool:
        """Evaluate if policy allows the requested access"""
        context = context or {}
        
        # Check access level
        if action == "read" and policy.access_level in [AccessLevel.READ_ONLY, AccessLevel.READ_WRITE, AccessLevel.ADMIN]:
            pass
        elif action in ["write", "update"] and policy.access_level in [AccessLevel.READ_WRITE, AccessLevel.ADMIN]:
            pass
        elif action in ["delete", "rotate"] and policy.access_level == AccessLevel.ADMIN:
            pass
        else:
            return False
        
        # Check IP whitelist
        if policy.ip_whitelist:
            client_ip = context.get("ip_address", "")
            if not any(self._ip_matches(client_ip, allowed_ip) for allowed_ip in policy.ip_whitelist):
                return False
        
        # Check time restrictions
        if policy.time_restrictions:
            if not await self._check_time_restrictions(policy.time_restrictions):
                return False
        
        # Check additional conditions
        for condition_key, condition_value in policy.conditions.items():
            if condition_key not in context or context[condition_key] != condition_value:
                return False
        
        return True
    
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(value, pattern)
    
    def _ip_matches(self, ip: str, allowed_ip: str) -> bool:
        """Check if IP matches allowed IP (supports CIDR)"""
        # Simplified IP matching - in production would use proper CIDR matching
        if "/" in allowed_ip:
            # CIDR notation
            network, prefix = allowed_ip.split("/")
            # Simplified check
            return ip.startswith(network.rsplit(".", 1)[0])
        else:
            return ip == allowed_ip
    
    async def _check_time_restrictions(self, restrictions: Dict[str, Any]) -> bool:
        """Check time-based restrictions"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        
        # Check allowed hours
        if "allowed_hours" in restrictions:
            start_hour, end_hour = restrictions["allowed_hours"]
            if not (start_hour <= current_time.hour <= end_hour):
                return False
        
        # Check allowed days
        if "allowed_days" in restrictions:
            allowed_days = restrictions["allowed_days"]
            if current_day not in allowed_days:
                return False
        
        return True
    
    async def _log_access(self, secret_id: str, principal: str, action: str, 
                         success: bool, context: Dict[str, Any] = None,
                         error_message: Optional[str] = None):
        """Log access attempt"""
        context = context or {}
        
        log_entry = AccessAuditLog(
            log_id=str(uuid.uuid4()),
            secret_id=secret_id,
            principal=principal,
            action=action,
            success=success,
            timestamp=datetime.now(),
            ip_address=context.get("ip_address", ""),
            user_agent=context.get("user_agent", ""),
            request_id=context.get("request_id", ""),
            error_message=error_message,
            metadata=context
        )
        
        self.audit_logs.append(log_entry)
        
        # In production, would also send to external audit system
        logger.info(f"Access logged: {principal} {action} {secret_id} - {'SUCCESS' if success else 'FAILED'}")
    
    def get_audit_logs(self, secret_id: Optional[str] = None, 
                      principal: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        filtered_logs = self.audit_logs
        
        if secret_id:
            filtered_logs = [log for log in filtered_logs if log.secret_id == secret_id]
        
        if principal:
            filtered_logs = [log for log in filtered_logs if log.principal == principal]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        return [
            {
                "log_id": log.log_id,
                "secret_id": log.secret_id,
                "principal": log.principal,
                "action": log.action,
                "success": log.success,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "error_message": log.error_message
            }
            for log in filtered_logs
        ]


class SecretRotator:
    """Handles automatic secret rotation"""
    
    def __init__(self, secrets_manager: 'SecretsManager'):
        self.secrets_manager = secrets_manager
        self.rotation_jobs = {}
    
    async def schedule_rotation(self, secret_id: str, 
                              rotation_function: Optional[Callable] = None):
        """Schedule automatic rotation for a secret"""
        try:
            metadata = await self.secrets_manager.get_secret_metadata(secret_id)
            if not metadata or not metadata.rotation_interval_days:
                logger.warning(f"Cannot schedule rotation for {secret_id}: no rotation interval set")
                return
            
            # Calculate next rotation time
            last_rotated = metadata.last_rotated or metadata.created_at
            next_rotation = last_rotated + timedelta(days=metadata.rotation_interval_days)
            
            # Schedule rotation job
            rotation_job = {
                "secret_id": secret_id,
                "next_rotation": next_rotation,
                "rotation_function": rotation_function,
                "scheduled_at": datetime.now()
            }
            
            self.rotation_jobs[secret_id] = rotation_job
            
            logger.info(f"Scheduled rotation for {secret_id} at {next_rotation}")
            
        except Exception as e:
            logger.error(f"Failed to schedule rotation for {secret_id}: {e}")
    
    async def rotate_secret(self, secret_id: str, 
                          rotation_function: Optional[Callable] = None) -> bool:
        """Rotate a secret immediately"""
        try:
            logger.info(f"Starting rotation for secret {secret_id}")
            
            # Update rotation status
            await self.secrets_manager.update_secret_metadata(
                secret_id, {"rotation_status": RotationStatus.ROTATING}
            )
            
            if rotation_function:
                # Use custom rotation function
                new_value = await rotation_function(secret_id)
            else:
                # Use default rotation based on secret type
                new_value = await self._generate_new_secret_value(secret_id)
            
            # Update the secret with new value
            await self.secrets_manager.update_secret(secret_id, new_value)
            
            # Update metadata
            await self.secrets_manager.update_secret_metadata(secret_id, {
                "rotation_status": RotationStatus.ACTIVE,
                "last_rotated": datetime.now()
            })
            
            logger.info(f"Successfully rotated secret {secret_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate secret {secret_id}: {e}")
            
            # Update status to indicate failure
            await self.secrets_manager.update_secret_metadata(
                secret_id, {"rotation_status": RotationStatus.ACTIVE}
            )
            
            return False
    
    async def _generate_new_secret_value(self, secret_id: str) -> str:
        """Generate new secret value based on secret type"""
        metadata = await self.secrets_manager.get_secret_metadata(secret_id)
        if not metadata:
            raise ValueError(f"Secret {secret_id} not found")
        
        secret_type = metadata.secret_type
        
        if secret_type == SecretType.API_KEY:
            return self._generate_api_key()
        elif secret_type == SecretType.DATABASE_PASSWORD:
            return self._generate_password()
        elif secret_type == SecretType.ACCESS_TOKEN:
            return self._generate_access_token()
        elif secret_type == SecretType.ENCRYPTION_KEY:
            return self._generate_encryption_key()
        elif secret_type == SecretType.WEBHOOK_SECRET:
            return self._generate_webhook_secret()
        else:
            # For other types, generate a secure random string
            return self._generate_secure_string(32)
    
    def _generate_api_key(self) -> str:
        """Generate a new API key"""
        return f"ak_{secrets.token_urlsafe(32)}"
    
    def _generate_password(self) -> str:
        """Generate a secure password"""
        import string
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(16))
    
    def _generate_access_token(self) -> str:
        """Generate a new access token"""
        return f"at_{secrets.token_urlsafe(48)}"
    
    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key"""
        return base64.b64encode(secrets.token_bytes(32)).decode()
    
    def _generate_webhook_secret(self) -> str:
        """Generate a new webhook secret"""
        return secrets.token_hex(32)
    
    def _generate_secure_string(self, length: int) -> str:
        """Generate a secure random string"""
        return secrets.token_urlsafe(length)
    
    async def check_pending_rotations(self):
        """Check for secrets that need rotation"""
        now = datetime.now()
        
        for secret_id, job in self.rotation_jobs.items():
            if now >= job["next_rotation"]:
                logger.info(f"Triggering scheduled rotation for {secret_id}")
                
                success = await self.rotate_secret(
                    secret_id, 
                    job.get("rotation_function")
                )
                
                if success:
                    # Reschedule next rotation
                    await self.schedule_rotation(secret_id, job.get("rotation_function"))


class SecretsManager:
    """Main secrets management system"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.encryption_manager = EncryptionManager(master_key)
        self.access_controller = AccessController()
        self.rotator = SecretRotator(self)
        
        # In-memory storage for demo (in production, would use secure database)
        self.secrets_store = {}
        self.metadata_store = {}
    
    async def create_secret(self, metadata: SecretMetadata, value: str,
                          creator_principal: str, context: Dict[str, Any] = None) -> str:
        """Create a new secret"""
        try:
            # Check access
            has_access = await self.access_controller.check_access(
                creator_principal, metadata.secret_id, "write", context
            )
            
            if not has_access:
                raise PermissionError(f"Access denied for {creator_principal}")
            
            # Check if secret already exists
            if metadata.secret_id in self.secrets_store:
                raise ValueError(f"Secret {metadata.secret_id} already exists")
            
            # Encrypt the secret value
            encrypted_value = self.encryption_manager.encrypt_secret(value, metadata.secret_id)
            
            # Store encrypted secret
            self.secrets_store[metadata.secret_id] = encrypted_value
            
            # Store metadata
            metadata.created_by = creator_principal
            metadata.created_at = datetime.now()
            metadata.updated_at = datetime.now()
            self.metadata_store[metadata.secret_id] = metadata
            
            # Schedule rotation if configured
            if metadata.rotation_interval_days:
                await self.rotator.schedule_rotation(metadata.secret_id)
            
            logger.info(f"Created secret {metadata.secret_id} by {creator_principal}")
            
            return metadata.secret_id
            
        except Exception as e:
            logger.error(f"Failed to create secret {metadata.secret_id}: {e}")
            raise
    
    async def get_secret(self, secret_id: str, principal: str,
                        context: Dict[str, Any] = None) -> Optional[str]:
        """Retrieve a secret value"""
        try:
            # Check access
            has_access = await self.access_controller.check_access(
                principal, secret_id, "read", context
            )
            
            if not has_access:
                raise PermissionError(f"Access denied for {principal}")
            
            # Check if secret exists
            if secret_id not in self.secrets_store:
                return None
            
            # Decrypt the secret
            encrypted_value = self.secrets_store[secret_id]
            decrypted_value = self.encryption_manager.decrypt_secret(encrypted_value, secret_id)
            
            # Update access metadata
            if secret_id in self.metadata_store:
                metadata = self.metadata_store[secret_id]
                metadata.access_count += 1
                metadata.last_accessed = datetime.now()
            
            logger.info(f"Secret {secret_id} accessed by {principal}")
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to get secret {secret_id}: {e}")
            raise
    
    async def update_secret(self, secret_id: str, new_value: str,
                          updater_principal: str = "system",
                          context: Dict[str, Any] = None) -> bool:
        """Update a secret value"""
        try:
            # Check access
            has_access = await self.access_controller.check_access(
                updater_principal, secret_id, "write", context
            )
            
            if not has_access:
                raise PermissionError(f"Access denied for {updater_principal}")
            
            # Check if secret exists
            if secret_id not in self.secrets_store:
                raise ValueError(f"Secret {secret_id} not found")
            
            # Encrypt new value
            encrypted_value = self.encryption_manager.encrypt_secret(new_value, secret_id)
            
            # Update secret
            self.secrets_store[secret_id] = encrypted_value
            
            # Update metadata
            if secret_id in self.metadata_store:
                metadata = self.metadata_store[secret_id]
                metadata.updated_at = datetime.now()
            
            logger.info(f"Secret {secret_id} updated by {updater_principal}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update secret {secret_id}: {e}")
            return False
    
    async def delete_secret(self, secret_id: str, deleter_principal: str,
                          context: Dict[str, Any] = None) -> bool:
        """Delete a secret"""
        try:
            # Check access
            has_access = await self.access_controller.check_access(
                deleter_principal, secret_id, "delete", context
            )
            
            if not has_access:
                raise PermissionError(f"Access denied for {deleter_principal}")
            
            # Remove secret and metadata
            if secret_id in self.secrets_store:
                del self.secrets_store[secret_id]
            
            if secret_id in self.metadata_store:
                del self.metadata_store[secret_id]
            
            # Remove from rotation jobs
            if secret_id in self.rotator.rotation_jobs:
                del self.rotator.rotation_jobs[secret_id]
            
            logger.info(f"Secret {secret_id} deleted by {deleter_principal}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {e}")
            return False
    
    async def get_secret_metadata(self, secret_id: str) -> Optional[SecretMetadata]:
        """Get secret metadata"""
        return self.metadata_store.get(secret_id)
    
    async def update_secret_metadata(self, secret_id: str, 
                                   updates: Dict[str, Any]) -> bool:
        """Update secret metadata"""
        if secret_id not in self.metadata_store:
            return False
        
        metadata = self.metadata_store[secret_id]
        
        for key, value in updates.items():
            if hasattr(metadata, key):
                if key == "rotation_status" and isinstance(value, RotationStatus):
                    setattr(metadata, key, value)
                elif key in ["expires_at", "last_rotated"] and isinstance(value, datetime):
                    setattr(metadata, key, value)
                else:
                    setattr(metadata, key, value)
        
        metadata.updated_at = datetime.now()
        
        return True
    
    def list_secrets(self, principal: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List secrets accessible to principal"""
        filters = filters or {}
        secret_list = []
        
        for secret_id, metadata in self.metadata_store.items():
            # Simple access check (in production, would be more sophisticated)
            try:
                # Filter by criteria
                if filters.get("secret_type") and metadata.secret_type != filters["secret_type"]:
                    continue
                
                if filters.get("environment") and metadata.environment != filters["environment"]:
                    continue
                
                if filters.get("service") and metadata.service != filters["service"]:
                    continue
                
                secret_info = {
                    "secret_id": metadata.secret_id,
                    "name": metadata.name,
                    "secret_type": metadata.secret_type.value,
                    "description": metadata.description,
                    "environment": metadata.environment,
                    "service": metadata.service,
                    "created_at": metadata.created_at.isoformat(),
                    "updated_at": metadata.updated_at.isoformat(),
                    "expires_at": metadata.expires_at.isoformat() if metadata.expires_at else None,
                    "rotation_status": metadata.rotation_status.value,
                    "access_count": metadata.access_count,
                    "last_accessed": metadata.last_accessed.isoformat() if metadata.last_accessed else None
                }
                
                secret_list.append(secret_info)
                
            except Exception as e:
                logger.warning(f"Error processing secret {secret_id}: {e}")
                continue
        
        return secret_list
    
    async def backup_secrets(self, backup_path: str, backup_key: bytes) -> str:
        """Create encrypted backup of all secrets"""
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "secrets": {},
                "metadata": {}
            }
            
            # Backup encrypted secrets (they're already encrypted)
            backup_data["secrets"] = self.secrets_store.copy()
            
            # Backup metadata
            for secret_id, metadata in self.metadata_store.items():
                backup_data["metadata"][secret_id] = {
                    "secret_id": metadata.secret_id,
                    "name": metadata.name,
                    "secret_type": metadata.secret_type.value,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "created_by": metadata.created_by,
                    "created_at": metadata.created_at.isoformat(),
                    "updated_at": metadata.updated_at.isoformat(),
                    "expires_at": metadata.expires_at.isoformat() if metadata.expires_at else None,
                    "rotation_interval_days": metadata.rotation_interval_days,
                    "last_rotated": metadata.last_rotated.isoformat() if metadata.last_rotated else None,
                    "rotation_status": metadata.rotation_status.value,
                    "environment": metadata.environment,
                    "service": metadata.service,
                    "owner": metadata.owner
                }
            
            # Encrypt backup
            backup_json = json.dumps(backup_data)
            backup_fernet = Fernet(backup_key)
            encrypted_backup = backup_fernet.encrypt(backup_json.encode())
            
            # Write to file
            with open(backup_path, 'wb') as f:
                f.write(encrypted_backup)
            
            logger.info(f"Secrets backup created: {backup_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    async def restore_secrets(self, backup_path: str, backup_key: bytes) -> int:
        """Restore secrets from encrypted backup"""
        try:
            # Read backup file
            with open(backup_path, 'rb') as f:
                encrypted_backup = f.read()
            
            # Decrypt backup
            backup_fernet = Fernet(backup_key)
            backup_json = backup_fernet.decrypt(encrypted_backup).decode()
            backup_data = json.loads(backup_json)
            
            restored_count = 0
            
            # Restore secrets
            for secret_id, encrypted_value in backup_data["secrets"].items():
                self.secrets_store[secret_id] = encrypted_value
                restored_count += 1
            
            # Restore metadata
            for secret_id, metadata_dict in backup_data["metadata"].items():
                metadata = SecretMetadata(
                    secret_id=metadata_dict["secret_id"],
                    name=metadata_dict["name"],
                    secret_type=SecretType(metadata_dict["secret_type"]),
                    description=metadata_dict["description"],
                    tags=metadata_dict["tags"],
                    created_by=metadata_dict["created_by"],
                    created_at=datetime.fromisoformat(metadata_dict["created_at"]),
                    updated_at=datetime.fromisoformat(metadata_dict["updated_at"]),
                    expires_at=datetime.fromisoformat(metadata_dict["expires_at"]) if metadata_dict["expires_at"] else None,
                    rotation_interval_days=metadata_dict["rotation_interval_days"],
                    last_rotated=datetime.fromisoformat(metadata_dict["last_rotated"]) if metadata_dict["last_rotated"] else None,
                    rotation_status=RotationStatus(metadata_dict["rotation_status"]),
                    environment=metadata_dict["environment"],
                    service=metadata_dict["service"],
                    owner=metadata_dict["owner"]
                )
                
                self.metadata_store[secret_id] = metadata
            
            logger.info(f"Restored {restored_count} secrets from backup")
            
            return restored_count
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise


# Factory function
def create_secrets_manager(master_key: Optional[bytes] = None) -> SecretsManager:
    """Create a configured secrets manager"""
    return SecretsManager(master_key)


# Export main classes
__all__ = [
    "SecretsManager",
    "SecretMetadata",
    "AccessPolicy",
    "SecretType",
    "AccessLevel",
    "RotationStatus",
    "create_secrets_manager"
]