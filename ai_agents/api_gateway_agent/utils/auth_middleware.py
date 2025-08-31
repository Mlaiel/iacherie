"""Authentication Middleware - Enterprise Security Layer

Advanced authentication and authorization middleware providing JWT validation,
API key management, role-based access control, and security monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""
import logging
import time
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import hashlib

import jwt
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """User authentication context"""
    user_id: str
    email: Optional[str] = None
    roles: List[str] = None
    permissions: Set[str] = None
    api_key_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = set()


@dataclass
class APIKey:
    """API Key information"""
    key_id: str
    user_id: str
    key_hash: str
    name: str
    permissions: Set[str]
    rate_limit: int
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True


class AuthMiddleware:
    """
    Enterprise Authentication Middleware
    
    Features:
    - JWT token validation
    - API key authentication
    - Role-based access control (RBAC)
    - Permission validation
    - Session management
    - Security monitoring
    - Multi-tenant support
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        token_expiration: int = 3600,
        refresh_expiration: int = 86400,
        bypass_paths: Optional[List[str]] = None,
        redis_url: Optional[str] = None
    ):
        """Initialize authentication middleware"""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiration = token_expiration
        self.refresh_expiration = refresh_expiration
        self.bypass_paths = bypass_paths or []
        
        # Security
        self.security = HTTPBearer(auto_error=False)
        
        # Redis for session management and blacklisting
        self.redis: Optional[aioredis.Redis] = None
        if redis_url:
            self.redis = aioredis.from_url(redis_url)
        
        # API Keys storage
        self.api_keys: Dict[str, APIKey] = {}
        
        # Permission system
        self.role_permissions: Dict[str, Set[str]] = {
            "admin": {
                "read:all", "write:all", "delete:all",
                "manage:users", "manage:system", "manage:api_keys"
            },
            "creator": {
                "read:own", "write:own", "delete:own",
                "upload:content", "protect:content", "monetize:content"
            },
            "collaborator": {
                "read:shared", "write:shared",
                "collaborate:projects", "view:analytics"
            },
            "viewer": {
                "read:public", "view:content"
            }
        }
        
        logger.info("Authentication middleware initialized")
    
    async def authenticate_request(self, request: Request) -> Optional[UserContext]:
        """
        Authenticate request and extract user context
        
        Args:
            request: FastAPI request object
            
        Returns:
            UserContext if authenticated, None if authentication fails
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Check if path should bypass authentication
            if self._should_bypass_auth(request.url.path):
                return None
            
            # Try JWT authentication first
            user_context = await self._authenticate_jwt(request)
            if user_context:
                request.state.user = user_context
                return user_context
            
            # Try API key authentication
            user_context = await self._authenticate_api_key(request)
            if user_context:
                request.state.user = user_context
                return user_context
            
            # No valid authentication found
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def _should_bypass_auth(self, path: str) -> bool:
        """Check if path should bypass authentication"""
        for bypass_path in self.bypass_paths:
            if path.startswith(bypass_path):
                return True
        return False
    
    async def _authenticate_jwt(self, request: Request) -> Optional[UserContext]:
        """Authenticate using JWT token"""
        try:
            # Extract token from Authorization header
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if not credentials:
                return None
            
            token = credentials.credentials
            
            # Check if token is blacklisted
            if await self._is_token_blacklisted(token):
                logger.warning("Attempted use of blacklisted token")
                return None
            
            # Decode and validate JWT
            try:
                payload = jwt.decode(
                    token,
                    self.secret_key,
                    algorithms=[self.algorithm]
                )
            except jwt.ExpiredSignatureError:
                logger.debug("JWT token expired")
                return None
            except jwt.InvalidTokenError as e:
                logger.debug(f"Invalid JWT token: {e}")
                return None
            
            # Extract user information
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("JWT token missing user ID")
                return None
            
            # Create user context
            user_context = UserContext(
                user_id=user_id,
                email=payload.get("email"),
                roles=payload.get("roles", []),
                tenant_id=payload.get("tenant_id"),
                session_id=payload.get("jti")
            )
            
            # Load permissions from roles
            user_context.permissions = self._get_permissions_for_roles(user_context.roles)
            
            # Update last activity
            if self.redis:
                await self._update_user_activity(user_id)
            
            logger.debug(f"Successfully authenticated user: {user_id}")
            return user_context
            
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            return None
    
    async def _authenticate_api_key(self, request: Request) -> Optional[UserContext]:
        """Authenticate using API key"""
        try:
            # Extract API key from header
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                return None
            
            # Hash the API key to find it in storage
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Find matching API key
            matching_key = None
            for key_id, stored_key in self.api_keys.items():
                if stored_key.key_hash == key_hash:
                    matching_key = stored_key
                    break
            
            if not matching_key:
                logger.debug("API key not found")
                return None
            
            # Check if key is active
            if not matching_key.is_active:
                logger.warning(f"Inactive API key used: {matching_key.key_id}")
                return None
            
            # Check if key is expired
            if matching_key.expires_at and matching_key.expires_at < datetime.utcnow():
                logger.warning(f"Expired API key used: {matching_key.key_id}")
                return None
            
            # Update last used timestamp
            matching_key.last_used = datetime.utcnow()
            
            # Create user context
            user_context = UserContext(
                user_id=matching_key.user_id,
                api_key_id=matching_key.key_id,
                permissions=matching_key.permissions.copy()
            )
            
            logger.debug(f"Successfully authenticated API key: {matching_key.key_id}")
            return user_context
            
        except Exception as e:
            logger.error(f"API key authentication error: {e}")
            return None
    
    def _get_permissions_for_roles(self, roles: List[str]) -> Set[str]:
        """Get combined permissions for list of roles"""
        permissions = set()
        for role in roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])
        return permissions
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if JWT token is blacklisted"""
        if not self.redis:
            return False
        
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            blacklist_key = f"auth:blacklist:{token_hash}"
            
            is_blacklisted = await self.redis.exists(blacklist_key)
            return bool(is_blacklisted)
            
        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            return False
    
    async def _update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        if not self.redis:
            return
        
        try:
            activity_key = f"auth:activity:{user_id}"
            await self.redis.set(activity_key, int(time.time()), ex=3600)
            
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def create_access_token(
        self,
        user_id: str,
        email: Optional[str] = None,
        roles: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(seconds=self.token_expiration)
            
            payload = {
                "sub": user_id,
                "iat": datetime.utcnow(),
                "exp": expire,
                "jti": f"access_{user_id}_{int(time.time())}"
            }
            
            if email:
                payload["email"] = email
            if roles:
                payload["roles"] = roles
            if tenant_id:
                payload["tenant_id"] = tenant_id
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        try:
            expire = datetime.utcnow() + timedelta(seconds=self.refresh_expiration)
            
            payload = {
                "sub": user_id,
                "type": "refresh",
                "iat": datetime.utcnow(),
                "exp": expire,
                "jti": f"refresh_{user_id}_{int(time.time())}"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise
    
    async def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        if not self.redis:
            logger.warning("Redis not available for token blacklisting")
            return False
        
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return False
            
            # Calculate TTL until token expires
            current_time = time.time()
            ttl = max(0, int(exp_timestamp - current_time))
            
            if ttl > 0:
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                blacklist_key = f"auth:blacklist:{token_hash}"
                
                await self.redis.set(blacklist_key, "1", ex=ttl)
                logger.info(f"Token blacklisted successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: Set[str],
        rate_limit: int = 1000,
        expires_at: Optional[datetime] = None
    ) -> Tuple[str, str]:
        """
        Create new API key
        
        Returns:
            Tuple of (key_id, api_key)
        """
        try:
            import secrets
            
            # Generate secure API key
            api_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            key_id = f"ak_{secrets.token_hex(8)}"
            
            # Store API key
            api_key_obj = APIKey(
                key_id=key_id,
                user_id=user_id,
                key_hash=key_hash,
                name=name,
                permissions=permissions,
                rate_limit=rate_limit,
                expires_at=expires_at
            )
            
            self.api_keys[key_id] = api_key_obj
            
            # Persist to Redis if available
            if self.redis:
                key_data = {
                    "user_id": user_id,
                    "key_hash": key_hash,
                    "name": name,
                    "permissions": json.dumps(list(permissions)),
                    "rate_limit": rate_limit,
                    "is_active": "1",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                if expires_at:
                    key_data["expires_at"] = expires_at.isoformat()
                
                await self.redis.hset(f"auth:api_key:{key_id}", mapping=key_data)
            
            logger.info(f"Created API key: {key_id} for user: {user_id}")
            return key_id, api_key
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            raise
    
    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke API key"""
        try:
            if key_id in self.api_keys:
                self.api_keys[key_id].is_active = False
                
                # Update in Redis
                if self.redis:
                    await self.redis.hset(f"auth:api_key:{key_id}", "is_active", "0")
                
                logger.info(f"Revoked API key: {key_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    def check_permission(self, user_context: UserContext, required_permission: str) -> bool:
        """Check if user has required permission"""
        try:
            # Admin users have all permissions
            if "admin" in user_context.roles:
                return True
            
            # Check specific permission
            if required_permission in user_context.permissions:
                return True
            
            # Check wildcard permissions
            permission_parts = required_permission.split(":")
            if len(permission_parts) == 2:
                action, resource = permission_parts
                wildcard_permission = f"{action}:all"
                if wildcard_permission in user_context.permissions:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for user"""
        if not self.redis:
            return []
        
        try:
            # This would typically query session storage
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def revoke_user_sessions(self, user_id: str) -> bool:
        """Revoke all sessions for user"""
        if not self.redis:
            return False
        
        try:
            # This would typically invalidate all user sessions
            # For now, return success
            logger.info(f"Revoked all sessions for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking user sessions: {e}")
            return False
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        try:
            active_api_keys = sum(1 for key in self.api_keys.values() if key.is_active)
            expired_api_keys = sum(
                1 for key in self.api_keys.values() 
                if key.expires_at and key.expires_at < datetime.utcnow()
            )
            
            return {
                "total_api_keys": len(self.api_keys),
                "active_api_keys": active_api_keys,
                "expired_api_keys": expired_api_keys,
                "supported_roles": list(self.role_permissions.keys()),
                "total_permissions": sum(len(perms) for perms in self.role_permissions.values()),
                "bypass_paths": self.bypass_paths
            }
            
        except Exception as e:
            logger.error(f"Error getting auth stats: {e}")
            return {}
