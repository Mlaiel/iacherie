"""Enterprise Session Pool Management System
=========================================

Professional session pooling and lifecycle management for industrial-grade automation.
Handles session reuse, resource optimization, and automated cleanup for high-performance crawling.

Key Features:
- Session pooling and reuse for performance optimization
- Intelligent session lifecycle management
- Resource monitoring and automatic cleanup
- Session health monitoring and recovery
- Load balancing across session pools
- Performance metrics and analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
import threading
import psutil
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from ...core.config import settings
from ...core.exceptions import SessionError, ResourceError
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.health_checker import HealthChecker
from .browser_manager import BrowserConfiguration, BrowserSession, SessionStatus
from .webdriver_factory import WebDriverFactory, DriverProfile, EnvironmentType

logger = logging.getLogger(__name__)


class PoolStrategy(Enum):
    """Session pool management strategies"""    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    PERFORMANCE_BASED = "performance_based"
    RANDOM = "random"


class SessionPriority(Enum):
    """Session priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PoolConfiguration:
    """Session pool configuration"""    min_size: int = 5
    max_size: int = 20
    initial_size: int = 10
    max_idle_time: int = 300  # 5 minutes
    max_session_age: int = 3600  # 1 hour
    health_check_interval: int = 30  # 30 seconds
    cleanup_interval: int = 60  # 1 minute
    strategy: PoolStrategy = PoolStrategy.LEAST_USED
    enable_auto_scaling: bool = True
    scale_up_threshold: float = 0.8  # 80% utilization
    scale_down_threshold: float = 0.3  # 30% utilization


@dataclass
class SessionMetrics:
    """Session performance and usage metrics"""    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: float = 0.0
    total_usage_time: float = 0.0
    error_rate: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0


@dataclass
class PooledSession:
    """Enhanced session container for pool management"""    session: BrowserSession
    metrics: SessionMetrics = field(default_factory=SessionMetrics)
    priority: SessionPriority = SessionPriority.NORMAL
    pool_id: str = ""
    checkout_time: Optional[float] = None
    checkout_count: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)
    in_use: bool = False
    health_score: float = 1.0


class SessionPool:
    """    Enterprise Session Pool Management
    
    Manages a pool of browser sessions with intelligent allocation,
    health monitoring, and performance optimization.
    """    
    def __init__(self, pool_id: str, config: PoolConfiguration,
                 browser_config: BrowserConfiguration):
        self.pool_id = pool_id
        self.config = config
        self.browser_config = browser_config
        
        # Session storage
        self.sessions: Dict[str, PooledSession] = {}
        self.available_sessions: deque = deque()
        self.in_use_sessions: Set[str] = set()
        
        # Pool management
        self.factory = WebDriverFactory()
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        
        # Statistics
        self.stats = {
            'total_created': 0,
            'total_destroyed': 0,
            'total_checkouts': 0,
            'total_checkins': 0,
            'peak_usage': 0,
            'average_wait_time': 0.0
        }
        
        # Threading
        self.pool_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Monitoring tasks
        self.monitoring_active = True
        self.monitor_task = None
        self.cleanup_task = None
        
        logger.info(f"SessionPool {pool_id} initialized with config: {config}")
    
    async def initialize(self) -> None:
        """Initialize session pool with initial sessions"""        try:
            # Create initial sessions
            for i in range(self.config.initial_size):
                await self._create_session()
            
            # Start monitoring tasks
            self.monitor_task = asyncio.create_task(self._monitor_pool())
            self.cleanup_task = asyncio.create_task(self._cleanup_sessions())
            
            logger.info(f"SessionPool {self.pool_id} initialized with {len(self.sessions)} sessions")
            
        except Exception as e:
            logger.error(f"Failed to initialize session pool {self.pool_id}: {str(e)}")
            raise SessionError(f"Pool initialization failed: {str(e)}")
    
    async def checkout_session(self, priority: SessionPriority = SessionPriority.NORMAL,
                             timeout: float = 30.0) -> Optional[PooledSession]:
        """Checkout a session from the pool"""        start_time = time.time()
        
        try:
            # Wait for available session
            while time.time() - start_time < timeout:
                with self.pool_lock:
                    # Find best available session
                    session = self._select_session(priority)
                    if session:
                        # Mark as in use
                        session.in_use = True
                        session.checkout_time = time.time()
                        session.checkout_count += 1
                        session.priority = priority
                        
                        self.in_use_sessions.add(session.session.session_id)
                        self.available_sessions.remove(session.session.session_id)
                        
                        # Update statistics
                        self.stats['total_checkouts'] += 1
                        current_usage = len(self.in_use_sessions)
                        if current_usage > self.stats['peak_usage']:
                            self.stats['peak_usage'] = current_usage
                        
                        logger.debug(f"Session {session.session.session_id} checked out from pool {self.pool_id}")
                        return session
                
                # Auto-scaling if enabled
                if (self.config.enable_auto_scaling and 
                    self._should_scale_up() and 
                    len(self.sessions) < self.config.max_size):
                    await self._create_session()
                
                # Wait before retry
                await asyncio.sleep(0.1)
            
            # Timeout reached
            wait_time = time.time() - start_time
            self._update_average_wait_time(wait_time)
            logger.warning(f"Session checkout timeout for pool {self.pool_id}")
            return None
            
        except Exception as e:
            logger.error(f"Session checkout failed for pool {self.pool_id}: {str(e)}")
            raise SessionError(f"Session checkout failed: {str(e)}")
    
    async def checkin_session(self, session: PooledSession) -> bool:
        """Return a session to the pool"""        try:
            with self.pool_lock:
                session_id = session.session.session_id
                
                if session_id not in self.sessions:
                    logger.warning(f"Attempting to checkin unknown session {session_id}")
                    return False
                
                # Update session metrics
                if session.checkout_time:
                    usage_time = time.time() - session.checkout_time
                    session.metrics.total_usage_time += usage_time
                
                # Mark as available
                session.in_use = False
                session.checkout_time = None
                session.session.last_activity = time.time()
                
                self.in_use_sessions.discard(session_id)
                self.available_sessions.append(session_id)
                
                # Update statistics
                self.stats['total_checkins'] += 1
                
                logger.debug(f"Session {session_id} checked in to pool {self.pool_id}")
                return True
                
        except Exception as e:
            logger.error(f"Session checkin failed: {str(e)}")
            return False
    
    @asynccontextmanager
    async def get_session(self, priority: SessionPriority = SessionPriority.NORMAL):
        """Context manager for automatic session checkout/checkin"""        session = None
        try:
            session = await self.checkout_session(priority)
            if session:
                yield session
            else:
                raise SessionError("No session available")
        finally:
            if session:
                await self.checkin_session(session)
    
    async def _create_session(self) -> Optional[PooledSession]:
        """Create a new session and add to pool"""        try:
            # Create WebDriver instance
            driver = self.factory.create_driver(self.browser_config)
            
            # Create session object
            session_id = str(uuid.uuid4())
            browser_session = BrowserSession(
                session_id=session_id,
                browser_type=self.browser_config.browser_type,
                driver=driver,
                config=self.browser_config,
                status=SessionStatus.ACTIVE,
                created_at=time.time(),
                last_activity=time.time()
            )
            
            # Create pooled session
            pooled_session = PooledSession(
                session=browser_session,
                pool_id=self.pool_id
            )
            
            with self.pool_lock:
                self.sessions[session_id] = pooled_session
                self.available_sessions.append(session_id)
                self.stats['total_created'] += 1
            
            logger.info(f"Created new session {session_id} for pool {self.pool_id}")
            return pooled_session
            
        except Exception as e:
            logger.error(f"Failed to create session for pool {self.pool_id}: {str(e)}")
            return None
    
    async def _destroy_session(self, session_id: str) -> bool:
        """Destroy a session and cleanup resources"""        try:
            with self.pool_lock:
                pooled_session = self.sessions.get(session_id)
                if not pooled_session:
                    return False
                
                # Remove from tracking
                self.sessions.pop(session_id, None)
                self.available_sessions = deque([sid for sid in self.available_sessions if sid != session_id])
                self.in_use_sessions.discard(session_id)
            
            # Cleanup driver
            try:
                if pooled_session.session.driver:
                    pooled_session.session.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver for session {session_id}: {str(e)}")
            
            self.stats['total_destroyed'] += 1
            logger.info(f"Destroyed session {session_id} from pool {self.pool_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy session {session_id}: {str(e)}")
            return False
    
    def _select_session(self, priority: SessionPriority) -> Optional[PooledSession]:
        """Select best available session based on strategy"""        if not self.available_sessions:
            return None
        
        available_pooled_sessions = [
            self.sessions[sid] for sid in self.available_sessions 
            if sid in self.sessions and not self.sessions[sid].in_use
        ]
        
        if not available_pooled_sessions:
            return None
        
        if self.config.strategy == PoolStrategy.ROUND_ROBIN:
            return available_pooled_sessions[0]
        
        elif self.config.strategy == PoolStrategy.LEAST_USED:
            return min(available_pooled_sessions, key=lambda s: s.checkout_count)
        
        elif self.config.strategy == PoolStrategy.PERFORMANCE_BASED:
            return max(available_pooled_sessions, key=lambda s: s.health_score)
        
        elif self.config.strategy == PoolStrategy.RANDOM:
            import random
            return random.choice(available_pooled_sessions)
        
        return available_pooled_sessions[0]
    
    def _should_scale_up(self) -> bool:
        """Check if pool should scale up"""        if not self.config.enable_auto_scaling:
            return False
        
        utilization = len(self.in_use_sessions) / len(self.sessions) if self.sessions else 1.0
        return utilization >= self.config.scale_up_threshold
    
    def _should_scale_down(self) -> bool:
        """Check if pool should scale down"""        if not self.config.enable_auto_scaling:
            return False
        
        if len(self.sessions) <= self.config.min_size:
            return False
        
        utilization = len(self.in_use_sessions) / len(self.sessions)
        return utilization <= self.config.scale_down_threshold
    
    async def _monitor_pool(self) -> None:
        """Monitor pool health and performance"""        while self.monitoring_active:
            try:
                # Health checks
                await self._perform_health_checks()
                
                # Auto-scaling
                if self.config.enable_auto_scaling:
                    await self._auto_scale()
                
                # Update session metrics
                await self._update_session_metrics()
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Pool monitoring error for {self.pool_id}: {str(e)}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _cleanup_sessions(self) -> None:
        """Cleanup expired and unhealthy sessions"""        while self.monitoring_active:
            try:
                current_time = time.time()
                sessions_to_remove = []
                
                with self.pool_lock:
                    for session_id, pooled_session in self.sessions.items():
                        session = pooled_session.session
                        
                        # Check if session is expired
                        age = current_time - session.created_at
                        idle_time = current_time - session.last_activity
                        
                        should_remove = (
                            age > self.config.max_session_age or
                            (not pooled_session.in_use and idle_time > self.config.max_idle_time) or
                            session.error_count > 10 or
                            pooled_session.health_score < 0.5
                        )
                        
                        if should_remove and not pooled_session.in_use:
                            sessions_to_remove.append(session_id)
                
                # Remove expired sessions
                for session_id in sessions_to_remove:
                    await self._destroy_session(session_id)
                
                # Ensure minimum pool size
                current_size = len(self.sessions)
                if current_size < self.config.min_size:
                    sessions_to_create = self.config.min_size - current_size
                    for _ in range(sessions_to_create):
                        await self._create_session()
                
                await asyncio.sleep(self.config.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Cleanup error for pool {self.pool_id}: {str(e)}")
                await asyncio.sleep(self.config.cleanup_interval)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all sessions"""        for session_id, pooled_session in list(self.sessions.items()):
            if pooled_session.in_use:
                continue
            
            try:
                # Basic responsiveness test
                driver = pooled_session.session.driver
                current_url = driver.current_url
                
                # Update health score
                pooled_session.health_score = min(1.0, pooled_session.health_score + 0.1)
                
            except Exception as e:
                # Decrease health score
                pooled_session.health_score = max(0.0, pooled_session.health_score - 0.2)
                pooled_session.session.error_count += 1
                
                logger.warning(f"Health check failed for session {session_id}: {str(e)}")
    
    async def _auto_scale(self) -> None:
        """Perform auto-scaling based on utilization"""        if self._should_scale_up() and len(self.sessions) < self.config.max_size:
            await self._create_session()
            logger.info(f"Scaled up pool {self.pool_id} to {len(self.sessions)} sessions")
        
        elif self._should_scale_down() and len(self.sessions) > self.config.min_size:
            # Find least used session to remove
            available_sessions = [
                (sid, s) for sid, s in self.sessions.items() 
                if not s.in_use and sid in self.available_sessions
            ]
            
            if available_sessions:
                session_to_remove = min(available_sessions, key=lambda x: x[1].checkout_count)
                await self._destroy_session(session_to_remove[0])
                logger.info(f"Scaled down pool {self.pool_id} to {len(self.sessions)} sessions")
    
    async def _update_session_metrics(self) -> None:
        """Update performance metrics for all sessions"""        for pooled_session in self.sessions.values():
            try:
                # Update system metrics if session has driver
                if hasattr(pooled_session.session.driver, 'service'):
                    process = pooled_session.session.driver.service.process
                    if process:
                        psutil_process = psutil.Process(process.pid)
                        pooled_session.metrics.memory_usage = psutil_process.memory_info().rss / 1024 / 1024  # MB
                        pooled_session.metrics.cpu_usage = psutil_process.cpu_percent()
                
            except Exception as e:
                logger.debug(f"Failed to update metrics for session: {str(e)}")
    
    def _update_average_wait_time(self, wait_time: float) -> None:
        """Update average wait time statistic"""        total_checkouts = self.stats['total_checkouts']
        if total_checkouts > 0:
            current_avg = self.stats['average_wait_time']
            self.stats['average_wait_time'] = (
                (current_avg * (total_checkouts - 1) + wait_time) / total_checkouts
            )
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status information"""        with self.pool_lock:
            available_count = len(self.available_sessions)
            in_use_count = len(self.in_use_sessions)
            total_count = len(self.sessions)
            
            utilization = in_use_count / total_count if total_count > 0 else 0.0
            
            # Calculate average health score
            avg_health = (
                sum(s.health_score for s in self.sessions.values()) / total_count
                if total_count > 0 else 0.0
            )
            
            # Calculate total memory usage
            total_memory = sum(s.metrics.memory_usage for s in self.sessions.values())
            
            return {
                'pool_id': self.pool_id,
                'total_sessions': total_count,
                'available_sessions': available_count,
                'in_use_sessions': in_use_count,
                'utilization': utilization,
                'average_health_score': avg_health,
                'total_memory_usage_mb': total_memory,
                'statistics': self.stats.copy(),
                'configuration': {
                    'min_size': self.config.min_size,
                    'max_size': self.config.max_size,
                    'strategy': self.config.strategy.value,
                    'auto_scaling': self.config.enable_auto_scaling
                }
            }
    
    async def shutdown(self) -> None:
        """Shutdown pool and cleanup all resources"""        logger.info(f"Shutting down SessionPool {self.pool_id}")
        
        # Stop monitoring
        self.monitoring_active = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Destroy all sessions
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self._destroy_session(session_id)
        
        # Cleanup executor
        self.executor.shutdown(wait=True)
        
        logger.info(f"SessionPool {self.pool_id} shutdown completed")


class SessionPoolManager:
    """    Enterprise Session Pool Manager
    
    Manages multiple session pools for different browser configurations
    and use cases. Provides load balancing and failover capabilities.
    """    
    def __init__(self):
        self.pools: Dict[str, SessionPool] = {}
        self.pool_configs: Dict[str, Tuple[PoolConfiguration, BrowserConfiguration]] = {}
        
        logger.info("SessionPoolManager initialized")
    
    async def create_pool(self, pool_id: str, pool_config: PoolConfiguration,
                         browser_config: BrowserConfiguration) -> None:
        """Create and initialize a new session pool"""        if pool_id in self.pools:
            raise SessionError(f"Pool {pool_id} already exists")
        
        try:
            pool = SessionPool(pool_id, pool_config, browser_config)
            await pool.initialize()
            
            self.pools[pool_id] = pool
            self.pool_configs[pool_id] = (pool_config, browser_config)
            
            logger.info(f"Created session pool {pool_id}")
            
        except Exception as e:
            logger.error(f"Failed to create pool {pool_id}: {str(e)}")
            raise SessionError(f"Pool creation failed: {str(e)}")
    
    async def get_session(self, pool_id: str, 
                         priority: SessionPriority = SessionPriority.NORMAL) -> Optional[PooledSession]:
        """Get session from specified pool"""        pool = self.pools.get(pool_id)
        if not pool:
            raise SessionError(f"Pool {pool_id} not found")
        
        return await pool.checkout_session(priority)
    
    async def return_session(self, pool_id: str, session: PooledSession) -> bool:
        """Return session to specified pool"""        pool = self.pools.get(pool_id)
        if not pool:
            return False
        
        return await pool.checkin_session(session)
    
    @asynccontextmanager
    async def session_from_pool(self, pool_id: str, 
                               priority: SessionPriority = SessionPriority.NORMAL):
        """Context manager for pool session usage"""        pool = self.pools.get(pool_id)
        if not pool:
            raise SessionError(f"Pool {pool_id} not found")
        
        async with pool.get_session(priority) as session:
            yield session
    
    async def destroy_pool(self, pool_id: str) -> bool:
        """Destroy session pool and cleanup resources"""        pool = self.pools.get(pool_id)
        if not pool:
            return False
        
        try:
            await pool.shutdown()
            del self.pools[pool_id]
            del self.pool_configs[pool_id]
            
            logger.info(f"Destroyed session pool {pool_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy pool {pool_id}: {str(e)}")
            return False
    
    async def get_all_pool_status(self) -> Dict[str, Any]:
        """Get status for all managed pools"""        pool_statuses = {}
        
        for pool_id, pool in self.pools.items():
            pool_statuses[pool_id] = await pool.get_pool_status()
        
        return {
            'total_pools': len(self.pools),
            'pools': pool_statuses
        }
    
    async def shutdown_all(self) -> None:
        """Shutdown all pools and cleanup resources"""        logger.info("Shutting down all session pools")
        
        pool_ids = list(self.pools.keys())
        for pool_id in pool_ids:
            await self.destroy_pool(pool_id)
        
        logger.info("All session pools shut down")


# Factory functions for common pool configurations
def create_stealth_pool_config() -> PoolConfiguration:
    """Create configuration for stealth crawling pool"""    return PoolConfiguration(
        min_size=3,
        max_size=10,
        initial_size=5,
        max_idle_time=600,  # 10 minutes for stealth operations
        strategy=PoolStrategy.RANDOM,  # Random allocation for stealth
        enable_auto_scaling=True
    )


def create_performance_pool_config() -> PoolConfiguration:
    """Create configuration for high-performance pool"""    return PoolConfiguration(
        min_size=10,
        max_size=50,
        initial_size=20,
        max_idle_time=180,  # 3 minutes for fast turnover
        strategy=PoolStrategy.LEAST_USED,
        enable_auto_scaling=True,
        scale_up_threshold=0.7,
        scale_down_threshold=0.2
    )
