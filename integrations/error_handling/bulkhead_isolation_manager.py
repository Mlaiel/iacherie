#!/usr/bin/env python3
"""Bulkhead Isolation Manager - Resource Protection Pattern
=========================================================

Advanced bulkhead isolation implementation for Ainflue platform error handling.
Provides resource pool isolation, thread pool management, and fault containment
to prevent cascading failures across services.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import resource

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class IsolationType(Enum):
    """Types of bulkhead isolation."""
    THREAD_POOL = "thread_pool"
    SEMAPHORE = "semaphore"
    RESOURCE_POOL = "resource_pool"
    CONNECTION_POOL = "connection_pool"
    MEMORY_POOL = "memory_pool"


class ResourceState(Enum):
    """Resource state enumeration."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    EXHAUSTED = "exhausted"
    DEGRADED = "degraded"


@dataclass
class BulkheadConfig:
    """Bulkhead isolation configuration."""
    max_concurrent_requests: int = 10
    max_queue_size: int = 100
    timeout_seconds: float = 30.0
    isolation_type: IsolationType = IsolationType.SEMAPHORE
    thread_pool_size: int = 5
    resource_limits: Dict[str, int] = field(default_factory=dict)
    enable_fallback: bool = True
    fallback_pool_size: int = 2
    monitoring_interval: float = 5.0


@dataclass
class ResourceMetrics:
    """Resource utilization metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    rejected_requests: int = 0
    timeout_requests: int = 0
    current_active: int = 0
    peak_active: int = 0
    queue_size: int = 0
    peak_queue_size: int = 0
    average_execution_time: float = 0.0
    resource_utilization: float = 0.0
    contention_events: int = 0


@dataclass
class IsolationBreach:
    """Information about isolation breach event."""
    service_name: str
    breach_time: datetime
    breach_type: str
    affected_resources: List[str]
    severity: ErrorSeverity
    recovery_action: str


class BulkheadIsolationManager:
    """Bulkhead isolation enterprise avec resource pool management."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """Initialize bulkhead isolation manager.
        
        Args:
            error_handler: Optional error handler for integration
        """
        self.error_handler = error_handler
        self.bulkheads: Dict[str, 'Bulkhead'] = {}
        self.global_config = BulkheadConfig()
        self.metrics: Dict[str, ResourceMetrics] = defaultdict(ResourceMetrics)
        self.isolation_breaches: List[IsolationBreach] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.logger = logger
        self._lock = threading.Lock()
        
    def create_bulkhead(
        self,
        service_name: str,
        config: Optional[BulkheadConfig] = None
    ) -> 'Bulkhead':
        """Create bulkhead for service.
        
        Args:
            service_name: Name of the service
            config: Optional specific configuration
            
        Returns:
            Bulkhead instance
        """
        with self._lock:
            if service_name not in self.bulkheads:
                bulkhead_config = config or self.global_config
                self.bulkheads[service_name] = Bulkhead(
                    service_name=service_name,
                    config=bulkhead_config,
                    error_handler=self.error_handler,
                    metrics=self.metrics[service_name]
                )
                
        return self.bulkheads[service_name]
    
    def get_bulkhead(self, service_name: str) -> Optional['Bulkhead']:
        """Get existing bulkhead for service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Bulkhead instance if exists, None otherwise
        """
        return self.bulkheads.get(service_name)
    
    async def resource_pool_isolation(self) -> Dict[str, Any]:
        """Manage resource pool isolation across all bulkheads.
        
        Returns:
            Resource pool isolation status
        """
        isolation_status = {
            "total_bulkheads": len(self.bulkheads),
            "resource_pools": {},
            "isolation_effectiveness": {},
            "resource_contention": {}
        }
        
        for service_name, bulkhead in self.bulkheads.items():
            pool_status = await bulkhead.get_resource_pool_status()
            isolation_status["resource_pools"][service_name] = pool_status
            
            # Calculate isolation effectiveness
            metrics = self.metrics[service_name]
            effectiveness = self._calculate_isolation_effectiveness(metrics)
            isolation_status["isolation_effectiveness"][service_name] = effectiveness
            
            # Check for resource contention
            contention = await self._check_resource_contention(service_name, metrics)
            isolation_status["resource_contention"][service_name] = contention
        
        return isolation_status
    
    async def thread_pool_bulkhead_implementation(self) -> Dict[str, Any]:
        """Implement and monitor thread pool bulkheads.
        
        Returns:
            Thread pool implementation status
        """
        thread_pool_status = {
            "active_thread_pools": {},
            "thread_utilization": {},
            "pool_health": {},
            "scaling_recommendations": {}
        }
        
        for service_name, bulkhead in self.bulkheads.items():
            if bulkhead.config.isolation_type == IsolationType.THREAD_POOL:
                pool_info = await bulkhead.get_thread_pool_info()
                thread_pool_status["active_thread_pools"][service_name] = pool_info
                
                # Calculate thread utilization
                utilization = pool_info["active_threads"] / pool_info["pool_size"]
                thread_pool_status["thread_utilization"][service_name] = utilization
                
                # Assess pool health
                health = await self._assess_thread_pool_health(service_name, pool_info)
                thread_pool_status["pool_health"][service_name] = health
                
                # Generate scaling recommendations
                recommendations = await self._generate_thread_pool_scaling_recommendations(
                    service_name, pool_info, utilization
                )
                thread_pool_status["scaling_recommendations"][service_name] = recommendations
        
        return thread_pool_status
    
    async def semaphore_based_isolation(self) -> Dict[str, Any]:
        """Manage semaphore-based isolation.
        
        Returns:
            Semaphore isolation status
        """
        semaphore_status = {
            "active_semaphores": {},
            "permit_utilization": {},
            "waiting_queues": {},
            "optimization_suggestions": {}
        }
        
        for service_name, bulkhead in self.bulkheads.items():
            if bulkhead.config.isolation_type == IsolationType.SEMAPHORE:
                semaphore_info = await bulkhead.get_semaphore_info()
                semaphore_status["active_semaphores"][service_name] = semaphore_info
                
                # Calculate permit utilization
                utilization = (
                    semaphore_info["acquired_permits"] / 
                    semaphore_info["total_permits"]
                )
                semaphore_status["permit_utilization"][service_name] = utilization
                
                # Monitor waiting queues
                queue_info = await bulkhead.get_queue_info()
                semaphore_status["waiting_queues"][service_name] = queue_info
                
                # Generate optimization suggestions
                suggestions = await self._generate_semaphore_optimization_suggestions(
                    service_name, semaphore_info, queue_info
                )
                semaphore_status["optimization_suggestions"][service_name] = suggestions
        
        return semaphore_status
    
    async def resource_contention_monitoring(self) -> Dict[str, Any]:
        """Monitor resource contention across all bulkheads.
        
        Returns:
            Resource contention monitoring results
        """
        contention_analysis = {
            "global_contention_level": 0.0,
            "service_contention": {},
            "contention_hotspots": [],
            "mitigation_strategies": {}
        }
        
        total_contention = 0.0
        service_count = 0
        
        for service_name, bulkhead in self.bulkheads.items():
            metrics = self.metrics[service_name]
            contention_level = await self._calculate_contention_level(service_name, metrics)
            
            contention_analysis["service_contention"][service_name] = {
                "contention_level": contention_level,
                "contention_events": metrics.contention_events,
                "resource_utilization": metrics.resource_utilization,
                "rejection_rate": metrics.rejected_requests / max(metrics.total_requests, 1)
            }
            
            total_contention += contention_level
            service_count += 1
            
            # Identify hotspots
            if contention_level > 0.7:
                contention_analysis["contention_hotspots"].append({
                    "service": service_name,
                    "level": contention_level,
                    "type": "high_contention"
                })
            
            # Generate mitigation strategies
            strategies = await self._generate_contention_mitigation_strategies(
                service_name, contention_level, metrics
            )
            contention_analysis["mitigation_strategies"][service_name] = strategies
        
        contention_analysis["global_contention_level"] = (
            total_contention / service_count if service_count > 0 else 0.0
        )
        
        return contention_analysis
    
    async def isolation_breach_detection(self) -> Dict[str, Any]:
        """Detect isolation breaches and containment failures.
        
        Returns:
            Isolation breach detection results
        """
        breach_detection = {
            "active_breaches": [],
            "breach_history": [],
            "breach_patterns": {},
            "containment_effectiveness": {}
        }
        
        # Check for current breaches
        for service_name, bulkhead in self.bulkheads.items():
            breach_indicators = await self._check_isolation_breach_indicators(
                service_name, bulkhead
            )
            
            if breach_indicators["breach_detected"]:
                breach = IsolationBreach(
                    service_name=service_name,
                    breach_time=datetime.now(),
                    breach_type=breach_indicators["breach_type"],
                    affected_resources=breach_indicators["affected_resources"],
                    severity=breach_indicators["severity"],
                    recovery_action=breach_indicators["recovery_action"]
                )
                
                self.isolation_breaches.append(breach)
                breach_detection["active_breaches"].append({
                    "service": service_name,
                    "type": breach.breach_type,
                    "severity": breach.severity.value,
                    "affected_resources": breach.affected_resources,
                    "recovery_action": breach.recovery_action
                })
                
                # Integrate with error handler
                if self.error_handler:
                    await self.error_handler.handle_error(
                        exception=Exception(f"Isolation breach detected in {service_name}"),
                        context={
                            "service": service_name,
                            "breach_type": breach.breach_type,
                            "affected_resources": breach.affected_resources
                        },
                        severity=breach.severity,
                        category=ErrorCategory.BUSINESS_LOGIC
                    )
        
        # Analyze breach history
        recent_breaches = [
            breach for breach in self.isolation_breaches
            if (datetime.now() - breach.breach_time).total_seconds() < 3600
        ]
        
        breach_detection["breach_history"] = [
            {
                "service": breach.service_name,
                "time": breach.breach_time.isoformat(),
                "type": breach.breach_type,
                "severity": breach.severity.value
            }
            for breach in recent_breaches
        ]
        
        # Analyze breach patterns
        breach_detection["breach_patterns"] = await self._analyze_breach_patterns()
        
        # Calculate containment effectiveness
        breach_detection["containment_effectiveness"] = await self._calculate_containment_effectiveness()
        
        return breach_detection
    
    async def dynamic_resource_allocation(self) -> Dict[str, Any]:
        """Dynamically allocate resources based on demand and performance.
        
        Returns:
            Dynamic allocation results
        """
        allocation_results = {
            "current_allocations": {},
            "allocation_changes": [],
            "optimization_opportunities": {},
            "resource_efficiency": {}
        }
        
        for service_name, bulkhead in self.bulkheads.items():
            metrics = self.metrics[service_name]
            current_allocation = await bulkhead.get_current_resource_allocation()
            
            allocation_results["current_allocations"][service_name] = current_allocation
            
            # Calculate optimal allocation
            optimal_allocation = await self._calculate_optimal_allocation(
                service_name, metrics, current_allocation
            )
            
            # Apply allocation changes if needed
            if await self._should_adjust_allocation(current_allocation, optimal_allocation):
                changes = await bulkhead.adjust_resource_allocation(optimal_allocation)
                allocation_results["allocation_changes"].append({
                    "service": service_name,
                    "changes": changes,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                service_name, metrics, current_allocation
            )
            allocation_results["optimization_opportunities"][service_name] = opportunities
            
            # Calculate resource efficiency
            efficiency = await self._calculate_resource_efficiency(metrics, current_allocation)
            allocation_results["resource_efficiency"][service_name] = efficiency
        
        return allocation_results
    
    async def start_monitoring(self):
        """Start continuous monitoring of bulkheads."""
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                # Update metrics for all bulkheads
                for service_name, bulkhead in self.bulkheads.items():
                    await bulkhead.update_metrics()
                
                # Check for isolation breaches
                await self.isolation_breach_detection()
                
                # Monitor resource contention
                await self.resource_contention_monitoring()
                
                # Perform dynamic resource allocation
                await self.dynamic_resource_allocation()
                
                await asyncio.sleep(self.global_config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.global_config.monitoring_interval)
    
    def _calculate_isolation_effectiveness(self, metrics: ResourceMetrics) -> float:
        """Calculate isolation effectiveness for a service."""
        if metrics.total_requests == 0:
            return 1.0
        
        success_rate = metrics.successful_requests / metrics.total_requests
        containment_rate = 1.0 - (metrics.contention_events / max(metrics.total_requests, 1))
        
        return (success_rate + containment_rate) / 2.0
    
    async def _check_resource_contention(self, service_name: str, metrics: ResourceMetrics) -> Dict[str, Any]:
        """Check for resource contention in a service."""
        return {
            "contention_detected": metrics.contention_events > 0,
            "contention_level": metrics.contention_events / max(metrics.total_requests, 1),
            "queue_pressure": metrics.queue_size / max(metrics.peak_queue_size, 1),
            "utilization_pressure": metrics.resource_utilization
        }
    
    async def _assess_thread_pool_health(self, service_name: str, pool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess thread pool health."""
        utilization = pool_info["active_threads"] / pool_info["pool_size"]
        
        health_score = 1.0
        if utilization > 0.9:
            health_score = 0.3  # Critical
        elif utilization > 0.7:
            health_score = 0.6  # Warning
        elif utilization > 0.5:
            health_score = 0.8  # Good
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "critical",
            "utilization": utilization,
            "queue_length": pool_info.get("queue_length", 0)
        }
    
    async def _generate_thread_pool_scaling_recommendations(
        self,
        service_name: str,
        pool_info: Dict[str, Any],
        utilization: float
    ) -> List[str]:
        """Generate thread pool scaling recommendations."""
        recommendations = []
        
        if utilization > 0.8:
            recommendations.append("Consider increasing thread pool size")
        elif utilization < 0.3:
            recommendations.append("Consider decreasing thread pool size to save resources")
        
        if pool_info.get("queue_length", 0) > 10:
            recommendations.append("High queue length detected, consider increasing pool size or request timeout")
        
        return recommendations
    
    async def _generate_semaphore_optimization_suggestions(
        self,
        service_name: str,
        semaphore_info: Dict[str, Any],
        queue_info: Dict[str, Any]
    ) -> List[str]:
        """Generate semaphore optimization suggestions."""
        suggestions = []
        
        utilization = semaphore_info["acquired_permits"] / semaphore_info["total_permits"]
        
        if utilization > 0.9:
            suggestions.append("Consider increasing semaphore permits")
        elif utilization < 0.3:
            suggestions.append("Consider decreasing semaphore permits")
        
        if queue_info.get("waiting_requests", 0) > 20:
            suggestions.append("High queue size detected, consider increasing permits or timeout")
        
        return suggestions
    
    async def _calculate_contention_level(self, service_name: str, metrics: ResourceMetrics) -> float:
        """Calculate contention level for a service."""
        if metrics.total_requests == 0:
            return 0.0
        
        rejection_rate = metrics.rejected_requests / metrics.total_requests
        timeout_rate = metrics.timeout_requests / metrics.total_requests
        utilization = metrics.resource_utilization
        
        contention_level = (rejection_rate * 0.4 + timeout_rate * 0.3 + utilization * 0.3)
        return min(1.0, contention_level)
    
    async def _generate_contention_mitigation_strategies(
        self,
        service_name: str,
        contention_level: float,
        metrics: ResourceMetrics
    ) -> List[str]:
        """Generate contention mitigation strategies."""
        strategies = []
        
        if contention_level > 0.7:
            strategies.append("Critical contention detected - consider emergency resource scaling")
            strategies.append("Implement request prioritization")
        elif contention_level > 0.5:
            strategies.append("High contention - increase resource allocation")
            strategies.append("Consider load balancing adjustments")
        elif contention_level > 0.3:
            strategies.append("Moderate contention - monitor closely")
        
        if metrics.rejected_requests > metrics.successful_requests:
            strategies.append("High rejection rate - increase capacity or implement backpressure")
        
        return strategies
    
    async def _check_isolation_breach_indicators(
        self,
        service_name: str,
        bulkhead: 'Bulkhead'
    ) -> Dict[str, Any]:
        """Check for isolation breach indicators."""
        metrics = self.metrics[service_name]
        
        breach_detected = False
        breach_type = "none"
        affected_resources = []
        severity = ErrorSeverity.LOW
        recovery_action = "monitor"
        
        # Check for resource exhaustion
        if metrics.resource_utilization > 0.95:
            breach_detected = True
            breach_type = "resource_exhaustion"
            affected_resources.append("compute_resources")
            severity = ErrorSeverity.CRITICAL
            recovery_action = "scale_resources"
        
        # Check for queue overflow
        if metrics.queue_size > bulkhead.config.max_queue_size * 0.9:
            breach_detected = True
            breach_type = "queue_overflow"
            affected_resources.append("request_queue")
            severity = ErrorSeverity.HIGH
            recovery_action = "increase_capacity"
        
        # Check for high rejection rate
        rejection_rate = metrics.rejected_requests / max(metrics.total_requests, 1)
        if rejection_rate > 0.5:
            breach_detected = True
            breach_type = "high_rejection_rate"
            affected_resources.append("request_processing")
            severity = ErrorSeverity.HIGH
            recovery_action = "adjust_limits"
        
        return {
            "breach_detected": breach_detected,
            "breach_type": breach_type,
            "affected_resources": affected_resources,
            "severity": severity,
            "recovery_action": recovery_action
        }
    
    async def _analyze_breach_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in isolation breaches."""
        if not self.isolation_breaches:
            return {"patterns": [], "recommendations": []}
        
        # Group breaches by service
        service_breaches = defaultdict(list)
        for breach in self.isolation_breaches:
            service_breaches[breach.service_name].append(breach)
        
        patterns = []
        for service, breaches in service_breaches.items():
            if len(breaches) > 2:
                patterns.append({
                    "service": service,
                    "breach_count": len(breaches),
                    "most_common_type": max(
                        set(b.breach_type for b in breaches),
                        key=lambda x: sum(1 for b in breaches if b.breach_type == x)
                    ),
                    "average_severity": sum(
                        ["low", "medium", "high", "critical"].index(b.severity.value)
                        for b in breaches
                    ) / len(breaches)
                })
        
        recommendations = []
        if patterns:
            recommendations.append("Implement proactive monitoring for high-breach services")
            recommendations.append("Consider adjusting resource allocation for problematic services")
        
        return {"patterns": patterns, "recommendations": recommendations}
    
    async def _calculate_containment_effectiveness(self) -> float:
        """Calculate overall containment effectiveness."""
        if not self.isolation_breaches:
            return 1.0
        
        total_services = len(self.bulkheads)
        breached_services = len(set(b.service_name for b in self.isolation_breaches))
        
        containment_rate = 1.0 - (breached_services / total_services)
        return max(0.0, containment_rate)
    
    async def _calculate_optimal_allocation(
        self,
        service_name: str,
        metrics: ResourceMetrics,
        current_allocation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimal resource allocation."""
        optimal = current_allocation.copy()
        
        # Adjust based on utilization
        if metrics.resource_utilization > 0.8:
            optimal["max_concurrent"] = int(current_allocation["max_concurrent"] * 1.2)
        elif metrics.resource_utilization < 0.3:
            optimal["max_concurrent"] = max(1, int(current_allocation["max_concurrent"] * 0.8))
        
        # Adjust queue size based on rejection rate
        rejection_rate = metrics.rejected_requests / max(metrics.total_requests, 1)
        if rejection_rate > 0.1:
            optimal["queue_size"] = int(current_allocation["queue_size"] * 1.5)
        
        return optimal
    
    async def _should_adjust_allocation(
        self,
        current: Dict[str, Any],
        optimal: Dict[str, Any]
    ) -> bool:
        """Check if allocation should be adjusted."""
        for key, value in optimal.items():
            if abs(value - current.get(key, 0)) / max(current.get(key, 1), 1) > 0.1:
                return True
        return False
    
    async def _identify_optimization_opportunities(
        self,
        service_name: str,
        metrics: ResourceMetrics,
        allocation: Dict[str, Any]
    ) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = []
        
        if metrics.resource_utilization < 0.5:
            opportunities.append("Low utilization - consider reducing allocated resources")
        
        if metrics.average_execution_time > 5.0:
            opportunities.append("High execution time - consider performance optimization")
        
        if metrics.rejected_requests > 0 and metrics.resource_utilization < 0.8:
            opportunities.append("Rejections with low utilization - review configuration")
        
        return opportunities
    
    async def _calculate_resource_efficiency(
        self,
        metrics: ResourceMetrics,
        allocation: Dict[str, Any]
    ) -> float:
        """Calculate resource efficiency."""
        if metrics.total_requests == 0:
            return 0.0
        
        success_rate = metrics.successful_requests / metrics.total_requests
        utilization_efficiency = min(1.0, metrics.resource_utilization / 0.8)
        
        return (success_rate + utilization_efficiency) / 2.0


class Bulkhead:
    """Individual bulkhead implementation."""
    
    def __init__(
        self,
        service_name: str,
        config: BulkheadConfig,
        error_handler: Optional[ErrorHandler] = None,
        metrics: Optional[ResourceMetrics] = None
    ):
        """Initialize bulkhead.
        
        Args:
            service_name: Name of the service
            config: Bulkhead configuration
            error_handler: Optional error handler
            metrics: Optional metrics instance
        """
        self.service_name = service_name
        self.config = config
        self.error_handler = error_handler
        self.metrics = metrics or ResourceMetrics()
        
        # Initialize isolation mechanisms
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=config.thread_pool_size,
            thread_name_prefix=f"bulkhead-{service_name}"
        )
        self.request_queue = Queue(maxsize=config.max_queue_size)
        self._active_requests = 0
        self._lock = threading.Lock()
        
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with bulkhead protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        start_time = time.time()
        
        try:
            if self.config.isolation_type == IsolationType.SEMAPHORE:
                return await self._execute_with_semaphore(func, start_time, *args, **kwargs)
            elif self.config.isolation_type == IsolationType.THREAD_POOL:
                return await self._execute_with_thread_pool(func, start_time, *args, **kwargs)
            else:
                return await self._execute_with_resource_pool(func, start_time, *args, **kwargs)
                
        except Exception as e:
            execution_time = time.time() - start_time
            await self._record_failure(e, execution_time)
            raise
    
    async def _execute_with_semaphore(self, func: Callable, start_time: float, *args, **kwargs) -> Any:
        """Execute function with semaphore-based isolation."""
        try:
            # Try to acquire semaphore with timeout
            await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.config.timeout_seconds
            )
        except asyncio.TimeoutError:
            self.metrics.timeout_requests += 1
            self.metrics.rejected_requests += 1
            raise TimeoutError(f"Timeout acquiring semaphore for {self.service_name}")
        
        try:
            with self._lock:
                self._active_requests += 1
                self.metrics.current_active = self._active_requests
                self.metrics.peak_active = max(self.metrics.peak_active, self._active_requests)
            
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            await self._record_success(execution_time)
            return result
            
        finally:
            with self._lock:
                self._active_requests -= 1
                self.metrics.current_active = self._active_requests
            self.semaphore.release()
    
    async def _execute_with_thread_pool(self, func: Callable, start_time: float, *args, **kwargs) -> Any:
        """Execute function with thread pool isolation."""
        loop = asyncio.get_event_loop()
        
        try:
            future = loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
            result = await asyncio.wait_for(future, timeout=self.config.timeout_seconds)
            execution_time = time.time() - start_time
            await self._record_success(execution_time)
            return result
            
        except asyncio.TimeoutError:
            self.metrics.timeout_requests += 1
            self.metrics.rejected_requests += 1
            raise TimeoutError(f"Timeout in thread pool execution for {self.service_name}")
    
    async def _execute_with_resource_pool(self, func: Callable, start_time: float, *args, **kwargs) -> Any:
        """Execute function with resource pool isolation."""
        # Check if we can accept the request
        if self._active_requests >= self.config.max_concurrent_requests:
            self.metrics.rejected_requests += 1
            raise Exception(f"Resource pool exhausted for {self.service_name}")
        
        with self._lock:
            self._active_requests += 1
            self.metrics.current_active = self._active_requests
            self.metrics.peak_active = max(self.metrics.peak_active, self._active_requests)
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            await self._record_success(execution_time)
            return result
            
        finally:
            with self._lock:
                self._active_requests -= 1
                self.metrics.current_active = self._active_requests
    
    async def _record_success(self, execution_time: float):
        """Record successful execution."""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        
        # Update average execution time
        total_time = self.metrics.average_execution_time * (self.metrics.successful_requests - 1)
        self.metrics.average_execution_time = (total_time + execution_time) / self.metrics.successful_requests
        
        # Update resource utilization
        self.metrics.resource_utilization = self._active_requests / self.config.max_concurrent_requests
    
    async def _record_failure(self, exception: Exception, execution_time: float):
        """Record failed execution."""
        self.metrics.total_requests += 1
        
        # Update resource utilization
        self.metrics.resource_utilization = self._active_requests / self.config.max_concurrent_requests
        
        # Record contention event if resource-related
        if isinstance(exception, (TimeoutError, ResourceError)):
            self.metrics.contention_events += 1
    
    async def get_resource_pool_status(self) -> Dict[str, Any]:
        """Get current resource pool status."""
        return {
            "service_name": self.service_name,
            "isolation_type": self.config.isolation_type.value,
            "max_concurrent": self.config.max_concurrent_requests,
            "current_active": self.metrics.current_active,
            "peak_active": self.metrics.peak_active,
            "utilization": self.metrics.resource_utilization,
            "queue_size": self.metrics.queue_size,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "rejected_requests": self.metrics.rejected_requests
        }
    
    async def get_thread_pool_info(self) -> Dict[str, Any]:
        """Get thread pool information."""
        return {
            "pool_size": self.config.thread_pool_size,
            "active_threads": getattr(self.thread_pool, '_threads', 0),
            "queue_length": getattr(self.thread_pool._work_queue, 'qsize', lambda: 0)()
        }
    
    async def get_semaphore_info(self) -> Dict[str, Any]:
        """Get semaphore information."""
        return {
            "total_permits": self.config.max_concurrent_requests,
            "acquired_permits": self.config.max_concurrent_requests - self.semaphore._value,
            "available_permits": self.semaphore._value
        }
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Get queue information."""
        return {
            "max_size": self.config.max_queue_size,
            "current_size": self.metrics.queue_size,
            "peak_size": self.metrics.peak_queue_size,
            "waiting_requests": max(0, self.metrics.queue_size)
        }
    
    async def get_current_resource_allocation(self) -> Dict[str, Any]:
        """Get current resource allocation."""
        return {
            "max_concurrent": self.config.max_concurrent_requests,
            "queue_size": self.config.max_queue_size,
            "thread_pool_size": self.config.thread_pool_size,
            "timeout": self.config.timeout_seconds
        }
    
    async def adjust_resource_allocation(self, new_allocation: Dict[str, Any]) -> List[str]:
        """Adjust resource allocation based on new configuration."""
        changes = []
        
        if "max_concurrent" in new_allocation:
            old_value = self.config.max_concurrent_requests
            self.config.max_concurrent_requests = new_allocation["max_concurrent"]
            changes.append(f"max_concurrent: {old_value} -> {new_allocation['max_concurrent']}")
        
        if "queue_size" in new_allocation:
            old_value = self.config.max_queue_size
            self.config.max_queue_size = new_allocation["queue_size"]
            changes.append(f"queue_size: {old_value} -> {new_allocation['queue_size']}")
        
        if "thread_pool_size" in new_allocation:
            old_value = self.config.thread_pool_size
            self.config.thread_pool_size = new_allocation["thread_pool_size"]
            # Note: ThreadPoolExecutor doesn't support dynamic resizing
            changes.append(f"thread_pool_size: {old_value} -> {new_allocation['thread_pool_size']} (requires restart)")
        
        return changes
    
    async def update_metrics(self):
        """Update internal metrics."""
        self.metrics.queue_size = getattr(self.request_queue, 'qsize', lambda: 0)()
        self.metrics.peak_queue_size = max(self.metrics.peak_queue_size, self.metrics.queue_size)
        self.metrics.resource_utilization = self._active_requests / self.config.max_concurrent_requests


class ResourceError(Exception):
    """Exception raised when resource limits are exceeded."""
    pass