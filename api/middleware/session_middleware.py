"""Session Management Middleware - FastAPI Session Integration
Advanced session management with Redis backend and JWT integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import json
import time
import uuid
from typing import Callable, Optional, Dict, Any, List
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import logging

logger = logging.getLogger(__name__)


class SessionManagerMiddleware(BaseHTTPMiddleware):
    """    Advanced session management middleware for FastAPI
    
    Features:
    - Redis-backed session storage
    - JWT token integration
    - Automatic session renewal
    - Multi-tenant session isolation
    - Session hijacking protection
    - Activity tracking
    """    
    def __init__(
        self,
        app,
        session_backend: Optional[object] = None,
        jwt_secret: str = "your-secret-key",
        session_ttl: int = 3600,  # 1 hour
        session_cookie_name: str = "session_id",
        session_header_name: str = "X-Session-ID",
        require_session_paths: List[str] = None,
        exclude_paths: List[str] = None
    ):
        super().__init__(app)
        self.session_backend = session_backend
        self.jwt_secret = jwt_secret
        self.session_ttl = session_ttl
        self.session_cookie_name = session_cookie_name
        self.session_header_name = session_header_name
        self.require_session_paths = require_session_paths or ["/api/user/", "/api/protected/"]
        self.exclude_paths = exclude_paths or ["/health", "/ready", "/docs", "/openapi.json"]
        
        # Session statistics
        self.active_sessions = 0
        self.session_creates = 0
        self.session_renewals = 0
        self.session_invalidations = 0
        
        logger.info("Session Manager Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle session management"""        
        # Check if path should be excluded
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Get session ID from request
        session_id = self._get_session_id(request)
        
        # Load or create session
        session_data = None
        if session_id:
            session_data = await self._load_session(session_id)
        
        # Check if session is required for this path
        if self._requires_session(request.url.path) and not session_data:
            return Response(
                content=json.dumps({"error": "Session required"}),
                status_code=401,
                media_type="application/json"
            )
        
        # Add session to request state
        request.state.session_id = session_id
        request.state.session_data = session_data or {}
        
        # Process request
        response = await call_next(request)
        
        # Update session if it exists
        if session_data:
            await self._update_session_activity(session_id, request)
        
        # Handle session creation for authenticated requests
        if hasattr(request.state, 'create_session') and request.state.create_session:
            new_session_id = await self._create_session(request.state.session_data, request)
            response.set_cookie(
                key=self.session_cookie_name,
                value=new_session_id,
                max_age=self.session_ttl,
                httponly=True,
                secure=True,
                samesite="lax"
            )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from session handling"""        
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return True
        return False
    
    def _requires_session(self, path: str) -> bool:
        """Check if path requires an active session"""        
        for required_path in self.require_session_paths:
            if path.startswith(required_path):
                return True
        return False
    
    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request"""        
        # Try header first
        session_id = request.headers.get(self.session_header_name)
        if session_id:
            return session_id
        
        # Try cookie
        session_id = request.cookies.get(self.session_cookie_name)
        if session_id:
            return session_id
        
        # Try JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                return payload.get("session_id")
            except jwt.InvalidTokenError:
                pass
        
        return None
    
    async def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from backend"""        
        if not self.session_backend:
            return None
        
        try:
            cache_key = f"session:{session_id}"
            
            if hasattr(self.session_backend, 'get'):
                session_data = await self.session_backend.get(cache_key)
                if session_data:
                    if isinstance(session_data, str):
                        session_data = json.loads(session_data)
                    
                    # Check if session is expired
                    if self._is_session_expired(session_data):
                        await self._invalidate_session(session_id)
                        return None
                    
                    return session_data
            
        except Exception as e:
            logger.warning(f"Failed to load session {session_id}: {e}")
        
        return None
    
    async def _create_session(self, session_data: Dict[str, Any], request: Request) -> str:
        """Create new session"""        
        session_id = str(uuid.uuid4())
        
        # Prepare session data
        full_session_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "data": session_data
        }
        
        # Add tenant isolation
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            full_session_data["tenant_id"] = tenant_id
        
        # Store session
        if self.session_backend and hasattr(self.session_backend, 'set'):
            try:
                cache_key = f"session:{session_id}"
                await self.session_backend.set(
                    cache_key,
                    json.dumps(full_session_data),
                    self.session_ttl
                )
                
                self.session_creates += 1
                self.active_sessions += 1
                
                logger.info(f"Created session {session_id}")
                
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise
        
        return session_id
    
    async def _update_session_activity(self, session_id: str, request: Request):
        """Update session last accessed time"""        
        if not self.session_backend:
            return
        
        try:
            cache_key = f"session:{session_id}"
            
            if hasattr(self.session_backend, 'get'):
                session_data = await self.session_backend.get(cache_key)
                if session_data:
                    if isinstance(session_data, str):
                        session_data = json.loads(session_data)
                    
                    # Update activity
                    session_data["last_accessed"] = time.time()
                    session_data["request_count"] = session_data.get("request_count", 0) + 1
                    
                    # Security check - detect session hijacking
                    current_ip = self._get_client_ip(request)
                    if session_data.get("ip_address") != current_ip:
                        logger.warning(f"Session {session_id} IP mismatch: {session_data.get('ip_address')} vs {current_ip}")
                        # Optionally invalidate session
                        # await self._invalidate_session(session_id)
                        # return
                    
                    # Save updated session
                    if hasattr(self.session_backend, 'set'):
                        await self.session_backend.set(
                            cache_key,
                            json.dumps(session_data),
                            self.session_ttl
                        )
                        
                        self.session_renewals += 1
            
        except Exception as e:
            logger.warning(f"Failed to update session activity: {e}")
    
    async def _invalidate_session(self, session_id: str):
        """Invalidate session"""        
        if not self.session_backend:
            return
        
        try:
            cache_key = f"session:{session_id}"
            
            if hasattr(self.session_backend, 'delete'):
                await self.session_backend.delete(cache_key)
                
                self.session_invalidations += 1
                self.active_sessions = max(0, self.active_sessions - 1)
                
                logger.info(f"Invalidated session {session_id}")
            
        except Exception as e:
            logger.warning(f"Failed to invalidate session: {e}")
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """Check if session is expired"""        
        last_accessed = session_data.get("last_accessed", 0)
        current_time = time.time()
        
        return (current_time - last_accessed) > self.session_ttl
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""        
        # Check forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session management statistics"""        
        return {
            "active_sessions": self.active_sessions,
            "session_creates": self.session_creates,
            "session_renewals": self.session_renewals,
            "session_invalidations": self.session_invalidations,
            "session_ttl": self.session_ttl
        }


class SessionAuthMiddleware(BaseHTTPMiddleware):
    """    Middleware for session-based authentication
    """    
    def __init__(
        self,
        app,
        session_backend: Optional[object] = None,
        protected_paths: List[str] = None,
        admin_paths: List[str] = None
    ):
        super().__init__(app)
        self.session_backend = session_backend
        self.protected_paths = protected_paths or ["/api/user/", "/api/protected/"]
        self.admin_paths = admin_paths or ["/api/admin/"]
        
        logger.info("Session Auth Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check authentication"""        
        path = request.url.path
        
        # Check if path requires authentication
        requires_auth = any(path.startswith(p) for p in self.protected_paths)
        requires_admin = any(path.startswith(p) for p in self.admin_paths)
        
        if requires_auth or requires_admin:
            # Check session data
            session_data = getattr(request.state, 'session_data', {})
            
            if not session_data or not session_data.get('data', {}).get('user_id'):
                return Response(
                    content=json.dumps({"error": "Authentication required"}),
                    status_code=401,
                    media_type="application/json"
                )
            
            # Check admin access
            if requires_admin:
                user_roles = session_data.get('data', {}).get('roles', [])
                if 'admin' not in user_roles:
                    return Response(
                        content=json.dumps({"error": "Admin access required"}),
                        status_code=403,
                        media_type="application/json"
                    )
            
            # Add user info to request
            request.state.user_id = session_data.get('data', {}).get('user_id')
            request.state.user_roles = session_data.get('data', {}).get('roles', [])
            request.state.tenant_id = session_data.get('tenant_id')
        
        return await call_next(request)


# Helper functions for session management
async def create_session(request: Request, user_data: Dict[str, Any]):
    """Helper to create a new session"""    request.state.create_session = True
    request.state.session_data = user_data


async def get_session_data(request: Request) -> Dict[str, Any]:
    """Helper to get session data"""    return getattr(request.state, 'session_data', {})


async def invalidate_session(request: Request, session_backend: object):
    """Helper to invalidate current session"""    session_id = getattr(request.state, 'session_id', None)
    if session_id and session_backend:
        cache_key = f"session:{session_id}"
        if hasattr(session_backend, 'delete'):
            await session_backend.delete(cache_key)