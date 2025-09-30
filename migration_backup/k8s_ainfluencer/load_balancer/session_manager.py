"""Session Manager for Load Balancer - IA Influencer Agent Platform

Advanced session affinity and sticky session management for the IA Influencer
Agent platform. Ensures consistent user experience across microservices while
maintaining load distribution efficiency.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import hashlib
import time
import json
import redis
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
from urllib.parse import urlencode
import hmac
import base64

logger = logging.getLogger(__name__)


class SessionAffinityType(Enum):
    """
Session affinity types for different services"""

    NONE = "none"
    IP_HASH = "ip_hash"
    COOKIE_BASED = "cookie"
    HEADER_BASED = "header"
    JWT_BASED = "jwt"
    USER_ID_BASED = "user_id"
    LEAST_CONNECTIONS = "least_conn"
    ROUND_ROBIN = "round_robin"


@dataclass
class SessionConfiguration:
    """Session configuration for a service"""
    service_name: str
    affinity_type: SessionAffinityType
    cookie_name: str = "ia_session"
    header_name: str = "X-Session-ID"
    timeout: int = 3600  # 1 hour
    max_idle_time: int = 1800  # 30 minutes
    sticky_sessions: bool = True
    failover_enabled: bool = True
    health_check_interval: int = 30
    max_retries: int = 3


@dataclass
class ServerNode:
    """Server node information"""
    id: str
    host: str
    port: int
    weight: int = 1
    current_connections: int = 0
    max_connections: int = 1000
    health_status: str = "healthy"
    last_health_check: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0


@dataclass
class UserSession:
    """User session information"""
    session_id: str
    user_id: Optional[str]
    server_node_id: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Enterprise Session Manager for Load Balancer
    
    Manages session affinity, sticky sessions, and intelligent traffic
    distribution for the IA Influencer Agent platform's microservices.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, secret_key: str = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.secret_key = secret_key or self._generate_secret_key()
        
        # Session storage
        self.active_sessions: Dict[str, UserSession] = {}
        self.server_nodes: Dict[str, ServerNode] = {}
        self.service_configs: Dict[str, SessionConfiguration] = {}
        
        # Runtime metrics
        self.session_count = 0
        self.total_requests = 0
        self.session_hits = 0
        self.session_misses = 0
        self.failover_count = 0
        
        # Background tasks
        self.cleanup_task = None
        self.health_check_task = None
        self.is_running = False
        
        logger.info("Session Manager initialized")
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes).decode('utf-8')
    
    async def initialize(self) -> None:
        """
Initialize session manager"""
        try:
            logger.info("Initializing Session Manager...")
            
            # Configure platform services
            await self._configure_platform_services()
            
            # Initialize server nodes
            await self._initialize_server_nodes()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            logger.info("Session Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Session Manager: {e}")
            raise
    
    async def _configure_platform_services(self) -> None:
        """Configure session settings for platform services"""
        # Fingerprinting service - high CPU, needs sticky sessions
        self.service_configs["fingerprinting"] = SessionConfiguration(
            service_name="fingerprinting",
            affinity_type=SessionAffinityType.USER_ID_BASED,
            timeout=7200,  # 2 hours for long processing
            sticky_sessions=True,
            failover_enabled=True
        )
        
        # Protection service - stateless, can use round robin
        self.service_configs["protection"] = SessionConfiguration(
            service_name="protection",
            affinity_type=SessionAffinityType.LEAST_CONNECTIONS,
            timeout=3600,
            sticky_sessions=False,
            failover_enabled=True
        )
        
        # Monetization service - needs user affinity
        self.service_configs["monetization"] = SessionConfiguration(
            service_name="monetization",
            affinity_type=SessionAffinityType.USER_ID_BASED,
            timeout=3600,
            sticky_sessions=True,
            failover_enabled=True
        )
        
        # AI Agent service - needs user context
        self.service_configs["ai_agent"] = SessionConfiguration(
            service_name="ai_agent",
            affinity_type=SessionAffinityType.USER_ID_BASED,
            timeout=1800,  # 30 minutes
            sticky_sessions=True,
            failover_enabled=True
        )
        
        # Crawler service - can be stateless
        self.service_configs["crawlers"] = SessionConfiguration(
            service_name="crawlers",
            affinity_type=SessionAffinityType.ROUND_ROBIN,
            timeout=3600,
            sticky_sessions=False,
            failover_enabled=True
        )
        
        logger.info("Platform services configured for session management")
    
    async def _initialize_server_nodes(self) -> None:
        """Initialize server nodes for each service"""
        # Fingerprinting service nodes
        for i in range(3):
            node_id = f"fingerprinting_{i+1}"
            self.server_nodes[node_id] = ServerNode(
                id=node_id,
                host="localhost",
                port=8001 + i,
                weight=1,
                max_connections=500  # CPU intensive
            )
        
        # Protection service nodes
        for i in range(2):
            node_id = f"protection_{i+1}"
            self.server_nodes[node_id] = ServerNode(
                id=node_id,
                host="localhost",
                port=8002 + i,
                weight=1,
                max_connections=1000
            )
        
        # Monetization service nodes
        for i in range(2):
            node_id = f"monetization_{i+1}"
            self.server_nodes[node_id] = ServerNode(
                id=node_id,
                host="localhost",
                port=8003 + i,
                weight=1,
                max_connections=1000
            )
        
        # AI Agent service nodes
        for i in range(2):
            node_id = f"ai_agent_{i+1}"
            self.server_nodes[node_id] = ServerNode(
                id=node_id,
                host="localhost",
                port=8004 + i,
                weight=1,
                max_connections=800
            )
        
        # Crawler service nodes
        for i in range(2):
            node_id = f"crawlers_{i+1}"
            self.server_nodes[node_id] = ServerNode(
                id=node_id,
                host="localhost",
                port=8005 + i,
                weight=1,
                max_connections=1200
            )
        
        logger.info(f"Initialized {len(self.server_nodes)} server nodes")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        self.cleanup_task = asyncio.create_task(self._session_cleanup_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Background tasks started")
    
    async def create_session(self, user_id: Optional[str], ip_address: str, 
                           user_agent: str, service_name: str,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new user session"""
        try:
            session_id = self._generate_session_id(user_id, ip_address)
            
            # Get service configuration
            config = self.service_configs.get(service_name)
            if not config:
                raise ValueError(f"Unknown service: {service_name}")
            
            # Select server node based on affinity type
            server_node_id = await self._select_server_node(
                service_name, user_id, ip_address, user_agent
            )
            
            # Create session
            now = datetime.now()
            expires_at = now + timedelta(seconds=config.timeout)
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                server_node_id=server_node_id,
                created_at=now,
                last_accessed=now,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {}
            )
            
            # Store session
            self.active_sessions[session_id] = session
            await self._store_session_in_redis(session)
            
            # Update metrics
            self.session_count += 1
            
            logger.debug(f"Session created: {session_id} -> {server_node_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_server_for_session(self, session_id: str, 
                                   service_name: str) -> Optional[ServerNode]:
        """Get the server node for a session"""
        try:
            # Check local cache first
            session = self.active_sessions.get(session_id)
            
            if not session:
                # Try to load from Redis
                session = await self._load_session_from_redis(session_id)
                if session:
                    self.active_sessions[session_id] = session
            
            if not session or session.expires_at < datetime.now():
                self.session_misses += 1
                return None
            
            # Update last accessed time
            session.last_accessed = datetime.now()
            await self._store_session_in_redis(session)
            
            # Get server node
            server_node = self.server_nodes.get(session.server_node_id)
            if not server_node or server_node.health_status != "healthy":
                # Failover to another node
                new_node_id = await self._failover_session(session, service_name)
                if new_node_id:
                    server_node = self.server_nodes.get(new_node_id)
                    self.failover_count += 1
            
            self.session_hits += 1
            self.total_requests += 1
            
            return server_node
            
        except Exception as e:
            logger.error(f"Failed to get server for session {session_id}: {e}")
            return None
    
    async def _select_server_node(self, service_name: str, user_id: Optional[str],
                                ip_address: str, user_agent: str) -> str:
        """Select the best server node based on affinity type"""
        config = self.service_configs[service_name]
        
        # Get available nodes for the service
        available_nodes = [
            node for node in self.server_nodes.values()
            if node.id.startswith(service_name) and node.health_status == "healthy"
        ]
        
        if not available_nodes:
            raise RuntimeError(f"No healthy nodes available for service {service_name}")
        
        if config.affinity_type == SessionAffinityType.IP_HASH:
            # Hash-based on IP address
            hash_value = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
            selected_node = available_nodes[hash_value % len(available_nodes)]
            
        elif config.affinity_type == SessionAffinityType.USER_ID_BASED:
            # Hash-based on user ID
            if user_id:
                hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                selected_node = available_nodes[hash_value % len(available_nodes)]
            else:
                # Fallback to least connections
                selected_node = min(available_nodes, key=lambda x: x.current_connections)
                
        elif config.affinity_type == SessionAffinityType.LEAST_CONNECTIONS:
            # Select node with least connections
            selected_node = min(available_nodes, key=lambda x: x.current_connections)
            
        elif config.affinity_type == SessionAffinityType.ROUND_ROBIN:
            # Simple round robin
            node_index = self.total_requests % len(available_nodes)
            selected_node = available_nodes[node_index]
            
        else:
            # Default to round robin
            node_index = self.total_requests % len(available_nodes)
            selected_node = available_nodes[node_index]
        
        # Update connection count
        selected_node.current_connections += 1
        
        return selected_node.id
    
    async def _failover_session(self, session: UserSession, 
                              service_name: str) -> Optional[str]:
        """Failover session to a healthy node"""
        try:
            # Get new server node
            new_node_id = await self._select_server_node(
                service_name, session.user_id, session.ip_address, session.user_agent
            )
            
            # Update session
            old_node_id = session.server_node_id
            session.server_node_id = new_node_id
            await self._store_session_in_redis(session)
            
            # Update connection counts
            if old_node_id in self.server_nodes:
                self.server_nodes[old_node_id].current_connections -= 1
            
            logger.info(f"Session {session.session_id} failed over: {old_node_id} -> {new_node_id}")
            return new_node_id
            
        except Exception as e:
            logger.error(f"Failover failed for session {session.session_id}: {e}")
            return None
    
    def _generate_session_id(self, user_id: Optional[str], ip_address: str) -> str:
        """Generate a unique session ID"""
        timestamp = str(int(time.time() * 1000))
        data = f"{user_id or 'anonymous'}:{ip_address}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"ia_session_{timestamp}_{signature[:16]}"
    
    async def _store_session_in_redis(self, session: UserSession) -> None:
        """Store session data in Redis"""
        try:
            key = f"session:{session.session_id}"
            data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "server_node_id": session.server_node_id,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "metadata": session.metadata
            }
            
            ttl = int((session.expires_at - datetime.now()).total_seconds())
            if ttl > 0:
                self.redis_client.setex(key, ttl, json.dumps(data))
                
        except Exception as e:
            logger.error(f"Failed to store session in Redis: {e}")
    
    async def _load_session_from_redis(self, session_id: str) -> Optional[UserSession]:
        """Load session data from Redis"""
        try:
            key = f"session:{session_id}"
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            session_data = json.loads(data)
            return UserSession(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                server_node_id=session_data["server_node_id"],
                created_at=datetime.fromisoformat(session_data["created_at"]),
                last_accessed=datetime.fromisoformat(session_data["last_accessed"]),
                expires_at=datetime.fromisoformat(session_data["expires_at"]),
                ip_address=session_data["ip_address"],
                user_agent=session_data["user_agent"],
                metadata=session_data["metadata"]
            )
            
        except Exception as e:
            logger.error(f"Failed to load session from Redis: {e}")
            return None
    
    async def _session_cleanup_loop(self) -> None:
        """Background task to cleanup expired sessions"""
        while self.is_running:
            try:
                now = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if session.expires_at < now:
                        expired_sessions.append(session_id)
                
                # Remove expired sessions
                for session_id in expired_sessions:
                    session = self.active_sessions.pop(session_id, None)
                    if session and session.server_node_id in self.server_nodes:
                        self.server_nodes[session.server_node_id].current_connections -= 1
                    
                    # Remove from Redis
                    try:
                        self.redis_client.delete(f"session:{session_id}")
                    except Exception:
                        pass
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                self.session_count = len(self.active_sessions)
                
                # Sleep for 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self) -> None:
        """Background task to monitor server node health"""
        while self.is_running:
            try:
                for node in self.server_nodes.values():
                    try:
                        # Simple TCP connection test
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        result = sock.connect_ex((node.host, node.port))
                        sock.close()
                        
                        if result == 0:
                            node.health_status = "healthy"
                        else:
                            node.health_status = "unhealthy"
                            logger.warning(f"Node {node.id} health check failed")
                        
                        node.last_health_check = datetime.now()
                        
                    except Exception as e:
                        node.health_status = "unhealthy"
                        logger.error(f"Health check error for node {node.id}: {e}")
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session management statistics"""
        healthy_nodes = sum(1 for node in self.server_nodes.values() 
                          if node.health_status == "healthy")
        
        hit_ratio = 0.0
        if self.total_requests > 0:
            hit_ratio = (self.session_hits / self.total_requests) * 100
        
        return {
            "active_sessions": self.session_count,
            "total_requests": self.total_requests,
            "session_hits": self.session_hits,
            "session_misses": self.session_misses,
            "hit_ratio_percentage": round(hit_ratio, 2),
            "failover_count": self.failover_count,
            "total_nodes": len(self.server_nodes),
            "healthy_nodes": healthy_nodes,
            "services_configured": len(self.service_configs),
            "is_running": self.is_running
        }
    
    async def shutdown(self) -> None:
        """Shutdown session manager"""
        try:
            logger.info("Shutting down Session Manager...")
            
            self.is_running = False
            
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Store remaining sessions to Redis
            for session in self.active_sessions.values():
                await self._store_session_in_redis(session)
            
            logger.info("Session Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Session Manager shutdown: {e}")
