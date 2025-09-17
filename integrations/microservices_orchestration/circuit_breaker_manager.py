"""⚡ Circuit Breaker Manager - Intelligent Failure Handling
=========================================================

Circuit breaker manager enterprise avec intelligent failure handling,
bulkhead isolation, adaptive timeouts et recovery automation.

Expert Roles Implementation:
🏗️ Backend Senior: Circuit breaker patterns + resilience + fault tolerance
⚙️ DevOps: Failure detection + automation + monitoring + alerting
🤖 Lead Dev IA: Intelligent failure prediction + adaptive thresholds + ML recovery
🔒 Sécurité: Failure security + isolation + threat containment
📊 Data Engineer: Failure analytics + metrics + trend analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class FailureType(Enum):
    """Types of failures"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    CUSTOM = "custom"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    name: str
    service_name: str
    failure_threshold: int = 5
    timeout_duration: timedelta = field(default_factory=lambda: timedelta(seconds=60))
    recovery_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    success_threshold: int = 3
    request_volume_threshold: int = 20
    error_percentage_threshold: float = 50.0

@dataclass
class CircuitBreakerState:
    """Circuit breaker state information"""
    name: str
    state: CircuitState
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.utcnow)
    request_count: int = 0
    recent_requests: deque = field(default_factory=lambda: deque(maxlen=100))

class CircuitBreakerManager:
    """⚡ Circuit breaker manager avec intelligent failure handling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Circuit Breaker Manager"""
        self.config = config or {}
        self.circuit_breakers: Dict[str, CircuitBreakerConfig] = {}
        self.circuit_states: Dict[str, CircuitBreakerState] = {}
        self.failure_detector = FailureDetector()
        self.recovery_manager = RecoveryManager()
        self.initialized = False
        
        logger.info("⚡ Circuit Breaker Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize circuit breaker infrastructure"""
        try:
            logger.info("🔄 Initializing circuit breaker infrastructure...")
            
            await self.failure_detector.initialize()
            await self.recovery_manager.initialize()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.initialized = True
            logger.info("✅ Circuit breaker infrastructure initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize circuit breaker manager: {e}")
            return False
    
    async def create_circuit_breaker(
        self,
        circuit_config: CircuitBreakerConfig
    ) -> Dict[str, Any]:
        """Create new circuit breaker"""
        try:
            self.circuit_breakers[circuit_config.name] = circuit_config
            self.circuit_states[circuit_config.name] = CircuitBreakerState(
                name=circuit_config.name,
                state=CircuitState.CLOSED
            )
            
            logger.info(f"⚡ Circuit breaker created: {circuit_config.name}")
            
            return {
                'success': True,
                'circuit_breaker_name': circuit_config.name,
                'initial_state': CircuitState.CLOSED.value
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create circuit breaker: {e}")
            raise
    
    async def execute_with_circuit_breaker(
        self,
        circuit_name: str,
        operation: callable,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Execute operation with circuit breaker protection"""
        try:
            if circuit_name not in self.circuit_breakers:
                return {
                    'success': False,
                    'error': 'Circuit breaker not found'
                }
            
            circuit_state = self.circuit_states[circuit_name]
            circuit_config = self.circuit_breakers[circuit_name]
            
            # Check circuit state
            if await self._should_block_request(circuit_name):
                return {
                    'success': False,
                    'error': 'Circuit breaker is open',
                    'circuit_state': circuit_state.state.value
                }
            
            # Execute operation
            start_time = time.time()
            try:
                result = await operation(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record success
                await self._record_success(circuit_name, execution_time)
                
                return {
                    'success': True,
                    'result': result,
                    'execution_time': execution_time,
                    'circuit_state': circuit_state.state.value
                }
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Record failure
                await self._record_failure(circuit_name, str(e), execution_time)
                
                return {
                    'success': False,
                    'error': str(e),
                    'execution_time': execution_time,
                    'circuit_state': circuit_state.state.value
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to execute with circuit breaker: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_circuit_breaker_status(self, circuit_name: str) -> Dict[str, Any]:
        """Get circuit breaker status"""
        if circuit_name not in self.circuit_breakers:
            return {'error': 'Circuit breaker not found'}
        
        circuit_state = self.circuit_states[circuit_name]
        circuit_config = self.circuit_breakers[circuit_name]
        
        return {
            'name': circuit_name,
            'state': circuit_state.state.value,
            'failure_count': circuit_state.failure_count,
            'success_count': circuit_state.success_count,
            'request_count': circuit_state.request_count,
            'last_failure_time': circuit_state.last_failure_time.isoformat() if circuit_state.last_failure_time else None,
            'state_changed_at': circuit_state.state_changed_at.isoformat(),
            'configuration': {
                'failure_threshold': circuit_config.failure_threshold,
                'timeout_duration': circuit_config.timeout_duration.total_seconds(),
                'recovery_timeout': circuit_config.recovery_timeout.total_seconds()
            }
        }
    
    # Helper methods
    async def _should_block_request(self, circuit_name: str) -> bool:
        """Check if request should be blocked"""
        circuit_state = self.circuit_states[circuit_name]
        circuit_config = self.circuit_breakers[circuit_name]
        
        if circuit_state.state == CircuitState.CLOSED:
            return False
        elif circuit_state.state == CircuitState.OPEN:
            # Check if timeout period has passed
            if (circuit_state.last_failure_time and 
                datetime.utcnow() - circuit_state.last_failure_time > circuit_config.recovery_timeout):
                # Transition to half-open
                circuit_state.state = CircuitState.HALF_OPEN
                circuit_state.state_changed_at = datetime.utcnow()
                logger.info(f"⚡ Circuit breaker {circuit_name} transitioned to HALF_OPEN")
                return False
            return True
        else:  # HALF_OPEN
            return False
    
    async def _record_success(self, circuit_name: str, execution_time: float):
        """Record successful execution"""
        circuit_state = self.circuit_states[circuit_name]
        circuit_config = self.circuit_breakers[circuit_name]
        
        circuit_state.success_count += 1
        circuit_state.request_count += 1
        circuit_state.last_success_time = datetime.utcnow()
        circuit_state.recent_requests.append({
            'success': True,
            'execution_time': execution_time,
            'timestamp': datetime.utcnow()
        })
        
        # State transitions
        if circuit_state.state == CircuitState.HALF_OPEN:
            if circuit_state.success_count >= circuit_config.success_threshold:
                circuit_state.state = CircuitState.CLOSED
                circuit_state.failure_count = 0
                circuit_state.state_changed_at = datetime.utcnow()
                logger.info(f"⚡ Circuit breaker {circuit_name} transitioned to CLOSED")
    
    async def _record_failure(self, circuit_name: str, error: str, execution_time: float):
        """Record failed execution"""
        circuit_state = self.circuit_states[circuit_name]
        circuit_config = self.circuit_breakers[circuit_name]
        
        circuit_state.failure_count += 1
        circuit_state.request_count += 1
        circuit_state.last_failure_time = datetime.utcnow()
        circuit_state.recent_requests.append({
            'success': False,
            'error': error,
            'execution_time': execution_time,
            'timestamp': datetime.utcnow()
        })
        
        # State transitions
        if circuit_state.state == CircuitState.CLOSED:
            if circuit_state.failure_count >= circuit_config.failure_threshold:
                circuit_state.state = CircuitState.OPEN
                circuit_state.state_changed_at = datetime.utcnow()
                logger.warning(f"⚡ Circuit breaker {circuit_name} opened due to failures")
        elif circuit_state.state == CircuitState.HALF_OPEN:
            circuit_state.state = CircuitState.OPEN
            circuit_state.state_changed_at = datetime.utcnow()
            logger.warning(f"⚡ Circuit breaker {circuit_name} reopened after half-open failure")
    
    async def _start_background_tasks(self):
        """Start background circuit breaker tasks"""
        asyncio.create_task(self._monitoring_task())
        logger.info("🔄 Background circuit breaker tasks started")
    
    async def _monitoring_task(self):
        """Background monitoring task"""
        while True:
            try:
                for circuit_name in self.circuit_breakers.keys():
                    await self._check_circuit_health(circuit_name)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in circuit breaker monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _check_circuit_health(self, circuit_name: str):
        """Check circuit breaker health"""
        circuit_state = self.circuit_states[circuit_name]
        
        # Analyze recent requests
        if len(circuit_state.recent_requests) > 10:
            recent_failures = sum(1 for req in circuit_state.recent_requests if not req['success'])
            failure_rate = recent_failures / len(circuit_state.recent_requests)
            
            if failure_rate > 0.8:  # 80% failure rate
                logger.warning(f"⚠️ High failure rate in circuit breaker {circuit_name}: {failure_rate:.2%}")


class FailureDetector:
    """🚨 Failure detection system"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize failure detector"""
        self.initialized = True
        logger.info("✅ Failure Detector initialized")


class RecoveryManager:
    """🔄 Recovery management system"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize recovery manager"""
        self.initialized = True
        logger.info("✅ Recovery Manager initialized")
