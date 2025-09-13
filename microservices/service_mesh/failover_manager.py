#!/usr/bin/env python3
"""
Enterprise Failover Manager Service
Automatic failover and recovery mechanisms for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import aiohttp
import json
import random

logger = logging.getLogger(__name__)

class ServiceState(Enum):
    """Service state enumeration"""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class FailoverStrategy(Enum):
    """Failover strategy enumeration"""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    GEOGRAPHIC = "geographic"
    PERFORMANCE_BASED = "performance_based"

class FailoverTrigger(Enum):
    """Failover trigger types"""
    HEALTH_CHECK = "health_check"
    TIMEOUT = "timeout"
    ERROR_RATE = "error_rate"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

@dataclass
class ServiceInstance:
    """Service instance configuration"""
    id: str
    endpoint: str
    weight: int = 100
    priority: int = 1
    region: str = "default"
    state: ServiceState = ServiceState.UNKNOWN
    health_score: float = 1.0
    last_health_check: float = 0.0
    failure_count: int = 0
    recovery_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FailoverConfig:
    """Failover configuration"""
    service_name: str
    strategy: FailoverStrategy = FailoverStrategy.ACTIVE_PASSIVE
    health_check_interval: float = 30.0
    health_check_timeout: float = 10.0
    failure_threshold: int = 3
    recovery_threshold: int = 2
    recovery_delay: float = 60.0
    auto_recovery: bool = True
    maintenance_mode: bool = False
    max_instances: int = 10

@dataclass
class FailoverEvent:
    """Failover event record"""
    timestamp: float
    service_name: str
    trigger: FailoverTrigger
    from_instance: Optional[str]
    to_instance: Optional[str]
    reason: str
    success: bool
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class FailoverManager:
    """
    Enterprise Failover Manager
    
    Provides comprehensive failover management with:
    - Multiple failover strategies
    - Automatic health monitoring
    - Recovery mechanisms
    - Performance-based routing
    - Geographic distribution
    """
    
    def __init__(self):
        """Initialize failover manager"""
        self.services: Dict[str, FailoverConfig] = {}
        self.instances: Dict[str, List[ServiceInstance]] = {}
        self.active_instances: Dict[str, str] = {}  # service -> active instance id
        self.failover_history: List[FailoverEvent] = []
        
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # HTTP session for health checks
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Performance tracking
        self.instance_metrics: Dict[str, Dict[str, float]] = {}
        
        logger.info("FailoverManager initialized")
    
    async def start(self):
        """Start the failover manager"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Start health check tasks
            await self._start_health_checks()
            
            logger.info("FailoverManager started successfully")
        except Exception as e:
            logger.error("Failed to start FailoverManager: %s", e)
            raise
    
    async def stop(self):
        """Stop the failover manager"""
        try:
            self.shutdown_event.set()
            
            # Stop health check tasks
            await self._stop_health_checks()
            
            # Close HTTP session
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("FailoverManager stopped successfully")
        except Exception as e:
            logger.error("Error stopping FailoverManager: %s", e)
    
    async def register_service(
        self,
        config: FailoverConfig,
        instances: List[ServiceInstance]
    ):
        """Register a service with failover configuration"""
        async with self._lock:
            # Store configuration
            self.services[config.service_name] = config
            self.instances[config.service_name] = instances
            
            # Initialize metrics
            for instance in instances:
                instance_key = f"{config.service_name}.{instance.id}"
                self.instance_metrics[instance_key] = {
                    "response_time": 0.0,
                    "success_rate": 1.0,
                    "request_count": 0,
                    "error_count": 0
                }
            
            # Select initial active instance
            await self._select_active_instance(config.service_name)
            
            # Start health checks
            if not self.shutdown_event.is_set():
                await self._start_service_health_check(config.service_name)
        
        logger.info(
            "Registered service '%s' with %d instances",
            config.service_name, len(instances)
        )
    
    async def unregister_service(self, service_name: str):
        """Unregister a service"""
        async with self._lock:
            # Stop health check task
            task = self.health_check_tasks.pop(service_name, None)
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Remove service data
            self.services.pop(service_name, None)
            self.instances.pop(service_name, None)
            self.active_instances.pop(service_name, None)
            
            # Clean up metrics
            metrics_to_remove = [
                key for key in self.instance_metrics.keys()
                if key.startswith(f"{service_name}.")
            ]
            for key in metrics_to_remove:
                self.instance_metrics.pop(key, None)
        
        logger.info("Unregistered service '%s'", service_name)
    
    async def get_active_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get the current active instance for a service"""
        async with self._lock:
            active_id = self.active_instances.get(service_name)
            if not active_id:
                return None
            
            instances = self.instances.get(service_name, [])
            for instance in instances:
                if instance.id == active_id:
                    return instance
            
            return None
    
    async def get_available_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all available instances for a service"""
        async with self._lock:
            instances = self.instances.get(service_name, [])
            return [
                instance for instance in instances
                if instance.state in [ServiceState.ACTIVE, ServiceState.STANDBY]
            ]
    
    async def trigger_failover(
        self,
        service_name: str,
        reason: str,
        trigger: FailoverTrigger = FailoverTrigger.MANUAL,
        target_instance: Optional[str] = None
    ) -> bool:
        """Manually trigger failover for a service"""
        start_time = time.time()
        
        async with self._lock:
            config = self.services.get(service_name)
            if not config:
                logger.error("Service '%s' not found for failover", service_name)
                return False
            
            current_active = self.active_instances.get(service_name)
            
            # Select target instance
            if target_instance:
                target = await self._find_instance(service_name, target_instance)
                if not target or target.state not in [ServiceState.STANDBY, ServiceState.ACTIVE]:
                    logger.error("Target instance '%s' not available", target_instance)
                    return False
            else:
                target = await self._select_best_instance(service_name, exclude=current_active)
                if not target:
                    logger.error("No available instances for failover")
                    return False
            
            # Perform failover
            success = await self._perform_failover(
                service_name, current_active, target.id, trigger, reason
            )
            
            duration = time.time() - start_time
            
            # Record event
            event = FailoverEvent(
                timestamp=time.time(),
                service_name=service_name,
                trigger=trigger,
                from_instance=current_active,
                to_instance=target.id,
                reason=reason,
                success=success,
                duration=duration
            )
            self.failover_history.append(event)
            
            # Keep only last 1000 events
            if len(self.failover_history) > 1000:
                self.failover_history = self.failover_history[-1000:]
            
            return success
    
    async def update_instance_metrics(
        self,
        service_name: str,
        instance_id: str,
        response_time: float,
        success: bool
    ):
        """Update performance metrics for an instance"""
        instance_key = f"{service_name}.{instance_id}"
        
        async with self._lock:
            if instance_key not in self.instance_metrics:
                self.instance_metrics[instance_key] = {
                    "response_time": 0.0,
                    "success_rate": 1.0,
                    "request_count": 0,
                    "error_count": 0
                }
            
            metrics = self.instance_metrics[instance_key]
            metrics["request_count"] += 1
            
            if success:
                # Update running average response time
                old_avg = metrics["response_time"]
                metrics["response_time"] = (
                    (old_avg * (metrics["request_count"] - 1) + response_time) /
                    metrics["request_count"]
                )
            else:
                metrics["error_count"] += 1
            
            # Update success rate
            metrics["success_rate"] = (
                (metrics["request_count"] - metrics["error_count"]) /
                metrics["request_count"]
            )
            
            # Update instance health score
            instance = await self._find_instance(service_name, instance_id)
            if instance:
                instance.health_score = min(1.0, metrics["success_rate"])
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get comprehensive status for a service"""
        async with self._lock:
            config = self.services.get(service_name)
            instances = self.instances.get(service_name, [])
            active_id = self.active_instances.get(service_name)
            
            if not config:
                return {"error": "Service not found"}
            
            instance_statuses = []
            for instance in instances:
                instance_key = f"{service_name}.{instance.id}"
                metrics = self.instance_metrics.get(instance_key, {})
                
                instance_statuses.append({
                    "id": instance.id,
                    "endpoint": instance.endpoint,
                    "state": instance.state.value,
                    "weight": instance.weight,
                    "priority": instance.priority,
                    "region": instance.region,
                    "health_score": instance.health_score,
                    "failure_count": instance.failure_count,
                    "is_active": instance.id == active_id,
                    "metrics": metrics
                })
            
            return {
                "service_name": service_name,
                "strategy": config.strategy.value,
                "active_instance": active_id,
                "total_instances": len(instances),
                "healthy_instances": len([i for i in instances if i.state == ServiceState.ACTIVE]),
                "instances": instance_statuses,
                "maintenance_mode": config.maintenance_mode
            }
    
    async def get_failover_history(self, service_name: Optional[str] = None, limit: int = 100) -> List[FailoverEvent]:
        """Get failover history"""
        async with self._lock:
            events = self.failover_history
            
            if service_name:
                events = [e for e in events if e.service_name == service_name]
            
            return events[-limit:]
    
    async def _start_health_checks(self):
        """Start health check tasks for all services"""
        for service_name in self.services.keys():
            await self._start_service_health_check(service_name)
    
    async def _start_service_health_check(self, service_name: str):
        """Start health check task for a specific service"""
        if service_name in self.health_check_tasks:
            self.health_check_tasks[service_name].cancel()
        
        self.health_check_tasks[service_name] = asyncio.create_task(
            self._health_check_loop(service_name)
        )
    
    async def _stop_health_checks(self):
        """Stop all health check tasks"""
        tasks = list(self.health_check_tasks.values())
        self.health_check_tasks.clear()
        
        for task in tasks:
            task.cancel()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _health_check_loop(self, service_name: str):
        """Health check loop for a service"""
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_checks(service_name)
                
                config = self.services.get(service_name)
                if config:
                    await asyncio.sleep(config.health_check_interval)
                else:
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health check loop for %s: %s", service_name, e)
                await asyncio.sleep(30)  # Default interval on error
    
    async def _perform_health_checks(self, service_name: str):
        """Perform health checks for all instances of a service"""
        async with self._lock:
            config = self.services.get(service_name)
            instances = self.instances.get(service_name, [])
            
            if not config:
                return
            
            for instance in instances:
                if instance.state == ServiceState.MAINTENANCE:
                    continue
                
                start_time = time.time()
                healthy = await self._check_instance_health(instance, config.health_check_timeout)
                response_time = time.time() - start_time
                
                # Update metrics
                await self.update_instance_metrics(
                    service_name, instance.id, response_time, healthy
                )
                
                # Update instance state
                if healthy:
                    if instance.state == ServiceState.FAILED:
                        instance.failure_count = max(0, instance.failure_count - 1)
                        if instance.failure_count <= 0:
                            instance.state = ServiceState.STANDBY
                            instance.recovery_time = time.time()
                            logger.info("Instance %s recovered", instance.id)
                    elif instance.state in [ServiceState.STANDBY, ServiceState.RECOVERING]:
                        instance.state = ServiceState.ACTIVE
                        
                else:
                    instance.failure_count += 1
                    if instance.failure_count >= config.failure_threshold:
                        if instance.state != ServiceState.FAILED:
                            instance.state = ServiceState.FAILED
                            logger.warning("Instance %s marked as failed", instance.id)
                            
                            # Trigger failover if this was the active instance
                            active_id = self.active_instances.get(service_name)
                            if active_id == instance.id:
                                await self._handle_active_instance_failure(service_name)
                
                instance.last_health_check = time.time()
    
    async def _check_instance_health(self, instance: ServiceInstance, timeout: float) -> bool:
        """Check health of a single instance"""
        if not self.session:
            return False
        
        try:
            health_endpoint = f"{instance.endpoint}/health"
            async with self.session.get(health_endpoint, timeout=timeout) as response:
                return response.status < 400
        except Exception:
            return False
    
    async def _handle_active_instance_failure(self, service_name: str):
        """Handle failure of the active instance"""
        logger.warning("Active instance failed for service %s, triggering failover", service_name)
        
        success = await self.trigger_failover(
            service_name,
            "Active instance health check failed",
            FailoverTrigger.HEALTH_CHECK
        )
        
        if not success:
            logger.error("Failed to failover service %s", service_name)
    
    async def _select_active_instance(self, service_name: str):
        """Select the initial active instance for a service"""
        best_instance = await self._select_best_instance(service_name)
        if best_instance:
            self.active_instances[service_name] = best_instance.id
            best_instance.state = ServiceState.ACTIVE
            logger.info("Selected instance %s as active for service %s", best_instance.id, service_name)
    
    async def _select_best_instance(self, service_name: str, exclude: Optional[str] = None) -> Optional[ServiceInstance]:
        """Select the best available instance based on strategy"""
        config = self.services.get(service_name)
        instances = self.instances.get(service_name, [])
        
        if not config or not instances:
            return None
        
        # Filter available instances
        available = [
            instance for instance in instances
            if (instance.state in [ServiceState.ACTIVE, ServiceState.STANDBY] and
                instance.id != exclude)
        ]
        
        if not available:
            return None
        
        strategy = config.strategy
        
        if strategy == FailoverStrategy.ACTIVE_PASSIVE:
            # Select highest priority instance
            return max(available, key=lambda x: x.priority)
        
        elif strategy == FailoverStrategy.WEIGHTED:
            # Weighted random selection
            total_weight = sum(instance.weight for instance in available)
            if total_weight == 0:
                return random.choice(available)
            
            r = random.uniform(0, total_weight)
            cumulative = 0
            for instance in available:
                cumulative += instance.weight
                if r <= cumulative:
                    return instance
            return available[-1]
        
        elif strategy == FailoverStrategy.PERFORMANCE_BASED:
            # Select based on health score and performance
            def score_instance(instance):
                instance_key = f"{service_name}.{instance.id}"
                metrics = self.instance_metrics.get(instance_key, {})
                response_time = metrics.get("response_time", float('inf'))
                success_rate = metrics.get("success_rate", 0.0)
                
                # Lower response time and higher success rate is better
                if response_time == 0:
                    response_time = 1.0  # Avoid division by zero
                
                return (success_rate * instance.health_score) / response_time
            
            return max(available, key=score_instance)
        
        else:
            # Default to first available
            return available[0]
    
    async def _perform_failover(
        self,
        service_name: str,
        from_instance: Optional[str],
        to_instance: str,
        trigger: FailoverTrigger,
        reason: str
    ) -> bool:
        """Perform the actual failover"""
        try:
            # Update instance states
            instances = self.instances.get(service_name, [])
            
            # Mark old instance as standby or failed
            if from_instance:
                old_instance = await self._find_instance(service_name, from_instance)
                if old_instance:
                    old_instance.state = ServiceState.STANDBY
            
            # Mark new instance as active
            new_instance = await self._find_instance(service_name, to_instance)
            if new_instance:
                new_instance.state = ServiceState.ACTIVE
                self.active_instances[service_name] = to_instance
                
                logger.info(
                    "Failover completed for service %s: %s -> %s (reason: %s)",
                    service_name, from_instance, to_instance, reason
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error("Error performing failover: %s", e)
            return False
    
    async def _find_instance(self, service_name: str, instance_id: str) -> Optional[ServiceInstance]:
        """Find an instance by ID"""
        instances = self.instances.get(service_name, [])
        for instance in instances:
            if instance.id == instance_id:
                return instance
        return None

# Global failover manager instance
_failover_manager: Optional[FailoverManager] = None

async def get_failover_manager() -> FailoverManager:
    """Get global failover manager instance"""
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = FailoverManager()
        await _failover_manager.start()
    return _failover_manager

async def shutdown_failover_manager():
    """Shutdown global failover manager"""
    global _failover_manager
    if _failover_manager:
        await _failover_manager.stop()
        _failover_manager = None

if __name__ == "__main__":
    async def test_failover_manager():
        """Test failover manager functionality"""
        manager = FailoverManager()
        await manager.start()
        
        try:
            # Create test instances
            instances = [
                ServiceInstance(
                    id="instance_1",
                    endpoint="http://localhost:8001",
                    priority=1,
                    weight=100
                ),
                ServiceInstance(
                    id="instance_2", 
                    endpoint="http://localhost:8002",
                    priority=2,
                    weight=80
                ),
                ServiceInstance(
                    id="instance_3",
                    endpoint="http://localhost:8003",
                    priority=3,
                    weight=60
                )
            ]
            
            # Create configuration
            config = FailoverConfig(
                service_name="test_service",
                strategy=FailoverStrategy.ACTIVE_PASSIVE,
                health_check_interval=5.0,
                failure_threshold=2
            )
            
            # Register service
            await manager.register_service(config, instances)
            
            # Get active instance
            active = await manager.get_active_instance("test_service")
            print(f"Active instance: {active.id if active else None}")
            
            # Get service status
            status = await manager.get_service_status("test_service")
            print(f"Service status: {status}")
            
            # Trigger manual failover
            success = await manager.trigger_failover(
                "test_service",
                "Manual test failover",
                FailoverTrigger.MANUAL
            )
            print(f"Failover success: {success}")
            
            # Get updated active instance
            active = await manager.get_active_instance("test_service")
            print(f"New active instance: {active.id if active else None}")
            
            # Get failover history
            history = await manager.get_failover_history("test_service")
            print(f"Failover history: {len(history)} events")
            
        finally:
            await manager.stop()
    
    # Run test
    asyncio.run(test_failover_manager())