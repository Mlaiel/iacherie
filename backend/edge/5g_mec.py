"""5G Multi-access Edge Computing (MEC) Integration
==================================================

Advanced 5G MEC orchestration for edge computing services,
low-latency processing, and mobile network optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
import aiohttp
import time
import socket
import subprocess
import psutil
from collections import defaultdict

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """MEC service types."""
    CONTENT_DELIVERY = "content_delivery"
    AUGMENTED_REALITY = "augmented_reality"
    VIDEO_STREAMING = "video_streaming"
    GAMING = "gaming"
    IOT_PROCESSING = "iot_processing"
    AI_INFERENCE = "ai_inference"
    VOICE_PROCESSING = "voice_processing"
    IMAGE_PROCESSING = "image_processing"
    REAL_TIME_ANALYTICS = "real_time_analytics"
    COLLABORATIVE_APPS = "collaborative_apps"


class EdgeNodeType(str, Enum):
    """Edge node types."""
    BASE_STATION = "base_station"
    REGIONAL_DATA_CENTER = "regional_data_center"
    LOCAL_BREAKOUT = "local_breakout"
    MOBILE_EDGE_HOST = "mobile_edge_host"
    CLOUDLET = "cloudlet"
    FOG_NODE = "fog_node"


class NetworkSliceType(str, Enum):
    """5G network slice types."""
    ENHANCED_MOBILE_BROADBAND = "embb"  # eMBB
    ULTRA_RELIABLE_LOW_LATENCY = "urllc"  # URLLC
    MASSIVE_IOT = "miot"  # mIoT
    CUSTOM = "custom"


class QoSClass(str, Enum):
    """Quality of Service classes."""
    BEST_EFFORT = "best_effort"
    GUARANTEED_BANDWIDTH = "guaranteed_bandwidth"
    LOW_LATENCY = "low_latency"
    ULTRA_LOW_LATENCY = "ultra_low_latency"
    HIGH_RELIABILITY = "high_reliability"
    CRITICAL = "critical"


@dataclass
class EdgeNode:
    """Edge computing node."""
    node_id: str
    node_type: EdgeNodeType
    location: Dict[str, float]  # latitude, longitude
    ip_address: str
    port: int
    capabilities: List[ServiceType]
    resources: Dict[str, Any]  # CPU, memory, storage, GPU
    network_info: Dict[str, Any]
    status: str
    load_percentage: float
    latency_ms: float
    bandwidth_mbps: float
    connected_devices: int
    last_heartbeat: datetime
    metadata: Dict[str, Any]


@dataclass
class ServiceInstance:
    """MEC service instance."""
    instance_id: str
    service_type: ServiceType
    node_id: str
    container_id: Optional[str]
    image_name: str
    resource_allocation: Dict[str, Any]
    network_requirements: Dict[str, Any]
    qos_requirements: Dict[str, Any]
    configuration: Dict[str, Any]
    status: str
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any]


@dataclass
class MobileDevice:
    """Connected mobile device."""
    device_id: str
    imsi: str
    ip_address: str
    current_cell_id: str
    current_node_id: str
    location: Optional[Dict[str, float]]
    network_slice: NetworkSliceType
    qos_profile: QoSClass
    bandwidth_usage_mbps: float
    latency_ms: float
    signal_strength_dbm: float
    handover_count: int
    connected_services: List[str]
    last_seen: datetime
    metadata: Dict[str, Any]


@dataclass
class NetworkSlice:
    """5G network slice."""
    slice_id: str
    slice_type: NetworkSliceType
    tenant_id: str
    sla_requirements: Dict[str, Any]
    resource_allocation: Dict[str, Any]
    traffic_policy: Dict[str, Any]
    security_policy: Dict[str, Any]
    mobility_policy: Dict[str, Any]
    connected_devices: List[str]
    active_services: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class ServiceMigration:
    """Service migration between edge nodes."""
    migration_id: str
    service_instance_id: str
    source_node_id: str
    target_node_id: str
    migration_type: str  # proactive, reactive, user_triggered
    trigger_reason: str
    migration_strategy: str
    estimated_downtime_ms: float
    actual_downtime_ms: Optional[float]
    data_transfer_mb: float
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]


class MECOrchestrator:
    """5G Multi-access Edge Computing orchestrator."""
    
    def __init__(
        self,
        orchestrator_id -> None: str,
        management_ip -> None: str = "0.0.0.0",
        management_port -> None: int = 8080,
        enable_5g_core_integration -> None: bool = True,
        enable_network_slicing -> None: bool = True,
        enable_auto_scaling -> None: bool = True,
        enable_service_migration -> None: bool = True
    ) -> None:
        self.orchestrator_id = orchestrator_id
        self.management_ip = management_ip
        self.management_port = management_port
        self.enable_5g_core_integration = enable_5g_core_integration
        self.enable_network_slicing = enable_network_slicing
        self.enable_auto_scaling = enable_auto_scaling
        self.enable_service_migration = enable_service_migration
        
        # Node management
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.service_instances: Dict[str, ServiceInstance] = {}
        self.mobile_devices: Dict[str, MobileDevice] = {}
        self.network_slices: Dict[str, NetworkSlice] = {}
        
        # Migration tracking
        self.active_migrations: Dict[str, ServiceMigration] = {}
        self.migration_history: List[ServiceMigration] = []
        
        # Performance monitoring
        self.orchestrator_start_time = datetime.now()
        self.total_services_deployed = 0
        self.total_migrations_performed = 0
        self.total_handovers_handled = 0
        
        # HTTP session for API calls
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.running = False
        
        logger.info(f"MEC Orchestrator {orchestrator_id} initialized")
    
    async def start(self) -> None:
        """Start the MEC orchestrator."""
        self.running = True
        await self._initialize_session()
        
        # Start background monitoring tasks
        if self.enable_auto_scaling:
            task = asyncio.create_task(self._auto_scaling_monitor())
            self.monitoring_tasks.append(task)
        
        if self.enable_service_migration:
            task = asyncio.create_task(self._migration_monitor())
            self.monitoring_tasks.append(task)
        
        # Start node health monitoring
        task = asyncio.create_task(self._node_health_monitor())
        self.monitoring_tasks.append(task)
        
        # Start device tracking
        task = asyncio.create_task(self._device_tracker())
        self.monitoring_tasks.append(task)
        
        logger.info("MEC Orchestrator started")
    
    async def stop(self) -> None:
        """Stop the MEC orchestrator."""
        self.running = False
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        if self.session:
            await self.session.close()
        
        logger.info("MEC Orchestrator stopped")
    
    async def _initialize_session(self) -> None:
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def register_edge_node(
        self,
        node_type: EdgeNodeType,
        location: Dict[str, float],
        ip_address: str,
        port: int,
        capabilities: List[ServiceType],
        resources: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new edge node."""
        node_id = str(uuid.uuid4())
        
        # Test connectivity to node
        latency = await self._measure_latency(ip_address)
        bandwidth = await self._measure_bandwidth(ip_address, port)
        
        node = EdgeNode(
            node_id=node_id,
            node_type=node_type,
            location=location,
            ip_address=ip_address,
            port=port,
            capabilities=capabilities,
            resources=resources,
            network_info={
                "latency_ms": latency,
                "bandwidth_mbps": bandwidth,
                "packet_loss": 0.0,
                "jitter_ms": 0.0
            },
            status="active",
            load_percentage=0.0,
            latency_ms=latency,
            bandwidth_mbps=bandwidth,
            connected_devices=0,
            last_heartbeat=datetime.now(),
            metadata=metadata or {}
        )
        
        self.edge_nodes[node_id] = node
        
        logger.info(f"Edge node registered: {node_id} at {ip_address}:{port}")
        return node_id
    
    async def unregister_edge_node(self, node_id: str) -> bool:
        """Unregister an edge node."""
        if node_id not in self.edge_nodes:
            return False
        
        # Migrate all services from this node
        services_to_migrate = [
            instance for instance in self.service_instances.values()
            if instance.node_id == node_id
        ]
        
        for service in services_to_migrate:
            await self._migrate_service(service.instance_id, trigger_reason="node_shutdown")
        
        # Remove node
        del self.edge_nodes[node_id]
        
        logger.info(f"Edge node unregistered: {node_id}")
        return True
    
    async def deploy_service(
        self,
        service_type: ServiceType,
        image_name: str,
        resource_requirements: Dict[str, Any],
        network_requirements: Dict[str, Any],
        qos_requirements: Dict[str, Any],
        target_node_id: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Deploy a service on an edge node."""
        instance_id = str(uuid.uuid4())
        
        # Select target node if not specified
        if target_node_id is None:
            target_node_id = await self._select_optimal_node(
                service_type, resource_requirements, qos_requirements
            )
        
        if target_node_id not in self.edge_nodes:
            raise ValueError(f"Target node {target_node_id} not found")
        
        # Deploy container/service
        container_id = await self._deploy_container(
            target_node_id, image_name, resource_requirements, configuration
        )
        
        # Create service instance
        service_instance = ServiceInstance(
            instance_id=instance_id,
            service_type=service_type,
            node_id=target_node_id,
            container_id=container_id,
            image_name=image_name,
            resource_allocation=resource_requirements,
            network_requirements=network_requirements,
            qos_requirements=qos_requirements,
            configuration=configuration or {},
            status="running",
            created_at=datetime.now(),
            last_updated=datetime.now(),
            metadata=metadata or {}
        )
        
        self.service_instances[instance_id] = service_instance
        self.total_services_deployed += 1
        
        # Update node load
        await self._update_node_load(target_node_id)
        
        logger.info(f"Service deployed: {service_type.value} on node {target_node_id}")
        return instance_id
    
    async def undeploy_service(self, instance_id: str) -> bool:
        """Undeploy a service."""
        if instance_id not in self.service_instances:
            return False
        
        service = self.service_instances[instance_id]
        
        # Stop container
        if service.container_id:
            await self._stop_container(service.node_id, service.container_id)
        
        # Remove service instance
        del self.service_instances[instance_id]
        
        # Update node load
        await self._update_node_load(service.node_id)
        
        logger.info(f"Service undeployed: {instance_id}")
        return True
    
    async def register_mobile_device(
        self,
        device_id: str,
        imsi: str,
        ip_address: str,
        current_cell_id: str,
        location: Optional[Dict[str, float]] = None,
        qos_profile: QoSClass = QoSClass.BEST_EFFORT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a mobile device."""
        # Find nearest edge node
        node_id = await self._find_nearest_node(location) if location else None
        
        device = MobileDevice(
            device_id=device_id,
            imsi=imsi,
            ip_address=ip_address,
            current_cell_id=current_cell_id,
            current_node_id=node_id or "",
            location=location,
            network_slice=NetworkSliceType.ENHANCED_MOBILE_BROADBAND,
            qos_profile=qos_profile,
            bandwidth_usage_mbps=0.0,
            latency_ms=0.0,
            signal_strength_dbm=-70.0,
            handover_count=0,
            connected_services=[],
            last_seen=datetime.now(),
            metadata=metadata or {}
        )
        
        self.mobile_devices[device_id] = device
        
        # Update node device count
        if node_id and node_id in self.edge_nodes:
            self.edge_nodes[node_id].connected_devices += 1
        
        logger.info(f"Mobile device registered: {device_id}")
        return True
    
    async def handle_device_handover(
        self,
        device_id: str,
        new_cell_id: str,
        new_location: Optional[Dict[str, float]] = None
    ) -> bool:
        """Handle device handover between cells."""
        if device_id not in self.mobile_devices:
            return False
        
        device = self.mobile_devices[device_id]
        old_node_id = device.current_node_id
        
        # Find new optimal node
        new_node_id = await self._find_nearest_node(new_location) if new_location else old_node_id
        
        # Update device info
        device.current_cell_id = new_cell_id
        device.current_node_id = new_node_id
        device.location = new_location
        device.handover_count += 1
        device.last_seen = datetime.now()
        
        # Update node device counts
        if old_node_id and old_node_id in self.edge_nodes and old_node_id != new_node_id:
            self.edge_nodes[old_node_id].connected_devices -= 1
        
        if new_node_id and new_node_id in self.edge_nodes and old_node_id != new_node_id:
            self.edge_nodes[new_node_id].connected_devices += 1
        
        # Migrate services if needed
        if old_node_id != new_node_id and device.connected_services:
            for service_id in device.connected_services:
                if service_id in self.service_instances:
                    await self._migrate_service(
                        service_id, 
                        target_node_id=new_node_id,
                        trigger_reason="device_handover"
                    )
        
        self.total_handovers_handled += 1
        
        logger.info(f"Device handover: {device_id} from {old_node_id} to {new_node_id}")
        return True
    
    async def create_network_slice(
        self,
        slice_type: NetworkSliceType,
        tenant_id: str,
        sla_requirements: Dict[str, Any],
        resource_allocation: Dict[str, Any],
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a 5G network slice."""
        slice_id = str(uuid.uuid4())
        
        network_slice = NetworkSlice(
            slice_id=slice_id,
            slice_type=slice_type,
            tenant_id=tenant_id,
            sla_requirements=sla_requirements,
            resource_allocation=resource_allocation,
            traffic_policy={
                "bandwidth_limit_mbps": resource_allocation.get("bandwidth_mbps", 100),
                "latency_target_ms": sla_requirements.get("latency_ms", 10),
                "priority": sla_requirements.get("priority", 5)
            },
            security_policy={
                "encryption": True,
                "isolation_level": "strong",
                "authentication": "required"
            },
            mobility_policy={
                "handover_threshold_ms": 50,
                "migration_enabled": True
            },
            connected_devices=[],
            active_services=[],
            created_at=datetime.now(),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self.network_slices[slice_id] = network_slice
        
        logger.info(f"Network slice created: {slice_type.value} for tenant {tenant_id}")
        return slice_id
    
    async def _select_optimal_node(
        self,
        service_type: ServiceType,
        resource_requirements: Dict[str, Any],
        qos_requirements: Dict[str, Any]
    ) -> str:
        """Select optimal edge node for service deployment."""
        suitable_nodes = []
        
        for node_id, node in self.edge_nodes.items():
            # Check if node supports service type
            if service_type not in node.capabilities:
                continue
            
            # Check if node has sufficient resources
            if not self._check_node_resources(node, resource_requirements):
                continue
            
            # Calculate suitability score
            score = self._calculate_node_score(node, qos_requirements)
            suitable_nodes.append((node_id, score))
        
        if not suitable_nodes:
            raise RuntimeError("No suitable edge node found")
        
        # Sort by score (higher is better)
        suitable_nodes.sort(key=lambda x: x[1], reverse=True)
        return suitable_nodes[0][0]
    
    def _check_node_resources(self, node: EdgeNode, requirements: Dict[str, Any]) -> bool:
        """Check if node has sufficient resources."""
        cpu_required = requirements.get("cpu_cores", 1)
        memory_required = requirements.get("memory_mb", 512)
        storage_required = requirements.get("storage_mb", 1024)
        
        cpu_available = node.resources.get("cpu_cores", 0) * (1 - node.load_percentage / 100)
        memory_available = node.resources.get("memory_mb", 0) * (1 - node.load_percentage / 100)
        storage_available = node.resources.get("storage_mb", 0)
        
        return (
            cpu_available >= cpu_required and
            memory_available >= memory_required and
            storage_available >= storage_required
        )
    
    def _calculate_node_score(self, node: EdgeNode, qos_requirements: Dict[str, Any]) -> float:
        """Calculate node suitability score."""
        score = 100.0
        
        # Penalize high load
        score -= node.load_percentage
        
        # Penalize high latency
        target_latency = qos_requirements.get("latency_ms", 50)
        if node.latency_ms > target_latency:
            score -= (node.latency_ms - target_latency) * 2
        
        # Reward high bandwidth
        min_bandwidth = qos_requirements.get("bandwidth_mbps", 10)
        if node.bandwidth_mbps >= min_bandwidth:
            score += min(node.bandwidth_mbps / min_bandwidth * 10, 20)
        
        # Penalize many connected devices
        score -= node.connected_devices * 0.5
        
        return max(score, 0.0)
    
    async def _deploy_container(
        self,
        node_id: str,
        image_name: str,
        resource_requirements: Dict[str, Any],
        configuration: Optional[Dict[str, Any]]
    ) -> str:
        """Deploy container on edge node."""
        # In a real implementation, this would use Docker/Kubernetes APIs
        # For simulation, return a mock container ID
        container_id = f"container_{uuid.uuid4().hex[:8]}"
        
        # Simulate deployment delay
        await asyncio.sleep(2.0)
        
        logger.info(f"Container deployed: {container_id} on node {node_id}")
        return container_id
    
    async def _stop_container(self, node_id: str, container_id: str) -> bool:
        """Stop container on edge node."""
        # In a real implementation, this would use Docker/Kubernetes APIs
        await asyncio.sleep(1.0)
        
        logger.info(f"Container stopped: {container_id} on node {node_id}")
        return True
    
    async def _migrate_service(
        self,
        service_instance_id: str,
        target_node_id: Optional[str] = None,
        trigger_reason: str = "manual"
    ) -> bool:
        """Migrate service to another edge node."""
        if service_instance_id not in self.service_instances:
            return False
        
        service = self.service_instances[service_instance_id]
        source_node_id = service.node_id
        
        # Select target node if not specified
        if target_node_id is None:
            target_node_id = await self._select_optimal_node(
                service.service_type,
                service.resource_allocation,
                service.qos_requirements
            )
        
        if target_node_id == source_node_id:
            return True  # No migration needed
        
        migration_id = str(uuid.uuid4())
        
        migration = ServiceMigration(
            migration_id=migration_id,
            service_instance_id=service_instance_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            migration_type="reactive",
            trigger_reason=trigger_reason,
            migration_strategy="live_migration",
            estimated_downtime_ms=100.0,
            actual_downtime_ms=None,
            data_transfer_mb=service.resource_allocation.get("memory_mb", 512) * 0.8,
            status="in_progress",
            started_at=datetime.now(),
            completed_at=None,
            metadata={}
        )
        
        self.active_migrations[migration_id] = migration
        
        try:
            # Perform migration
            start_time = time.time()
            
            # Deploy on target node
            new_container_id = await self._deploy_container(
                target_node_id,
                service.image_name,
                service.resource_allocation,
                service.configuration
            )
            
            # Stop old container
            if service.container_id:
                await self._stop_container(source_node_id, service.container_id)
            
            # Update service instance
            service.node_id = target_node_id
            service.container_id = new_container_id
            service.last_updated = datetime.now()
            
            # Complete migration
            end_time = time.time()
            migration.actual_downtime_ms = (end_time - start_time) * 1000
            migration.status = "completed"
            migration.completed_at = datetime.now()
            
            # Move to history
            self.migration_history.append(migration)
            del self.active_migrations[migration_id]
            
            self.total_migrations_performed += 1
            
            logger.info(f"Service migrated: {service_instance_id} from {source_node_id} to {target_node_id}")
            return True
            
        except Exception as e:
            migration.status = "failed"
            migration.completed_at = datetime.now()
            migration.metadata["error"] = str(e)
            
            self.migration_history.append(migration)
            del self.active_migrations[migration_id]
            
            logger.error(f"Service migration failed: {e}")
            return False
    
    async def _find_nearest_node(self, location: Optional[Dict[str, float]]) -> Optional[str]:
        """Find nearest edge node to a location."""
        if not location or not self.edge_nodes:
            return None
        
        min_distance = float('inf')
        nearest_node_id = None
        
        for node_id, node in self.edge_nodes.items():
            distance = self._calculate_distance(location, node.location)
            if distance < min_distance:
                min_distance = distance
                nearest_node_id = node_id
        
        return nearest_node_id
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations (simplified)."""
        lat_diff = loc1.get("latitude", 0) - loc2.get("latitude", 0)
        lon_diff = loc1.get("longitude", 0) - loc2.get("longitude", 0)
        return (lat_diff ** 2 + lon_diff ** 2) ** 0.5
    
    async def _measure_latency(self, ip_address: str) -> float:
        """Measure network latency to a node."""
        try:
            start_time = time.time()
            
            # Simple TCP connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            result = sock.connect_ex((ip_address, 80))
            sock.close()
            
            end_time = time.time()
            
            if result == 0:
                return (end_time - start_time) * 1000  # Convert to ms
            else:
                return 100.0  # Default high latency for unreachable hosts
                
        except Exception:
            return 100.0
    
    async def _measure_bandwidth(self, ip_address: str, port: int) -> float:
        """Measure bandwidth to a node (simplified)."""
        # In a real implementation, this would perform actual bandwidth testing
        # For simulation, return a mock value based on IP
        return hash(ip_address) % 1000 + 100  # 100-1100 Mbps
    
    async def _update_node_load(self, node_id -> None: str) -> None:
        """Update node load percentage."""
        if node_id not in self.edge_nodes:
            return
        
        node = self.edge_nodes[node_id]
        
        # Calculate load based on running services
        total_cpu_allocated = 0
        total_memory_allocated = 0
        
        for service in self.service_instances.values():
            if service.node_id == node_id:
                total_cpu_allocated += service.resource_allocation.get("cpu_cores", 1)
                total_memory_allocated += service.resource_allocation.get("memory_mb", 512)
        
        cpu_load = (total_cpu_allocated / node.resources.get("cpu_cores", 1)) * 100
        memory_load = (total_memory_allocated / node.resources.get("memory_mb", 1024)) * 100
        
        node.load_percentage = max(cpu_load, memory_load)
        node.last_heartbeat = datetime.now()
    
    async def _auto_scaling_monitor(self) -> None:
        """Monitor and trigger auto-scaling decisions."""
        while self.running:
            try:
                for node_id, node in self.edge_nodes.items():
                    # Scale up if load is high
                    if node.load_percentage > 80:
                        await self._trigger_scale_up(node_id)
                    
                    # Scale down if load is low
                    elif node.load_percentage < 20:
                        await self._trigger_scale_down(node_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Auto-scaling monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _migration_monitor(self) -> None:
        """Monitor and trigger service migrations."""
        while self.running:
            try:
                # Check for overloaded nodes
                for node_id, node in self.edge_nodes.items():
                    if node.load_percentage > 90:
                        # Find services to migrate
                        services_to_migrate = [
                            s for s in self.service_instances.values()
                            if s.node_id == node_id
                        ]
                        
                        # Migrate least critical services first
                        for service in services_to_migrate[:2]:  # Migrate up to 2 services
                            await self._migrate_service(
                                service.instance_id,
                                trigger_reason="load_balancing"
                            )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Migration monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _node_health_monitor(self) -> None:
        """Monitor edge node health."""
        while self.running:
            try:
                current_time = datetime.now()
                
                for node_id, node in list(self.edge_nodes.items()):
                    # Check if node is responsive
                    time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > 300:  # 5 minutes
                        logger.warning(f"Node {node_id} appears to be unresponsive")
                        node.status = "unresponsive"
                        
                        # Migrate services from unresponsive node
                        services_to_migrate = [
                            s for s in self.service_instances.values()
                            if s.node_id == node_id
                        ]
                        
                        for service in services_to_migrate:
                            await self._migrate_service(
                                service.instance_id,
                                trigger_reason="node_failure"
                            )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Node health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _device_tracker(self) -> None:
        """Track mobile device movements and optimize services."""
        while self.running:
            try:
                current_time = datetime.now()
                
                for device_id, device in self.mobile_devices.items():
                    # Remove stale devices
                    time_since_seen = (current_time - device.last_seen).total_seconds()
                    
                    if time_since_seen > 3600:  # 1 hour
                        logger.info(f"Removing stale device: {device_id}")
                        del self.mobile_devices[device_id]
                        continue
                    
                    # Predict movement and pre-migrate services
                    if device.connected_services:
                        await self._predict_and_premigrate(device)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Device tracker error: {e}")
                await asyncio.sleep(30)
    
    async def _predict_and_premigrate(self, device -> None: MobileDevice) -> None:
        """Predict device movement and pre-migrate services."""
        # Simplified prediction based on historical handovers
        # In reality, this would use ML models and mobility patterns
        
        if device.handover_count > 5:  # Highly mobile device
            # Consider pre-migration to nearby nodes
            pass
    
    async def _trigger_scale_up(self, node_id -> None: str) -> None:
        """Trigger scale-up for overloaded node."""
        logger.info(f"Triggering scale-up for node {node_id}")
        # In reality, this would provision additional resources
    
    async def _trigger_scale_down(self, node_id -> None: str) -> None:
        """Trigger scale-down for underutilized node."""
        logger.info(f"Triggering scale-down for node {node_id}")
        # In reality, this would deallocate unused resources
    
    def get_edge_nodes(self) -> List[EdgeNode]:
        """Get list of registered edge nodes."""
        return list(self.edge_nodes.values())
    
    def get_service_instances(self) -> List[ServiceInstance]:
        """Get list of service instances."""
        return list(self.service_instances.values())
    
    def get_mobile_devices(self) -> List[MobileDevice]:
        """Get list of mobile devices."""
        return list(self.mobile_devices.values())
    
    def get_network_slices(self) -> List[NetworkSlice]:
        """Get list of network slices."""
        return list(self.network_slices.values())
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics."""
        uptime = (datetime.now() - self.orchestrator_start_time).total_seconds()
        
        return {
            "orchestrator_id": self.orchestrator_id,
            "status": "running" if self.running else "stopped",
            "uptime_seconds": uptime,
            "edge_nodes_count": len(self.edge_nodes),
            "active_services": len(self.service_instances),
            "connected_devices": len(self.mobile_devices),
            "network_slices": len(self.network_slices),
            "active_migrations": len(self.active_migrations),
            "total_services_deployed": self.total_services_deployed,
            "total_migrations_performed": self.total_migrations_performed,
            "total_handovers_handled": self.total_handovers_handled,
            "features": {
                "5g_core_integration": self.enable_5g_core_integration,
                "network_slicing": self.enable_network_slicing,
                "auto_scaling": self.enable_auto_scaling,
                "service_migration": self.enable_service_migration
            }
        }


# Utility functions
async def create_mec_orchestrator(
    orchestrator_id: str = "mec_orchestrator_1",
    enable_all_features: bool = True
) -> MECOrchestrator:
    """Create and start MEC orchestrator."""
    orchestrator = MECOrchestrator(
        orchestrator_id=orchestrator_id,
        enable_5g_core_integration=enable_all_features,
        enable_network_slicing=enable_all_features,
        enable_auto_scaling=enable_all_features,
        enable_service_migration=enable_all_features
    )
    await orchestrator.start()
    return orchestrator


async def deploy_edge_service(
    orchestrator: MECOrchestrator,
    service_type: ServiceType,
    image_name: str,
    cpu_cores: int = 1,
    memory_mb: int = 512,
    latency_requirement_ms: int = 50
) -> str:
    """Quick service deployment utility."""
    return await orchestrator.deploy_service(
        service_type=service_type,
        image_name=image_name,
        resource_requirements={
            "cpu_cores": cpu_cores,
            "memory_mb": memory_mb,
            "storage_mb": 1024
        },
        network_requirements={
            "bandwidth_mbps": 10
        },
        qos_requirements={
            "latency_ms": latency_requirement_ms,
            "reliability": 0.99
        }
    )


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        orchestrator = await create_mec_orchestrator()
        
        try:
            # Register edge nodes
            node1_id = await orchestrator.register_edge_node(
                node_type=EdgeNodeType.BASE_STATION,
                location={"latitude": 52.5200, "longitude": 13.4050},
                ip_address="192.168.1.100",
                port=8080,
                capabilities=[ServiceType.AI_INFERENCE, ServiceType.VIDEO_STREAMING],
                resources={"cpu_cores": 8, "memory_mb": 16384, "storage_mb": 102400}
            )
            
            node2_id = await orchestrator.register_edge_node(
                node_type=EdgeNodeType.REGIONAL_DATA_CENTER,
                location={"latitude": 52.5300, "longitude": 13.4150},
                ip_address="192.168.1.101",
                port=8080,
                capabilities=[ServiceType.CONTENT_DELIVERY, ServiceType.REAL_TIME_ANALYTICS],
                resources={"cpu_cores": 16, "memory_mb": 32768, "storage_mb": 204800}
            )
            
            print(f"Registered nodes: {node1_id}, {node2_id}")
            
            # Deploy services
            service1_id = await deploy_edge_service(
                orchestrator=orchestrator,
                service_type=ServiceType.AI_INFERENCE,
                image_name="ai-inference:latest",
                cpu_cores=2,
                memory_mb=2048,
                latency_requirement_ms=10
            )
            
            service2_id = await deploy_edge_service(
                orchestrator=orchestrator,
                service_type=ServiceType.VIDEO_STREAMING,
                image_name="video-streaming:latest",
                cpu_cores=4,
                memory_mb=4096,
                latency_requirement_ms=25
            )
            
            print(f"Deployed services: {service1_id}, {service2_id}")
            
            # Register mobile device
            device_registered = await orchestrator.register_mobile_device(
                device_id="device_001",
                imsi="123456789012345",
                ip_address="10.0.0.100",
                current_cell_id="cell_001",
                location={"latitude": 52.5250, "longitude": 13.4100},
                qos_profile=QoSClass.LOW_LATENCY
            )
            
            print(f"Device registered: {device_registered}")
            
            # Create network slice
            slice_id = await orchestrator.create_network_slice(
                slice_type=NetworkSliceType.ULTRA_RELIABLE_LOW_LATENCY,
                tenant_id="tenant_001",
                sla_requirements={"latency_ms": 1, "reliability": 0.9999},
                resource_allocation={"bandwidth_mbps": 100, "cpu_cores": 4}
            )
            
            print(f"Network slice created: {slice_id}")
            
            # Get status
            status = orchestrator.get_orchestrator_status()
            print(f"Orchestrator status: {status}")
            
            # Simulate some time passing
            await asyncio.sleep(5)
            
            # Simulate device handover
            handover_success = await orchestrator.handle_device_handover(
                device_id="device_001",
                new_cell_id="cell_002",
                new_location={"latitude": 52.5280, "longitude": 13.4120}
            )
            
            print(f"Handover handled: {handover_success}")
            
        finally:
            await orchestrator.stop()
    
    asyncio.run(main())