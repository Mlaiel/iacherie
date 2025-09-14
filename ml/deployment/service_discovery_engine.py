"""
Service Discovery Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ML Module - Service Discovery Engine
Service discovery and registration for ML microservices

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0
Letztes Update: Januar 2025

⚠️ WARNUNG: Dieser Code ist urheberrechtlich geschützt und vertraulich.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
import hashlib
import socket
import aiohttp
from pathlib import Path
from collections import defaultdict, deque
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class ServiceType(Enum):
    """Types of ML services."""
    INFERENCE = "inference"
    TRAINING = "training"
    FEATURE_STORE = "feature_store"
    MODEL_REGISTRY = "model_registry"
    MONITORING = "monitoring"
    SECURITY = "security"
    API_GATEWAY = "api_gateway"
    DATA_PIPELINE = "data_pipeline"

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    CREATOR_AFFINITY = "creator_affinity"

class CreatorType(Enum):
    """Creator types for service affinity."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class ServiceInstance:
    """ML service instance registration."""
    service_id: str
    service_name: str
    service_type: ServiceType
    host: str
    port: int
    version: str
    status: ServiceStatus
    health_check_url: str
    registration_time: datetime
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    creator_affinity: Optional[List[CreatorType]] = None
    load_score: float = 0.0
    connection_count: int = 0
    response_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['registration_time'] = self.registration_time.isoformat()
        result['last_heartbeat'] = self.last_heartbeat.isoformat()
        result['status'] = self.status.value
        result['service_type'] = self.service_type.value
        if self.creator_affinity:
            result['creator_affinity'] = [c.value for c in self.creator_affinity]
        return result

@dataclass
class ServiceDiscoveryConfig:
    """Configuration for service discovery."""
    heartbeat_interval_seconds: int = 30
    health_check_timeout_seconds: int = 5
    service_timeout_seconds: int = 120
    max_retry_attempts: int = 3
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    enable_service_mesh: bool = True

@dataclass
class HealthCheck:
    """Service health check result."""
    service_id: str
    timestamp: datetime
    status: ServiceStatus
    response_time_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class LoadBalancingDecision:
    """Load balancing decision result."""
    selected_service: ServiceInstance
    strategy_used: LoadBalancingStrategy
    decision_factors: Dict[str, Any]
    timestamp: datetime

class ServiceDiscoveryEngine:
    """
    🌐 MICROSERVICES - Enterprise Service Discovery System
    
    Sophisticated service discovery with health monitoring, load balancing,
    creator affinity routing, and ML-aware service orchestration.
    """
    
    def __init__(self, config -> None: Optional[ServiceDiscoveryConfig] = None) -> None:
        """Initialize service discovery engine."""
        self.config = config or ServiceDiscoveryConfig()
        self.services: Dict[str, ServiceInstance] = {}
        self.service_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.health_checks: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.load_balancing_state: Dict[str, Any] = defaultdict(dict)
        self.circuit_breaker_state: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "failure_count": 0,
            "last_failure": None,
            "state": "closed"  # closed, open, half_open
        })
        
        # Creator affinity routing
        self.creator_service_affinity: Dict[CreatorType, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Performance tracking
        self.performance_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Initialize logging
        logger.info("🌐 ServiceDiscoveryEngine initialized - Microservices expertise")
        
        # Start background tasks
        asyncio.create_task(self._start_health_monitoring())
        asyncio.create_task(self._start_service_cleanup())
        asyncio.create_task(self._start_performance_tracking())
    
    async def register_service(
        self,
        service_name: str,
        service_type: ServiceType,
        host: str,
        port: int,
        version: str = "1.0.0",
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        creator_affinity: Optional[List[CreatorType]] = None
    ) -> str:
        """
        Register a new service instance.
        
        Args:
            service_name: Name of the service
            service_type: Type of ML service
            host: Service host address
            port: Service port
            version: Service version
            health_check_url: Health check endpoint
            metadata: Additional service metadata
            creator_affinity: Creator types this service is optimized for
            
        Returns:
            Service ID
        """
        # Generate unique service ID
        service_id = f"{service_name}_{host}_{port}_{int(time.time())}"
        
        # Set default health check URL
        if not health_check_url:
            health_check_url = f"http://{host}:{port}/health"
        
        # Create service instance
        service_instance = ServiceInstance(
            service_id=service_id,
            service_name=service_name,
            service_type=service_type,
            host=host,
            port=port,
            version=version,
            status=ServiceStatus.STARTING,
            health_check_url=health_check_url,
            registration_time=datetime.now(),
            last_heartbeat=datetime.now(),
            metadata=metadata or {},
            creator_affinity=creator_affinity or []
        )
        
        # Register the service
        self.services[service_id] = service_instance
        
        # Perform initial health check
        await self._perform_health_check(service_id)
        
        # Initialize load balancing state
        self._initialize_load_balancing_state(service_id)
        
        # Notify event handlers
        await self._notify_event_handlers("service_registered", service_instance)
        
        logger.info(f"✅ Service registered: {service_name} ({service_id})")
        return service_id
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service instance.
        
        Args:
            service_id: Service ID to deregister
            
        Returns:
            Success status
        """
        if service_id not in self.services:
            logger.warning(f"⚠️ Service not found for deregistration: {service_id}")
            return False
        
        service_instance = self.services[service_id]
        service_instance.status = ServiceStatus.STOPPING
        
        # Notify event handlers
        await self._notify_event_handlers("service_deregistering", service_instance)
        
        # Remove from registry
        del self.services[service_id]
        
        # Clean up state
        if service_id in self.load_balancing_state:
            del self.load_balancing_state[service_id]
        
        if service_id in self.circuit_breaker_state:
            del self.circuit_breaker_state[service_id]
        
        logger.info(f"✅ Service deregistered: {service_instance.service_name} ({service_id})")
        return True
    
    async def discover_services(
        self,
        service_name: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        creator_type: Optional[CreatorType] = None,
        include_unhealthy: bool = False
    ) -> List[ServiceInstance]:
        """
        Discover available services.
        
        Args:
            service_name: Filter by service name
            service_type: Filter by service type
            creator_type: Filter by creator affinity
            include_unhealthy: Include unhealthy services
            
        Returns:
            List of matching service instances
        """
        matching_services = []
        
        for service in self.services.values():
            # Apply filters
            if service_name and service.service_name != service_name:
                continue
            
            if service_type and service.service_type != service_type:
                continue
            
            if creator_type and service.creator_affinity:
                if creator_type not in service.creator_affinity:
                    continue
            
            if not include_unhealthy and service.status != ServiceStatus.HEALTHY:
                continue
            
            matching_services.append(service)
        
        logger.info(f"🔍 Discovered {len(matching_services)} services")
        return matching_services
    
    async def get_service_for_request(
        self,
        service_name: str,
        creator_type: Optional[CreatorType] = None,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[LoadBalancingDecision]:
        """
        Get the best service instance for a request using load balancing.
        
        Args:
            service_name: Name of the service needed
            creator_type: Creator type for affinity routing
            request_metadata: Additional request metadata
            
        Returns:
            Load balancing decision with selected service
        """
        # Discover available services
        available_services = await self.discover_services(
            service_name=service_name,
            creator_type=creator_type,
            include_unhealthy=False
        )
        
        if not available_services:
            logger.warning(f"⚠️ No healthy services found for: {service_name}")
            return None
        
        # Apply circuit breaker filtering
        if self.config.enable_circuit_breaker:
            available_services = [
                s for s in available_services
                if self.circuit_breaker_state[s.service_id]["state"] != "open"
            ]
        
        if not available_services:
            logger.warning(f"⚠️ All services circuit breaker open for: {service_name}")
            return None
        
        # Select service based on load balancing strategy
        selected_service = await self._select_service_by_strategy(
            available_services,
            self.config.load_balancing_strategy,
            creator_type,
            request_metadata
        )
        
        if not selected_service:
            return None
        
        # Update connection count
        selected_service.connection_count += 1
        
        # Create decision record
        decision = LoadBalancingDecision(
            selected_service=selected_service,
            strategy_used=self.config.load_balancing_strategy,
            decision_factors={
                "available_services": len(available_services),
                "creator_type": creator_type.value if creator_type else None,
                "load_score": selected_service.load_score,
                "response_time": selected_service.response_time_ms
            },
            timestamp=datetime.now()
        )
        
        logger.info(f"🎯 Selected service: {selected_service.service_name} ({selected_service.service_id})")
        return decision
    
    async def _select_service_by_strategy(
        self,
        available_services: List[ServiceInstance],
        strategy: LoadBalancingStrategy,
        creator_type: Optional[CreatorType],
        request_metadata: Optional[Dict[str, Any]]
    ) -> Optional[ServiceInstance]:
        """Select service based on load balancing strategy."""
        
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin_selection(available_services)
        
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(available_services, key=lambda s: s.connection_count)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_selection(available_services)
        
        elif strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(available_services)
        
        elif strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return await self._consistent_hash_selection(available_services, request_metadata)
        
        elif strategy == LoadBalancingStrategy.CREATOR_AFFINITY:
            return await self._creator_affinity_selection(available_services, creator_type)
        
        else:
            # Default to round robin
            return await self._round_robin_selection(available_services)
    
    async def _round_robin_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Round robin service selection."""
        if not services:
            return None
        
        # Get or initialize round robin counter
        service_names = {s.service_name for s in services}
        for service_name in service_names:
            if service_name not in self.load_balancing_state:
                self.load_balancing_state[service_name]["round_robin_index"] = 0
        
        # Use the first service's name for the counter (all services have same name in this context)
        service_name = services[0].service_name
        current_index = self.load_balancing_state[service_name]["round_robin_index"]
        
        # Select service and update index
        selected_service = services[current_index % len(services)]
        self.load_balancing_state[service_name]["round_robin_index"] = (current_index + 1) % len(services)
        
        return selected_service
    
    async def _weighted_round_robin_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round robin based on service capacity and performance."""
        if not services:
            return None
        
        # Calculate weights based on inverse response time and load
        weights = []
        for service in services:
            # Lower response time = higher weight
            response_weight = 1.0 / (service.response_time_ms + 1.0)
            # Lower load = higher weight
            load_weight = 1.0 / (service.load_score + 1.0)
            # Combine weights
            total_weight = response_weight * load_weight
            weights.append(total_weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(services)
        
        normalized_weights = [w / total_weight for w in weights]
        
        # Weighted random selection
        r = random.random()
        cumulative_weight = 0
        for i, weight in enumerate(normalized_weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return services[i]
        
        return services[-1]  # Fallback
    
    async def _consistent_hash_selection(
        self,
        services: List[ServiceInstance],
        request_metadata: Optional[Dict[str, Any]]
    ) -> ServiceInstance:
        """Consistent hash selection for sticky sessions."""
        if not services:
            return None
        
        # Create hash key from request metadata
        hash_key = ""
        if request_metadata:
            user_id = request_metadata.get("user_id", "")
            session_id = request_metadata.get("session_id", "")
            hash_key = f"{user_id}_{session_id}"
        
        if not hash_key:
            hash_key = str(time.time())  # Fallback to timestamp
        
        # Generate hash and select service
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        selected_index = hash_value % len(services)
        
        return services[selected_index]
    
    async def _creator_affinity_selection(
        self,
        services: List[ServiceInstance],
        creator_type: Optional[CreatorType]
    ) -> ServiceInstance:
        """Select service based on creator type affinity."""
        if not services:
            return None
        
        if not creator_type:
            # No creator type, use round robin
            return await self._round_robin_selection(services)
        
        # Filter services with creator affinity
        affinity_services = [
            s for s in services
            if s.creator_affinity and creator_type in s.creator_affinity
        ]
        
        if affinity_services:
            # Among affinity services, select by performance
            return min(affinity_services, key=lambda s: s.response_time_ms)
        else:
            # No affinity services, use best performing
            return min(services, key=lambda s: s.response_time_ms)
    
    async def heartbeat(self, service_id: str) -> bool:
        """
        Process service heartbeat.
        
        Args:
            service_id: Service ID sending heartbeat
            
        Returns:
            Success status
        """
        if service_id not in self.services:
            logger.warning(f"⚠️ Heartbeat from unknown service: {service_id}")
            return False
        
        service = self.services[service_id]
        service.last_heartbeat = datetime.now()
        
        # Update service status if it was starting
        if service.status == ServiceStatus.STARTING:
            service.status = ServiceStatus.HEALTHY
            await self._notify_event_handlers("service_healthy", service)
        
        logger.debug(f"💓 Heartbeat received from: {service.service_name} ({service_id})")
        return True
    
    async def update_service_metrics(
        self,
        service_id: str,
        response_time_ms: Optional[float] = None,
        connection_count: Optional[int] = None,
        load_score: Optional[float] = None,
        custom_metrics: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Update service performance metrics.
        
        Args:
            service_id: Service ID
            response_time_ms: Average response time
            connection_count: Current connection count
            load_score: Current load score (0-1)
            custom_metrics: Additional custom metrics
            
        Returns:
            Success status
        """
        if service_id not in self.services:
            logger.warning(f"⚠️ Metrics update for unknown service: {service_id}")
            return False
        
        service = self.services[service_id]
        
        if response_time_ms is not None:
            service.response_time_ms = response_time_ms
        
        if connection_count is not None:
            service.connection_count = connection_count
        
        if load_score is not None:
            service.load_score = load_score
        
        # Store custom metrics
        if custom_metrics:
            self.performance_metrics[service_id].update(custom_metrics)
        
        # Update service history
        self.service_history[service_id].append({
            "timestamp": datetime.now(),
            "response_time_ms": service.response_time_ms,
            "connection_count": service.connection_count,
            "load_score": service.load_score,
            "custom_metrics": custom_metrics or {}
        })
        
        logger.debug(f"📊 Metrics updated for: {service.service_name} ({service_id})")
        return True
    
    async def report_service_error(self, service_id: str, error_details: Dict[str, Any]) -> bool:
        """
        Report service error for circuit breaker.
        
        Args:
            service_id: Service ID that experienced error
            error_details: Error details
            
        Returns:
            Success status
        """
        if service_id not in self.services:
            return False
        
        if not self.config.enable_circuit_breaker:
            return True
        
        # Update circuit breaker state
        cb_state = self.circuit_breaker_state[service_id]
        cb_state["failure_count"] += 1
        cb_state["last_failure"] = datetime.now()
        
        # Check if threshold exceeded
        if cb_state["failure_count"] >= self.config.circuit_breaker_threshold:
            cb_state["state"] = "open"
            self.services[service_id].status = ServiceStatus.UNHEALTHY
            
            await self._notify_event_handlers("circuit_breaker_opened", self.services[service_id])
            
            logger.warning(f"🔴 Circuit breaker opened for: {self.services[service_id].service_name}")
        
        return True
    
    async def _start_health_monitoring(self) -> None:
        """Start health monitoring background task."""
        logger.info("💓 Starting health monitoring")
        
        while True:
            try:
                # Perform health checks for all services
                health_check_tasks = [
                    self._perform_health_check(service_id)
                    for service_id in self.services.keys()
                ]
                
                if health_check_tasks:
                    await asyncio.gather(*health_check_tasks, return_exceptions=True)
                
                # Wait for next health check interval
                await asyncio.sleep(self.config.heartbeat_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_check(self, service_id -> None: str) -> None:
        """Perform health check for a service."""
        if service_id not in self.services:
            return
        
        service = self.services[service_id]
        
        try:
            start_time = time.time()
            
            # Perform HTTP health check
            timeout = aiohttp.ClientTimeout(total=self.config.health_check_timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(service.health_check_url) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        # Service is healthy
                        if service.status != ServiceStatus.HEALTHY:
                            service.status = ServiceStatus.HEALTHY
                            await self._notify_event_handlers("service_recovered", service)
                        
                        # Reset circuit breaker on successful health check
                        if self.config.enable_circuit_breaker:
                            cb_state = self.circuit_breaker_state[service_id]
                            if cb_state["state"] == "open":
                                cb_state["state"] = "half_open"
                            elif cb_state["state"] == "half_open":
                                cb_state["state"] = "closed"
                                cb_state["failure_count"] = 0
                        
                        # Update response time
                        service.response_time_ms = response_time_ms
                        
                        # Record health check
                        health_check = HealthCheck(
                            service_id=service_id,
                            timestamp=datetime.now(),
                            status=ServiceStatus.HEALTHY,
                            response_time_ms=response_time_ms
                        )
                        
                    else:
                        # Service is unhealthy
                        service.status = ServiceStatus.UNHEALTHY
                        await self._notify_event_handlers("service_unhealthy", service)
                        
                        health_check = HealthCheck(
                            service_id=service_id,
                            timestamp=datetime.now(),
                            status=ServiceStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            error_message=f"HTTP {response.status}"
                        )
            
        except asyncio.TimeoutError:
            service.status = ServiceStatus.UNHEALTHY
            health_check = HealthCheck(
                service_id=service_id,
                timestamp=datetime.now(),
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=self.config.health_check_timeout_seconds * 1000,
                error_message="Health check timeout"
            )
            
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            health_check = HealthCheck(
                service_id=service_id,
                timestamp=datetime.now(),
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=0.0,
                error_message=str(e)
            )
        
        # Store health check result
        self.health_checks[service_id].append(health_check)
    
    async def _start_service_cleanup(self) -> None:
        """Start service cleanup background task."""
        logger.info("🧹 Starting service cleanup")
        
        while True:
            try:
                # Remove stale services
                current_time = datetime.now()
                stale_services = []
                
                for service_id, service in self.services.items():
                    time_since_heartbeat = current_time - service.last_heartbeat
                    
                    if time_since_heartbeat.total_seconds() > self.config.service_timeout_seconds:
                        stale_services.append(service_id)
                
                # Remove stale services
                for service_id in stale_services:
                    await self.deregister_service(service_id)
                    logger.info(f"🗑️ Removed stale service: {service_id}")
                
                # Clean up old health check data
                cutoff_time = current_time - timedelta(hours=24)
                for service_id in list(self.health_checks.keys()):
                    health_checks = self.health_checks[service_id]
                    # Keep only recent health checks
                    while health_checks and health_checks[0].timestamp < cutoff_time:
                        health_checks.popleft()
                
                await asyncio.sleep(60)  # Run cleanup every minute
                
            except Exception as e:
                logger.error(f"Error in service cleanup: {e}")
                await asyncio.sleep(10)
    
    async def _start_performance_tracking(self) -> None:
        """Start performance tracking background task."""
        logger.info("📊 Starting performance tracking")
        
        while True:
            try:
                # Calculate performance metrics for each service
                for service_id, service in self.services.items():
                    # Update creator affinity scores
                    if service.creator_affinity:
                        for creator_type in service.creator_affinity:
                            # Simple scoring based on response time and load
                            performance_score = 1.0 / (service.response_time_ms + 1.0)
                            load_score = 1.0 / (service.load_score + 1.0)
                            combined_score = (performance_score + load_score) / 2.0
                            
                            # Update affinity score with exponential moving average
                            current_score = self.creator_service_affinity[creator_type][service_id]
                            alpha = 0.1  # Smoothing factor
                            new_score = alpha * combined_score + (1 - alpha) * current_score
                            self.creator_service_affinity[creator_type][service_id] = new_score
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance tracking: {e}")
                await asyncio.sleep(30)
    
    def _initialize_load_balancing_state(self, service_id -> None: str) -> None:
        """Initialize load balancing state for a service."""
        service = self.services[service_id]
        service_name = service.service_name
        
        if service_name not in self.load_balancing_state:
            self.load_balancing_state[service_name] = {
                "round_robin_index": 0,
                "weighted_scores": {},
                "consistent_hash_ring": []
            }
    
    async def _notify_event_handlers(self, event_type -> None: str, service -> None: ServiceInstance) -> None:
        """Notify registered event handlers."""
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(service)
                else:
                    handler(service)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(self, event_type -> None: str, handler -> None: Callable) -> None:
        """Register event handler for service events."""
        self.event_handlers[event_type].append(handler)
        logger.info(f"📢 Event handler registered for: {event_type}")
    
    async def get_service_topology(self) -> Dict[str, Any]:
        """
        Get service topology and relationships.
        
        Returns:
            Service topology information
        """
        topology = {
            "total_services": len(self.services),
            "services_by_type": defaultdict(int),
            "services_by_status": defaultdict(int),
            "creator_affinity_mapping": {},
            "performance_summary": {},
            "load_balancing_state": {}
        }
        
        # Aggregate service information
        for service in self.services.values():
            topology["services_by_type"][service.service_type.value] += 1
            topology["services_by_status"][service.status.value] += 1
        
        # Creator affinity mapping
        for creator_type, service_scores in self.creator_service_affinity.items():
            if service_scores:
                best_service_id = max(service_scores, key=service_scores.get)
                best_service = self.services.get(best_service_id)
                if best_service:
                    topology["creator_affinity_mapping"][creator_type.value] = {
                        "preferred_service": best_service.service_name,
                        "service_id": best_service_id,
                        "affinity_score": service_scores[best_service_id]
                    }
        
        # Performance summary
        if self.services:
            response_times = [s.response_time_ms for s in self.services.values()]
            load_scores = [s.load_score for s in self.services.values()]
            
            topology["performance_summary"] = {
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "max_response_time_ms": max(response_times),
                "min_response_time_ms": min(response_times),
                "avg_load_score": sum(load_scores) / len(load_scores),
                "total_connections": sum(s.connection_count for s in self.services.values())
            }
        
        # Load balancing state
        topology["load_balancing_state"] = {
            "strategy": self.config.load_balancing_strategy.value,
            "circuit_breaker_enabled": self.config.enable_circuit_breaker,
            "services_with_open_circuit_breaker": len([
                cb for cb in self.circuit_breaker_state.values()
                if cb["state"] == "open"
            ])
        }
        
        return topology
    
    async def generate_service_discovery_report(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate comprehensive service discovery report.
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            Service discovery report
        """
        logger.info("📊 Generating service discovery report")
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Service availability analysis
        availability_stats = {}
        for service_id, health_checks in self.health_checks.items():
            recent_checks = [hc for hc in health_checks if hc.timestamp >= cutoff_time]
            if recent_checks:
                healthy_checks = [hc for hc in recent_checks if hc.status == ServiceStatus.HEALTHY]
                availability = len(healthy_checks) / len(recent_checks)
                avg_response_time = sum(hc.response_time_ms for hc in recent_checks) / len(recent_checks)
                
                availability_stats[service_id] = {
                    "availability_percentage": availability,
                    "total_checks": len(recent_checks),
                    "healthy_checks": len(healthy_checks),
                    "avg_response_time_ms": avg_response_time
                }
        
        # Load balancing effectiveness
        topology = await self.get_service_topology()
        
        # Circuit breaker statistics
        circuit_breaker_stats = {
            "services_with_circuit_breaker": len(self.circuit_breaker_state),
            "open_circuit_breakers": 0,
            "half_open_circuit_breakers": 0,
            "recent_failures": 0
        }
        
        for cb_state in self.circuit_breaker_state.values():
            if cb_state["state"] == "open":
                circuit_breaker_stats["open_circuit_breakers"] += 1
            elif cb_state["state"] == "half_open":
                circuit_breaker_stats["half_open_circuit_breakers"] += 1
            
            if cb_state["last_failure"] and cb_state["last_failure"] >= cutoff_time:
                circuit_breaker_stats["recent_failures"] += 1
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "time_window_hours": time_window_hours,
                "total_services": len(self.services)
            },
            "service_topology": topology,
            "availability_statistics": availability_stats,
            "circuit_breaker_statistics": circuit_breaker_stats,
            "performance_metrics": {
                "load_balancing_strategy": self.config.load_balancing_strategy.value,
                "avg_service_response_time": topology["performance_summary"].get("avg_response_time_ms", 0),
                "total_active_connections": topology["performance_summary"].get("total_connections", 0)
            },
            "creator_affinity_analysis": topology["creator_affinity_mapping"],
            "recommendations": await self._generate_service_recommendations(topology, availability_stats)
        }
        
        logger.info("✅ Service discovery report generated")
        return report
    
    async def _generate_service_recommendations(
        self,
        topology: Dict[str, Any],
        availability_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate service optimization recommendations."""
        recommendations = []
        
        # Check service availability
        low_availability_services = [
            service_id for service_id, stats in availability_stats.items()
            if stats["availability_percentage"] < 0.95
        ]
        
        if low_availability_services:
            recommendations.append(f"⚠️ {len(low_availability_services)} services have availability below 95%")
        
        # Check response time
        performance = topology.get("performance_summary", {})
        avg_response_time = performance.get("avg_response_time_ms", 0)
        
        if avg_response_time > 500:
            recommendations.append("🐌 Average response time is high - consider scaling or optimization")
        
        # Check load distribution
        if self.config.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            if len(self.services) > 10:
                recommendations.append("🔄 Consider switching to weighted load balancing for better performance")
        
        # Check circuit breaker effectiveness
        open_circuits = topology["load_balancing_state"]["services_with_open_circuit_breaker"]
        if open_circuits > 0:
            recommendations.append(f"🔴 {open_circuits} services have open circuit breakers - investigate issues")
        
        # Service type distribution
        services_by_type = topology["services_by_type"]
        if services_by_type.get("inference", 0) < 2:
            recommendations.append("🤖 Consider deploying additional inference service instances for redundancy")
        
        return recommendations

# Export main class
__all__ = ['ServiceDiscoveryEngine', 'ServiceStatus', 'ServiceType', 'LoadBalancingStrategy', 'CreatorType', 'ServiceInstance', 'ServiceDiscoveryConfig', 'HealthCheck', 'LoadBalancingDecision']

if __name__ == "__main__":
    # Test the service discovery engine
    async def test_service_discovery_engine() -> None:
        engine = ServiceDiscoveryEngine()
        
        print("🌐 Testing Service Discovery Engine:")
        print("-" * 50)
        
        # Register test services
        services = [
            ("ml-inference", ServiceType.INFERENCE, "localhost", 8001, [CreatorType.MUSICIAN]),
            ("ml-inference", ServiceType.INFERENCE, "localhost", 8002, [CreatorType.BLOGGER]),
            ("feature-store", ServiceType.FEATURE_STORE, "localhost", 8003, None),
            ("model-registry", ServiceType.MODEL_REGISTRY, "localhost", 8004, None),
        ]
        
        service_ids = []
        for name, stype, host, port, affinity in services:
            service_id = await engine.register_service(
                service_name=name,
                service_type=stype,
                host=host,
                port=port,
                creator_affinity=affinity
            )
            service_ids.append(service_id)
            print(f"✅ Registered: {name} on {host}:{port}")
        
        # Test service discovery
        print(f"\n🔍 Testing service discovery:")
        
        # Discover all inference services
        inference_services = await engine.discover_services(service_type=ServiceType.INFERENCE)
        print(f"  Found {len(inference_services)} inference services")
        
        # Discover services for musicians
        musician_services = await engine.discover_services(creator_type=CreatorType.MUSICIAN)
        print(f"  Found {len(musician_services)} services optimized for musicians")
        
        # Test load balancing
        print(f"\n⚖️ Testing load balancing:")
        
        for i in range(5):
            decision = await engine.get_service_for_request(
                service_name="ml-inference",
                creator_type=CreatorType.MUSICIAN
            )
            if decision:
                service = decision.selected_service
                print(f"  Request {i+1}: {service.host}:{service.port} (strategy: {decision.strategy_used.value})")
        
        # Test heartbeats
        print(f"\n💓 Testing heartbeats:")
        for service_id in service_ids[:2]:
            success = await engine.heartbeat(service_id)
            print(f"  Heartbeat for {service_id}: {'✅' if success else '❌'}")
        
        # Update service metrics
        print(f"\n📊 Updating service metrics:")
        await engine.update_service_metrics(
            service_ids[0],
            response_time_ms=150.5,
            connection_count=5,
            load_score=0.3
        )
        print(f"  Updated metrics for {service_ids[0]}")
        
        # Get service topology
        print(f"\n🗺️ Service topology:")
        topology = await engine.get_service_topology()
        print(f"  Total services: {topology['total_services']}")
        print(f"  Services by type: {dict(topology['services_by_type'])}")
        print(f"  Avg response time: {topology['performance_summary'].get('avg_response_time_ms', 0):.1f}ms")
        
        # Test creator affinity
        if topology['creator_affinity_mapping']:
            print(f"  Creator affinity mapping:")
            for creator, mapping in topology['creator_affinity_mapping'].items():
                print(f"    {creator}: {mapping['preferred_service']} (score: {mapping['affinity_score']:.3f})")
        
        # Generate report
        print(f"\n📈 Generating service discovery report...")
        report = await engine.generate_service_discovery_report(time_window_hours=1)
        
        print(f"  Report generated at: {report['report_metadata']['generated_at']}")
        print(f"  Availability stats: {len(report['availability_statistics'])} services analyzed")
        print(f"  Recommendations: {len(report['recommendations'])}")
        
        for rec in report['recommendations']:
            print(f"    - {rec}")
        
        # Test deregistration
        print(f"\n🗑️ Testing service deregistration:")
        success = await engine.deregister_service(service_ids[0])
        print(f"  Deregistered service: {'✅' if success else '❌'}")
        
        final_topology = await engine.get_service_topology()
        print(f"  Services remaining: {final_topology['total_services']}")
        
        print("\n✅ ServiceDiscoveryEngine test completed successfully!")
    
    # Run test
    asyncio.run(test_service_discovery_engine())