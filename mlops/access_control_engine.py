#!/usr/bin/env python3
"""
🔐 MLOps Access Control Engine - Enterprise RBAC System

Système de contrôle d'accès basé sur les rôles pour ressources ML enterprise.
Implémente RBAC granulaire avec audit trails complets et gouvernance des modèles.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: Security Expert + DBA + Backend Senior
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union
import logging
import json
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Permission(Enum):
    """Permissions granulaires MLOps"""
    # Model Permissions
    MODEL_READ = "model:read"
    MODEL_WRITE = "model:write"
    MODEL_DELETE = "model:delete"
    MODEL_DEPLOY = "model:deploy"
    MODEL_ROLLBACK = "model:rollback"
    
    # Pipeline Permissions
    PIPELINE_CREATE = "pipeline:create"
    PIPELINE_EXECUTE = "pipeline:execute"
    PIPELINE_MODIFY = "pipeline:modify"
    PIPELINE_DELETE = "pipeline:delete"
    
    # Data Permissions
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"
    
    # Infrastructure Permissions
    INFRA_MANAGE = "infra:manage"
    INFRA_MONITOR = "infra:monitor"
    INFRA_DEPLOY = "infra:deploy"
    
    # Admin Permissions
    ADMIN_USER_MANAGE = "admin:user_manage"
    ADMIN_ROLE_MANAGE = "admin:role_manage"
    ADMIN_AUDIT_VIEW = "admin:audit_view"
    ADMIN_SYSTEM_CONFIG = "admin:system_config"


class ResourceType(Enum):
    """Types de ressources MLOps"""
    MODEL = "model"
    PIPELINE = "pipeline"
    DATASET = "dataset"
    EXPERIMENT = "experiment"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    AUDIT_LOG = "audit_log"


@dataclass
class Role:
    """Définition d'un rôle RBAC"""
    name: str
    description: str
    permissions: Set[Permission]
    resource_restrictions: Dict[ResourceType, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """Utilisateur avec rôles et métadonnées"""
    user_id: str
    username: str
    email: str
    roles: Set[str]
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_access: Optional[datetime] = None
    is_active: bool = True
    session_token: Optional[str] = None


@dataclass
class AccessRequest:
    """Requête d'accès à une ressource"""
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission: Permission
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AccessAuditEntry:
    """Entrée d'audit pour traçabilité"""
    request_id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission: Permission
    decision: bool
    reason: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


class AccessControlEngine:
    """
    🔐 Engine de contrôle d'accès RBAC enterprise pour MLOps
    
    Fonctionnalités:
    - RBAC granulaire avec permissions fine-grained
    - Audit trails complets pour compliance
    - Session management sécurisé avec JWT
    - Resource-level access control
    - Dynamic permission evaluation
    - Multi-tenant support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.active_sessions: Dict[str, str] = {}  # token -> user_id
        self.audit_log: List[AccessAuditEntry] = []
        
        # Security configuration
        self.jwt_secret = self.config.get('jwt_secret', self._generate_secret())
        self.session_timeout = self.config.get('session_timeout', 3600)  # 1 hour
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize default roles
        self._initialize_default_roles()
        
        logger.info("🔐 Access Control Engine initialized with enterprise security")
    
    def _generate_secret(self) -> str:
        """Génère une clé secrète sécurisée"""
        return hashlib.sha256(f"{time.time()}{id(self)}".encode()).hexdigest()
    
    def _initialize_default_roles(self):
        """Initialize default enterprise roles"""
        # MLOps Engineer Role
        mlops_engineer = Role(
            name="mlops_engineer",
            description="MLOps Engineer with model and pipeline management",
            permissions={
                Permission.MODEL_READ, Permission.MODEL_WRITE, Permission.MODEL_DEPLOY,
                Permission.PIPELINE_CREATE, Permission.PIPELINE_EXECUTE, Permission.PIPELINE_MODIFY,
                Permission.DATA_READ, Permission.DATA_WRITE,
                Permission.INFRA_MONITOR
            }
        )
        
        # Data Scientist Role
        data_scientist = Role(
            name="data_scientist",
            description="Data Scientist with experiment and model development access",
            permissions={
                Permission.MODEL_READ, Permission.MODEL_WRITE,
                Permission.PIPELINE_CREATE, Permission.PIPELINE_EXECUTE,
                Permission.DATA_READ, Permission.DATA_WRITE
            }
        )
        
        # DevOps Engineer Role
        devops_engineer = Role(
            name="devops_engineer",
            description="DevOps Engineer with infrastructure management",
            permissions={
                Permission.MODEL_DEPLOY, Permission.MODEL_ROLLBACK,
                Permission.PIPELINE_EXECUTE,
                Permission.INFRA_MANAGE, Permission.INFRA_MONITOR, Permission.INFRA_DEPLOY
            }
        )
        
        # Security Auditor Role
        security_auditor = Role(
            name="security_auditor",
            description="Security Auditor with read-only audit access",
            permissions={
                Permission.MODEL_READ,
                Permission.DATA_READ,
                Permission.ADMIN_AUDIT_VIEW
            }
        )
        
        # Platform Admin Role
        platform_admin = Role(
            name="platform_admin",
            description="Platform Administrator with full access",
            permissions=set(Permission)  # All permissions
        )
        
        # Register default roles
        for role in [mlops_engineer, data_scientist, devops_engineer, security_auditor, platform_admin]:
            self.roles[role.name] = role
    
    async def create_user(self, username: str, email: str, roles: List[str], 
                         attributes: Optional[Dict[str, Any]] = None) -> str:
        """Crée un nouvel utilisateur avec rôles assignés"""
        user_id = hashlib.sha256(f"{username}{email}{time.time()}".encode()).hexdigest()[:16]
        
        # Validate roles exist
        invalid_roles = set(roles) - set(self.roles.keys())
        if invalid_roles:
            raise ValueError(f"Invalid roles: {invalid_roles}")
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=set(roles),
            attributes=attributes or {}
        )
        
        self.users[user_id] = user
        
        # Audit log entry
        await self._log_audit_entry(
            request_id=f"create_user_{user_id}",
            user_id="system",
            resource_type=ResourceType.AUDIT_LOG,
            resource_id=user_id,
            permission=Permission.ADMIN_USER_MANAGE,
            decision=True,
            reason=f"User {username} created with roles: {roles}",
            context={"operation": "create_user", "username": username, "email": email}
        )
        
        logger.info(f"✅ User created: {username} ({user_id}) with roles: {roles}")
        return user_id
    
    async def authenticate_user(self, username: str, password_hash: str) -> Optional[str]:
        """Authentifie un utilisateur et génère un token de session"""
        # Find user by username
        user = next((u for u in self.users.values() if u.username == username), None)
        if not user or not user.is_active:
            return None
        
        # In production, verify password hash against stored hash
        # For demo, we'll assume authentication is successful
        
        # Generate JWT token
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'roles': list(user.roles),
            'exp': datetime.utcnow() + timedelta(seconds=self.session_timeout),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Store active session
        self.active_sessions[token] = user.user_id
        user.session_token = token
        user.last_access = datetime.now()
        
        logger.info(f"🔑 User authenticated: {username}")
        return token
    
    async def validate_session(self, token: str) -> Optional[User]:
        """Valide un token de session"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if token not in self.active_sessions or self.active_sessions[token] != user_id:
                return None
            
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return None
            
            # Update last access
            user.last_access = datetime.now()
            return user
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"⚠️ Expired token: {token[:20]}...")
            self._invalidate_session(token)
            return None
        except jwt.InvalidTokenError:
            logger.warning(f"⚠️ Invalid token: {token[:20]}...")
            return None
    
    def _invalidate_session(self, token: str):
        """Invalide une session"""
        if token in self.active_sessions:
            user_id = self.active_sessions[token]
            user = self.users.get(user_id)
            if user:
                user.session_token = None
            del self.active_sessions[token]
    
    async def check_permission(self, token: str, resource_type: ResourceType, 
                              resource_id: str, permission: Permission,
                              context: Optional[Dict[str, Any]] = None) -> bool:
        """Vérifie si un utilisateur a la permission pour une ressource"""
        # Validate session
        user = await self.validate_session(token)
        if not user:
            await self._log_audit_entry(
                request_id=f"perm_check_{int(time.time())}",
                user_id="unknown",
                resource_type=resource_type,
                resource_id=resource_id,
                permission=permission,
                decision=False,
                reason="Invalid or expired session",
                context=context or {}
            )
            return False
        
        # Check user permissions through roles
        user_permissions = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                user_permissions.update(role.permissions)
        
        has_permission = permission in user_permissions
        
        # Additional context-based checks
        if has_permission:
            has_permission = await self._check_resource_restrictions(
                user, resource_type, resource_id, permission, context
            )
        
        # Log audit entry
        await self._log_audit_entry(
            request_id=f"perm_check_{int(time.time())}",
            user_id=user.user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission=permission,
            decision=has_permission,
            reason="Permission granted" if has_permission else "Permission denied",
            context=context or {}
        )
        
        return has_permission
    
    async def _check_resource_restrictions(self, user: User, resource_type: ResourceType,
                                         resource_id: str, permission: Permission,
                                         context: Optional[Dict[str, Any]]) -> bool:
        """Vérifie les restrictions au niveau des ressources"""
        # Check role-based resource restrictions
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role and resource_type in role.resource_restrictions:
                allowed_resources = role.resource_restrictions[resource_type]
                if allowed_resources and resource_id not in allowed_resources:
                    return False
        
        # Additional business logic checks based on context
        if context:
            # Example: Check creator type permissions for Ainflue business logic
            creator_type = context.get('creator_type')
            if creator_type and not await self._check_creator_permissions(user, creator_type):
                return False
        
        return True
    
    async def _check_creator_permissions(self, user: User, creator_type: str) -> bool:
        """Vérifie les permissions spécifiques aux créateurs Ainflue"""
        # Business logic: Different permissions for musicians, bloggers, etc.
        creator_permissions = user.attributes.get('creator_permissions', [])
        return creator_type in creator_permissions or 'all' in creator_permissions
    
    async def assign_role(self, admin_token: str, user_id: str, role_name: str) -> bool:
        """Assigne un rôle à un utilisateur (admin only)"""
        # Check admin permission
        has_permission = await self.check_permission(
            admin_token, ResourceType.AUDIT_LOG, user_id, Permission.ADMIN_ROLE_MANAGE
        )
        if not has_permission:
            return False
        
        user = self.users.get(user_id)
        role = self.roles.get(role_name)
        
        if not user or not role:
            return False
        
        user.roles.add(role_name)
        user.updated_at = datetime.now()
        
        logger.info(f"🎭 Role {role_name} assigned to user {user.username}")
        return True
    
    async def revoke_role(self, admin_token: str, user_id: str, role_name: str) -> bool:
        """Révoque un rôle d'un utilisateur (admin only)"""
        # Check admin permission
        has_permission = await self.check_permission(
            admin_token, ResourceType.AUDIT_LOG, user_id, Permission.ADMIN_ROLE_MANAGE
        )
        if not has_permission:
            return False
        
        user = self.users.get(user_id)
        if not user or role_name not in user.roles:
            return False
        
        user.roles.remove(role_name)
        user.updated_at = datetime.now()
        
        logger.info(f"❌ Role {role_name} revoked from user {user.username}")
        return True
    
    async def create_custom_role(self, admin_token: str, role_name: str, 
                               description: str, permissions: List[Permission],
                               resource_restrictions: Optional[Dict[ResourceType, List[str]]] = None) -> bool:
        """Crée un rôle personnalisé (admin only)"""
        # Check admin permission
        has_permission = await self.check_permission(
            admin_token, ResourceType.AUDIT_LOG, "roles", Permission.ADMIN_ROLE_MANAGE
        )
        if not has_permission:
            return False
        
        if role_name in self.roles:
            return False  # Role already exists
        
        role = Role(
            name=role_name,
            description=description,
            permissions=set(permissions),
            resource_restrictions=resource_restrictions or {}
        )
        
        self.roles[role_name] = role
        
        logger.info(f"🎭 Custom role created: {role_name}")
        return True
    
    async def _log_audit_entry(self, request_id: str, user_id: str, resource_type: ResourceType,
                              resource_id: str, permission: Permission, decision: bool,
                              reason: str, context: Dict[str, Any]):
        """Log audit entry for compliance"""
        audit_entry = AccessAuditEntry(
            request_id=request_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission=permission,
            decision=decision,
            reason=reason,
            timestamp=datetime.now(),
            context=context
        )
        
        self.audit_log.append(audit_entry)
        
        # In production, also write to persistent audit storage
        # Example: database, S3, CloudWatch, etc.
    
    async def get_audit_logs(self, admin_token: str, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None, user_id: Optional[str] = None,
                           resource_type: Optional[ResourceType] = None) -> List[AccessAuditEntry]:
        """Récupère les logs d'audit (admin only)"""
        # Check admin permission
        has_permission = await self.check_permission(
            admin_token, ResourceType.AUDIT_LOG, "audit", Permission.ADMIN_AUDIT_VIEW
        )
        if not has_permission:
            return []
        
        filtered_logs = self.audit_log
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log.resource_type == resource_type]
        
        return filtered_logs
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Récupère toutes les permissions d'un utilisateur"""
        user = self.users.get(user_id)
        if not user:
            return set()
        
        user_permissions = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                user_permissions.update(role.permissions)
        
        return user_permissions
    
    async def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        expired_tokens = []
        
        for token in self.active_sessions:
            try:
                jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self._invalidate_session(token)
        
        logger.info(f"🧹 Cleaned up {len(expired_tokens)} expired sessions")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de sécurité"""
        total_users = len(self.users)
        active_sessions = len(self.active_sessions)
        total_audit_entries = len(self.audit_log)
        
        # Calculate permission denials in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_denials = len([
            log for log in self.audit_log 
            if log.timestamp >= one_hour_ago and not log.decision
        ])
        
        return {
            "total_users": total_users,
            "active_sessions": active_sessions,
            "total_roles": len(self.roles),
            "total_audit_entries": total_audit_entries,
            "recent_permission_denials": recent_denials,
            "session_timeout_minutes": self.session_timeout // 60
        }


# Demo function for testing
async def demo_access_control():
    """Démo du système de contrôle d'accès"""
    print("🔐 MLOps Access Control Engine Demo")
    
    # Initialize access control
    access_control = AccessControlEngine()
    
    # Create users
    ml_engineer_id = await access_control.create_user(
        "alice_ml", "alice@ainflue.com", ["mlops_engineer"],
        attributes={"creator_permissions": ["musician", "blogger"]}
    )
    
    data_scientist_id = await access_control.create_user(
        "bob_ds", "bob@ainflue.com", ["data_scientist"]
    )
    
    admin_id = await access_control.create_user(
        "admin", "admin@ainflue.com", ["platform_admin"]
    )
    
    # Authenticate users
    ml_token = await access_control.authenticate_user("alice_ml", "hashed_password")
    admin_token = await access_control.authenticate_user("admin", "admin_password")
    
    # Test permissions
    can_deploy = await access_control.check_permission(
        ml_token, ResourceType.MODEL, "model_123", Permission.MODEL_DEPLOY
    )
    print(f"✅ ML Engineer can deploy model: {can_deploy}")
    
    can_manage_users = await access_control.check_permission(
        ml_token, ResourceType.AUDIT_LOG, "users", Permission.ADMIN_USER_MANAGE
    )
    print(f"❌ ML Engineer can manage users: {can_manage_users}")
    
    # Admin operations
    role_assigned = await access_control.assign_role(admin_token, ml_engineer_id, "devops_engineer")
    print(f"✅ Admin assigned DevOps role: {role_assigned}")
    
    # Get audit logs
    audit_logs = await access_control.get_audit_logs(admin_token)
    print(f"📋 Total audit entries: {len(audit_logs)}")
    
    # Security metrics
    metrics = access_control.get_security_metrics()
    print(f"📊 Security metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(demo_access_control())