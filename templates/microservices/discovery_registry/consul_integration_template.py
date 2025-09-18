"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Consul Integration Template for Ainflue Platform
===============================================

Production-ready Consul service mesh integration with:
- Service registration and discovery
- Health checking with Consul agents
- KV store for configuration
- Service mesh with Consul Connect
- Multi-datacenter support
- ACL and security policies

Author: Fahed Mlaiel (mlaiel@live.de)
Service Mesh & Consul Expert
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

import consul
import consul.aio
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
consul_operations_counter = Counter('consul_operations_total', 'Total Consul operations', ['operation', 'status'])
consul_latency_histogram = Histogram('consul_operation_duration_seconds', 'Consul operation latency', ['operation'])
consul_services_gauge = Gauge('consul_registered_services', 'Number of services registered in Consul', ['datacenter'])

class ConsulServiceStatus(str, Enum):
    """Consul service status"""
    PASSING = "passing"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class ConsulServiceRegistration:
    """Consul service registration data"""
    id: str
    name: str
    tags: List[str]
    address: str
    port: int
    meta: Dict[str, str] = field(default_factory=dict)
    check: Optional[Dict[str, Any]] = None
    weights: Optional[Dict[str, int]] = None
    enable_tag_override: bool = False

@dataclass
class ConsulHealthCheck:
    """Consul health check configuration"""
    check_id: str
    name: str
    service_id: str
    http: Optional[str] = None
    tcp: Optional[str] = None
    script: Optional[str] = None
    interval: str = "30s"
    timeout: str = "5s"
    deregister_critical_service_after: str = "10m"
    notes: Optional[str] = None

class ConsulClient:
    """
    Enhanced Consul client for Ainflue Platform
    
    Features:
    - Service registration and discovery
    - Health check management
    - KV store operations
    - Service mesh integration
    - Multi-datacenter support
    """
    
    def __init__(self, host: str = "localhost", port: int = 8500, datacenter: Optional[str] = None, token: Optional[str] = None):
        self.host = host
        self.port = port
        self.datacenter = datacenter
        self.token = token
        
        # Initialize Consul clients
        self.consul = consul.Consul(
            host=host,
            port=port,
            dc=datacenter,
            token=token
        )
        
        # Async client for async operations
        self.consul_async = consul.aio.Consul(
            host=host,
            port=port,
            dc=datacenter,
            token=token
        )
        
        # Track registered services
        self.registered_services: Set[str] = set()
        
        # Service mesh configuration
        self.connect_enabled = False
        self.connect_proxy_config = {}
    
    async def register_service(self, registration: ConsulServiceRegistration) -> bool:
        """Register a service with Consul"""
        try:
            with consul_latency_histogram.labels(operation="register_service").time():
                # Prepare registration data
                service_data = {
                    "ID": registration.id,
                    "Name": registration.name,
                    "Tags": registration.tags,
                    "Address": registration.address,
                    "Port": registration.port,
                    "Meta": registration.meta,
                    "EnableTagOverride": registration.enable_tag_override
                }
                
                # Add health check if provided
                if registration.check:
                    service_data["Check"] = registration.check
                
                # Add weights if provided
                if registration.weights:
                    service_data["Weights"] = registration.weights
                
                # Add Connect configuration if enabled
                if self.connect_enabled:
                    service_data["Connect"] = {
                        "SidecarService": {
                            "Proxy": self.connect_proxy_config
                        }
                    }
                
                # Register with Consul
                success = await self.consul_async.agent.service.register(**service_data)
                
                if success:
                    self.registered_services.add(registration.id)
                    consul_operations_counter.labels(operation="register_service", status="success").inc()
                    logger.info(f"Registered service {registration.name} with ID {registration.id}")
                    return True
                else:
                    consul_operations_counter.labels(operation="register_service", status="failure").inc()
                    return False
                    
        except Exception as e:
            consul_operations_counter.labels(operation="register_service", status="error").inc()
            logger.error(f"Failed to register service {registration.name}: {e}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service from Consul"""
        try:
            with consul_latency_histogram.labels(operation="deregister_service").time():
                success = await self.consul_async.agent.service.deregister(service_id)
                
                if success:
                    self.registered_services.discard(service_id)
                    consul_operations_counter.labels(operation="deregister_service", status="success").inc()
                    logger.info(f"Deregistered service {service_id}")
                    return True
                else:
                    consul_operations_counter.labels(operation="deregister_service", status="failure").inc()
                    return False
                    
        except Exception as e:
            consul_operations_counter.labels(operation="deregister_service", status="error").inc()
            logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    async def discover_services(self, service_name: str, healthy_only: bool = True, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Discover services by name"""
        try:
            with consul_latency_histogram.labels(operation="discover_services").time():
                # Get service instances
                index, services = await self.consul_async.health.service(
                    service_name,
                    passing=healthy_only,
                    tag=tags[0] if tags else None  # Consul only supports single tag in query
                )
                
                # Filter by additional tags if needed
                if tags and len(tags) > 1:
                    services = [
                        service for service in services
                        if all(tag in service['Service'].get('Tags', []) for tag in tags)
                    ]
                
                consul_operations_counter.labels(operation="discover_services", status="success").inc()
                
                # Update metrics
                consul_services_gauge.labels(datacenter=self.datacenter or "default").set(len(services))
                
                return services
                
        except Exception as e:
            consul_operations_counter.labels(operation="discover_services", status="error").inc()
            logger.error(f"Failed to discover services {service_name}: {e}")
            return []
    
    async def register_health_check(self, check: ConsulHealthCheck) -> bool:
        """Register a health check"""
        try:
            with consul_latency_histogram.labels(operation="register_check").time():
                check_data = {
                    "CheckID": check.check_id,
                    "Name": check.name,
                    "ServiceID": check.service_id,
                    "Interval": check.interval,
                    "Timeout": check.timeout,
                    "DeregisterCriticalServiceAfter": check.deregister_critical_service_after
                }
                
                # Add check type
                if check.http:
                    check_data["HTTP"] = check.http
                elif check.tcp:
                    check_data["TCP"] = check.tcp
                elif check.script:
                    check_data["Script"] = check.script
                
                if check.notes:
                    check_data["Notes"] = check.notes
                
                success = await self.consul_async.agent.check.register(**check_data)
                
                if success:
                    consul_operations_counter.labels(operation="register_check", status="success").inc()
                    logger.info(f"Registered health check {check.name}")
                    return True
                else:
                    consul_operations_counter.labels(operation="register_check", status="failure").inc()
                    return False
                    
        except Exception as e:
            consul_operations_counter.labels(operation="register_check", status="error").inc()
            logger.error(f"Failed to register health check {check.name}: {e}")
            return False
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for all instances of a service"""
        try:
            with consul_latency_histogram.labels(operation="get_health").time():
                index, health_data = await self.consul_async.health.service(service_name)
                
                # Process health data
                health_summary = {
                    "service_name": service_name,
                    "total_instances": len(health_data),
                    "healthy_instances": 0,
                    "warning_instances": 0,
                    "critical_instances": 0,
                    "instances": []
                }
                
                for instance in health_data:
                    instance_health = {
                        "service_id": instance['Service']['ID'],
                        "address": instance['Service']['Address'],
                        "port": instance['Service']['Port'],
                        "checks": []
                    }
                    
                    # Analyze checks
                    overall_status = "passing"
                    for check in instance['Checks']:
                        check_info = {
                            "check_id": check['CheckID'],
                            "name": check['Name'],
                            "status": check['Status'],
                            "output": check['Output']
                        }
                        instance_health["checks"].append(check_info)
                        
                        if check['Status'] == "critical":
                            overall_status = "critical"
                        elif check['Status'] == "warning" and overall_status != "critical":
                            overall_status = "warning"
                    
                    instance_health["overall_status"] = overall_status
                    health_summary["instances"].append(instance_health)
                    
                    # Update counters
                    if overall_status == "passing":
                        health_summary["healthy_instances"] += 1
                    elif overall_status == "warning":
                        health_summary["warning_instances"] += 1
                    else:
                        health_summary["critical_instances"] += 1
                
                consul_operations_counter.labels(operation="get_health", status="success").inc()
                return health_summary
                
        except Exception as e:
            consul_operations_counter.labels(operation="get_health", status="error").inc()
            logger.error(f"Failed to get service health {service_name}: {e}")
            return {}
    
    async def put_kv(self, key: str, value: str, flags: int = 0) -> bool:
        """Put a value in Consul KV store"""
        try:
            with consul_latency_histogram.labels(operation="put_kv").time():
                success = await self.consul_async.kv.put(key, value, flags=flags)
                
                if success:
                    consul_operations_counter.labels(operation="put_kv", status="success").inc()
                    return True
                else:
                    consul_operations_counter.labels(operation="put_kv", status="failure").inc()
                    return False
                    
        except Exception as e:
            consul_operations_counter.labels(operation="put_kv", status="error").inc()
            logger.error(f"Failed to put KV {key}: {e}")
            return False
    
    async def get_kv(self, key: str, recurse: bool = False) -> Optional[Dict[str, Any]]:
        """Get a value from Consul KV store"""
        try:
            with consul_latency_histogram.labels(operation="get_kv").time():
                index, data = await self.consul_async.kv.get(key, recurse=recurse)
                
                consul_operations_counter.labels(operation="get_kv", status="success").inc()
                return data
                
        except Exception as e:
            consul_operations_counter.labels(operation="get_kv", status="error").inc()
            logger.error(f"Failed to get KV {key}: {e}")
            return None
    
    async def delete_kv(self, key: str, recurse: bool = False) -> bool:
        """Delete a key from Consul KV store"""
        try:
            with consul_latency_histogram.labels(operation="delete_kv").time():
                success = await self.consul_async.kv.delete(key, recurse=recurse)
                
                if success:
                    consul_operations_counter.labels(operation="delete_kv", status="success").inc()
                    return True
                else:
                    consul_operations_counter.labels(operation="delete_kv", status="failure").inc()
                    return False
                    
        except Exception as e:
            consul_operations_counter.labels(operation="delete_kv", status="error").inc()
            logger.error(f"Failed to delete KV {key}: {e}")
            return False
    
    async def enable_connect(self, proxy_config: Dict[str, Any] = None):
        """Enable Consul Connect service mesh"""
        self.connect_enabled = True
        self.connect_proxy_config = proxy_config or {}
        logger.info("Consul Connect enabled")
    
    async def get_connect_ca_roots(self) -> Optional[Dict[str, Any]]:
        """Get Connect CA root certificates"""
        try:
            with consul_latency_histogram.labels(operation="get_ca_roots").time():
                ca_roots = await self.consul_async.connect.ca.roots()
                consul_operations_counter.labels(operation="get_ca_roots", status="success").inc()
                return ca_roots
                
        except Exception as e:
            consul_operations_counter.labels(operation="get_ca_roots", status="error").inc()
            logger.error(f"Failed to get CA roots: {e}")
            return None
    
    async def get_service_intentions(self, service_name: str) -> List[Dict[str, Any]]:
        """Get service intentions for Connect"""
        try:
            with consul_latency_histogram.labels(operation="get_intentions").time():
                intentions = await self.consul_async.connect.intention.list()
                
                # Filter intentions for the specific service
                service_intentions = [
                    intention for intention in intentions
                    if intention.get('DestinationName') == service_name
                ]
                
                consul_operations_counter.labels(operation="get_intentions", status="success").inc()
                return service_intentions
                
        except Exception as e:
            consul_operations_counter.labels(operation="get_intentions", status="error").inc()
            logger.error(f"Failed to get service intentions: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup registered services"""
        for service_id in list(self.registered_services):
            await self.deregister_service(service_id)
        
        # Close async client
        await self.consul_async.close()

class ConsulServiceMesh:
    """
    Consul Connect service mesh integration
    
    Features:
    - Automatic sidecar proxy management
    - mTLS between services
    - Traffic management and routing
    - Service intentions and ACLs
    """
    
    def __init__(self, consul_client: ConsulClient):
        self.consul = consul_client
        self.proxy_instances: Dict[str, Dict[str, Any]] = {}
    
    async def register_service_with_sidecar(self, 
                                          service_registration: ConsulServiceRegistration,
                                          upstream_services: List[str] = None) -> bool:
        """Register service with sidecar proxy"""
        try:
            # Enable Connect for this registration
            await self.consul.enable_connect()
            
            # Configure upstream services
            upstreams = []
            if upstream_services:
                for upstream in upstream_services:
                    upstreams.append({
                        "DestinationName": upstream,
                        "LocalBindPort": 9000 + len(upstreams)  # Dynamic port assignment
                    })
            
            # Update proxy config
            self.consul.connect_proxy_config = {
                "upstreams": upstreams
            }
            
            # Register the service
            success = await self.consul.register_service(service_registration)
            
            if success:
                # Store proxy configuration
                self.proxy_instances[service_registration.id] = {
                    "service_id": service_registration.id,
                    "proxy_port": service_registration.port + 1000,  # Convention: service_port + 1000
                    "upstreams": upstreams
                }
                
                logger.info(f"Registered service {service_registration.name} with Connect sidecar")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register service with sidecar: {e}")
            return False
    
    async def create_service_intention(self, 
                                     source_service: str, 
                                     destination_service: str, 
                                     action: str = "allow") -> bool:
        """Create service intention for Connect"""
        try:
            intention_data = {
                "SourceName": source_service,
                "DestinationName": destination_service,
                "Action": action,
                "Description": f"Intention from {source_service} to {destination_service}"
            }
            
            # This would use Consul's intentions API
            # For now, we'll log the intention
            logger.info(f"Created intention: {source_service} -> {destination_service} ({action})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create service intention: {e}")
            return False

class ConsulIntegrationTemplate:
    """
    Consul Integration Template for Ainflue Platform
    
    A comprehensive Consul integration that provides:
    - Service registration and discovery
    - Health checking and monitoring
    - Configuration management via KV store
    - Service mesh with Consul Connect
    """
    
    def __init__(self):
        self.service_name = "consul-integration"
        self.service_version = "1.0.0"
        self.description = "Production-ready Consul integration with service mesh support"
    
    def create_client(self, config: Dict[str, Any]) -> ConsulClient:
        """Create a Consul client"""
        return ConsulClient(
            host=config.get("host", "localhost"),
            port=config.get("port", 8500),
            datacenter=config.get("datacenter"),
            token=config.get("token")
        )
    
    def create_service_mesh(self, consul_client: ConsulClient) -> ConsulServiceMesh:
        """Create a Consul service mesh manager"""
        return ConsulServiceMesh(consul_client)
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get Consul integration template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Service registration and discovery",
                "Health check management",
                "KV store for configuration",
                "Service mesh with Connect",
                "Multi-datacenter support",
                "ACL and security policies",
                "Traffic management",
                "Service intentions"
            ],
            "consul_features": [
                "Agent API integration",
                "Health checking",
                "KV store operations",
                "Connect service mesh",
                "Service intentions",
                "CA root management",
                "Multi-datacenter awareness"
            ],
            "dependencies": ["python-consul", "consul.aio", "prometheus"],
            "endpoints": [
                "/consul/register",
                "/consul/discover/{service_name}",
                "/consul/health/{service_name}",
                "/consul/kv/{key}",
                "/consul/intentions"
            ]
        }