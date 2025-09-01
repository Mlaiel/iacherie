"""Load Balancer - Advanced Load Balancing System

Enterprise load balancing with multiple strategies, health checking,
service discovery integration, and intelligent traffic distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import random
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp

from .config import LoadBalancingStrategy

logger = logging.getLogger(__name__)


@dataclass
class ServiceInstance:
    """
Service instance information"""
    service_name: str
    upstream_url: str
    weight: int = 10
    current_connections: int = 0
    max_connections: int = 1000
    health_status: bool = True
    last_health_check: Optional[datetime] = None
    response_times: List[float] = field(default_factory=list)
    error_count: int = 0
    total_requests: int = 0


class LoadBalancer:
    """
    Enterprise Load Balancer
    
    Supports multiple load balancing strategies:
    - Round Robin (with weights)
    - Least Connections
    - IP Hash
    - Random
    - Health-based routing
    - Response time based routing
    """
    
    def __init__(
        self, 
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        services: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """
Initialize load balancer"""
        self.strategy = strategy
        self.services: Dict[str, List[ServiceInstance]] = {}
        
        # Strategy-specific state
        self.round_robin_indices: Dict[str, int] = {}
        self.ip_hash_cache: Dict[str, str] = {}
        
        # Health checking
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5    # seconds
        
        # Initialize services
        if services:
            self._initialize_services(services)
        
        # Start health checking
        self._health_check_task = None
        
        logger.info(f"Load balancer initialized with strategy: {strategy.value}")
    
    def _initialize_services(self, services_config: Dict[str, Dict[str, Any]]):
        """Initialize service instances from configuration"""
        try:
            for service_name, config in services_config.items():
                instance = ServiceInstance(
                    service_name=service_name,
                    upstream_url=config["upstream"],
                    weight=config.get("weight", 10),
                    max_connections=config.get("max_connections", 1000)
                )
                
                if service_name not in self.services:
                    self.services[service_name] = []
                
                self.services[service_name].append(instance)
                self.round_robin_indices[service_name] = 0
            
            logger.info(f"Initialized {len(services_config)} services")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    async def get_upstream(
        self, 
        service_name: str, 
        client_ip: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get upstream URL for service using configured strategy
        
        Args:
            service_name: Target service name
            client_ip: Client IP for IP hash strategy
            request_id: Request ID for logging
            
        Returns:
            Upstream URL or None if no healthy instance available
        """
        try:
            if service_name not in self.services:
                logger.warning(f"Service {service_name} not found")
                return None
            
            instances = self.services[service_name]
            healthy_instances = [
                instance for instance in instances 
                if instance.health_status and instance.current_connections < instance.max_connections
            ]
            
            if not healthy_instances:
                logger.error(f"No healthy instances available for service {service_name}")
                return None
            
            # Select instance based on strategy
            selected_instance = await self._select_instance(
                service_name, healthy_instances, client_ip
            )
            
            if selected_instance:
                # Update connection count
                selected_instance.current_connections += 1
                selected_instance.total_requests += 1
                
                logger.debug(
                    f"Selected instance {selected_instance.upstream_url} for {service_name} "
                    f"(strategy: {self.strategy.value})"
                )
                
                return selected_instance.upstream_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting upstream for {service_name}: {e}")
            return None
    
    async def _select_instance(
        self,
        service_name: str,
        instances: List[ServiceInstance],
        client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Select instance based on load balancing strategy"""
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(service_name, instances)
        
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(service_name, instances)
        
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(instances)
        
        elif self.strategy == LoadBalancingStrategy.IP_HASH:
            return self._ip_hash_selection(service_name, instances, client_ip)
        
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_selection(instances)
        
        elif self.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based_selection(instances)
        
        else:
            # Fallback to round robin
            return self._round_robin_selection(service_name, instances)
    
    def _round_robin_selection(
        self, 
        service_name: str, 
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """
Round robin instance selection"""
        index = self.round_robin_indices.get(service_name, 0)
        selected = instances[index % len(instances)]
        
        # Update index for next selection
        self.round_robin_indices[service_name] = (index + 1) % len(instances)
        
        return selected
    
    def _weighted_round_robin_selection(
        self, 
        service_name: str, 
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """
Weighted round robin instance selection"""
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)
        
        if not weighted_instances:
            return instances[0]
        
        index = self.round_robin_indices.get(service_name, 0)
        selected = weighted_instances[index % len(weighted_instances)]
        
        # Update index for next selection
        self.round_robin_indices[service_name] = (index + 1) % len(weighted_instances)
        
        return selected
    
    def _least_connections_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
Least connections instance selection"""
        return min(instances, key=lambda x: x.current_connections)
    
    def _ip_hash_selection(
        self, 
        service_name: str,
        instances: List[ServiceInstance], 
        client_ip: Optional[str]
    ) -> ServiceInstance:
        """
IP hash based instance selection"""
        if not client_ip:
            # Fallback to round robin
            return self._round_robin_selection(service_name, instances)
        
        # Create consistent hash
        hash_key = f"{service_name}:{client_ip}"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        index = hash_value % len(instances)
        
        return instances[index]
    
    def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random instance selection"""
        return random.choice(instances)
    
    def _health_based_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
Health and performance based instance selection"""
        # Score instances based on health metrics
        scored_instances = []
        
        for instance in instances:
            score = self._calculate_instance_score(instance)
            scored_instances.append((instance, score))
        
        # Sort by score (higher is better)
        scored_instances.sort(key=lambda x: x[1], reverse=True)
        
        return scored_instances[0][0]
    
    def _calculate_instance_score(self, instance: ServiceInstance) -> float:
        """
Calculate instance health score"""
        try:
            score = 100.0  # Base score
            
            # Connection load factor (lower is better)
            if instance.max_connections > 0:
                connection_ratio = instance.current_connections / instance.max_connections
                score -= connection_ratio * 30
            
            # Error rate factor (lower is better)
            if instance.total_requests > 0:
                error_rate = instance.error_count / instance.total_requests
                score -= error_rate * 40
            
            # Response time factor (lower is better)
            if instance.response_times:
                avg_response_time = sum(instance.response_times) / len(instance.response_times)
                # Penalize high response times
                score -= min(avg_response_time * 10, 30)
            
            # Health check factor
            if not instance.health_status:
                score = 0  # Unhealthy instances get zero score
            
            return max(score, 0)
            
        except Exception as e:
            logger.error(f"Error calculating instance score: {e}")
            return 0
    
    async def release_connection(self, service_name: str, upstream_url: str):
        """Release connection after request completion"""
        try:
            if service_name in self.services:
                for instance in self.services[service_name]:
                    if instance.upstream_url == upstream_url:
                        instance.current_connections = max(0, instance.current_connections - 1)
                        break
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
    
    async def record_request_metrics(
        self, 
        service_name: str, 
        upstream_url: str, 
        response_time: float, 
        success: bool
    ):
        """Record request metrics for instance"""
        try:
            if service_name in self.services:
                for instance in self.services[service_name]:
                    if instance.upstream_url == upstream_url:
                        # Record response time
                        instance.response_times.append(response_time)
                        
                        # Keep only last 100 response times
                        if len(instance.response_times) > 100:
                            instance.response_times = instance.response_times[-100:]
                        
                        # Record errors
                        if not success:
                            instance.error_count += 1
                        
                        break
                        
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")
    
    async def add_service_instance(
        self, 
        service_name: str, 
        upstream_url: str, 
        weight: int = 10,
        max_connections: int = 1000
    ) -> bool:
        """Add new service instance"""
        try:
            instance = ServiceInstance(
                service_name=service_name,
                upstream_url=upstream_url,
                weight=weight,
                max_connections=max_connections
            )
            
            if service_name not in self.services:
                self.services[service_name] = []
                self.round_robin_indices[service_name] = 0
            
            self.services[service_name].append(instance)
            
            logger.info(f"Added service instance: {service_name} -> {upstream_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding service instance: {e}")
            return False
    
    async def remove_service_instance(self, service_name: str, upstream_url: str) -> bool:
        """Remove service instance"""
        try:
            if service_name in self.services:
                initial_count = len(self.services[service_name])
                
                self.services[service_name] = [
                    instance for instance in self.services[service_name]
                    if instance.upstream_url != upstream_url
                ]
                
                removed = initial_count > len(self.services[service_name])
                
                # Clean up empty service
                if not self.services[service_name]:
                    del self.services[service_name]
                    self.round_robin_indices.pop(service_name, None)
                
                if removed:
                    logger.info(f"Removed service instance: {service_name} -> {upstream_url}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing service instance: {e}")
            return False
    
    async def start_health_checking(self):
        """Start background health checking"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Started health checking loop")
    
    async def stop_health_checking(self):
        """Stop background health checking"""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped health checking loop")
    
    async def _health_check_loop(self):
        """Background health checking loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all service instances"""
        try:
            tasks = []
            
            for service_name, instances in self.services.items():
                for instance in instances:
                    task = asyncio.create_task(
                        self._check_instance_health(instance)
                    )
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
    
    async def _check_instance_health(self, instance: ServiceInstance):
        """Check health of individual service instance"""
        try:
            health_url = f"{instance.upstream_url}/health"
            
            timeout = aiohttp.ClientTimeout(total=self.health_check_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                
                async with session.get(health_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        instance.health_status = True
                        instance.response_times.append(response_time)
                        
                        # Keep only recent response times
                        if len(instance.response_times) > 100:
                            instance.response_times = instance.response_times[-100:]
                    else:
                        instance.health_status = False
                        instance.error_count += 1
                    
                    instance.last_health_check = datetime.utcnow()
        
        except Exception as e:
            logger.debug(f"Health check failed for {instance.upstream_url}: {e}")
            instance.health_status = False
            instance.error_count += 1
            instance.last_health_check = datetime.utcnow()
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        try:
            stats = {
                "strategy": self.strategy.value,
                "total_services": len(self.services),
                "total_instances": sum(len(instances) for instances in self.services.values()),
                "services": {}
            }
            
            for service_name, instances in self.services.items():
                service_stats = {
                    "instance_count": len(instances),
                    "healthy_instances": sum(1 for i in instances if i.health_status),
                    "total_connections": sum(i.current_connections for i in instances),
                    "total_requests": sum(i.total_requests for i in instances),
                    "total_errors": sum(i.error_count for i in instances),
                    "instances": []
                }
                
                for instance in instances:
                    avg_response_time = 0
                    if instance.response_times:
                        avg_response_time = sum(instance.response_times) / len(instance.response_times)
                    
                    instance_stats = {
                        "upstream_url": instance.upstream_url,
                        "health_status": instance.health_status,
                        "weight": instance.weight,
                        "current_connections": instance.current_connections,
                        "max_connections": instance.max_connections,
                        "total_requests": instance.total_requests,
                        "error_count": instance.error_count,
                        "avg_response_time": round(avg_response_time, 3),
                        "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None
                    }
                    service_stats["instances"].append(instance_stats)
                
                stats["services"][service_name] = service_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting load balancer stats: {e}")
            return {}
