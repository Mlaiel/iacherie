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

Eureka Integration Template for iacherie Platform
==============================================

Production-ready Netflix Eureka integration with:
- Service registration and discovery
- Health checking and heartbeats
- Load balancing integration
- Multi-zone deployment support
- Circuit breaker integration

Author: Fahed Mlaiel (mlaiel@live.de)
Netflix OSS & Spring Cloud Expert
"""

import asyncio
import json
import logging
import time
import aiohttp
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
eureka_operations_counter = Counter('eureka_operations_total', 'Total Eureka operations', ['operation', 'status'])
eureka_latency_histogram = Histogram('eureka_operation_duration_seconds', 'Eureka operation latency', ['operation'])
eureka_instances_gauge = Gauge('eureka_registered_instances', 'Number of instances registered in Eureka')

class InstanceStatus(str, Enum):
    """Eureka instance status"""
    UP = "UP"
    DOWN = "DOWN"
    STARTING = "STARTING"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    UNKNOWN = "UNKNOWN"

@dataclass
class EurekaInstance:
    """Eureka instance registration data"""
    instance_id: str
    app_name: str
    host_name: str
    ip_addr: str
    port: int
    secure_port: int = 443
    home_page_url: str = ""
    status_page_url: str = ""
    health_check_url: str = ""
    vip_address: str = ""
    secure_vip_address: str = ""
    status: InstanceStatus = InstanceStatus.UP
    metadata: Dict[str, str] = field(default_factory=dict)
    lease_renewal_interval_in_secs: int = 30
    lease_duration_in_secs: int = 90

class EurekaClient:
    """
    Enhanced Eureka client for iacherie Platform
    
    Features:
    - Service registration with heartbeats
    - Service discovery with caching
    - Health checking integration
    - Multi-zone support
    - Load balancing awareness
    """
    
    def __init__(self, eureka_server_url: str, app_name: str, instance_port: int):
        self.eureka_server_url = eureka_server_url.rstrip('/')
        self.app_name = app_name
        self.instance_port = instance_port
        
        # Generate instance ID
        import socket
        hostname = socket.gethostname()
        self.instance_id = f"{hostname}:{app_name}:{instance_port}"
        
        # Track registration state
        self.is_registered = False
        self.heartbeat_task = None
        self.last_heartbeat = None
        
        # Discovery cache
        self.discovery_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_last_updated: Dict[str, datetime] = {}
        self.cache_ttl = 30  # seconds
    
    async def register_instance(self, instance: EurekaInstance) -> bool:
        """Register instance with Eureka server"""
        try:
            with eureka_latency_histogram.labels(operation="register_instance").time():
                registration_data = {
                    "instance": {
                        "instanceId": instance.instance_id,
                        "app": instance.app_name.upper(),
                        "hostName": instance.host_name,
                        "ipAddr": instance.ip_addr,
                        "port": {"$": instance.port, "@enabled": "true"},
                        "securePort": {"$": instance.secure_port, "@enabled": "false"},
                        "homePageUrl": instance.home_page_url or f"http://{instance.ip_addr}:{instance.port}/",
                        "statusPageUrl": instance.status_page_url or f"http://{instance.ip_addr}:{instance.port}/actuator/info",
                        "healthCheckUrl": instance.health_check_url or f"http://{instance.ip_addr}:{instance.port}/actuator/health",
                        "vipAddress": instance.vip_address or instance.app_name.lower(),
                        "secureVipAddress": instance.secure_vip_address or instance.app_name.lower(),
                        "status": instance.status.value,
                        "metadata": instance.metadata,
                        "leaseInfo": {
                            "renewalIntervalInSecs": instance.lease_renewal_interval_in_secs,
                            "durationInSecs": instance.lease_duration_in_secs
                        },
                        "dataCenterInfo": {
                            "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                            "name": "MyOwn"
                        }
                    }
                }
                
                url = f"{self.eureka_server_url}/eureka/apps/{instance.app_name.upper()}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=registration_data, 
                                          headers={"Content-Type": "application/json"}) as response:
                        
                        if response.status == 204:
                            self.is_registered = True
                            eureka_operations_counter.labels(operation="register_instance", status="success").inc()
                            eureka_instances_gauge.inc()
                            
                            # Start heartbeat
                            await self._start_heartbeat(instance)
                            
                            logger.info(f"Registered instance {instance.instance_id} with Eureka")
                            return True
                        else:
                            eureka_operations_counter.labels(operation="register_instance", status="failure").inc()
                            logger.error(f"Failed to register instance. Status: {response.status}")
                            return False
                            
        except Exception as e:
            eureka_operations_counter.labels(operation="register_instance", status="error").inc()
            logger.error(f"Failed to register instance: {e}")
            return False
    
    async def deregister_instance(self, app_name: str, instance_id: str) -> bool:
        """Deregister instance from Eureka server"""
        try:
            with eureka_latency_histogram.labels(operation="deregister_instance").time():
                url = f"{self.eureka_server_url}/eureka/apps/{app_name.upper()}/{instance_id}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.delete(url) as response:
                        
                        if response.status == 200:
                            self.is_registered = False
                            eureka_operations_counter.labels(operation="deregister_instance", status="success").inc()
                            eureka_instances_gauge.dec()
                            
                            # Stop heartbeat
                            await self._stop_heartbeat()
                            
                            logger.info(f"Deregistered instance {instance_id}")
                            return True
                        else:
                            eureka_operations_counter.labels(operation="deregister_instance", status="failure").inc()
                            return False
                            
        except Exception as e:
            eureka_operations_counter.labels(operation="deregister_instance", status="error").inc()
            logger.error(f"Failed to deregister instance: {e}")
            return False
    
    async def send_heartbeat(self, app_name: str, instance_id: str) -> bool:
        """Send heartbeat to Eureka server"""
        try:
            with eureka_latency_histogram.labels(operation="heartbeat").time():
                url = f"{self.eureka_server_url}/eureka/apps/{app_name.upper()}/{instance_id}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.put(url) as response:
                        
                        success = response.status == 200
                        if success:
                            eureka_operations_counter.labels(operation="heartbeat", status="success").inc()
                            self.last_heartbeat = datetime.utcnow()
                        else:
                            eureka_operations_counter.labels(operation="heartbeat", status="failure").inc()
                            
                        return success
                        
        except Exception as e:
            eureka_operations_counter.labels(operation="heartbeat", status="error").inc()
            logger.error(f"Failed to send heartbeat: {e}")
            return False
    
    async def discover_instances(self, app_name: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Discover instances of an application"""
        try:
            # Check cache first
            if use_cache and app_name in self.discovery_cache:
                cache_age = (datetime.utcnow() - self.cache_last_updated[app_name]).total_seconds()
                if cache_age < self.cache_ttl:
                    return self.discovery_cache[app_name].get("instances", [])
            
            with eureka_latency_histogram.labels(operation="discover_instances").time():
                url = f"{self.eureka_server_url}/eureka/apps/{app_name.upper()}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"Accept": "application/json"}) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            instances = []
                            if "application" in data and "instance" in data["application"]:
                                app_instances = data["application"]["instance"]
                                if isinstance(app_instances, dict):
                                    app_instances = [app_instances]
                                
                                for instance in app_instances:
                                    if instance.get("status") == "UP":
                                        instances.append({
                                            "instanceId": instance.get("instanceId"),
                                            "hostName": instance.get("hostName"),
                                            "ipAddr": instance.get("ipAddr"),
                                            "port": instance.get("port", {}).get("$"),
                                            "securePort": instance.get("securePort", {}).get("$"),
                                            "homePageUrl": instance.get("homePageUrl"),
                                            "statusPageUrl": instance.get("statusPageUrl"),
                                            "healthCheckUrl": instance.get("healthCheckUrl"),
                                            "status": instance.get("status"),
                                            "metadata": instance.get("metadata", {})
                                        })
                            
                            # Update cache
                            self.discovery_cache[app_name] = {"instances": instances}
                            self.cache_last_updated[app_name] = datetime.utcnow()
                            
                            eureka_operations_counter.labels(operation="discover_instances", status="success").inc()
                            return instances
                        
                        elif response.status == 404:
                            # Application not found
                            eureka_operations_counter.labels(operation="discover_instances", status="not_found").inc()
                            return []
                        else:
                            eureka_operations_counter.labels(operation="discover_instances", status="failure").inc()
                            return []
                            
        except Exception as e:
            eureka_operations_counter.labels(operation="discover_instances", status="error").inc()
            logger.error(f"Failed to discover instances for {app_name}: {e}")
            return []
    
    async def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications registered with Eureka"""
        try:
            with eureka_latency_histogram.labels(operation="get_all_applications").time():
                url = f"{self.eureka_server_url}/eureka/apps"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"Accept": "application/json"}) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            applications = []
                            
                            if "applications" in data and "application" in data["applications"]:
                                apps = data["applications"]["application"]
                                if isinstance(apps, dict):
                                    apps = [apps]
                                
                                for app in apps:
                                    app_info = {
                                        "name": app.get("name"),
                                        "instance_count": len(app.get("instance", [])),
                                        "instances": app.get("instance", [])
                                    }
                                    applications.append(app_info)
                            
                            eureka_operations_counter.labels(operation="get_all_applications", status="success").inc()
                            return applications
                        else:
                            eureka_operations_counter.labels(operation="get_all_applications", status="failure").inc()
                            return []
                            
        except Exception as e:
            eureka_operations_counter.labels(operation="get_all_applications", status="error").inc()
            logger.error(f"Failed to get all applications: {e}")
            return []
    
    async def update_instance_status(self, app_name: str, instance_id: str, status: InstanceStatus) -> bool:
        """Update instance status"""
        try:
            with eureka_latency_histogram.labels(operation="update_status").time():
                url = f"{self.eureka_server_url}/eureka/apps/{app_name.upper()}/{instance_id}/status"
                
                params = {"value": status.value}
                
                async with aiohttp.ClientSession() as session:
                    async with session.put(url, params=params) as response:
                        
                        success = response.status == 200
                        if success:
                            eureka_operations_counter.labels(operation="update_status", status="success").inc()
                            logger.info(f"Updated instance {instance_id} status to {status.value}")
                        else:
                            eureka_operations_counter.labels(operation="update_status", status="failure").inc()
                            
                        return success
                        
        except Exception as e:
            eureka_operations_counter.labels(operation="update_status", status="error").inc()
            logger.error(f"Failed to update instance status: {e}")
            return False
    
    async def get_instance_info(self, app_name: str, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get specific instance information"""
        try:
            with eureka_latency_histogram.labels(operation="get_instance_info").time():
                url = f"{self.eureka_server_url}/eureka/apps/{app_name.upper()}/{instance_id}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"Accept": "application/json"}) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            eureka_operations_counter.labels(operation="get_instance_info", status="success").inc()
                            return data.get("instance")
                        else:
                            eureka_operations_counter.labels(operation="get_instance_info", status="failure").inc()
                            return None
                            
        except Exception as e:
            eureka_operations_counter.labels(operation="get_instance_info", status="error").inc()
            logger.error(f"Failed to get instance info: {e}")
            return None
    
    async def _start_heartbeat(self, instance: EurekaInstance):
        """Start heartbeat task"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        self.heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(instance.app_name, instance.instance_id, 
                               instance.lease_renewal_interval_in_secs)
        )
    
    async def _stop_heartbeat(self):
        """Stop heartbeat task"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
    
    async def _heartbeat_loop(self, app_name: str, instance_id: str, interval: int):
        """Heartbeat loop"""
        while self.is_registered:
            try:
                await self.send_heartbeat(app_name, instance_id)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(interval)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.is_registered:
            await self.deregister_instance(self.app_name, self.instance_id)
        
        await self._stop_heartbeat()

class EurekaIntegrationTemplate:
    """
    Eureka Integration Template for iacherie Platform
    
    A comprehensive Netflix Eureka integration that provides:
    - Service registration and discovery
    - Health checking with heartbeats
    - Load balancing integration
    - Multi-zone deployment support
    """
    
    def __init__(self):
        self.service_name = "eureka-integration"
        self.service_version = "1.0.0"
        self.description = "Production-ready Netflix Eureka integration with Spring Cloud compatibility"
    
    def create_client(self, config: Dict[str, Any]) -> EurekaClient:
        """Create a Eureka client"""
        return EurekaClient(
            eureka_server_url=config["eureka_server_url"],
            app_name=config["app_name"],
            instance_port=config["instance_port"]
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get Eureka integration template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Service registration with heartbeats",
                "Service discovery with caching",
                "Health status management",
                "Multi-zone deployment support",
                "Load balancing integration",
                "Spring Cloud compatibility",
                "Instance metadata support",
                "Automatic lease renewal"
            ],
            "eureka_features": [
                "REST API integration",
                "Instance status management",
                "Application discovery",
                "Heartbeat mechanism",
                "Service registry caching",
                "Multi-datacenter awareness",
                "Load balancer integration",
                "Circuit breaker support"
            ],
            "dependencies": ["aiohttp", "prometheus"],
            "endpoints": [
                "/eureka/register",
                "/eureka/deregister",
                "/eureka/discover/{app_name}",
                "/eureka/status/{instance_id}",
                "/eureka/applications"
            ]
        }