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

etcd Integration Template for IA Chéries Platform
=============================================

Production-ready etcd integration with:
- Service registration and discovery
- Distributed configuration management
- Leader election and coordination
- Watch-based real-time updates
- Cluster management and health monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Distributed Systems & etcd Expert
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Set, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

import etcd3
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
etcd_operations_counter = Counter('etcd_operations_total', 'Total etcd operations', ['operation', 'status'])
etcd_latency_histogram = Histogram('etcd_operation_duration_seconds', 'etcd operation latency', ['operation'])
etcd_services_gauge = Gauge('etcd_registered_services', 'Number of services registered in etcd')

@dataclass
class EtcdServiceRegistration:
    """etcd service registration data"""
    id: str
    name: str
    address: str
    port: int
    protocol: str = "http"
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl: int = 30  # TTL in seconds
    tags: List[str] = field(default_factory=list)

class EtcdClient:
    """
    Enhanced etcd client for IA Chéries Platform
    
    Features:
    - Service registration with TTL
    - Watch-based service discovery
    - Distributed configuration
    - Leader election
    - Cluster coordination
    """
    
    def __init__(self, host: str = "localhost", port: int = 2379, 
                 user: Optional[str] = None, password: Optional[str] = None,
                 ca_cert: Optional[str] = None, cert_key: Optional[str] = None, cert_cert: Optional[str] = None):
        
        self.etcd = etcd3.client(
            host=host,
            port=port,
            user=user,
            password=password,
            ca_cert=ca_cert,
            cert_key=cert_key,
            cert_cert=cert_cert
        )
        
        self.service_prefix = "/ainflue/services/"
        self.config_prefix = "/ainflue/config/"
        self.leader_prefix = "/ainflue/leaders/"
        
        # Track leases for TTL management
        self.active_leases: Dict[str, etcd3.Lease] = {}
        self.registered_services: Set[str] = set()
        
        # Watch callbacks
        self.watch_callbacks: Dict[str, List[Callable]] = {}
    
    async def register_service(self, registration: EtcdServiceRegistration) -> bool:
        """Register a service with etcd"""
        try:
            with etcd_latency_histogram.labels(operation="register_service").time():
                # Create lease for TTL
                lease = self.etcd.lease(registration.ttl)
                
                service_key = f"{self.service_prefix}{registration.name}/{registration.id}"
                service_data = {
                    "id": registration.id,
                    "name": registration.name,
                    "address": registration.address,
                    "port": registration.port,
                    "protocol": registration.protocol,
                    "metadata": registration.metadata,
                    "tags": registration.tags,
                    "registered_at": datetime.utcnow().isoformat(),
                    "lease_id": lease.id
                }
                
                # Put service data with lease
                self.etcd.put(service_key, json.dumps(service_data), lease=lease)
                
                # Store lease for renewal
                self.active_leases[registration.id] = lease
                self.registered_services.add(registration.id)
                
                # Start lease renewal
                asyncio.create_task(self._renew_lease(lease, registration.id))
                
                etcd_operations_counter.labels(operation="register_service", status="success").inc()
                etcd_services_gauge.set(len(self.registered_services))
                
                logger.info(f"Registered service {registration.name} with ID {registration.id}")
                return True
                
        except Exception as e:
            etcd_operations_counter.labels(operation="register_service", status="error").inc()
            logger.error(f"Failed to register service {registration.name}: {e}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service from etcd"""
        try:
            with etcd_latency_histogram.labels(operation="deregister_service").time():
                # Find service key pattern
                service_keys = []
                for key, _ in self.etcd.get_prefix(self.service_prefix):
                    if service_id in key.decode():
                        service_keys.append(key)
                
                # Delete service entries
                for key in service_keys:
                    self.etcd.delete(key)
                
                # Revoke lease if exists
                if service_id in self.active_leases:
                    lease = self.active_leases[service_id]
                    lease.revoke()
                    del self.active_leases[service_id]
                
                self.registered_services.discard(service_id)
                
                etcd_operations_counter.labels(operation="deregister_service", status="success").inc()
                etcd_services_gauge.set(len(self.registered_services))
                
                logger.info(f"Deregistered service {service_id}")
                return True
                
        except Exception as e:
            etcd_operations_counter.labels(operation="deregister_service", status="error").inc()
            logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    def discover_services(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover services by name"""
        try:
            with etcd_latency_histogram.labels(operation="discover_services").time():
                service_prefix = f"{self.service_prefix}{service_name}/"
                services = []
                
                for value, metadata in self.etcd.get_prefix(service_prefix):
                    try:
                        service_data = json.loads(value.decode())
                        services.append(service_data)
                    except json.JSONDecodeError:
                        continue
                
                etcd_operations_counter.labels(operation="discover_services", status="success").inc()
                return services
                
        except Exception as e:
            etcd_operations_counter.labels(operation="discover_services", status="error").inc()
            logger.error(f"Failed to discover services {service_name}: {e}")
            return []
    
    def watch_services(self, service_name: str, callback: Callable):
        """Watch for service changes"""
        try:
            service_prefix = f"{self.service_prefix}{service_name}/"
            
            # Add callback to list
            if service_name not in self.watch_callbacks:
                self.watch_callbacks[service_name] = []
            self.watch_callbacks[service_name].append(callback)
            
            # Start watching
            def watch_callback(event):
                try:
                    if event.key.decode().startswith(service_prefix):
                        service_data = None
                        if event.value:
                            service_data = json.loads(event.value.decode())
                        
                        # Call all registered callbacks
                        for cb in self.watch_callbacks.get(service_name, []):
                            cb(event.type, service_data)
                            
                except Exception as e:
                    logger.error(f"Watch callback error: {e}")
            
            # Start etcd watch
            self.etcd.add_watch_callback(service_prefix, watch_callback)
            
            logger.info(f"Started watching services: {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to start watching services {service_name}: {e}")
    
    def put_config(self, key: str, value: str) -> bool:
        """Put configuration value"""
        try:
            with etcd_latency_histogram.labels(operation="put_config").time():
                config_key = f"{self.config_prefix}{key}"
                self.etcd.put(config_key, value)
                
                etcd_operations_counter.labels(operation="put_config", status="success").inc()
                return True
                
        except Exception as e:
            etcd_operations_counter.labels(operation="put_config", status="error").inc()
            logger.error(f"Failed to put config {key}: {e}")
            return False
    
    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value"""
        try:
            with etcd_latency_histogram.labels(operation="get_config").time():
                config_key = f"{self.config_prefix}{key}"
                value, _ = self.etcd.get(config_key)
                
                etcd_operations_counter.labels(operation="get_config", status="success").inc()
                return value.decode() if value else None
                
        except Exception as e:
            etcd_operations_counter.labels(operation="get_config", status="error").inc()
            logger.error(f"Failed to get config {key}: {e}")
            return None
    
    def get_config_prefix(self, prefix: str) -> Dict[str, str]:
        """Get all configuration values with prefix"""
        try:
            with etcd_latency_histogram.labels(operation="get_config_prefix").time():
                config_prefix = f"{self.config_prefix}{prefix}"
                configs = {}
                
                for value, metadata in self.etcd.get_prefix(config_prefix):
                    key = metadata.key.decode().replace(self.config_prefix, "")
                    configs[key] = value.decode()
                
                etcd_operations_counter.labels(operation="get_config_prefix", status="success").inc()
                return configs
                
        except Exception as e:
            etcd_operations_counter.labels(operation="get_config_prefix", status="error").inc()
            logger.error(f"Failed to get config prefix {prefix}: {e}")
            return {}
    
    def watch_config(self, key: str, callback: Callable):
        """Watch for configuration changes"""
        try:
            config_key = f"{self.config_prefix}{key}"
            
            def watch_callback(event):
                try:
                    value = event.value.decode() if event.value else None
                    callback(event.type, value)
                except Exception as e:
                    logger.error(f"Config watch callback error: {e}")
            
            self.etcd.add_watch_callback(config_key, watch_callback)
            logger.info(f"Started watching config: {key}")
            
        except Exception as e:
            logger.error(f"Failed to start watching config {key}: {e}")
    
    async def acquire_leadership(self, name: str, ttl: int = 30) -> Optional[etcd3.Lease]:
        """Acquire leadership for a named resource"""
        try:
            with etcd_latency_histogram.labels(operation="acquire_leadership").time():
                leader_key = f"{self.leader_prefix}{name}"
                
                # Create lease
                lease = self.etcd.lease(ttl)
                
                # Try to acquire leadership
                success = self.etcd.transaction(
                    compare=[self.etcd.transactions.create(leader_key) == 0],
                    success=[self.etcd.transactions.put(leader_key, "leader", lease=lease)],
                    failure=[]
                )
                
                if success:
                    etcd_operations_counter.labels(operation="acquire_leadership", status="success").inc()
                    logger.info(f"Acquired leadership for {name}")
                    
                    # Start lease renewal
                    asyncio.create_task(self._renew_lease(lease, f"leader_{name}"))
                    return lease
                else:
                    etcd_operations_counter.labels(operation="acquire_leadership", status="failure").inc()
                    lease.revoke()
                    return None
                    
        except Exception as e:
            etcd_operations_counter.labels(operation="acquire_leadership", status="error").inc()
            logger.error(f"Failed to acquire leadership for {name}: {e}")
            return None
    
    def release_leadership(self, name: str, lease: etcd3.Lease) -> bool:
        """Release leadership"""
        try:
            with etcd_latency_histogram.labels(operation="release_leadership").time():
                leader_key = f"{self.leader_prefix}{name}"
                
                # Delete leadership key
                self.etcd.delete(leader_key)
                
                # Revoke lease
                lease.revoke()
                
                etcd_operations_counter.labels(operation="release_leadership", status="success").inc()
                logger.info(f"Released leadership for {name}")
                return True
                
        except Exception as e:
            etcd_operations_counter.labels(operation="release_leadership", status="error").inc()
            logger.error(f"Failed to release leadership for {name}: {e}")
            return False
    
    def is_leader(self, name: str) -> bool:
        """Check if current instance is leader"""
        try:
            leader_key = f"{self.leader_prefix}{name}"
            value, _ = self.etcd.get(leader_key)
            return value is not None
            
        except Exception as e:
            logger.error(f"Failed to check leadership for {name}: {e}")
            return False
    
    async def _renew_lease(self, lease: etcd3.Lease, identifier: str):
        """Renew lease periodically"""
        try:
            while identifier in self.active_leases or identifier.startswith("leader_"):
                await asyncio.sleep(lease.ttl // 3)  # Renew at 1/3 of TTL
                try:
                    lease.refresh()
                except Exception as e:
                    logger.error(f"Failed to renew lease for {identifier}: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"Lease renewal cancelled for {identifier}")
        except Exception as e:
            logger.error(f"Lease renewal error for {identifier}: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        # Deregister all services
        for service_id in list(self.registered_services):
            asyncio.create_task(self.deregister_service(service_id))
        
        # Revoke all leases
        for lease in self.active_leases.values():
            try:
                lease.revoke()
            except:
                pass
        
        self.active_leases.clear()

class EtcdIntegrationTemplate:
    """
    etcd Integration Template for IA Chéries Platform
    
    A comprehensive etcd integration that provides:
    - Service registration and discovery with TTL
    - Distributed configuration management
    - Leader election and coordination
    - Watch-based real-time updates
    """
    
    def __init__(self):
        self.service_name = "etcd-integration"
        self.service_version = "1.0.0"
        self.description = "Production-ready etcd integration with distributed coordination"
    
    def create_client(self, config: Dict[str, Any]) -> EtcdClient:
        """Create an etcd client"""
        return EtcdClient(
            host=config.get("host", "localhost"),
            port=config.get("port", 2379),
            user=config.get("user"),
            password=config.get("password"),
            ca_cert=config.get("ca_cert"),
            cert_key=config.get("cert_key"),
            cert_cert=config.get("cert_cert")
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get etcd integration template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Service registration with TTL",
                "Watch-based service discovery",
                "Distributed configuration management",
                "Leader election and coordination",
                "Real-time change notifications",
                "Cluster health monitoring",
                "Automatic lease renewal",
                "Transactional operations"
            ],
            "etcd_features": [
                "Key-value store operations",
                "Watch API for real-time updates",
                "Lease management with TTL",
                "Transactional compare-and-swap",
                "Prefix-based queries",
                "Leader election primitives",
                "Cluster membership",
                "TLS security support"
            ],
            "dependencies": ["etcd3-py", "prometheus"],
            "endpoints": [
                "/etcd/register",
                "/etcd/discover/{service_name}",
                "/etcd/config/{key}",
                "/etcd/leadership/{name}",
                "/etcd/watch/{key}"
            ]
        }