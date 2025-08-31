"""
Session Manager Module
======================

Professional session management for web crawling with persistent state.
Implements intelligent session handling, cookie management, and state persistence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import logging
import pickle
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import time

from .proxy_manager import ProxyManager, ProxyInfo
from .user_agent_rotator import UserAgentRotator, UserAgentInfo
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class SessionState:
    """Session state information."""
    session_id: str
    user_agent: str
    proxy: Optional[Dict] = None
    cookies: Dict[str, Any] = None
    headers: Dict[str, str] = None
    created_at: datetime = None
    last_used: datetime = None
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    is_active: bool = True
    platform: Optional[str] = None
    domain: Optional[str] = None

@dataclass
class SessionMetrics:
    """Session performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    data_transferred: int = 0
    cookies_collected: int = 0
    last_activity: Optional[datetime] = None
    success_rate: float = 1.0

class SessionManager:
    """
    Professional session management system.
    
    Features:
    - Persistent session state
    - Cookie management
    - Proxy rotation per session
    - User agent consistency
    - Session pooling
    - Automatic cleanup
    - Performance tracking
    - State persistence
    - Anti-detection measures
    - Session recovery
    """
    
    def __init__(
        self,
        proxy_manager: Optional[ProxyManager] = None,
        user_agent_rotator: Optional[UserAgentRotator] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        """Initialize session manager."""
        self.proxy_manager = proxy_manager or ProxyManager()
        self.user_agent_rotator = user_agent_rotator or UserAgentRotator()
        self.rate_limiter = rate_limiter
        
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.session_states: Dict[str, SessionState] = {}
        self.session_metrics: Dict[str, SessionMetrics] = {}
        
        # Configuration
        self.max_sessions = 100
        self.session_timeout = 3600  # 1 hour
        self.max_requests_per_session = 1000
        self.session_cleanup_interval = 300  # 5 minutes
        self.persist_sessions = True
        self.session_data_dir = Path("./data/sessions")
        
        # Ensure data directory exists
        self.session_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load persisted sessions
        if self.persist_sessions:
            self._load_session_states()
        
        # Start background cleanup
        asyncio.create_task(self._session_cleanup_task())
    
    async def create_session(
        self,
        platform: Optional[str] = None,
        domain: Optional[str] = None,
        mobile: Optional[bool] = None,
        country: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a new session with specified configuration.
        
        Args:
            platform: Target platform name
            domain: Target domain
            mobile: Force mobile or desktop user agent
            country: Preferred proxy country
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        
        # Check session limits
        if len(self.sessions) >= self.max_sessions:
            await self._cleanup_oldest_session()
        
        # Get user agent
        user_agent = self.user_agent_rotator.get_user_agent(mobile=mobile)
        
        # Get proxy
        proxy = None
        if self.proxy_manager:
            proxy_info = await self.proxy_manager.get_proxy(country)
            if proxy_info:
                proxy = self._proxy_to_dict(proxy_info)
        
        # Generate headers
        headers = self.user_agent_rotator.get_headers(user_agent)
        
        # Create session configuration
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector_kwargs = {
            'limit': 100,
            'limit_per_host': 10,
            'ttl_dns_cache': 300,
            'use_dns_cache': True,
        }
        
        if proxy:
            connector_kwargs['trust_env'] = True
        
        connector = aiohttp.TCPConnector(**connector_kwargs)
        
        # Create aiohttp session
        session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers,
            cookie_jar=aiohttp.CookieJar()
        )
        
        # Store session
        self.sessions[session_id] = session
        
        # Create session state
        session_state = SessionState(
            session_id=session_id,
            user_agent=user_agent.string,
            proxy=proxy,
            cookies={},
            headers=headers,
            created_at=datetime.now(),
            last_used=datetime.now(),
            platform=platform,
            domain=domain
        )
        
        self.session_states[session_id] = session_state
        self.session_metrics[session_id] = SessionMetrics()
        
        logger.info(f"Created session {session_id} for platform: {platform}")
        
        # Persist session state
        if self.persist_sessions:
            await self._save_session_state(session_id)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[aiohttp.ClientSession]:
        """Get session by ID."""
        if session_id not in self.sessions:
            return None
        
        session_state = self.session_states.get(session_id)
        if not session_state or not session_state.is_active:
            return None
        
        # Check if session is expired
        if self._is_session_expired(session_state):
            await self.close_session(session_id)
            return None
        
        # Update last used
        session_state.last_used = datetime.now()
        
        return self.sessions[session_id]
    
    async def make_request(
        self,
        session_id: str,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        """
        Make HTTP request using managed session.
        
        Args:
            session_id: Session identifier
            method: HTTP method
            url: Target URL
            **kwargs: Additional aiohttp parameters
            
        Returns:
            aiohttp.ClientResponse or None
        """
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found or expired")
            return None
        
        session_state = self.session_states[session_id]
        session_metrics = self.session_metrics[session_id]
        
        # Apply rate limiting
        if self.rate_limiter and session_state.domain:
            await self.rate_limiter.wait_if_needed(session_state.domain)
        
        # Apply proxy if configured
        if session_state.proxy:
            kwargs['proxy'] = self._build_proxy_url(session_state.proxy)
        
        try:
            start_time = time.time()
            
            # Make request
            response = await session.request(method, url, **kwargs)
            
            response_time = time.time() - start_time
            
            # Update metrics
            await self._update_session_metrics(
                session_id, True, response_time, len(kwargs.get('data', b''))
            )
            
            # Update cookies
            await self._update_session_cookies(session_id, session)
            
            logger.debug(f"Request successful: {method} {url} ({response.status})")
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Update metrics
            await self._update_session_metrics(session_id, False, response_time, 0)
            
            logger.error(f"Request failed: {method} {url} - {e}")
            
            # Record proxy failure if applicable
            if session_state.proxy and self.proxy_manager:
                proxy_info = self._dict_to_proxy(session_state.proxy)
                await self.proxy_manager.record_proxy_usage(
                    proxy_info, False, response_time, str(type(e).__name__)
                )
            
            return None
    
    def _proxy_to_dict(self, proxy: ProxyInfo) -> Dict:
        """Convert ProxyInfo to dictionary."""



        return {
            'host': proxy.host,
            'port': proxy.port,
            'username': proxy.username,
            'password': proxy.password,
            'protocol': proxy.protocol
        }
    
    def _dict_to_proxy(self, proxy_dict: Dict) -> ProxyInfo:
        """Convert dictionary to ProxyInfo."""



        return ProxyInfo(
            host=proxy_dict['host'],
            port=proxy_dict['port'],
            username=proxy_dict.get('username'),
            password=proxy_dict.get('password'),
            protocol=proxy_dict.get('protocol', 'http')
        )
    
    def _build_proxy_url(self, proxy_dict: Dict) -> str:
        """Build proxy URL for aiohttp."""
        username = proxy_dict.get('username')
        password = proxy_dict.get('password')
        protocol = proxy_dict.get('protocol', 'http')
        host = proxy_dict['host']
        port = proxy_dict['port']
        
        if username and password:
            return f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            return f"{protocol}://{host}:{port}"
    
    async def _update_session_metrics(
        self,
        session_id: str,
        success: bool,
        response_time: float,
        data_size: int
    ) -> None:
        """Update session metrics."""
        state = self.session_states[session_id]
        metrics = self.session_metrics[session_id]
        
        # Update state
        state.request_count += 1
        state.last_used = datetime.now()
        
        if success:
            state.success_count += 1
        else:
            state.failure_count += 1
        
        # Update metrics
        metrics.total_requests += 1
        metrics.last_activity = datetime.now()
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update average response time
        if metrics.average_response_time == 0:
            metrics.average_response_time = response_time
        else:
            alpha = 0.3  # Exponential moving average
            metrics.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * metrics.average_response_time
            )
        
        metrics.data_transferred += data_size
        metrics.success_rate = metrics.successful_requests / metrics.total_requests
        
        # Persist metrics
        if self.persist_sessions:
            await self._save_session_state(session_id)
    
    async def _update_session_cookies(
        self,
        session_id: str,
        session: aiohttp.ClientSession
    ) -> None:
        """Update session cookies."""
        state = self.session_states[session_id]
        
        # Extract cookies
        cookies = {}
        for cookie in session.cookie_jar:
            cookies[cookie.key] = {
                'value': cookie.value,
                'domain': cookie.get('domain', ''),
                'path': cookie.get('path', '/'),
                'expires': cookie.get('expires'),
                'secure': cookie.get('secure', False),
                'httponly': cookie.get('httponly', False)
            }
        
        state.cookies = cookies
        
        # Update metrics
        metrics = self.session_metrics[session_id]
        metrics.cookies_collected = len(cookies)
    
    def _is_session_expired(self, session_state: SessionState) -> bool:
        """Check if session is expired."""
        if not session_state.last_used:
            return True
        
        age = datetime.now() - session_state.last_used
        
        # Check timeout
        if age.total_seconds() > self.session_timeout:
            return True
        
        # Check request limit
        if session_state.request_count >= self.max_requests_per_session:
            return True
        
        return False
    
    async def close_session(self, session_id: str) -> None:
        """Close and cleanup session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.close()
            del self.sessions[session_id]
        
        if session_id in self.session_states:
            self.session_states[session_id].is_active = False
            if self.persist_sessions:
                await self._save_session_state(session_id)
        
        logger.info(f"Closed session {session_id}")
    
    async def _cleanup_oldest_session(self) -> None:
        """Cleanup oldest session to make room for new ones."""
        if not self.session_states:
            return
        
        # Find oldest session
        oldest_session_id = min(
            self.session_states.keys(),
            key=lambda sid: self.session_states[sid].last_used or datetime.min
        )
        
        await self.close_session(oldest_session_id)
    
    async def _session_cleanup_task(self) -> None:
        """Background task to cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(self.session_cleanup_interval)
                
                expired_sessions = []
                for session_id, state in self.session_states.items():
                    if self._is_session_expired(state):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.close_session(session_id)
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
    
    def _save_session_state(self, session_id: str) -> None:
        """Save session state to disk."""



        try:
            state = self.session_states.get(session_id)
            metrics = self.session_metrics.get(session_id)
            
            if state and metrics:
                data = {
                    'state': asdict(state),
                    'metrics': asdict(metrics)
                }
                
                file_path = self.session_data_dir / f"{session_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(data, f, default=str, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to save session state {session_id}: {e}")
    
    def _load_session_states(self) -> None:
        """Load session states from disk."""



        try:
            for file_path in self.session_data_dir.glob("session_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    session_id = file_path.stem
                    
                    # Reconstruct state
                    state_data = data['state']
                    state_data['created_at'] = datetime.fromisoformat(state_data['created_at'])
                    state_data['last_used'] = datetime.fromisoformat(state_data['last_used'])
                    
                    state = SessionState(**state_data)
                    
                    # Reconstruct metrics
                    metrics_data = data['metrics']
                    if metrics_data.get('last_activity'):
                        metrics_data['last_activity'] = datetime.fromisoformat(metrics_data['last_activity'])
                    
                    metrics = SessionMetrics(**metrics_data)
                    
                    # Only load active, non-expired sessions
                    if state.is_active and not self._is_session_expired(state):
                        self.session_states[session_id] = state
                        self.session_metrics[session_id] = metrics
                    
                except Exception as e:
                    logger.error(f"Failed to load session {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load session states: {e}")
    
    async def get_session_statistics(self) -> Dict:
        """Get comprehensive session statistics."""
        active_sessions = len([s for s in self.session_states.values() if s.is_active])
        total_requests = sum(m.total_requests for m in self.session_metrics.values())
        total_success = sum(m.successful_requests for m in self.session_metrics.values())
        
        stats = {
            'total_sessions': len(self.session_states),
            'active_sessions': active_sessions,
            'total_requests': total_requests,
            'total_successful_requests': total_success,
            'overall_success_rate': (total_success / total_requests) if total_requests > 0 else 0,
            'session_details': []
        }
        
        for session_id, state in self.session_states.items():
            if state.is_active:
                metrics = self.session_metrics.get(session_id, SessionMetrics())
                
                session_detail = {
                    'session_id': session_id,
                    'platform': state.platform,
                    'domain': state.domain,
                    'created_at': state.created_at.isoformat() if state.created_at else None,
                    'last_used': state.last_used.isoformat() if state.last_used else None,
                    'request_count': state.request_count,
                    'success_rate': metrics.success_rate,
                    'average_response_time': metrics.average_response_time,
                    'cookies_collected': metrics.cookies_collected,
                    'has_proxy': state.proxy is not None
                }
                
                stats['session_details'].append(session_detail)
        
        return stats
    
    async def rotate_session_proxy(self, session_id: str, country: Optional[str] = None) -> bool:
        """Rotate proxy for existing session."""
        if session_id not in self.session_states:
            return False
        
        state = self.session_states[session_id]
        
        # Get new proxy
        if self.proxy_manager:
            new_proxy_info = await self.proxy_manager.get_proxy(country)
            if new_proxy_info:
                state.proxy = self._proxy_to_dict(new_proxy_info)
                
                # Persist change
                if self.persist_sessions:
                    await self._save_session_state(session_id)
                
                logger.info(f"Rotated proxy for session {session_id}")
                return True
        
        return False
    
    async def rotate_session_user_agent(self, session_id: str, mobile: Optional[bool] = None) -> bool:
        """Rotate user agent for existing session."""
        if session_id not in self.session_states:
            return False
        
        state = self.session_states[session_id]
        
        # Get new user agent
        new_user_agent = self.user_agent_rotator.get_user_agent(mobile=mobile)
        new_headers = self.user_agent_rotator.get_headers(new_user_agent)
        
        state.user_agent = new_user_agent.string
        state.headers = new_headers
        
        # Update session headers if it exists
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session._default_headers = aiohttp.multidict.CIMultiDict(new_headers)
        
        # Persist change
        if self.persist_sessions:
            await self._save_session_state(session_id)
        
        logger.info(f"Rotated user agent for session {session_id}")
        return True
    
    async def close_all_sessions(self) -> None:
        """Close all active sessions."""
        session_ids = list(self.sessions.keys())
        
        for session_id in session_ids:
            await self.close_session(session_id)
        
        logger.info(f"Closed all {len(session_ids)} sessions")
    
    def get_session_cookies(self, session_id: str) -> Optional[Dict]:
        """Get cookies for a session."""
        state = self.session_states.get(session_id)
        return state.cookies if state else None
    
    def set_session_cookies(self, session_id: str, cookies: Dict) -> bool:
        """Set cookies for a session."""
        if session_id not in self.session_states:
            return False
        
        state = self.session_states[session_id]
        state.cookies = cookies
        
        # Apply cookies to active session
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.cookie_jar.clear()
            
            for name, cookie_data in cookies.items():
                session.cookie_jar.update_cookies({
                    name: cookie_data.get('value', '')
                })
        
        # Persist change
        if self.persist_sessions:
            self._save_session_state(session_id)
        
        return True
