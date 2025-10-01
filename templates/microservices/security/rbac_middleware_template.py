"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

RBAC Middleware Template for iacherie Creator Economy Platform
Role-Based Access Control middleware with fine-grained permissions and audit
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Union, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import re

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class Permission(str, Enum):
    # Creator permissions
    CREATOR_READ = "creator:read"
    CREATOR_WRITE = "creator:write"
    CREATOR_DELETE = "creator:delete"
    CREATOR_MANAGE = "creator:manage"
    
    # Content permissions
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_MODERATE = "content:moderate"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_MANAGE = "analytics:manage"
    
    # Monetization permissions
    MONETIZATION_READ = "monetization:read"
    MONETIZATION_WRITE = "monetization:write"
    MONETIZATION_PAYOUT = "monetization:payout"
    
    # Collaboration permissions
    COLLABORATION_READ = "collaboration:read"
    COLLABORATION_WRITE = "collaboration:write"
    COLLABORATION_MANAGE = "collaboration:manage"
    
    # Admin permissions
    USER_MANAGE = "user:manage"
    SYSTEM_ADMIN = "system:admin"
    AUDIT_READ = "audit:read"


class Role(str, Enum):
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    CONTENT_MODERATOR = "content_moderator"
    ANALYTICS_VIEWER = "analytics_viewer"
    FINANCE_MANAGER = "finance_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class ResourceType(str, Enum):
    CREATOR = "creator"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    USER = "user"
    SYSTEM = "system"


@dataclass
class RBACConfig:
    """Configuration RBAC"""
    enable_resource_ownership: bool = True
    enable_dynamic_permissions: bool = True
    enable_permission_caching: bool = True
    cache_ttl_seconds: int = 300
    audit_enabled: bool = True
    strict_mode: bool = True  # Deny by default
    permission_inheritance: bool = True


class PermissionRule(BaseModel):
    """Règle de permission"""
    permission: Permission
    resource_type: Optional[ResourceType] = None
    resource_pattern: Optional[str] = None  # Regex pattern for resource ID
    conditions: Dict[str, Any] = {}
    deny: bool = False  # Explicit deny rule


class RoleDefinition(BaseModel):
    """Définition de rôle"""
    name: Role
    description: str
    permissions: List[PermissionRule]
    parent_roles: List[Role] = []
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserContext(BaseModel):
    """Contexte utilisateur pour autorisation"""
    user_id: str
    role: Role
    creator_id: Optional[str] = None
    organization_id: Optional[str] = None
    additional_permissions: List[Permission] = []
    resource_ownership: Dict[str, List[str]] = {}  # resource_type -> [resource_ids]
    session_data: Dict[str, Any] = {}


class AuthorizationRequest(BaseModel):
    """Demande d'autorisation"""
    user_context: UserContext
    permission: Permission
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    context: Dict[str, Any] = {}


class AuthorizationResult(BaseModel):
    """Résultat d'autorisation"""
    granted: bool
    reason: str
    matched_rules: List[str] = []
    user_id: str
    permission: Permission
    timestamp: datetime
    decision_time_ms: float


class RBACMiddlewareTemplate:
    """
    Template middleware RBAC enterprise pour iacherie Creator Economy
    
    Fonctionnalités:
    - Contrôle d'accès basé sur les rôles
    - Permissions granulaires par ressource
    - Ownership-based access control
    - Dynamic permissions
    - Permission inheritance
    - Caching intelligent
    - Audit complet
    - Performance monitoring
    """
    
    def __init__(self, config: RBACConfig = None):
        self.config = config or RBACConfig()
        self.security = HTTPBearer()
        
        # Redis pour cache permissions
        self.redis = Redis(host='localhost', port=6379, db=2, decode_responses=True)
        
        # Storage des rôles et règles
        self.role_definitions: Dict[Role, RoleDefinition] = {}
        self.permission_cache: Dict[str, bool] = {}
        
        # Métriques Prometheus
        self.authorization_requests = Counter('rbac_authorization_requests_total', ['permission', 'resource_type', 'granted'])
        self.authorization_duration = Histogram('rbac_authorization_duration_seconds', ['permission'])
        self.cache_hits = Counter('rbac_cache_hits_total')
        self.cache_misses = Counter('rbac_cache_misses_total')
        self.active_sessions = Gauge('rbac_active_sessions_total', ['role'])
        
        # Setup
        self._setup_default_roles()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_default_roles(self):
        """Configuration des rôles par défaut"""
        
        # Creator role
        creator_permissions = [
            PermissionRule(permission=Permission.CREATOR_READ, resource_type=ResourceType.CREATOR),
            PermissionRule(permission=Permission.CREATOR_WRITE, resource_type=ResourceType.CREATOR),
            PermissionRule(permission=Permission.CONTENT_READ, resource_type=ResourceType.CONTENT),
            PermissionRule(permission=Permission.CONTENT_WRITE, resource_type=ResourceType.CONTENT),
            PermissionRule(permission=Permission.CONTENT_PUBLISH, resource_type=ResourceType.CONTENT),
            PermissionRule(permission=Permission.ANALYTICS_READ, resource_type=ResourceType.ANALYTICS),
            PermissionRule(permission=Permission.MONETIZATION_READ, resource_type=ResourceType.MONETIZATION),
            PermissionRule(permission=Permission.COLLABORATION_READ, resource_type=ResourceType.COLLABORATION),
            PermissionRule(permission=Permission.COLLABORATION_WRITE, resource_type=ResourceType.COLLABORATION),
        ]
        
        self.role_definitions[Role.CREATOR] = RoleDefinition(
            name=Role.CREATOR,
            description="Content creator with full control over own content",
            permissions=creator_permissions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Collaborator role
        collaborator_permissions = [
            PermissionRule(permission=Permission.CONTENT_READ, resource_type=ResourceType.CONTENT),
            PermissionRule(permission=Permission.CONTENT_WRITE, resource_type=ResourceType.CONTENT),
            PermissionRule(permission=Permission.COLLABORATION_READ, resource_type=ResourceType.COLLABORATION),
            PermissionRule(permission=Permission.COLLABORATION_WRITE, resource_type=ResourceType.COLLABORATION),
        ]
        
        self.role_definitions[Role.COLLABORATOR] = RoleDefinition(
            name=Role.COLLABORATOR,
            description="Collaborator with limited content access",
            permissions=collaborator_permissions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Admin role
        admin_permissions = [
            PermissionRule(permission=Permission.USER_MANAGE),
            PermissionRule(permission=Permission.CONTENT_MODERATE),
            PermissionRule(permission=Permission.ANALYTICS_MANAGE),
            PermissionRule(permission=Permission.AUDIT_READ),
        ]
        
        self.role_definitions[Role.ADMIN] = RoleDefinition(
            name=Role.ADMIN,
            description="Administrator with management capabilities",
            permissions=admin_permissions,
            parent_roles=[Role.CREATOR, Role.COLLABORATOR],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Super Admin role
        super_admin_permissions = [
            PermissionRule(permission=Permission.SYSTEM_ADMIN),
        ]
        
        self.role_definitions[Role.SUPER_ADMIN] = RoleDefinition(
            name=Role.SUPER_ADMIN,
            description="Super administrator with all permissions",
            permissions=super_admin_permissions,
            parent_roles=[Role.ADMIN],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def authorize(
        self, 
        permission: Permission,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        user_context: Optional[UserContext] = None
    ) -> Callable:
        """
        Décorateur d'autorisation
        
        Usage:
        @rbac.authorize(Permission.CONTENT_WRITE, ResourceType.CONTENT)
        async def update_content(content_id: str, user=Depends(get_current_user)):
            pass
        """
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                # Extraire user context
                if user_context:
                    ctx = user_context
                else:
                    # Récupérer depuis les dépendances FastAPI
                    ctx = await self._extract_user_context_from_request(args, kwargs)
                
                # Résoudre resource_id si dynamique
                resolved_resource_id = resource_id
                if resource_id and resource_id.startswith("{") and resource_id.endswith("}"):
                    param_name = resource_id[1:-1]
                    resolved_resource_id = kwargs.get(param_name)
                
                # Vérifier autorisation
                request = AuthorizationRequest(
                    user_context=ctx,
                    permission=permission,
                    resource_type=resource_type,
                    resource_id=resolved_resource_id
                )
                
                result = await self._check_authorization(request)
                
                if not result.granted:
                    # Audit de l'accès refusé
                    await self._audit_access_denied(result)
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access denied: {result.reason}"
                    )
                
                # Audit de l'accès accordé
                await self._audit_access_granted(result)
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator

    async def check_permission(
        self,
        user_context: UserContext,
        permission: Permission,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> AuthorizationResult:
        """Vérification directe de permission"""
        request = AuthorizationRequest(
            user_context=user_context,
            permission=permission,
            resource_type=resource_type,
            resource_id=resource_id,
            context=context or {}
        )
        
        return await self._check_authorization(request)

    async def _check_authorization(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Logique principale d'autorisation"""
        start_time = datetime.utcnow()
        
        with self.authorization_duration.labels(permission=request.permission.value).time():
            try:
                # Vérifier cache si activé
                if self.config.enable_permission_caching:
                    cached_result = await self._get_cached_result(request)
                    if cached_result is not None:
                        self.cache_hits.inc()
                        return cached_result
                    self.cache_misses.inc()
                
                # Collecter toutes les permissions de l'utilisateur
                user_permissions = await self._collect_user_permissions(request.user_context)
                
                # Vérifier permission directe
                if request.permission in user_permissions:
                    result = await self._evaluate_permission_rules(request, user_permissions)
                else:
                    result = AuthorizationResult(
                        granted=False,
                        reason="Permission not assigned to user",
                        user_id=request.user_context.user_id,
                        permission=request.permission,
                        timestamp=datetime.utcnow(),
                        decision_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                    )
                
                # Mettre en cache si activé
                if self.config.enable_permission_caching:
                    await self._cache_result(request, result)
                
                # Métriques
                self.authorization_requests.labels(
                    permission=request.permission.value,
                    resource_type=request.resource_type.value if request.resource_type else "none",
                    granted=str(result.granted).lower()
                ).inc()
                
                return result
                
            except Exception as e:
                self.logger.error(f"Authorization error: {str(e)}")
                return AuthorizationResult(
                    granted=False,
                    reason=f"Authorization error: {str(e)}",
                    user_id=request.user_context.user_id,
                    permission=request.permission,
                    timestamp=datetime.utcnow(),
                    decision_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )

    async def _collect_user_permissions(self, user_context: UserContext) -> Set[Permission]:
        """Collecte toutes les permissions de l'utilisateur"""
        permissions = set(user_context.additional_permissions)
        
        # Permissions du rôle principal
        role_permissions = await self._get_role_permissions(user_context.role)
        permissions.update(role_permissions)
        
        # Permissions héritées si activé
        if self.config.permission_inheritance:
            inherited_permissions = await self._get_inherited_permissions(user_context.role)
            permissions.update(inherited_permissions)
        
        # Permissions dynamiques si activé
        if self.config.enable_dynamic_permissions:
            dynamic_permissions = await self._get_dynamic_permissions(user_context)
            permissions.update(dynamic_permissions)
        
        return permissions

    async def _get_role_permissions(self, role: Role) -> Set[Permission]:
        """Récupère permissions d'un rôle"""
        role_def = self.role_definitions.get(role)
        if not role_def:
            return set()
        
        return {rule.permission for rule in role_def.permissions if not rule.deny}

    async def _get_inherited_permissions(self, role: Role) -> Set[Permission]:
        """Récupère permissions héritées des rôles parents"""
        permissions = set()
        
        role_def = self.role_definitions.get(role)
        if not role_def:
            return permissions
        
        for parent_role in role_def.parent_roles:
            parent_permissions = await self._get_role_permissions(parent_role)
            permissions.update(parent_permissions)
            
            # Récursion pour héritage multiple
            inherited = await self._get_inherited_permissions(parent_role)
            permissions.update(inherited)
        
        return permissions

    async def _get_dynamic_permissions(self, user_context: UserContext) -> Set[Permission]:
        """Calcule permissions dynamiques basées sur le contexte"""
        permissions = set()
        
        # Exemple: permissions basées sur ownership
        if self.config.enable_resource_ownership:
            # Si l'utilisateur possède des créateurs, donner permissions creator
            if user_context.resource_ownership.get("creator"):
                permissions.update([
                    Permission.CREATOR_READ,
                    Permission.CREATOR_WRITE,
                    Permission.CONTENT_READ,
                    Permission.CONTENT_WRITE
                ])
        
        return permissions

    async def _evaluate_permission_rules(
        self, request: AuthorizationRequest, user_permissions: Set[Permission]
    ) -> AuthorizationResult:
        """Évalue les règles de permission spécifiques"""
        
        # Vérifier ownership si requis
        if (self.config.enable_resource_ownership and 
            request.resource_type and request.resource_id):
            
            owns_resource = await self._check_resource_ownership(
                request.user_context,
                request.resource_type,
                request.resource_id
            )
            
            if not owns_resource and not await self._has_admin_override(request.user_context):
                return AuthorizationResult(
                    granted=False,
                    reason="Resource ownership required",
                    user_id=request.user_context.user_id,
                    permission=request.permission,
                    timestamp=datetime.utcnow(),
                    decision_time_ms=0
                )
        
        # Vérifier règles de déni explicites
        deny_rules = await self._check_deny_rules(request)
        if deny_rules:
            return AuthorizationResult(
                granted=False,
                reason=f"Explicit deny rule: {deny_rules[0]}",
                matched_rules=deny_rules,
                user_id=request.user_context.user_id,
                permission=request.permission,
                timestamp=datetime.utcnow(),
                decision_time_ms=0
            )
        
        # Permission accordée
        return AuthorizationResult(
            granted=True,
            reason="Permission granted",
            user_id=request.user_context.user_id,
            permission=request.permission,
            timestamp=datetime.utcnow(),
            decision_time_ms=0
        )

    async def _check_resource_ownership(
        self, user_context: UserContext, resource_type: ResourceType, resource_id: str
    ) -> bool:
        """Vérifie si l'utilisateur possède la ressource"""
        owned_resources = user_context.resource_ownership.get(resource_type.value, [])
        return resource_id in owned_resources

    async def _has_admin_override(self, user_context: UserContext) -> bool:
        """Vérifie si l'utilisateur a des privilèges admin"""
        admin_roles = [Role.ADMIN, Role.SUPER_ADMIN]
        return user_context.role in admin_roles

    async def _check_deny_rules(self, request: AuthorizationRequest) -> List[str]:
        """Vérifie les règles de déni explicites"""
        deny_rules = []
        
        role_def = self.role_definitions.get(request.user_context.role)
        if role_def:
            for rule in role_def.permissions:
                if (rule.deny and 
                    rule.permission == request.permission and
                    self._matches_resource_pattern(rule, request)):
                    deny_rules.append(f"Role {role_def.name}: {rule.permission}")
        
        return deny_rules

    def _matches_resource_pattern(self, rule: PermissionRule, request: AuthorizationRequest) -> bool:
        """Vérifie si la requête correspond au pattern de la règle"""
        if not rule.resource_pattern or not request.resource_id:
            return True
        
        return bool(re.match(rule.resource_pattern, request.resource_id))

    async def _get_cached_result(self, request: AuthorizationRequest) -> Optional[AuthorizationResult]:
        """Récupère résultat depuis le cache"""
        cache_key = self._generate_cache_key(request)
        
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            try:
                data = json.loads(cached_data)
                return AuthorizationResult(**data)
            except Exception as e:
                self.logger.warning(f"Cache deserialization error: {str(e)}")
        
        return None

    async def _cache_result(self, request: AuthorizationRequest, result: AuthorizationResult):
        """Met en cache le résultat"""
        cache_key = self._generate_cache_key(request)
        
        try:
            cached_data = result.dict()
            await self.redis.setex(
                cache_key,
                self.config.cache_ttl_seconds,
                json.dumps(cached_data, default=str)
            )
        except Exception as e:
            self.logger.warning(f"Cache serialization error: {str(e)}")

    def _generate_cache_key(self, request: AuthorizationRequest) -> str:
        """Génère clé de cache pour la requête"""
        key_parts = [
            request.user_context.user_id,
            request.permission.value,
            request.resource_type.value if request.resource_type else "none",
            request.resource_id or "none"
        ]
        return f"rbac_cache:{':'.join(key_parts)}"

    async def _extract_user_context_from_request(self, args, kwargs) -> UserContext:
        """Extrait contexte utilisateur depuis les paramètres de la requête"""
        # Chercher user dans kwargs
        for key, value in kwargs.items():
            if hasattr(value, 'user_id') and hasattr(value, 'role'):
                return value
        
        # Context par défaut si pas trouvé
        return UserContext(
            user_id="anonymous",
            role=Role.CREATOR
        )

    async def _audit_access_granted(self, result: AuthorizationResult):
        """Audit d'accès accordé"""
        if self.config.audit_enabled:
            audit_data = {
                "event": "access_granted",
                "user_id": result.user_id,
                "permission": result.permission.value,
                "timestamp": result.timestamp.isoformat(),
                "decision_time_ms": result.decision_time_ms
            }
            
            await self.redis.lpush("rbac_audit_log", json.dumps(audit_data))
            self.logger.info(f"Access granted: {audit_data}")

    async def _audit_access_denied(self, result: AuthorizationResult):
        """Audit d'accès refusé"""
        if self.config.audit_enabled:
            audit_data = {
                "event": "access_denied",
                "user_id": result.user_id,
                "permission": result.permission.value,
                "reason": result.reason,
                "timestamp": result.timestamp.isoformat(),
                "decision_time_ms": result.decision_time_ms
            }
            
            await self.redis.lpush("rbac_audit_log", json.dumps(audit_data))
            self.logger.warning(f"Access denied: {audit_data}")

    # API Management
    
    def add_role(self, role_definition: RoleDefinition):
        """Ajoute une nouvelle définition de rôle"""
        self.role_definitions[role_definition.name] = role_definition
        self.logger.info(f"Role added: {role_definition.name}")

    def remove_role(self, role: Role):
        """Supprime une définition de rôle"""
        if role in self.role_definitions:
            del self.role_definitions[role]
            self.logger.info(f"Role removed: {role}")

    async def clear_cache(self, user_id: Optional[str] = None):
        """Vide le cache de permissions"""
        if user_id:
            # Vider cache pour utilisateur spécifique
            pattern = f"rbac_cache:{user_id}:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        else:
            # Vider tout le cache
            pattern = "rbac_cache:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        
        self.logger.info(f"Cache cleared for user: {user_id or 'all'}")

    async def get_user_permissions(self, user_context: UserContext) -> List[Permission]:
        """Récupère liste des permissions d'un utilisateur"""
        permissions = await self._collect_user_permissions(user_context)
        return list(permissions)

    def create_middleware(self):
        """Crée middleware FastAPI"""
        async def rbac_middleware(request: Request, call_next):
            # Middleware peut être utilisé pour logging global
            response = await call_next(request)
            return response
        
        return rbac_middleware


# Factory function
def create_rbac_middleware(config: RBACConfig = None) -> RBACMiddlewareTemplate:
    """
    Factory pour créer middleware RBAC
    
    Args:
        config: Configuration RBAC personnalisée
        
    Returns:
        RBACMiddlewareTemplate: Instance du middleware configuré
    """
    return RBACMiddlewareTemplate(config)


# Usage examples
if __name__ == "__main__":
    import asyncio
    
    async def test_rbac():
        """Test du système RBAC"""
        rbac = create_rbac_middleware()
        
        # Context utilisateur test
        user_context = UserContext(
            user_id="creator_123",
            role=Role.CREATOR,
            creator_id="creator_123",
            resource_ownership={"content": ["content_456"]}
        )
        
        # Test permission accordée
        result = await rbac.check_permission(
            user_context,
            Permission.CONTENT_WRITE,
            ResourceType.CONTENT,
            "content_456"
        )
        print(f"Permission granted: {result.granted}, reason: {result.reason}")
        
        # Test permission refusée
        result = await rbac.check_permission(
            user_context,
            Permission.SYSTEM_ADMIN
        )
        print(f"Permission granted: {result.granted}, reason: {result.reason}")
    
    asyncio.run(test_rbac())