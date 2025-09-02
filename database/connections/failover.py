"""Failover Manager - IA Influencer Agent Platform

Manages database failover and high availability:
- Automatic failover detection and switching
- Health-based endpoint selection
- Connection recovery and retry logic
- Load balancing across replicas
- Disaster recovery coordination
- Service degradation handling

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random


class EndpointStatus(Enum):
    """
Database endpoint status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class FailoverStrategy(Enum):
    """Failover strategies"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    NEAREST = "nearest"
    RANDOM = "random"
    PRIORITY = "priority"


@dataclass
class DatabaseEndpoint:
    """Database endpoint configuration"""
    endpoint_id: str
    host: str
    port: int
    priority: int = 1  # Lower numbers = higher priority
    weight: int = 100  # For weighted load balancing
    role: str = "primary"  # primary, replica, cache
    status: EndpointStatus = EndpointStatus.UNKNOWN
    last_check: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    response_time: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class FailoverManager:
    """
    Database failover manager for high availability.
    
    Provides:
    - Automatic failover to healthy endpoints
    - Load balancing across multiple endpoints
    - Health monitoring and status tracking
    - Connection retry and circuit breaker logic
    - Graceful degradation handling
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Endpoint configurations by database type
        self.endpoints: Dict[str, List[DatabaseEndpoint]] = {}
        
        # Current active endpoints
        self.active_endpoints: Dict[str, str] = {}  # db_type -> endpoint_id
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self.health_tasks: Dict[str, asyncio.Task] = {}
        
        # Failover configuration
        self.max_failure_threshold = 3
        self.failure_window = timedelta(minutes=5)
        self.recovery_check_interval = 60  # seconds
        
        # Strategies
        self.failover_strategies: Dict[str, FailoverStrategy] = {}
        
        # Callbacks
        self.failover_callbacks: List[Callable[[str, str, str], None]] = []
        
        # Statistics
        self.stats = {
            "total_failovers": 0,
            "successful_failovers": 0,
            "failed_failovers": 0,
            "total_health_checks": 0,
            "failed_health_checks": 0
        }
    
    async def initialize(self, 
                        endpoint_configs: Dict[str, List[Dict[str, Any]]],
                        strategies: Optional[Dict[str, FailoverStrategy]] = None) -> None:
        """Initialize failover manager with endpoint configurations"""
        
        # Configure endpoints
        for db_type, configs in endpoint_configs.items():
            self.endpoints[db_type] = []
            
            for config in configs:
                endpoint = DatabaseEndpoint(**config)
                self.endpoints[db_type].append(endpoint)
            
            # Sort by priority
            self.endpoints[db_type].sort(key=lambda ep: ep.priority)
            
            # Set initial active endpoint (highest priority healthy endpoint)
            self.active_endpoints[db_type] = self.endpoints[db_type][0].endpoint_id
        
        # Set failover strategies
        if strategies:
            self.failover_strategies.update(strategies)
        
        # Start health monitoring
        await self.start_health_monitoring()
        
        self.logger.info("Failover manager initialized")
    
    async def start_health_monitoring(self) -> None:
        """Start health monitoring for all endpoints"""
        for db_type in self.endpoints.keys():
            task = asyncio.create_task(self._health_monitoring_loop(db_type))
            self.health_tasks[db_type] = task
        
        self.logger.info("Started health monitoring for all endpoints")
    
    async def stop_health_monitoring(self) -> None:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "stop_health_monitoring",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric stop_health_monitoring collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection stop_health_monitoring failed: {e}")
                    return None
    async def _health_monitoring_loop(self, db_type: str) -> None:
        """Health monitoring loop for specific database type"""
        while True:
            try:
                await self._check_endpoints_health(db_type)
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error for {db_type}: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _check_endpoints_health(self, db_type: str) -> None:
        """Check health of all endpoints for a database type"""
        if db_type not in self.endpoints:
            return
        
        health_tasks = []
        for endpoint in self.endpoints[db_type]:
            task = asyncio.create_task(
                self._check_endpoint_health(db_type, endpoint)
            )
            health_tasks.append(task)
        
        # Wait for all health checks
        await asyncio.gather(*health_tasks, return_exceptions=True)
        
        # Check if failover is needed
        await self._evaluate_failover_need(db_type)
    
    async def _check_endpoint_health(self, db_type: str, endpoint: DatabaseEndpoint) -> None:
        """
Check health of a single endpoint"""
        start_time = datetime.utcnow()
        
        try:
            # Perform health check (simplified - actual implementation would check database)
            await self._perform_health_check(db_type, endpoint)
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            endpoint.response_time = response_time
            endpoint.last_check = datetime.utcnow()
            endpoint.success_count += 1
            
            # Determine status based on response time
            if response_time <= 1.0:
                endpoint.status = EndpointStatus.HEALTHY
            elif response_time <= 3.0:
                endpoint.status = EndpointStatus.DEGRADED
            else:
                endpoint.status = EndpointStatus.UNHEALTHY
                endpoint.failure_count += 1
            
            self.stats["total_health_checks"] += 1
            
        except Exception as e:
            endpoint.status = EndpointStatus.UNHEALTHY
            endpoint.failure_count += 1
            endpoint.last_check = datetime.utcnow()
            
            self.stats["total_health_checks"] += 1
            self.stats["failed_health_checks"] += 1
            
            self.logger.warning(f"Health check failed for {endpoint.endpoint_id}: {e}")
    
    async def _perform_health_check(self, db_type: str, endpoint: DatabaseEndpoint) -> None:
        """Perform actual health check on endpoint"""
        # This is a simplified implementation
        # In real scenario, this would connect to the database and perform a simple query
        
        try:
            # Simulate connection check with timeout
            await asyncio.wait_for(
                asyncio.sleep(0.1),  # Simulate network delay
                timeout=self.health_check_timeout
            )
            
            # Randomly simulate failures for testing
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Simulated health check failure")
                
        except asyncio.TimeoutError:
            raise Exception("Health check timeout")
    
    async def _evaluate_failover_need(self, db_type: str) -> None:
        """Evaluate if failover is needed for database type"""
        current_endpoint_id = self.active_endpoints.get(db_type)
        
        if not current_endpoint_id:
            return
        
        current_endpoint = self._get_endpoint(db_type, current_endpoint_id)
        
        if not current_endpoint:
            return
        
        # Check if current endpoint is unhealthy
        if current_endpoint.status == EndpointStatus.UNHEALTHY:
            # Check failure threshold
            recent_failures = self._count_recent_failures(current_endpoint)
            
            if recent_failures >= self.max_failure_threshold:
                await self._perform_failover(db_type, "endpoint_unhealthy")
    
    def _count_recent_failures(self, endpoint: DatabaseEndpoint) -> int:
        """Count recent failures within the failure window"""
        # Simplified implementation - in real scenario, track failure timestamps
        cutoff_time = datetime.utcnow() - self.failure_window
        
        if endpoint.last_check and endpoint.last_check > cutoff_time:
            return endpoint.failure_count
        
        return 0
    
    async def _perform_failover(self, db_type: str, reason: str) -> bool:
        """
Perform failover to next available endpoint"""
        try:
            current_endpoint_id = self.active_endpoints.get(db_type)
            
            # Find best alternative endpoint
            new_endpoint = await self._select_best_endpoint(db_type, exclude=current_endpoint_id)
            
            if not new_endpoint:
                self.logger.error(f"No healthy endpoints available for failover: {db_type}")
                self.stats["failed_failovers"] += 1
                return False
            
            # Perform failover
            old_endpoint_id = current_endpoint_id
            self.active_endpoints[db_type] = new_endpoint.endpoint_id
            
            self.logger.warning(
                f"Failover executed for {db_type}: {old_endpoint_id} -> {new_endpoint.endpoint_id} "
                f"(reason: {reason})"
            )
            
            # Update statistics
            self.stats["total_failovers"] += 1
            self.stats["successful_failovers"] += 1
            
            # Notify callbacks
            await self._notify_failover_callbacks(db_type, old_endpoint_id, new_endpoint.endpoint_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failover failed for {db_type}: {e}")
            self.stats["failed_failovers"] += 1
            return False
    
    async def _select_best_endpoint(self, 
                                  db_type: str, 
                                  exclude: Optional[str] = None) -> Optional[DatabaseEndpoint]:
        """Select best available endpoint using configured strategy"""
        
        if db_type not in self.endpoints:
            return None
        
        # Get healthy endpoints
        available_endpoints = [
            ep for ep in self.endpoints[db_type]
            if ep.status in [EndpointStatus.HEALTHY, EndpointStatus.DEGRADED]
            and ep.endpoint_id != exclude
        ]
        
        if not available_endpoints:
            return None
        
        # Apply selection strategy
        strategy = self.failover_strategies.get(db_type, FailoverStrategy.PRIORITY)
        
        if strategy == FailoverStrategy.PRIORITY:
            # Select highest priority (lowest number)
            return min(available_endpoints, key=lambda ep: ep.priority)
            
        elif strategy == FailoverStrategy.WEIGHTED:
            # Weighted random selection based on success rate and weight
            weights = [ep.weight * ep.success_rate() for ep in available_endpoints]
            return self._weighted_choice(available_endpoints, weights)
            
        elif strategy == FailoverStrategy.ROUND_ROBIN:
            # Simple round-robin (simplified implementation)
            return available_endpoints[0]
            
        elif strategy == FailoverStrategy.RANDOM:
            return random.choice(available_endpoints)
            
        elif strategy == FailoverStrategy.NEAREST:
            # Select endpoint with best response time
            return min(available_endpoints, key=lambda ep: ep.response_time)
        
        # Default to priority
        return min(available_endpoints, key=lambda ep: ep.priority)
    
    def _weighted_choice(self, endpoints: List[DatabaseEndpoint], weights: List[float]) -> DatabaseEndpoint:
        """
Weighted random selection"""
        if not weights or sum(weights) == 0:
            return random.choice(endpoints)
        
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for endpoint, weight in zip(endpoints, weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return endpoint
        
        return endpoints[-1]  # Fallback
    
    def _get_endpoint(self, db_type: str, endpoint_id: str) -> Optional[DatabaseEndpoint]:
        """
Get endpoint by ID"""
        if db_type not in self.endpoints:
            return None
        
        for endpoint in self.endpoints[db_type]:
            if endpoint.endpoint_id == endpoint_id:
                return endpoint
        
        return None
    
    async def _notify_failover_callbacks(self, 
                                       db_type: str, 
                                       old_endpoint: str, 
                                       new_endpoint: str) -> None:
        """
Notify registered failover callbacks"""
        for callback in self.failover_callbacks:
            try:
                await callback(db_type, old_endpoint, new_endpoint)
            except Exception as e:
                self.logger.error(f"Failover callback error: {e}")
    
    def register_failover_callback(self, 
                                 callback: Callable[[str, str, str], None]) -> None:
        """Register callback for failover events"""
        self.failover_callbacks.append(callback)
    
    def get_active_endpoint(self, db_type: str) -> Optional[DatabaseEndpoint]:
        """
Get currently active endpoint for database type"""
        endpoint_id = self.active_endpoints.get(db_type)
        if endpoint_id:
            return self._get_endpoint(db_type, endpoint_id)
        return None
    
    def get_all_endpoints(self, db_type: str) -> List[DatabaseEndpoint]:
        """
Get all endpoints for database type"""
        return self.endpoints.get(db_type, [])
    
    async def force_failover(self, db_type: str, target_endpoint_id: Optional[str] = None) -> bool:
        """
Force failover to specific endpoint or best available"""
        try:
            if target_endpoint_id:
                target_endpoint = self._get_endpoint(db_type, target_endpoint_id)
                if not target_endpoint:
                    raise ValueError(f"Target endpoint {target_endpoint_id} not found")
                
                if target_endpoint.status == EndpointStatus.UNHEALTHY:
                    raise ValueError(f"Target endpoint {target_endpoint_id} is unhealthy")
                
                old_endpoint_id = self.active_endpoints.get(db_type)
                self.active_endpoints[db_type] = target_endpoint_id
                
                self.logger.info(f"Forced failover for {db_type}: {old_endpoint_id} -> {target_endpoint_id}")
                
                # Notify callbacks
                await self._notify_failover_callbacks(db_type, old_endpoint_id, target_endpoint_id)
                
                return True
            else:
                return await self._perform_failover(db_type, "manual_failover")
                
        except Exception as e:
            self.logger.error(f"Force failover failed for {db_type}: {e}")
            return False
    
    def set_endpoint_status(self, 
                          db_type: str, 
                          endpoint_id: str, 
                          status: EndpointStatus) -> bool:
        """Manually set endpoint status"""
        endpoint = self._get_endpoint(db_type, endpoint_id)
        if endpoint:
            endpoint.status = status
            endpoint.last_check = datetime.utcnow()
            self.logger.info(f"Set endpoint {endpoint_id} status to {status.value}")
            return True
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive failover manager metrics"""
        endpoint_stats = {}
        
        for db_type, endpoints in self.endpoints.items():
            endpoint_stats[db_type] = {
                "total_endpoints": len(endpoints),
                "healthy_endpoints": len([ep for ep in endpoints if ep.status == EndpointStatus.HEALTHY]),
                "degraded_endpoints": len([ep for ep in endpoints if ep.status == EndpointStatus.DEGRADED]),
                "unhealthy_endpoints": len([ep for ep in endpoints if ep.status == EndpointStatus.UNHEALTHY]),
                "active_endpoint": self.active_endpoints.get(db_type),
                "endpoints": [
                    {
                        "endpoint_id": ep.endpoint_id,
                        "host": ep.host,
                        "port": ep.port,
                        "status": ep.status.value,
                        "priority": ep.priority,
                        "response_time": ep.response_time,
                        "success_rate": ep.success_rate(),
                        "last_check": ep.last_check.isoformat() if ep.last_check else None
                    }
                    for ep in endpoints
                ]
            }
        
        return {
            "statistics": self.stats,
            "endpoint_statistics": endpoint_stats,
            "configuration": {
                "health_check_interval": self.health_check_interval,
                "health_check_timeout": self.health_check_timeout,
                "max_failure_threshold": self.max_failure_threshold,
                "failure_window_minutes": self.failure_window.total_seconds() / 60,
                "recovery_check_interval": self.recovery_check_interval
            },
            "failover_strategies": {
                db_type: strategy.value for db_type, strategy in self.failover_strategies.items()
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown failover manager"""
        self.logger.info("Shutting down failover manager...")
        
        await self.stop_health_monitoring()
        
        # Clear data structures
        self.endpoints.clear()
        self.active_endpoints.clear()
        self.failover_callbacks.clear()
        
        self.logger.info("Failover manager shutdown completed")
