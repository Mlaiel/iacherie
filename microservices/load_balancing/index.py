"""
Load Balancing Service Index
Enterprise Load Balancing and Traffic Distribution

This module provides advanced load balancing capabilities for distributing
traffic across multiple service instances with intelligent routing algorithms.

Key Features:
- Multiple load balancing algorithms (Round Robin, Weighted, Least Connections)
- Health-aware routing and automatic failover
- Real-time performance monitoring
- Dynamic weight adjustment based on performance
- Integration with service discovery and circuit breakers

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import random
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithm types"""
    ROUND_ROBIN = "ROUND_ROBIN"
    WEIGHTED_ROUND_ROBIN = "WEIGHTED_ROUND_ROBIN"
    LEAST_CONNECTIONS = "LEAST_CONNECTIONS"
    RANDOM = "RANDOM"
    CONSISTENT_HASH = "CONSISTENT_HASH"

@dataclass
class ServiceInstance:
    """Service instance definition"""
    host: str
    port: int
    weight: int = 1
    active_connections: int = 0
    health_status: str = "HEALTHY"
    response_time: float = 0.0
    last_health_check: Optional[datetime] = None

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    health_check_interval: int = 30
    max_retries: int = 3
    timeout_seconds: int = 5

class LoadBalancerService:
    """Enterprise load balancing service"""
    
    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        self.config = config or LoadBalancerConfig()
        self.service_pools: Dict[str, List[ServiceInstance]] = {}
        self.round_robin_counters: Dict[str, int] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def register_service_pool(self, service_name: str, instances: List[ServiceInstance]) -> bool:
        """Register a pool of service instances"""
        try:
            self.service_pools[service_name] = instances
            self.round_robin_counters[service_name] = 0
            
            self.logger.info(f"Service pool registered: {service_name} with {len(instances)} instances")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service pool {service_name}: {str(e)}")
            return False
    
    async def add_service_instance(self, service_name: str, instance: ServiceInstance) -> bool:
        """Add a service instance to an existing pool"""
        try:
            if service_name not in self.service_pools:
                self.service_pools[service_name] = []
            
            self.service_pools[service_name].append(instance)
            self.logger.info(f"Instance added to {service_name}: {instance.host}:{instance.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add instance to {service_name}: {str(e)}")
            return False
    
    async def remove_service_instance(self, service_name: str, host: str, port: int) -> bool:
        """Remove a service instance from the pool"""
        try:
            if service_name in self.service_pools:
                instances = self.service_pools[service_name]
                self.service_pools[service_name] = [
                    inst for inst in instances 
                    if not (inst.host == host and inst.port == port)
                ]
                self.logger.info(f"Instance removed from {service_name}: {host}:{port}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove instance from {service_name}: {str(e)}")
            return False
    
    async def get_next_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get next service instance based on load balancing algorithm"""
        try:
            if service_name not in self.service_pools:
                return None
            
            healthy_instances = [
                inst for inst in self.service_pools[service_name]
                if inst.health_status == "HEALTHY"
            ]
            
            if not healthy_instances:
                self.logger.warning(f"No healthy instances available for {service_name}")
                return None
            
            if self.config.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return await self._round_robin_select(service_name, healthy_instances)
            
            elif self.config.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return await self._weighted_round_robin_select(service_name, healthy_instances)
            
            elif self.config.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return await self._least_connections_select(healthy_instances)
            
            elif self.config.algorithm == LoadBalancingAlgorithm.RANDOM:
                return random.choice(healthy_instances)
            
            elif self.config.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
                return await self._consistent_hash_select(service_name, healthy_instances)
            
            return healthy_instances[0]  # Fallback
            
        except Exception as e:
            self.logger.error(f"Failed to get next instance for {service_name}: {str(e)}")
            return None
    
    async def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round robin selection"""
        counter = self.round_robin_counters[service_name]
        selected = instances[counter % len(instances)]
        self.round_robin_counters[service_name] = (counter + 1) % len(instances)
        return selected
    
    async def _weighted_round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round robin selection"""
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)
        
        if not weighted_instances:
            return instances[0]
        
        counter = self.round_robin_counters[service_name]
        selected = weighted_instances[counter % len(weighted_instances)]
        self.round_robin_counters[service_name] = (counter + 1) % len(weighted_instances)
        return selected
    
    async def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(instances, key=lambda x: x.active_connections)
    
    async def _consistent_hash_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Consistent hash selection (simplified)"""
        # Simple hash-based selection
        hash_value = hash(service_name) % len(instances)
        return instances[hash_value]
    
    async def update_instance_metrics(self, service_name: str, host: str, port: int, 
                                     active_connections: int, response_time: float) -> bool:
        """Update instance performance metrics"""
        try:
            if service_name in self.service_pools:
                for instance in self.service_pools[service_name]:
                    if instance.host == host and instance.port == port:
                        instance.active_connections = active_connections
                        instance.response_time = response_time
                        return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics for {host}:{port}: {str(e)}")
            return False
    
    async def mark_instance_health(self, service_name: str, host: str, port: int, 
                                  health_status: str) -> bool:
        """Update instance health status"""
        try:
            if service_name in self.service_pools:
                for instance in self.service_pools[service_name]:
                    if instance.host == host and instance.port == port:
                        instance.health_status = health_status
                        instance.last_health_check = datetime.now()
                        self.logger.info(f"Instance {host}:{port} marked as {health_status}")
                        return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update health for {host}:{port}: {str(e)}")
            return False
    
    async def get_service_pool_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get status of service pool"""
        if service_name in self.service_pools:
            instances = self.service_pools[service_name]
            healthy_count = sum(1 for inst in instances if inst.health_status == "HEALTHY")
            
            return {
                'service': service_name,
                'total_instances': len(instances),
                'healthy_instances': healthy_count,
                'algorithm': self.config.algorithm.value,
                'instances': [
                    {
                        'host': inst.host,
                        'port': inst.port,
                        'weight': inst.weight,
                        'active_connections': inst.active_connections,
                        'health_status': inst.health_status,
                        'response_time': inst.response_time,
                        'last_health_check': inst.last_health_check.isoformat() if inst.last_health_check else None
                    }
                    for inst in instances
                ]
            }
        return None
    
    async def get_all_pools_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all service pools"""
        result = {}
        for service_name in self.service_pools.keys():
            status = await self.get_service_pool_status(service_name)
            if status:
                result[service_name] = status
        return result
    
    async def start_health_monitoring(self, health_check_func: Optional[Callable] = None):
        """Start health monitoring for all instances"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(
                self._health_monitoring_loop(health_check_func)
            )
            self.logger.info("Health monitoring started")
    
    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self.logger.info("Health monitoring stopped")
    
    async def _health_monitoring_loop(self, health_check_func: Optional[Callable] = None):
        """Health monitoring loop"""
        while True:
            try:
                for service_name, instances in self.service_pools.items():
                    for instance in instances:
                        if health_check_func:
                            try:
                                is_healthy = await health_check_func(instance.host, instance.port)
                                health_status = "HEALTHY" if is_healthy else "UNHEALTHY"
                                await self.mark_instance_health(
                                    service_name, instance.host, instance.port, health_status
                                )
                            except Exception as e:
                                self.logger.error(f"Health check failed for {instance.host}:{instance.port}: {str(e)}")
                                await self.mark_instance_health(
                                    service_name, instance.host, instance.port, "UNHEALTHY"
                                )
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {str(e)}")
                await asyncio.sleep(5)

# Global load balancer service instance
load_balancer_service = LoadBalancerService()

# Export main classes and functions
__all__ = [
    'LoadBalancerService',
    'LoadBalancerConfig',
    'LoadBalancingAlgorithm',
    'ServiceInstance',
    'load_balancer_service'
]