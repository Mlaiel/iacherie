"""Session and Authentication Cache for IA Influencer Agent Platform
High-performance user session management with Redis and JWT token caching

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""import asyncio
import logging
import json
import hashlib
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import jwt
from cryptography.fernet import Fernet
import secrets

from .redis_cache import RedisCache, RedisConfig
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """User session data structure"""    user_id: str
    session_id: str
    tenant_id: Optional[str]
    email: str
    username: str
    roles: List[str]
    permissions: List[str]
    
    # Session metadata
    created_at: datetime
    last_accessed: datetime
    ip_address: str
    user_agent: str
    
    # Authentication data
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Profile data
    profile_data: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    
    # Security flags
    is_active: bool = True
    is_verified: bool = False
    requires_mfa: bool = False
    suspicious_activity: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary"""        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'last_accessed', 'token_expires_at']
        for field in datetime_fields:
            if data.get(field) and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)

@dataclass
class AuthToken:
    """Authentication token data"""    token: str
    token_type: str  # access, refresh, api_key
    user_id: str
    session_id: str
    expires_at: datetime
    issued_at: datetime
    scopes: List[str]
    is_revoked: bool = False

class SessionCache:
    """    Advanced session cache with Redis backend and security features
    Handles user sessions, authentication tokens, and security tracking
    """    
    def __init__(self, 
                 redis_config: RedisConfig,
                 session_timeout: int = 3600,  # 1 hour
                 token_timeout: int = 900,     # 15 minutes
                 max_sessions_per_user: int = 5,
                 enable_security_tracking: bool = True):
        
        self.session_timeout = session_timeout
        self.token_timeout = token_timeout
        self.max_sessions_per_user = max_sessions_per_user
        self.enable_security_tracking = enable_security_tracking
        
        # Initialize Redis cache
        self.redis_cache = RedisCache(redis_config)
        
        # Memory cache for frequently accessed data
        self.memory_cache = MemoryCache(
            max_size=10000,
            default_ttl=300  # 5 minutes
        )
        
        # Encryption for sensitive data
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Cache key prefixes
        self.SESSION_PREFIX = "session"
        self.TOKEN_PREFIX = "token"
        self.USER_SESSIONS_PREFIX = "user_sessions"
        self.SECURITY_PREFIX = "security"
        self.RATE_LIMIT_PREFIX = "rate_limit"
        
        # Statistics
        self._stats = {
            'sessions_created': 0,
            'sessions_destroyed': 0,
            'tokens_issued': 0,
            'tokens_revoked': 0,
            'security_violations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("SessionCache initialized")
    
    async def initialize(self):
        """Initialize cache connections"""        await self.redis_cache.connect()
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""        return secrets.token_urlsafe(32)
    
    def _generate_token(self, user_id: str, session_id: str, token_type: str = "access") -> str:
        """Generate JWT token"""        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'token_type': token_type,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.token_timeout)
        }
        return jwt.encode(payload, str(self.encryption_key), algorithm='HS256')
    
    async def create_session(self,
                           user_id: str,
                           email: str,
                           username: str,
                           roles: List[str],
                           permissions: List[str],
                           ip_address: str,
                           user_agent: str,
                           tenant_id: Optional[str] = None,
                           profile_data: Optional[Dict[str, Any]] = None) -> UserSession:
        """Create new user session"""        
        # Check for existing sessions and enforce limits
        await self._enforce_session_limits(user_id)
        
        # Generate session ID
        session_id = self._generate_session_id()
        current_time = datetime.utcnow()
        
        # Create session object
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
            email=email,
            username=username,
            roles=roles,
            permissions=permissions,
            created_at=current_time,
            last_accessed=current_time,
            ip_address=ip_address,
            user_agent=user_agent,
            profile_data=profile_data or {},
            preferences={}
        )
        
        # Generate tokens
        access_token = self._generate_token(user_id, session_id, "access")
        refresh_token = self._generate_token(user_id, session_id, "refresh")
        
        session.access_token = access_token
        session.refresh_token = refresh_token
        session.token_expires_at = current_time + timedelta(seconds=self.token_timeout)
        
        # Store session in Redis
        session_key = f"{self.SESSION_PREFIX}:{session_id}"
        session_data = json.dumps(session.to_dict())
        await self.redis_cache.set(session_key, session_data, ttl=self.session_timeout)
        
        # Store session in memory cache
        self.memory_cache.set(session_key, session, ttl=300)
        
        # Track user sessions
        await self._add_user_session(user_id, session_id)
        
        # Store tokens
        await self._store_token(access_token, user_id, session_id, "access")
        await self._store_token(refresh_token, user_id, session_id, "refresh")
        
        # Security tracking
        if self.enable_security_tracking:
            await self._track_login(user_id, ip_address, user_agent, True)
        
        self._stats['sessions_created'] += 1
        logger.info(f"Session created for user {user_id}: {session_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""        session_key = f"{self.SESSION_PREFIX}:{session_id}"
        
        # Try memory cache first
        cached_session = self.memory_cache.get(session_key)
        if cached_session:
            self._stats['cache_hits'] += 1
            # Update last accessed time
            cached_session.last_accessed = datetime.utcnow()
            await self._update_session_access(session_id, cached_session)
            return cached_session
        
        # Try Redis cache
        session_data = await self.redis_cache.get(session_key)
        if session_data:
            self._stats['cache_hits'] += 1
            session_dict = json.loads(session_data)
            session = UserSession.from_dict(session_dict)
            
            # Update last accessed time
            session.last_accessed = datetime.utcnow()
            await self._update_session_access(session_id, session)
            
            # Cache in memory
            self.memory_cache.set(session_key, session, ttl=300)
            
            return session
        
        self._stats['cache_misses'] += 1
        return None
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.last_accessed = datetime.utcnow()
        
        # Store updated session
        session_key = f"{self.SESSION_PREFIX}:{session_id}"
        session_data = json.dumps(session.to_dict())
        await self.redis_cache.set(session_key, session_data, ttl=self.session_timeout)
        
        # Update memory cache
        self.memory_cache.set(session_key, session, ttl=300)
        
        return True
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy user session"""        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Remove from caches
        session_key = f"{self.SESSION_PREFIX}:{session_id}"
        await self.redis_cache.delete(session_key)
        self.memory_cache.delete(session_key)
        
        # Remove from user sessions tracking
        await self._remove_user_session(session.user_id, session_id)
        
        # Revoke tokens
        if session.access_token:
            await self._revoke_token(session.access_token)
        if session.refresh_token:
            await self._revoke_token(session.refresh_token)
        
        # Security tracking
        if self.enable_security_tracking:
            await self._track_logout(session.user_id, session.ip_address)
        
        self._stats['sessions_destroyed'] += 1
        logger.info(f"Session destroyed: {session_id}")
        
        return True
    
    async def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all sessions for a user"""        user_sessions_key = f"{self.USER_SESSIONS_PREFIX}:{user_id}"
        session_ids_data = await self.redis_cache.get(user_sessions_key)
        
        if not session_ids_data:
            return []
        
        session_ids = json.loads(session_ids_data)
        sessions = []
        
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session and session.is_active:
                sessions.append(session)
        
        return sessions
    
    async def destroy_user_sessions(self, user_id: str, except_session: Optional[str] = None) -> int:
        """Destroy all sessions for a user"""        sessions = await self.get_user_sessions(user_id)
        destroyed_count = 0
        
        for session in sessions:
            if except_session and session.session_id == except_session:
                continue
            
            if await self.destroy_session(session.session_id):
                destroyed_count += 1
        
        return destroyed_count
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""        try:
            # Check if token is revoked
            token_key = f"{self.TOKEN_PREFIX}:{hashlib.sha256(token.encode()).hexdigest()}"
            token_data = await self.redis_cache.get(token_key)
            
            if not token_data:
                return None
            
            auth_token = json.loads(token_data)
            if auth_token.get('is_revoked'):
                return None
            
            # Decode JWT
            payload = jwt.decode(token, str(self.encryption_key), algorithms=['HS256'])
            
            # Verify session exists
            session = await self.get_session(payload['session_id'])
            if not session or not session.is_active:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token"""        payload = await self.validate_token(refresh_token)
        if not payload or payload.get('token_type') != 'refresh':
            return None
        
        user_id = payload['user_id']
        session_id = payload['session_id']
        
        # Generate new access token
        new_access_token = self._generate_token(user_id, session_id, "access")
        
        # Store new token
        await self._store_token(new_access_token, user_id, session_id, "access")
        
        # Update session
        await self.update_session(session_id, {
            'access_token': new_access_token,
            'token_expires_at': datetime.utcnow() + timedelta(seconds=self.token_timeout)
        })
        
        self._stats['tokens_issued'] += 1
        
        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': self.token_timeout
        }
    
    async def _store_token(self, token: str, user_id: str, session_id: str, token_type: str):
        """Store token in cache"""        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_key = f"{self.TOKEN_PREFIX}:{token_hash}"
        
        token_data = {
            'token': token,
            'token_type': token_type,
            'user_id': user_id,
            'session_id': session_id,
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.token_timeout)).isoformat(),
            'issued_at': datetime.utcnow().isoformat(),
            'is_revoked': False
        }
        
        await self.redis_cache.set(token_key, json.dumps(token_data), ttl=self.token_timeout)
    
    async def _revoke_token(self, token: str):
        """Revoke token"""        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_key = f"{self.TOKEN_PREFIX}:{token_hash}"
        
        token_data = await self.redis_cache.get(token_key)
        if token_data:
            token_dict = json.loads(token_data)
            token_dict['is_revoked'] = True
            await self.redis_cache.set(token_key, json.dumps(token_dict), ttl=3600)  # Keep for 1 hour
            self._stats['tokens_revoked'] += 1
    
    async def _add_user_session(self, user_id: str, session_id: str):
        """Add session to user's session list"""        user_sessions_key = f"{self.USER_SESSIONS_PREFIX}:{user_id}"
        session_ids_data = await self.redis_cache.get(user_sessions_key)
        
        session_ids = json.loads(session_ids_data) if session_ids_data else []
        if session_id not in session_ids:
            session_ids.append(session_id)
        
        await self.redis_cache.set(user_sessions_key, json.dumps(session_ids), ttl=self.session_timeout * 2)
    
    async def _remove_user_session(self, user_id: str, session_id: str):
        """Remove session from user's session list"""        user_sessions_key = f"{self.USER_SESSIONS_PREFIX}:{user_id}"
        session_ids_data = await self.redis_cache.get(user_sessions_key)
        
        if session_ids_data:
            session_ids = json.loads(session_ids_data)
            if session_id in session_ids:
                session_ids.remove(session_id)
                await self.redis_cache.set(user_sessions_key, json.dumps(session_ids), ttl=self.session_timeout * 2)
    
    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""        sessions = await self.get_user_sessions(user_id)
        
        if len(sessions) >= self.max_sessions_per_user:
            # Sort by last accessed time and remove oldest
            sessions.sort(key=lambda s: s.last_accessed)
            oldest_session = sessions[0]
            await self.destroy_session(oldest_session.session_id)
            logger.info(f"Removed oldest session for user {user_id} to enforce limits")
    
    async def _update_session_access(self, session_id: str, session: UserSession):
        """Update session last accessed time"""        session_key = f"{self.SESSION_PREFIX}:{session_id}"
        session_data = json.dumps(session.to_dict())
        await self.redis_cache.set(session_key, session_data, ttl=self.session_timeout)
    
    async def _track_login(self, user_id: str, ip_address: str, user_agent: str, success: bool):
        """Track login attempt for security"""        if not self.enable_security_tracking:
            return
        
        security_key = f"{self.SECURITY_PREFIX}:login:{user_id}"
        login_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat(),
            'success': success
        }
        
        # Store recent login attempts
        attempts_data = await self.redis_cache.get(security_key)
        attempts = json.loads(attempts_data) if attempts_data else []
        attempts.append(login_data)
        
        # Keep only last 10 attempts
        attempts = attempts[-10:]
        
        await self.redis_cache.set(security_key, json.dumps(attempts), ttl=86400)  # 24 hours
    
    async def _track_logout(self, user_id: str, ip_address: str):
        """Track logout for security"""        if not self.enable_security_tracking:
            return
        
        security_key = f"{self.SECURITY_PREFIX}:logout:{user_id}"
        logout_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.redis_cache.set(security_key, json.dumps(logout_data), ttl=86400)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        
        return {
            'session_stats': self._stats,
            'redis_stats': redis_stats,
            'memory_stats': memory_stats,
            'session_timeout': self.session_timeout,
            'token_timeout': self.token_timeout,
            'max_sessions_per_user': self.max_sessions_per_user
        }
    
    async def close(self):
        """Close cache connections"""        await self.redis_cache.close()
        self.memory_cache.close()

class AuthCache:
    """    Simplified authentication cache for API tokens and permissions
    """    
    def __init__(self, redis_config: RedisConfig):
        self.redis_cache = RedisCache(redis_config)
        self.API_KEY_PREFIX = "api_key"
        self.PERMISSION_PREFIX = "permission"
        self.RATE_LIMIT_PREFIX = "rate_limit"
    
    async def initialize(self):
        """Initialize cache connection"""        await self.redis_cache.connect()
    
    async def store_api_key(self, api_key: str, user_id: str, permissions: List[str], ttl: int = 86400):
        """Store API key with permissions"""        api_key_data = {
            'user_id': user_id,
            'permissions': permissions,
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        key = f"{self.API_KEY_PREFIX}:{hashlib.sha256(api_key.encode()).hexdigest()}"
        await self.redis_cache.set(key, json.dumps(api_key_data), ttl=ttl)
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user data"""        key = f"{self.API_KEY_PREFIX}:{hashlib.sha256(api_key.encode()).hexdigest()}"
        data = await self.redis_cache.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""        key = f"{self.API_KEY_PREFIX}:{hashlib.sha256(api_key.encode()).hexdigest()}"
        return await self.redis_cache.delete(key)
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        """Check rate limit for identifier"""        key = f"{self.RATE_LIMIT_PREFIX}:{identifier}"
        current_count = await self.redis_cache.get(key)
        
        if current_count is None:
            await self.redis_cache.set(key, "1", ttl=window)
            return True
        
        count = int(current_count)
        if count >= limit:
            return False
        
        # Increment counter
        await self.redis_cache.set(key, str(count + 1), ttl=window)
        return True
    
    async def close(self):
        """Close cache connection"""        await self.redis_cache.close()
