"""
🔥 LOAD BALANCER - INTELLIGENT TRAFFIC DISTRIBUTION
Ultra-fast load balancing with Creator Economy optimization
Performance Target: < 5ms load balancing decisions

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - TOUS DROITS RÉSERVÉS
Commercial use forbidden without written authorization
Reverse engineering strictly prohibited
"""

import asyncio
import time
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

import logging


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms for different scenarios."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    GEOGRAPHIC = "geographic"
    CREATOR_AFFINITY = "creator_affinity"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    endpoint_id: str = field(default_factory=lambda: str(uuid4()))
    host: str = "localhost"
    port: int = 8080
    weight: float = 1.0
    health_status: bool = True
    current_connections: int = 0
    average_response_time: float = 100.0  # ms
    
    # Creator Economy specific
    supported_content_types: Set[str] = field(default_factory=set)
    creator_capacity: int = 100
    current_creator_load: int = 0
    geographic_region: str = "us-east-1"


class LoadBalancer:
    """
    🔥 ENTERPRISE LOAD BALANCER - CREATOR ECONOMY OPTIMIZED
    Ultra-fast load balancing with <5ms decisions
    """
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS):
        self.algorithm = algorithm
        self.balancing_algorithms = BalancingAlgorithms()
        self.health_checker = HealthChecker()
        self.traffic_distributor = TrafficDistributor()
        
        # Service endpoints
        self.endpoints = {}
        self.endpoint_stats = defaultdict(dict)
        
        # Performance metrics
        self.balancing_metrics = {
            'requests_balanced': 0,
            'total_balancing_time': 0.0,
            'algorithm_switches': 0,
            'health_check_failures': 0
        }
        
        # Creator Economy optimization
        self.creator_affinity_map = {}
        self.content_type_preferences = {}
        
        # Round robin state
        self._round_robin_index = 0
    
    async def balance_workflow_load(
        self,
        request_context: Dict[str, Any]
    ) -> Optional[ServiceEndpoint]:
        """Balance workflow load with Creator Economy optimization."""
        start_time = time.perf_counter()
        
        # Get healthy endpoints
        healthy_endpoints = await self._get_healthy_endpoints()
        if not healthy_endpoints:
            return None
        
        # Apply Creator Economy filtering
        filtered_endpoints = await self._filter_by_creator_requirements(
            healthy_endpoints, request_context
        )
        
        if not filtered_endpoints:
            filtered_endpoints = healthy_endpoints  # Fallback to all healthy
        
        # Select endpoint using configured algorithm
        selected_endpoint = await self.balancing_algorithms.select_endpoint(
            filtered_endpoints, self.algorithm, request_context
        )
        
        if selected_endpoint:
            # Update endpoint state
            selected_endpoint.current_connections += 1
            if 'creator_id' in request_context:
                selected_endpoint.current_creator_load += 1
        
        # Update metrics
        balancing_time = time.perf_counter() - start_time
        self.balancing_metrics['requests_balanced'] += 1
        self.balancing_metrics['total_balancing_time'] += balancing_time
        
        if balancing_time > 0.005:  # 5ms threshold
            logging.warning(f"Load balancing exceeded 5ms: {balancing_time*1000:.1f}ms")
        
        return selected_endpoint
    
    async def _get_healthy_endpoints(self) -> List[ServiceEndpoint]:
        """Get list of healthy service endpoints."""
        healthy = []
        for endpoint in self.endpoints.values():
            if await self.health_checker.is_healthy(endpoint):
                healthy.append(endpoint)
        return healthy
    
    async def _filter_by_creator_requirements(
        self,
        endpoints: List[ServiceEndpoint],
        request_context: Dict[str, Any]
    ) -> List[ServiceEndpoint]:
        """Filter endpoints based on Creator Economy requirements."""
        content_type = request_context.get('content_type')
        creator_id = request_context.get('creator_id')
        geographic_preference = request_context.get('region')
        
        filtered = []
        
        for endpoint in endpoints:
            # Content type filtering
            if (content_type and 
                endpoint.supported_content_types and 
                content_type not in endpoint.supported_content_types):
                continue
            
            # Creator capacity check
            if endpoint.current_creator_load >= endpoint.creator_capacity:
                continue
            
            # Geographic preference
            if (geographic_preference and 
                endpoint.geographic_region != geographic_preference):
                continue
            
            filtered.append(endpoint)
        
        return filtered
    
    async def register_endpoint(self, endpoint: ServiceEndpoint):
        """Register new service endpoint."""
        self.endpoints[endpoint.endpoint_id] = endpoint
        await self.health_checker.start_monitoring(endpoint)
        logging.info(f"Registered endpoint {endpoint.host}:{endpoint.port}")
    
    async def unregister_endpoint(self, endpoint_id: str):
        """Unregister service endpoint."""
        if endpoint_id in self.endpoints:
            endpoint = self.endpoints[endpoint_id]
            await self.health_checker.stop_monitoring(endpoint)
            del self.endpoints[endpoint_id]
            logging.info(f"Unregistered endpoint {endpoint_id}")
    
    def get_balancing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive load balancing metrics."""
        total_requests = self.balancing_metrics['requests_balanced']
        total_time = self.balancing_metrics['total_balancing_time']
        
        return {
            **self.balancing_metrics,
            'average_balancing_time_ms': (total_time / max(1, total_requests)) * 1000,
            'active_endpoints': len([e for e in self.endpoints.values() if e.health_status]),
            'total_endpoints': len(self.endpoints),
            'current_algorithm': self.algorithm.value
        }


class BalancingAlgorithms:
    """Implementation of various load balancing algorithms."""
    
    def __init__(self):
        self.round_robin_counters = defaultdict(int)
    
    async def select_endpoint(
        self,
        endpoints: List[ServiceEndpoint],
        algorithm: LoadBalancingAlgorithm,
        context: Dict[str, Any]
    ) -> Optional[ServiceEndpoint]:
        """Select endpoint using specified algorithm."""
        
        if not endpoints:
            return None
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return await self._round_robin(endpoints)
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin(endpoints)
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return await self._least_connections(endpoints)
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return await self._least_response_time(endpoints)
        elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            return await self._geographic_routing(endpoints, context)
        elif algorithm == LoadBalancingAlgorithm.CREATOR_AFFINITY:
            return await self._creator_affinity(endpoints, context)
        
        # Default to round robin
        return await self._round_robin(endpoints)
    
    async def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Simple round robin selection."""
        if not hasattr(self, '_rr_index'):
            self._rr_index = 0
        
        endpoint = endpoints[self._rr_index % len(endpoints)]
        self._rr_index += 1
        return endpoint
    
    async def _weighted_round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted round robin based on endpoint weights."""
        total_weight = sum(e.weight for e in endpoints)
        random_weight = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for endpoint in endpoints:
            cumulative_weight += endpoint.weight
            if random_weight <= cumulative_weight:
                return endpoint
        
        return endpoints[-1]  # Fallback
    
    async def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with least active connections."""
        return min(endpoints, key=lambda e: e.current_connections)
    
    async def _least_response_time(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with lowest average response time."""
        return min(endpoints, key=lambda e: e.average_response_time)
    
    async def _geographic_routing(
        self, 
        endpoints: List[ServiceEndpoint], 
        context: Dict[str, Any]
    ) -> ServiceEndpoint:
        """Route based on geographic proximity."""
        preferred_region = context.get('region')
        
        if preferred_region:
            # Prefer same region endpoints
            same_region = [e for e in endpoints if e.geographic_region == preferred_region]
            if same_region:
                return await self._least_connections(same_region)
        
        # Fallback to least connections
        return await self._least_connections(endpoints)
    
    async def _creator_affinity(
        self, 
        endpoints: List[ServiceEndpoint], 
        context: Dict[str, Any]
    ) -> ServiceEndpoint:
        """Route based on creator affinity and content type."""
        creator_id = context.get('creator_id')
        content_type = context.get('content_type')
        
        # Prefer endpoints that support the content type
        if content_type:
            content_optimized = [
                e for e in endpoints 
                if content_type in e.supported_content_types
            ]
            if content_optimized:
                return await self._least_connections(content_optimized)
        
        # Fallback to least connections
        return await self._least_connections(endpoints)


class HealthChecker:
    """Monitor service endpoint health."""
    
    def __init__(self):
        self.monitoring_tasks = {}
        self.health_check_interval = 30  # seconds
    
    async def is_healthy(self, endpoint: ServiceEndpoint) -> bool:
        """Check if endpoint is healthy."""
        return endpoint.health_status
    
    async def start_monitoring(self, endpoint: ServiceEndpoint):
        """Start health monitoring for endpoint."""
        if endpoint.endpoint_id not in self.monitoring_tasks:
            task = asyncio.create_task(self._monitor_endpoint(endpoint))
            self.monitoring_tasks[endpoint.endpoint_id] = task
    
    async def stop_monitoring(self, endpoint: ServiceEndpoint):
        """Stop health monitoring for endpoint."""
        if endpoint.endpoint_id in self.monitoring_tasks:
            task = self.monitoring_tasks[endpoint.endpoint_id]
            task.cancel()
            del self.monitoring_tasks[endpoint.endpoint_id]
    
    async def _monitor_endpoint(self, endpoint: ServiceEndpoint):
        """Background health monitoring task."""
        while True:
            try:
                # Simplified health check (would be HTTP/TCP check in production)
                health_check_result = await self._perform_health_check(endpoint)
                endpoint.health_status = health_check_result
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Health check failed for {endpoint.host}:{endpoint.port}: {e}")
                endpoint.health_status = False
                await asyncio.sleep(5)  # Shorter interval on failure
    
    async def _perform_health_check(self, endpoint: ServiceEndpoint) -> bool:
        """Perform actual health check (simplified)."""
        # In production, this would make HTTP request or TCP connection
        # For now, simulate health check
        return True  # Always healthy for demo


class TrafficDistributor:
    """Distribute traffic across service endpoints."""
    
    def __init__(self):
        self.distribution_stats = defaultdict(int)
    
    async def distribute_request(
        self, 
        endpoint: ServiceEndpoint,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distribute request to selected endpoint."""
        self.distribution_stats[endpoint.endpoint_id] += 1
        
        # Simulate request forwarding
        response = {
            'endpoint_id': endpoint.endpoint_id,
            'host': endpoint.host,
            'port': endpoint.port,
            'status': 'success',
            'response_time': endpoint.average_response_time
        }
        
        return response
    
    def get_distribution_stats(self) -> Dict[str, int]:
        """Get traffic distribution statistics."""
        return dict(self.distribution_stats)


# Enterprise factory functions
async def create_enterprise_load_balancer(
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS
) -> LoadBalancer:
    """Factory function for enterprise load balancer."""
    return LoadBalancer(algorithm)