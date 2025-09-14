"""
🌐 GATEWAY ROUTING SERVICE - ENTERPRISE MICROSERVICE
Intelligent routing service for API gateway with dynamic routing capabilities.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import aiohttp
import yaml
import json

logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """Routing strategy types"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    HEALTH_BASED = "health_based"
    GEOGRAPHIC = "geographic"
    CANARY = "canary"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    id: str
    host: str
    port: int
    weight: int = 1
    health_check_url: str = "/health"
    max_connections: int = 1000
    response_timeout: int = 30
    health_status: bool = True
    current_connections: int = 0
    avg_response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
        
    @property
    def is_healthy(self) -> bool:
        return self.health_status and self.current_connections < self.max_connections

@dataclass
class RoutingRule:
    """Routing rule configuration"""
    id: str
    path_pattern: str
    method: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    service_name: str = ""
    strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    weight: int = 100
    priority: int = 0
    enabled: bool = True
    canary_percentage: int = 0
    rate_limit: Optional[Dict[str, int]] = None
    timeout: int = 30
    retry_attempts: int = 3
    circuit_breaker: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.rate_limit is None:
            self.rate_limit = {}

class GatewayRouting:
    """
    🌐 Gateway Routing Service
    
    Intelligent routing service for API gateway with support for multiple routing strategies,
    health-based routing, canary deployments, and real-time configuration updates.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Service registry
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.routing_rules: List[RoutingRule] = []
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        
        # Routing state
        self.round_robin_counters: Dict[str, int] = {}
        self.connection_counts: Dict[str, int] = {}
        self.response_times: Dict[str, List[float]] = {}
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Geographic routing
        self.geographic_mapping: Dict[str, str] = {}
        
        self.running = False
        
    async def initialize(self):
        """Initialize routing service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load initial configuration
            await self._load_configuration()
            
            # Start background tasks
            asyncio.create_task(self._health_check_task())
            asyncio.create_task(self._metrics_update_task())
            asyncio.create_task(self._configuration_watch_task())
            
            self.running = True
            logger.info("Gateway Routing service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway routing: {e}")
            raise
            
    async def _load_configuration(self):
        """Load routing configuration from Redis"""
        try:
            # Load services
            services_data = await self.redis.get("gateway:routing:services")
            if services_data:
                services_config = json.loads(services_data)
                for service_name, endpoints in services_config.items():
                    self.services[service_name] = [
                        ServiceEndpoint(**endpoint) for endpoint in endpoints
                    ]
                    
            # Load routing rules
            rules_data = await self.redis.get("gateway:routing:rules")
            if rules_data:
                rules_config = json.loads(rules_data)
                self.routing_rules = [RoutingRule(**rule) for rule in rules_config]
                self._compile_routing_patterns()
                
            # Load geographic mapping
            geo_data = await self.redis.get("gateway:routing:geographic")
            if geo_data:
                self.geographic_mapping = json.loads(geo_data)
                
        except Exception as e:
            logger.error(f"Failed to load routing configuration: {e}")
            
    def _compile_routing_patterns(self):
        """Compile regex patterns for routing rules"""
        self.compiled_patterns = {}
        for rule in self.routing_rules:
            if rule.enabled:
                try:
                    # Convert path pattern to regex
                    pattern = rule.path_pattern
                    # Replace path parameters like {id} with regex groups
                    pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', pattern)
                    # Escape special regex characters except for our replacements
                    pattern = pattern.replace('*', '.*')
                    
                    self.compiled_patterns[rule.id] = re.compile(f"^{pattern}$")
                except re.error as e:
                    logger.error(f"Invalid regex pattern for rule {rule.id}: {e}")
                    
    async def register_service(self, service_name: str, endpoints: List[ServiceEndpoint]):
        """Register a service with its endpoints"""
        self.services[service_name] = endpoints
        
        # Initialize routing state
        self.round_robin_counters[service_name] = 0
        self.connection_counts[service_name] = 0
        self.response_times[service_name] = []
        
        # Save to Redis
        services_config = {
            name: [asdict(ep) for ep in eps] 
            for name, eps in self.services.items()
        }
        await self.redis.set(
            "gateway:routing:services", 
            json.dumps(services_config, default=str)
        )
        
        logger.info(f"Registered service {service_name} with {len(endpoints)} endpoints")
        
    async def add_routing_rule(self, rule: RoutingRule):
        """Add a new routing rule"""
        # Remove existing rule with same ID
        self.routing_rules = [r for r in self.routing_rules if r.id != rule.id]
        
        # Add new rule
        self.routing_rules.append(rule)
        
        # Sort by priority (higher priority first)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Recompile patterns
        self._compile_routing_patterns()
        
        # Save to Redis
        rules_config = [asdict(rule) for rule in self.routing_rules]
        await self.redis.set(
            "gateway:routing:rules", 
            json.dumps(rules_config, default=str)
        )
        
        logger.info(f"Added routing rule {rule.id}")
        
    async def route_request(self, path: str, method: str, headers: Dict[str, str],
                          client_ip: str = "") -> Optional[ServiceEndpoint]:
        """Route a request to appropriate service endpoint"""
        
        # Find matching routing rule
        matching_rule = await self._find_matching_rule(path, method, headers)
        if not matching_rule:
            logger.warning(f"No routing rule found for {method} {path}")
            return None
            
        # Get available endpoints for the service
        endpoints = self.services.get(matching_rule.service_name, [])
        if not endpoints:
            logger.error(f"No endpoints available for service {matching_rule.service_name}")
            return None
            
        # Filter healthy endpoints
        healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
        if not healthy_endpoints:
            logger.error(f"No healthy endpoints for service {matching_rule.service_name}")
            return None
            
        # Handle canary deployment
        if matching_rule.canary_percentage > 0:
            canary_endpoints = [ep for ep in healthy_endpoints 
                             if ep.metadata.get('canary', False)]
            production_endpoints = [ep for ep in healthy_endpoints 
                                  if not ep.metadata.get('canary', False)]
            
            # Determine if request should go to canary
            hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
            if hash_value % 100 < matching_rule.canary_percentage and canary_endpoints:
                healthy_endpoints = canary_endpoints
            else:
                healthy_endpoints = production_endpoints or healthy_endpoints
                
        # Select endpoint based on strategy
        endpoint = await self._select_endpoint(
            healthy_endpoints, matching_rule.strategy, 
            matching_rule.service_name, client_ip
        )
        
        if endpoint:
            # Update connection count
            endpoint.current_connections += 1
            self.connection_counts[matching_rule.service_name] += 1
            
        return endpoint
        
    async def _find_matching_rule(self, path: str, method: str, 
                                headers: Dict[str, str]) -> Optional[RoutingRule]:
        """Find the first matching routing rule"""
        for rule in self.routing_rules:
            if not rule.enabled:
                continue
                
            # Check method match
            if rule.method and rule.method.upper() != method.upper():
                continue
                
            # Check path pattern match
            pattern = self.compiled_patterns.get(rule.id)
            if pattern and not pattern.match(path):
                continue
                
            # Check header matches
            if rule.headers:
                header_match = True
                for header_name, header_value in rule.headers.items():
                    if headers.get(header_name.lower()) != header_value:
                        header_match = False
                        break
                if not header_match:
                    continue
                    
            return rule
            
        return None
        
    async def _select_endpoint(self, endpoints: List[ServiceEndpoint], 
                             strategy: RoutingStrategy, service_name: str,
                             client_ip: str = "") -> Optional[ServiceEndpoint]:
        """Select endpoint based on routing strategy"""
        
        if not endpoints:
            return None
            
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(endpoints, service_name)
            
        elif strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(endpoints, service_name)
            
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return min(endpoints, key=lambda ep: ep.current_connections)
            
        elif strategy == RoutingStrategy.LEAST_RESPONSE_TIME:
            return min(endpoints, key=lambda ep: ep.avg_response_time)
            
        elif strategy == RoutingStrategy.IP_HASH:
            return self._ip_hash_selection(endpoints, client_ip)
            
        elif strategy == RoutingStrategy.HEALTH_BASED:
            return self._health_based_selection(endpoints)
            
        elif strategy == RoutingStrategy.GEOGRAPHIC:
            return self._geographic_selection(endpoints, client_ip)
            
        else:
            # Default to round robin
            return self._round_robin_selection(endpoints, service_name)
            
    def _round_robin_selection(self, endpoints: List[ServiceEndpoint], 
                             service_name: str) -> ServiceEndpoint:
        """Round robin endpoint selection"""
        counter = self.round_robin_counters.get(service_name, 0)
        selected = endpoints[counter % len(endpoints)]
        self.round_robin_counters[service_name] = counter + 1
        return selected
        
    def _weighted_round_robin_selection(self, endpoints: List[ServiceEndpoint], 
                                      service_name: str) -> ServiceEndpoint:
        """Weighted round robin endpoint selection"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return self._round_robin_selection(endpoints, service_name)
            
        counter = self.round_robin_counters.get(service_name, 0)
        
        # Calculate cumulative weights
        cumulative_weight = 0
        position = counter % total_weight
        
        for endpoint in endpoints:
            cumulative_weight += endpoint.weight
            if position < cumulative_weight:
                self.round_robin_counters[service_name] = counter + 1
                return endpoint
                
        # Fallback
        return endpoints[0]
        
    def _ip_hash_selection(self, endpoints: List[ServiceEndpoint], 
                         client_ip: str) -> ServiceEndpoint:
        """IP hash-based endpoint selection"""
        if not client_ip:
            return endpoints[0]
            
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return endpoints[hash_value % len(endpoints)]
        
    def _health_based_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Health-based endpoint selection (best health score)"""
        def health_score(ep: ServiceEndpoint) -> float:
            score = 0.0
            
            # Response time factor (lower is better)
            if ep.avg_response_time > 0:
                score += 1.0 / ep.avg_response_time
            else:
                score += 1.0
                
            # Connection load factor (lower is better)
            load_factor = ep.current_connections / ep.max_connections
            score += 1.0 - load_factor
            
            # Weight factor
            score *= ep.weight
            
            return score
            
        return max(endpoints, key=health_score)
        
    def _geographic_selection(self, endpoints: List[ServiceEndpoint], 
                            client_ip: str) -> ServiceEndpoint:
        """Geographic-based endpoint selection"""
        # This is a simplified implementation
        # In practice, you'd use a GeoIP service
        
        client_region = self.geographic_mapping.get(client_ip, "default")
        
        # Find endpoints in the same region
        regional_endpoints = [
            ep for ep in endpoints 
            if ep.metadata.get("region") == client_region
        ]
        
        if regional_endpoints:
            return self._round_robin_selection(regional_endpoints, "geographic")
        else:
            # Fallback to any available endpoint
            return self._round_robin_selection(endpoints, "geographic")
            
    async def record_response(self, endpoint: ServiceEndpoint, response_time: float, 
                            success: bool):
        """Record response metrics for an endpoint"""
        try:
            # Update connection count
            endpoint.current_connections = max(0, endpoint.current_connections - 1)
            
            # Update response time
            if endpoint.id not in self.response_times:
                self.response_times[endpoint.id] = []
                
            self.response_times[endpoint.id].append(response_time)
            
            # Keep only last 100 response times
            if len(self.response_times[endpoint.id]) > 100:
                self.response_times[endpoint.id] = self.response_times[endpoint.id][-100:]
                
            # Update average response time
            endpoint.avg_response_time = sum(self.response_times[endpoint.id]) / \
                                       len(self.response_times[endpoint.id])
                                       
            # Update circuit breaker state
            await self._update_circuit_breaker(endpoint.id, success, response_time)
            
        except Exception as e:
            logger.error(f"Failed to record response for endpoint {endpoint.id}: {e}")
            
    async def _update_circuit_breaker(self, endpoint_id: str, success: bool, 
                                    response_time: float):
        """Update circuit breaker state"""
        if endpoint_id not in self.circuit_breakers:
            self.circuit_breakers[endpoint_id] = {
                'state': 'closed',  # closed, open, half_open
                'failure_count': 0,
                'last_failure_time': None,
                'success_count': 0,
                'timeout_count': 0
            }
            
        cb = self.circuit_breakers[endpoint_id]
        
        if success and response_time < 30.0:  # Success
            cb['success_count'] += 1
            cb['failure_count'] = 0
            
            # Close circuit if it was half-open and we have enough successes
            if cb['state'] == 'half_open' and cb['success_count'] >= 3:
                cb['state'] = 'closed'
                cb['success_count'] = 0
                
        else:  # Failure
            cb['failure_count'] += 1
            cb['last_failure_time'] = datetime.utcnow()
            cb['success_count'] = 0
            
            if response_time >= 30.0:
                cb['timeout_count'] += 1
                
            # Open circuit if too many failures
            if cb['failure_count'] >= 5:
                cb['state'] = 'open'
                
        # Auto-transition from open to half-open after timeout
        if (cb['state'] == 'open' and cb['last_failure_time'] and 
            (datetime.utcnow() - cb['last_failure_time']).seconds > 60):
            cb['state'] = 'half_open'
            cb['failure_count'] = 0
            cb['success_count'] = 0
            
    async def is_circuit_open(self, endpoint_id: str) -> bool:
        """Check if circuit breaker is open for endpoint"""
        cb = self.circuit_breakers.get(endpoint_id, {})
        return cb.get('state') == 'open'
        
    async def _health_check_task(self):
        """Background task for health checking endpoints"""
        while self.running:
            try:
                for service_name, endpoints in self.services.items():
                    for endpoint in endpoints:
                        await self._check_endpoint_health(endpoint)
                        
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health check task: {e}")
                await asyncio.sleep(10)
                
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """Check health of a single endpoint"""
        try:
            health_url = f"{endpoint.url}{endpoint.health_check_url}"
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        endpoint.health_status = True
                        endpoint.avg_response_time = response_time
                    else:
                        endpoint.health_status = False
                        
        except Exception as e:
            logger.warning(f"Health check failed for endpoint {endpoint.id}: {e}")
            endpoint.health_status = False
            
        endpoint.last_health_check = datetime.utcnow()
        
    async def _metrics_update_task(self):
        """Background task for updating metrics"""
        while self.running:
            try:
                # Update routing metrics in Redis
                metrics = await self.get_routing_metrics()
                await self.redis.setex(
                    "gateway:routing:metrics", 
                    60, 
                    json.dumps(metrics, default=str)
                )
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics update task: {e}")
                await asyncio.sleep(30)
                
    async def _configuration_watch_task(self):
        """Background task for watching configuration changes"""
        while self.running:
            try:
                # Check for configuration updates
                config_version = await self.redis.get("gateway:routing:version")
                if config_version:
                    stored_version = getattr(self, '_config_version', None)
                    if config_version != stored_version:
                        await self._load_configuration()
                        self._config_version = config_version
                        logger.info("Routing configuration updated")
                        
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in configuration watch task: {e}")
                await asyncio.sleep(10)
                
    async def get_routing_metrics(self) -> Dict[str, Any]:
        """Get routing metrics summary"""
        metrics = {
            'total_services': len(self.services),
            'total_endpoints': sum(len(endpoints) for endpoints in self.services.values()),
            'healthy_endpoints': sum(
                len([ep for ep in endpoints if ep.is_healthy]) 
                for endpoints in self.services.values()
            ),
            'total_rules': len(self.routing_rules),
            'active_rules': len([r for r in self.routing_rules if r.enabled]),
            'circuit_breakers_open': len([
                cb for cb in self.circuit_breakers.values() 
                if cb.get('state') == 'open'
            ]),
            'services': {}
        }
        
        for service_name, endpoints in self.services.items():
            service_metrics = {
                'total_endpoints': len(endpoints),
                'healthy_endpoints': len([ep for ep in endpoints if ep.is_healthy]),
                'total_connections': sum(ep.current_connections for ep in endpoints),
                'avg_response_time': sum(ep.avg_response_time for ep in endpoints) / len(endpoints) if endpoints else 0,
                'endpoints': [
                    {
                        'id': ep.id,
                        'url': ep.url,
                        'healthy': ep.is_healthy,
                        'connections': ep.current_connections,
                        'response_time': ep.avg_response_time,
                        'weight': ep.weight
                    }
                    for ep in endpoints
                ]
            }
            metrics['services'][service_name] = service_metrics
            
        return metrics
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for routing service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        total_endpoints = sum(len(endpoints) for endpoints in self.services.values())
        healthy_endpoints = sum(
            len([ep for ep in endpoints if ep.is_healthy]) 
            for endpoints in self.services.values()
        )
        
        health_percentage = (healthy_endpoints / total_endpoints * 100) if total_endpoints > 0 else 100
        
        return {
            'service': 'gateway_routing',
            'status': 'healthy' if redis_status == "healthy" and health_percentage >= 80 else 'unhealthy',
            'redis': redis_status,
            'total_services': len(self.services),
            'total_endpoints': total_endpoints,
            'healthy_endpoints': healthy_endpoints,
            'health_percentage': health_percentage,
            'active_rules': len([r for r in self.routing_rules if r.enabled])
        }
        
    async def shutdown(self):
        """Shutdown routing service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Gateway Routing service shut down")

# Example usage
async def create_gateway_routing():
    """Factory function to create gateway routing service"""
    routing = GatewayRouting()
    await routing.initialize()
    
    return routing

if __name__ == "__main__":
    async def main():
        routing = await create_gateway_routing()
        
        # Example service registration
        endpoints = [
            ServiceEndpoint("ep1", "localhost", 8001, weight=2),
            ServiceEndpoint("ep2", "localhost", 8002, weight=1),
            ServiceEndpoint("ep3", "localhost", 8003, weight=1, 
                          metadata={"region": "us-east-1"})
        ]
        
        await routing.register_service("creator-service", endpoints)
        
        # Example routing rule
        rule = RoutingRule(
            id="creators_rule",
            path_pattern="/api/v1/creators.*",
            method="GET",
            service_name="creator-service",
            strategy=RoutingStrategy.WEIGHTED_ROUND_ROBIN
        )
        
        await routing.add_routing_rule(rule)
        
        # Route a request
        endpoint = await routing.route_request(
            "/api/v1/creators/123", "GET", {}, "192.168.1.100"
        )
        
        if endpoint:
            print(f"Routed to: {endpoint.url}")
            
            # Record response
            await routing.record_response(endpoint, 0.15, True)
            
        # Get metrics
        metrics = await routing.get_routing_metrics()
        print("Routing Metrics:", metrics)
        
        await routing.shutdown()
        
    asyncio.run(main())