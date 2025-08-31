"""Session Management Manager
=========================

Advanced session management system for crawler operations with persistence,
authentication, cookies, and multi-domain session handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import aiohttp
import logging
import time
import json
import pickle
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import base64
from urllib.parse import urlparse, urljoin
from pathlib import Path
import sqlite3
import threading
from contextlib import asynccontextmanager

from ..config.session_config import SessionConfig
from ..utils.encryption import SessionEncryption
from ..utils.cookie_manager import CookieManager
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...models.crawler_session import CrawlerSession, SessionCookie


class SessionState(Enum):
    """Session state enumeration."""    INACTIVE = "inactive"
    ACTIVE = "active"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    ERROR = "error"


class AuthenticationType(Enum):
    """Authentication type enumeration."""    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    COOKIES = "cookies"
    FORM_LOGIN = "form_login"
    API_KEY = "api_key"
    CUSTOM = "custom"


@dataclass
class SessionCredentials:
    """Session authentication credentials."""    auth_type: AuthenticationType
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    oauth_tokens: Dict[str, str] = field(default_factory=dict)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    form_data: Dict[str, str] = field(default_factory=dict)
    expires_at: Optional[datetime] = None


@dataclass
class SessionConfiguration:
    """Session configuration settings."""    domain: str
    max_connections: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    user_agent: str = ""
    proxy: Optional[str] = None
    cookies_enabled: bool = True
    javascript_enabled: bool = False
    headers: Dict[str, str] = field(default_factory=dict)
    auth_config: Optional[SessionCredentials] = None
    persistence_enabled: bool = True
    auto_renew: bool = True
    session_lifetime: int = 3600  # seconds


@dataclass
class SessionMetrics:
    """Session performance metrics."""    session_id: str
    domain: str
    created_at: datetime
    last_active: datetime
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    bytes_transferred: int = 0
    average_response_time: float = 0.0
    auth_attempts: int = 0
    auth_failures: int = 0


class ManagedSession:
    """    Managed session wrapper with advanced features.
    """    
    def __init__(self, session_id: str, config: SessionConfiguration):
        """Initialize managed session."""        self.session_id = session_id
        self.config = config
        self.logger = get_logger(f"Session-{session_id[:8]}")
        
        # Session state
        self.state = SessionState.INACTIVE
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=config.session_lifetime)
        
        # HTTP session
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        
        # Authentication
        self.authenticated = False
        self.auth_token: Optional[str] = None
        self.auth_expires_at: Optional[datetime] = None
        
        # Metrics
        self.metrics = SessionMetrics(
            session_id=session_id,
            domain=config.domain,
            created_at=self.created_at,
            last_active=self.last_active
        )
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the session."""        async with self._lock:
            try:
                # Create connector
                self.connector = aiohttp.TCPConnector(
                    limit=self.config.max_connections,
                    limit_per_host=self.config.max_connections,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    ssl=False if self.config.domain.startswith('http://') else True
                )
                
                # Create timeout
                timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                
                # Create session
                self.http_session = aiohttp.ClientSession(
                    connector=self.connector,
                    timeout=timeout,
                    headers=self.config.headers
                )
                
                self.state = SessionState.ACTIVE
                self.logger.info(f"Session initialized for domain: {self.config.domain}")
                
                # Authenticate if configured
                if self.config.auth_config:
                    await self.authenticate()
                    
            except Exception as e:
                self.state = SessionState.ERROR
                self.logger.error(f"Session initialization failed: {e}")
                raise
                
    async def authenticate(self) -> bool:
        """Authenticate the session."""        if not self.config.auth_config:
            return True
            
        async with self._lock:
            try:
                self.state = SessionState.AUTHENTICATING
                auth_config = self.config.auth_config
                self.metrics.auth_attempts += 1
                
                if auth_config.auth_type == AuthenticationType.BASIC:
                    success = await self._authenticate_basic(auth_config)
                elif auth_config.auth_type == AuthenticationType.BEARER:
                    success = await self._authenticate_bearer(auth_config)
                elif auth_config.auth_type == AuthenticationType.OAUTH2:
                    success = await self._authenticate_oauth2(auth_config)
                elif auth_config.auth_type == AuthenticationType.FORM_LOGIN:
                    success = await self._authenticate_form_login(auth_config)
                elif auth_config.auth_type == AuthenticationType.API_KEY:
                    success = await self._authenticate_api_key(auth_config)
                elif auth_config.auth_type == AuthenticationType.COOKIES:
                    success = await self._authenticate_cookies(auth_config)
                else:
                    success = True  # No authentication
                    
                if success:
                    self.authenticated = True
                    self.state = SessionState.AUTHENTICATED
                    self.auth_expires_at = auth_config.expires_at
                    self.logger.info("Session authentication successful")
                else:
                    self.metrics.auth_failures += 1
                    self.logger.warning("Session authentication failed")
                    
                return success
                
            except Exception as e:
                self.metrics.auth_failures += 1
                self.state = SessionState.ERROR
                self.logger.error(f"Authentication error: {e}")
                return False
                
    async def _authenticate_basic(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using Basic Authentication."""        if not auth_config.username or not auth_config.password:
            return False
            
        auth_string = f"{auth_config.username}:{auth_config.password}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        self.http_session.headers['Authorization'] = f"Basic {auth_bytes}"
        return True
        
    async def _authenticate_bearer(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using Bearer token."""        if not auth_config.token:
            return False
            
        self.http_session.headers['Authorization'] = f"Bearer {auth_config.token}"
        self.auth_token = auth_config.token
        return True
        
    async def _authenticate_oauth2(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using OAuth2."""        # OAuth2 implementation would depend on specific provider
        return False
        
    async def _authenticate_form_login(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using form login."""        try:
            # Perform form login
            if not auth_config.form_data:
                return False
                
            # Implementation would depend on specific login form
            # This is a placeholder
            return False
            
        except Exception as e:
            self.logger.error(f"Form login failed: {e}")
            return False
            
    async def _authenticate_api_key(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using API key."""        if not auth_config.api_key:
            return False
            
        # Add API key to headers (common patterns)
        self.http_session.headers['X-API-Key'] = auth_config.api_key
        return True
        
    async def _authenticate_cookies(self, auth_config: SessionCredentials) -> bool:
        """Authenticate using cookies."""        # Cookie-based authentication would load existing cookies
        return True
        
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request through managed session."""        if not self.http_session:
            raise RuntimeError("Session not initialized")
            
        # Check if session is expired
        if self.is_expired():
            raise RuntimeError("Session expired")
            
        # Check if authentication is expired
        if self.is_auth_expired():
            await self.authenticate()
            
        try:
            self.metrics.request_count += 1
            start_time = time.time()
            
            # Make request
            response = await self.http_session.request(method, url, **kwargs)
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(response, response_time)
            
            self.last_active = datetime.utcnow()
            
            return response
            
        except Exception as e:
            self.metrics.error_count += 1
            self.logger.error(f"Request failed: {e}")
            raise
            
    def _update_metrics(self, response: aiohttp.ClientResponse, response_time: float):
        """Update session metrics."""        if response.status < 400:
            self.metrics.success_count += 1
        else:
            self.metrics.error_count += 1
            
        # Update average response time
        total_requests = self.metrics.request_count
        current_avg = self.metrics.average_response_time
        self.metrics.average_response_time = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
    def is_expired(self) -> bool:
        """Check if session is expired."""        return datetime.utcnow() > self.expires_at
        
    def is_auth_expired(self) -> bool:
        """Check if authentication is expired."""        if not self.auth_expires_at:
            return False
        return datetime.utcnow() > self.auth_expires_at
        
    async def renew(self):
        """Renew session."""        self.expires_at = datetime.utcnow() + timedelta(seconds=self.config.session_lifetime)
        if self.config.auth_config and self.is_auth_expired():
            await self.authenticate()
            
    async def close(self):
        """Close the session."""        try:
            if self.http_session:
                await self.http_session.close()
                
            if self.connector:
                await self.connector.close()
                
            self.state = SessionState.INACTIVE
            self.logger.info("Session closed")
            
        except Exception as e:
            self.logger.error(f"Session close error: {e}")


class SessionManager:
    """    Advanced session management system for crawler operations.
    
    Provides session pooling, authentication, persistence, and optimization
    for efficient multi-domain crawling operations.
    """    
    def __init__(self, config: Optional[SessionConfig] = None):
        """Initialize session manager."""        self.config = config or SessionConfig()
        self.logger = get_logger(self.__class__.__name__)
        
        # Session storage
        self.active_sessions: Dict[str, ManagedSession] = {}
        self.session_pools: Dict[str, List[ManagedSession]] = {}
        self.session_configs: Dict[str, SessionConfiguration] = {}
        
        # Session persistence
        self.persistence_db: Optional[str] = None
        self.encryption = SessionEncryption()
        self.cookie_manager = CookieManager()
        
        # Cleanup tracking
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 300  # 5 minutes
        
        # Statistics
        self.stats = {
            'total_sessions_created': 0,
            'active_sessions': 0,
            'expired_sessions': 0,
            'authentication_failures': 0,
            'total_requests': 0,
            'success_rate': 0.0
        }
        
        # Initialize persistence
        if self.config.ENABLE_PERSISTENCE:
            self._initialize_persistence()
            
    def _initialize_persistence(self):
        """Initialize session persistence storage."""        try:
            self.persistence_db = self.config.PERSISTENCE_PATH
            Path(self.persistence_db).parent.mkdir(parents=True, exist_ok=True)
            
            # Create persistence database
            with sqlite3.connect(self.persistence_db) as conn:
                conn.execute("""                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        domain TEXT NOT NULL,
                        config_data TEXT NOT NULL,
                        cookies_data TEXT,
                        auth_data TEXT,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        last_active TEXT NOT NULL
                    )
                """)
                
                conn.execute("""                    CREATE TABLE IF NOT EXISTS session_metrics (
                        session_id TEXT,
                        metric_name TEXT,
                        metric_value REAL,
                        timestamp TEXT,
                        PRIMARY KEY (session_id, metric_name, timestamp)
                    )
                """)
                
            self.logger.info("Session persistence initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize persistence: {e}")
            self.config.ENABLE_PERSISTENCE = False
            
    async def start(self):
        """Start session manager."""        try:
            # Load persisted sessions
            if self.config.ENABLE_PERSISTENCE:
                await self._load_persisted_sessions()
                
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info("Session manager started")
            
        except Exception as e:
            self.logger.error(f"Failed to start session manager: {e}")
            raise
            
    async def _load_persisted_sessions(self):
        """Load sessions from persistence storage."""        try:
            with sqlite3.connect(self.persistence_db) as conn:
                cursor = conn.execute("""                    SELECT session_id, domain, config_data, cookies_data, auth_data, 
                           created_at, expires_at, last_active
                    FROM sessions
                    WHERE expires_at > ?
                """, (datetime.utcnow().isoformat(),))
                
                for row in cursor.fetchall():
                    try:
                        session_id, domain, config_data, cookies_data, auth_data, created_at, expires_at, last_active = row
                        
                        # Decrypt and deserialize config
                        config_json = self.encryption.decrypt(config_data)
                        config_dict = json.loads(config_json)
                        
                        # Recreate session configuration
                        session_config = SessionConfiguration(**config_dict)
                        self.session_configs[domain] = session_config
                        
                        self.logger.info(f"Loaded persisted session for domain: {domain}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to load session {session_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to load persisted sessions: {e}")
            
    async def get_session(self, domain: str, config: Optional[SessionConfiguration] = None) -> ManagedSession:
        """        Get or create a session for the specified domain.
        
        Args:
            domain: Target domain
            config: Optional session configuration
            
        Returns:
            ManagedSession instance
        """        try:
            # Check for existing active session
            existing_session = await self._get_existing_session(domain)
            if existing_session:
                return existing_session
                
            # Create new session
            session = await self._create_session(domain, config)
            
            # Store session
            self.active_sessions[session.session_id] = session
            
            # Add to domain pool
            if domain not in self.session_pools:
                self.session_pools[domain] = []
            self.session_pools[domain].append(session)
            
            # Update statistics
            self.stats['total_sessions_created'] += 1
            self.stats['active_sessions'] = len(self.active_sessions)
            
            self.logger.info(f"Created new session {session.session_id} for domain: {domain}")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to get session for domain {domain}: {e}")
            raise
            
    async def _get_existing_session(self, domain: str) -> Optional[ManagedSession]:
        """Get existing active session for domain."""        domain_sessions = self.session_pools.get(domain, [])
        
        for session in domain_sessions:
            if (session.state in [SessionState.ACTIVE, SessionState.AUTHENTICATED] and
                not session.is_expired()):
                return session
                
        return None
        
    async def _create_session(self, domain: str, config: Optional[SessionConfiguration] = None) -> ManagedSession:
        """Create new managed session."""        try:
            # Use provided config or get default
            if config:
                session_config = config
            else:
                session_config = self.session_configs.get(domain)
                if not session_config:
                    session_config = self._create_default_config(domain)
                    
            # Generate session ID
            session_id = self._generate_session_id(domain)
            
            # Create managed session
            session = ManagedSession(session_id, session_config)
            await session.initialize()
            
            # Persist session if enabled
            if self.config.ENABLE_PERSISTENCE:
                await self._persist_session(session)
                
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
            
    def _create_default_config(self, domain: str) -> SessionConfiguration:
        """Create default session configuration for domain."""        return SessionConfiguration(
            domain=domain,
            max_connections=self.config.DEFAULT_MAX_CONNECTIONS,
            timeout=self.config.DEFAULT_TIMEOUT,
            retry_attempts=self.config.DEFAULT_RETRY_ATTEMPTS,
            user_agent=self.config.DEFAULT_USER_AGENT,
            headers=self.config.DEFAULT_HEADERS.copy()
        )
        
    def _generate_session_id(self, domain: str) -> str:
        """Generate unique session ID."""        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(8)
        domain_hash = hashlib.md5(domain.encode()).hexdigest()[:8]
        
        return f"sess_{domain_hash}_{timestamp}_{random_part}"
        
    async def _persist_session(self, session: ManagedSession):
        """Persist session to storage."""        try:
            if not self.persistence_db:
                return
                
            # Serialize session config
            config_dict = {
                'domain': session.config.domain,
                'max_connections': session.config.max_connections,
                'timeout': session.config.timeout,
                'retry_attempts': session.config.retry_attempts,
                'user_agent': session.config.user_agent,
                'headers': session.config.headers,
                'cookies_enabled': session.config.cookies_enabled,
                'javascript_enabled': session.config.javascript_enabled,
                'session_lifetime': session.config.session_lifetime
            }
            
            config_json = json.dumps(config_dict)
            encrypted_config = self.encryption.encrypt(config_json)
            
            # Store in database
            with sqlite3.connect(self.persistence_db) as conn:
                conn.execute("""                    INSERT OR REPLACE INTO sessions 
                    (session_id, domain, config_data, created_at, expires_at, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.config.domain,
                    encrypted_config,
                    session.created_at.isoformat(),
                    session.expires_at.isoformat(),
                    session.last_active.isoformat()
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to persist session: {e}")
            
    def configure_domain(self, domain: str, config: SessionConfiguration):
        """Configure session settings for a domain."""        self.session_configs[domain] = config
        self.logger.info(f"Domain configuration updated: {domain}")
        
    async def authenticate_domain(self, domain: str, credentials: SessionCredentials) -> bool:
        """Authenticate sessions for a domain."""        try:
            # Update domain configuration
            if domain in self.session_configs:
                self.session_configs[domain].auth_config = credentials
            else:
                config = self._create_default_config(domain)
                config.auth_config = credentials
                self.session_configs[domain] = config
                
            # Authenticate existing sessions
            domain_sessions = self.session_pools.get(domain, [])
            success_count = 0
            
            for session in domain_sessions:
                session.config.auth_config = credentials
                if await session.authenticate():
                    success_count += 1
                    
            self.logger.info(f"Authenticated {success_count}/{len(domain_sessions)} sessions for domain: {domain}")
            
            return success_count > 0 or len(domain_sessions) == 0
            
        except Exception as e:
            self.logger.error(f"Domain authentication failed for {domain}: {e}")
            return False
            
    async def close_session(self, session_id: str) -> bool:
        """Close a specific session."""        try:
            if session_id not in self.active_sessions:
                return False
                
            session = self.active_sessions.pop(session_id)
            await session.close()
            
            # Remove from domain pool
            domain_sessions = self.session_pools.get(session.config.domain, [])
            if session in domain_sessions:
                domain_sessions.remove(session)
                
            # Update statistics
            self.stats['active_sessions'] = len(self.active_sessions)
            
            self.logger.info(f"Session closed: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close session {session_id}: {e}")
            return False
            
    async def close_domain_sessions(self, domain: str) -> int:
        """Close all sessions for a domain."""        closed_count = 0
        domain_sessions = self.session_pools.get(domain, []).copy()
        
        for session in domain_sessions:
            if await self.close_session(session.session_id):
                closed_count += 1
                
        if domain in self.session_pools:
            self.session_pools[domain].clear()
            
        self.logger.info(f"Closed {closed_count} sessions for domain: {domain}")
        return closed_count
        
    async def _cleanup_loop(self):
        """Background cleanup task for expired sessions."""        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions."""        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_expired() or session.state == SessionState.ERROR:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            await self.close_session(session_id)
            
        if expired_sessions:
            self.stats['expired_sessions'] += len(expired_sessions)
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
    async def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get metrics for a specific session."""        session = self.active_sessions.get(session_id)
        if session:
            return session.metrics
        return None
        
    async def get_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """Get aggregated metrics for a domain."""        domain_sessions = self.session_pools.get(domain, [])
        
        if not domain_sessions:
            return {}
            
        total_requests = sum(s.metrics.request_count for s in domain_sessions)
        total_success = sum(s.metrics.success_count for s in domain_sessions)
        total_errors = sum(s.metrics.error_count for s in domain_sessions)
        avg_response_time = sum(s.metrics.average_response_time for s in domain_sessions) / len(domain_sessions)
        
        return {
            'domain': domain,
            'active_sessions': len(domain_sessions),
            'total_requests': total_requests,
            'success_count': total_success,
            'error_count': total_errors,
            'success_rate': total_success / total_requests if total_requests > 0 else 0.0,
            'average_response_time': avg_response_time,
            'oldest_session': min(s.created_at for s in domain_sessions),
            'newest_session': max(s.created_at for s in domain_sessions)
        }
        
    async def get_manager_stats(self) -> Dict[str, Any]:
        """Get session manager statistics."""        # Update current stats
        self.stats['active_sessions'] = len(self.active_sessions)
        
        # Calculate success rate
        if self.stats['total_requests'] > 0:
            success_requests = sum(s.metrics.success_count for s in self.active_sessions.values())
            self.stats['success_rate'] = success_requests / self.stats['total_requests']
            
        return self.stats.copy()
        
    @asynccontextmanager
    async def session_context(self, domain: str, config: Optional[SessionConfiguration] = None):
        """Context manager for session usage."""        session = None
        try:
            session = await self.get_session(domain, config)
            yield session
        finally:
            if session and self.config.AUTO_CLOSE_SESSIONS:
                await self.close_session(session.session_id)
                
    async def shutdown(self):
        """Shutdown session manager."""        try:
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                
            # Close all sessions
            session_ids = list(self.active_sessions.keys())
            for session_id in session_ids:
                await self.close_session(session_id)
                
            # Final persistence save
            if self.config.ENABLE_PERSISTENCE:
                await self._save_final_state()
                
            self.logger.info("Session manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            
    async def _save_final_state(self):
        """Save final state before shutdown."""        try:
            # Save final metrics
            if self.persistence_db:
                with sqlite3.connect(self.persistence_db) as conn:
                    timestamp = datetime.utcnow().isoformat()
                    
                    for session in self.active_sessions.values():
                        metrics = session.metrics
                        
                        # Save key metrics
                        metrics_data = [
                            (session.session_id, 'request_count', metrics.request_count, timestamp),
                            (session.session_id, 'success_count', metrics.success_count, timestamp),
                            (session.session_id, 'error_count', metrics.error_count, timestamp),
                            (session.session_id, 'average_response_time', metrics.average_response_time, timestamp),
                            (session.session_id, 'bytes_transferred', metrics.bytes_transferred, timestamp)
                        ]
                        
                        conn.executemany("""                            INSERT INTO session_metrics 
                            (session_id, metric_name, metric_value, timestamp)
                            VALUES (?, ?, ?, ?)
                        """, metrics_data)
                        
        except Exception as e:
            self.logger.error(f"Failed to save final state: {e}")


# Factory function
def create_session_manager(config: Optional[SessionConfig] = None) -> SessionManager:
    """Create and return a session manager instance."""    return SessionManager(config)


# Utility functions
async def create_authenticated_session(domain: str, credentials: SessionCredentials) -> ManagedSession:
    """Create an authenticated session for a domain."""    config = SessionConfiguration(
        domain=domain,
        auth_config=credentials
    )
    
    manager = create_session_manager()
    return await manager.get_session(domain, config)


async def bulk_authenticate_domains(domain_credentials: Dict[str, SessionCredentials]) -> Dict[str, bool]:
    """Authenticate multiple domains in bulk."""    manager = create_session_manager()
    results = {}
    
    try:
        await manager.start()
        
        for domain, credentials in domain_credentials.items():
            try:
                result = await manager.authenticate_domain(domain, credentials)
                results[domain] = result
            except Exception as e:
                results[domain] = False
                
    finally:
        await manager.shutdown()
        
    return results
