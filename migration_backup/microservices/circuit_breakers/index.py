"""
Circuit Breakers Service Index
Enterprise Circuit Breaker Pattern Implementation

This module provides distributed circuit breaker functionality to prevent
cascade failures and improve system resilience in microservices architecture.

Key Features:
- Automatic failure detection and isolation
- Configurable failure thresholds and timeouts
- Real-time monitoring and alerting
- Fast recovery and self-healing capabilities
- Integration with service mesh and API gateway

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    recovery_timeout: int = 30
    success_threshold: int = 2

class CircuitBreakerService:
    """Enterprise circuit breaker service"""
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.circuits: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_circuit(self, service_name: str, config: Optional[CircuitBreakerConfig] = None) -> bool:
        """Create a new circuit breaker for a service"""
        try:
            circuit_config = config or self.config
            self.circuits[service_name] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'config': circuit_config
            }
            
            self.logger.info(f"Circuit breaker created for service: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create circuit breaker for {service_name}: {str(e)}")
            return False
    
    async def call_with_circuit_breaker(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        try:
            if service_name not in self.circuits:
                await self.create_circuit(service_name)
            
            circuit = self.circuits[service_name]
            
            # Check circuit state
            if circuit['state'] == CircuitState.OPEN:
                if await self._should_attempt_reset(circuit):
                    circuit['state'] = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker OPEN for {service_name}")
            
            # Execute function
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                await self._on_success(service_name)
                return result
                
            except Exception as e:
                await self._on_failure(service_name)
                raise e
                
        except Exception as e:
            self.logger.error(f"Circuit breaker error for {service_name}: {str(e)}")
            raise e
    
    async def _on_success(self, service_name: str):
        """Handle successful call"""
        circuit = self.circuits[service_name]
        
        if circuit['state'] == CircuitState.HALF_OPEN:
            circuit['success_count'] += 1
            if circuit['success_count'] >= circuit['config'].success_threshold:
                circuit['state'] = CircuitState.CLOSED
                circuit['failure_count'] = 0
                circuit['success_count'] = 0
                self.logger.info(f"Circuit breaker for {service_name} reset to CLOSED")
        
        elif circuit['state'] == CircuitState.CLOSED:
            circuit['failure_count'] = 0
    
    async def _on_failure(self, service_name: str):
        """Handle failed call"""
        circuit = self.circuits[service_name]
        circuit['failure_count'] += 1
        circuit['last_failure_time'] = datetime.now()
        
        if circuit['failure_count'] >= circuit['config'].failure_threshold:
            circuit['state'] = CircuitState.OPEN
            circuit['success_count'] = 0
            self.logger.warning(f"Circuit breaker for {service_name} OPENED due to failures")
    
    async def _should_attempt_reset(self, circuit: Dict[str, Any]) -> bool:
        """Check if circuit should attempt reset"""
        if circuit['last_failure_time'] is None:
            return True
        
        time_since_failure = datetime.now() - circuit['last_failure_time']
        return time_since_failure.total_seconds() >= circuit['config'].recovery_timeout
    
    async def get_circuit_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get circuit breaker status"""
        if service_name in self.circuits:
            circuit = self.circuits[service_name]
            return {
                'service': service_name,
                'state': circuit['state'].value,
                'failure_count': circuit['failure_count'],
                'success_count': circuit['success_count'],
                'last_failure_time': circuit['last_failure_time']
            }
        return None
    
    async def get_all_circuits_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            service: await self.get_circuit_status(service)
            for service in self.circuits.keys()
        }

# Global circuit breaker service instance
circuit_breaker_service = CircuitBreakerService()

# Export main classes and functions
__all__ = [
    'CircuitBreakerService',
    'CircuitBreakerConfig',
    'CircuitState',
    'circuit_breaker_service'
]