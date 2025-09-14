"""IoT Mesh Network Orchestration
===============================

Device orchestration and mesh networking capabilities for IoT devices
in edge computing environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
import time
import hashlib
import random

logger = logging.getLogger(__name__)


class DeviceType(str, Enum):
    """IoT device types."""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    EDGE_COMPUTER = "edge_computer"
    MOBILE_DEVICE = "mobile_device"
    DRONE = "drone"
    VEHICLE = "vehicle"
    WEARABLE = "wearable"
    SMART_CAMERA = "smart_camera"
    INDUSTRIAL_CONTROLLER = "industrial_controller"


class DeviceCapability(str, Enum):
    """Device capabilities."""
    COMPUTE = "compute"
    STORAGE = "storage"
    SENSING = "sensing"
    COMMUNICATION = "communication"
    POWER_MANAGEMENT = "power_management"
    MOBILITY = "mobility"
    AI_INFERENCE = "ai_inference"
    DATA_PROCESSING = "data_processing"
    EDGE_CACHING = "edge_caching"
    REAL_TIME_ANALYTICS = "real_time_analytics"


class NetworkTopology(str, Enum):
    """Mesh network topologies."""
    STAR = "star"
    TREE = "tree"
    MESH = "mesh"
    HYBRID = "hybrid"
    CLUSTER = "cluster"
    RING = "ring"


class CommunicationProtocol(str, Enum):
    """Communication protocols for mesh networking."""
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    ZIGBEE = "zigbee"
    LORA = "lora"
    CELLULAR_5G = "cellular_5g"
    ETHERNET = "ethernet"
    CAN_BUS = "can_bus"
    MQTT = "mqtt"
    COAP = "coap"
    WEBSOCKET = "websocket"


class DeviceStatus(str, Enum):
    """Device status states."""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    DISCONNECTING = "disconnecting"
    SLEEPING = "sleeping"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    """IoT device information."""
    device_id: str
    device_name: str
    device_type: DeviceType
    capabilities: List[DeviceCapability]
    protocols: List[CommunicationProtocol]
    location: Optional[Dict[str, float]]  # latitude, longitude, altitude
    hardware_specs: Dict[str, Any]
    software_version: str
    battery_level: Optional[float]  # 0.0 to 1.0
    status: DeviceStatus
    last_seen: datetime
    metadata: Dict[str, Any]


@dataclass
class MeshLink:
    """Link between devices in mesh network."""
    link_id: str
    source_device_id: str
    target_device_id: str
    protocol: CommunicationProtocol
    signal_strength: float  # 0.0 to 1.0
    latency_ms: float
    bandwidth_mbps: float
    packet_loss_rate: float
    link_quality: float  # 0.0 to 1.0
    is_active: bool
    created_at: datetime
    last_updated: datetime


@dataclass
class MeshRoute:
    """Route through mesh network."""
    route_id: str
    source_device_id: str
    destination_device_id: str
    path: List[str]  # List of device IDs in the route
    total_hops: int
    total_latency_ms: float
    total_bandwidth_mbps: float
    route_quality: float
    is_optimal: bool
    created_at: datetime


@dataclass
class IoTMeshConfig:
    """Configuration for IoT mesh network."""
    network_name: str = "ainflue-mesh"
    topology: NetworkTopology = NetworkTopology.HYBRID
    default_protocols: List[CommunicationProtocol] = None
    max_hop_count: int = 5
    route_discovery_interval_seconds: int = 300
    device_heartbeat_interval_seconds: int = 30
    link_quality_threshold: float = 0.3
    auto_healing_enabled: bool = True
    load_balancing_enabled: bool = True
    power_optimization_enabled: bool = True
    security_enabled: bool = True
    encryption_algorithm: str = "AES-256"
    authentication_required: bool = True
    
    def __post_init__(self) -> None:
        if self.default_protocols is None:
            self.default_protocols = [CommunicationProtocol.WIFI, CommunicationProtocol.BLUETOOTH]


class IoTMeshOrchestrator:
    """IoT mesh network orchestrator.
    
    Manages device discovery, mesh networking, routing, and orchestration
    for IoT devices in edge computing environments.
    """
    
    def __init__(self, config -> None: Optional[IoTMeshConfig] = None) -> None:
        self.config = config or IoTMeshConfig()
        
        # Network state
        self.devices: Dict[str, DeviceInfo] = {}
        self.mesh_links: Dict[str, MeshLink] = {}
        self.routes: Dict[str, MeshRoute] = {}
        self.device_groups: Dict[str, Set[str]] = {}  # group_name -> device_ids
        
        # Network topology
        self.adjacency_list: Dict[str, Set[str]] = {}  # device_id -> connected_device_ids
        
        # Running state
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        
        # Metrics
        self.network_metrics = {
            "total_devices": 0,
            "active_devices": 0,
            "total_links": 0,
            "active_links": 0,
            "average_hop_count": 0.0,
            "network_coverage": 0.0,
            "total_data_transferred_mb": 0.0,
            "average_latency_ms": 0.0
        }
        
        logger.info(f"IoT mesh orchestrator initialized with topology: {self.config.topology}")
    
    async def start(self) -> None:
        """Start the IoT mesh orchestrator."""
        if self.running:
            logger.warning("IoT mesh orchestrator already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.background_tasks.extend([
            asyncio.create_task(self._device_discovery()),
            asyncio.create_task(self._route_maintenance()),
            asyncio.create_task(self._network_monitoring()),
            asyncio.create_task(self._auto_healing())
        ])
        
        logger.info("IoT mesh orchestrator started")
    
    async def stop(self) -> None:
        """Stop the IoT mesh orchestrator."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.background_tasks.clear()
        
        logger.info("IoT mesh orchestrator stopped")
    
    async def register_device(
        self,
        device_name: str,
        device_type: DeviceType,
        capabilities: List[DeviceCapability],
        protocols: List[CommunicationProtocol],
        hardware_specs: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new IoT device in the mesh network."""
        device_id = str(uuid.uuid4())
        
        device_info = DeviceInfo(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            capabilities=capabilities,
            protocols=protocols,
            location=location,
            hardware_specs=hardware_specs or {},
            software_version="1.0.0",
            battery_level=None,
            status=DeviceStatus.CONNECTING,
            last_seen=datetime.now(),
            metadata=metadata or {}
        )
        
        self.devices[device_id] = device_info
        self.adjacency_list[device_id] = set()
        
        # Try to establish connections with other devices
        await self._discover_neighbors(device_id)
        
        logger.info(f"Registered device: {device_name} ({device_id})")
        return device_id
    
    async def unregister_device(self, device_id: str) -> bool:
        """Unregister a device from the mesh network."""
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not found")
            return False
        
        device_info = self.devices.pop(device_id)
        
        # Remove all links involving this device
        links_to_remove = [
            link_id for link_id, link in self.mesh_links.items()
            if link.source_device_id == device_id or link.target_device_id == device_id
        ]
        
        for link_id in links_to_remove:
            self.mesh_links.pop(link_id)
        
        # Remove from adjacency list
        if device_id in self.adjacency_list:
            neighbors = self.adjacency_list.pop(device_id)
            for neighbor_id in neighbors:
                if neighbor_id in self.adjacency_list:
                    self.adjacency_list[neighbor_id].discard(device_id)
        
        # Remove from routes
        routes_to_remove = [
            route_id for route_id, route in self.routes.items()
            if device_id in route.path
        ]
        
        for route_id in routes_to_remove:
            self.routes.pop(route_id)
        
        logger.info(f"Unregistered device: {device_info.device_name}")
        return True
    
    async def update_device_status(
        self,
        device_id: str,
        status: DeviceStatus,
        battery_level: Optional[float] = None,
        location: Optional[Dict[str, float]] = None
    ) -> bool:
        """Update device status and metadata."""
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not found")
            return False
        
        device = self.devices[device_id]
        device.status = status
        device.last_seen = datetime.now()
        
        if battery_level is not None:
            device.battery_level = battery_level
        
        if location is not None:
            device.location = location
        
        logger.debug(f"Updated device {device_id} status to {status}")
        return True
    
    async def create_device_group(
        self,
        group_name: str,
        device_ids: List[str],
        group_capabilities: Optional[List[DeviceCapability]] = None
    ) -> bool:
        """Create a logical group of devices."""
        # Validate that all devices exist
        for device_id in device_ids:
            if device_id not in self.devices:
                logger.error(f"Device {device_id} not found")
                return False
        
        self.device_groups[group_name] = set(device_ids)
        
        logger.info(f"Created device group: {group_name} with {len(device_ids)} devices")
        return True
    
    async def send_message(
        self,
        source_device_id: str,
        destination_device_id: str,
        message: Dict[str, Any],
        priority: int = 5
    ) -> bool:
        """Send a message through the mesh network."""
        if source_device_id not in self.devices:
            logger.error(f"Source device {source_device_id} not found")
            return False
        
        if destination_device_id not in self.devices:
            logger.error(f"Destination device {destination_device_id} not found")
            return False
        
        # Find or create route
        route = await self._find_optimal_route(source_device_id, destination_device_id)
        
        if not route:
            logger.error(f"No route found from {source_device_id} to {destination_device_id}")
            return False
        
        # Simulate message transmission
        logger.info(f"Sending message from {source_device_id} to {destination_device_id} via route: {' -> '.join(route.path)}")
        
        # In a real implementation, this would send the actual message
        return True
    
    async def broadcast_message(
        self,
        source_device_id: str,
        message: Dict[str, Any],
        target_group: Optional[str] = None,
        max_hops: Optional[int] = None
    ) -> int:
        """Broadcast a message to multiple devices."""
        if source_device_id not in self.devices:
            logger.error(f"Source device {source_device_id} not found")
            return 0
        
        target_devices = set()
        
        if target_group and target_group in self.device_groups:
            target_devices = self.device_groups[target_group].copy()
        else:
            target_devices = set(self.devices.keys())
        
        # Remove source device
        target_devices.discard(source_device_id)
        
        successful_sends = 0
        
        for target_device_id in target_devices:
            if await self.send_message(source_device_id, target_device_id, message):
                successful_sends += 1
        
        logger.info(f"Broadcast from {source_device_id} reached {successful_sends}/{len(target_devices)} devices")
        return successful_sends
    
    async def orchestrate_computation(
        self,
        task_definition: Dict[str, Any],
        required_capabilities: List[DeviceCapability],
        preferred_devices: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Orchestrate distributed computation across mesh devices."""
        # Find suitable devices
        suitable_devices = []
        
        for device_id, device in self.devices.items():
            if (device.status == DeviceStatus.ONLINE and
                all(cap in device.capabilities for cap in required_capabilities)):
                
                if preferred_devices is None or device_id in preferred_devices:
                    suitable_devices.append(device_id)
        
        if not suitable_devices:
            logger.error("No suitable devices found for computation task")
            return {"success": False, "error": "No suitable devices"}
        
        # Select device based on capabilities and load
        selected_device = self._select_optimal_device(suitable_devices, required_capabilities)
        
        # Simulate task execution
        logger.info(f"Orchestrating computation task on device: {selected_device}")
        
        return {
            "success": True,
            "selected_device": selected_device,
            "task_id": str(uuid.uuid4()),
            "estimated_completion_time": datetime.now() + timedelta(seconds=30)
        }
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get comprehensive network status."""
        active_devices = [d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]
        active_links = [l for l in self.mesh_links.values() if l.is_active]
        
        self.network_metrics.update({
            "total_devices": len(self.devices),
            "active_devices": len(active_devices),
            "total_links": len(self.mesh_links),
            "active_links": len(active_links),
            "average_latency_ms": sum(l.latency_ms for l in active_links) / len(active_links) if active_links else 0
        })
        
        return {
            "network_info": {
                "name": self.config.network_name,
                "topology": self.config.topology,
                "running": self.running
            },
            "metrics": self.network_metrics,
            "devices": {
                device_id: {
                    "name": device.device_name,
                    "type": device.device_type,
                    "status": device.status,
                    "battery_level": device.battery_level,
                    "capabilities": device.capabilities,
                    "last_seen": device.last_seen.isoformat()
                }
                for device_id, device in self.devices.items()
            },
            "device_groups": {
                group_name: list(device_ids)
                for group_name, device_ids in self.device_groups.items()
            },
            "topology": {
                device_id: list(neighbors)
                for device_id, neighbors in self.adjacency_list.items()
            }
        }
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific device."""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        neighbors = list(self.adjacency_list.get(device_id, set()))
        
        device_links = [
            {
                "link_id": link.link_id,
                "target": link.target_device_id if link.source_device_id == device_id else link.source_device_id,
                "protocol": link.protocol,
                "signal_strength": link.signal_strength,
                "latency_ms": link.latency_ms,
                "quality": link.link_quality
            }
            for link in self.mesh_links.values()
            if link.source_device_id == device_id or link.target_device_id == device_id
        ]
        
        return {
            "device_info": asdict(device),
            "neighbors": neighbors,
            "links": device_links,
            "neighbor_count": len(neighbors)
        }
    
    async def _discover_neighbors(self, device_id -> None: str) -> None:
        """Discover neighboring devices for a given device."""
        if device_id not in self.devices:
            return
        
        device = self.devices[device_id]
        
        # Find compatible devices within range
        for other_device_id, other_device in self.devices.items():
            if (other_device_id != device_id and
                other_device.status == DeviceStatus.ONLINE and
                self._devices_can_connect(device, other_device)):
                
                # Create mesh link
                await self._create_mesh_link(device_id, other_device_id)
    
    def _devices_can_connect(self, device1: DeviceInfo, device2: DeviceInfo) -> bool:
        """Check if two devices can establish a connection."""
        # Check for common protocols
        common_protocols = set(device1.protocols) & set(device2.protocols)
        if not common_protocols:
            return False
        
        # Check distance if location is available
        if device1.location and device2.location:
            distance = self._calculate_distance(device1.location, device2.location)
            # Assume maximum connection range of 100 meters for now
            if distance > 100:
                return False
        
        return True
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations in meters."""
        # Simplified distance calculation (should use proper geographic calculation)
        lat_diff = abs(loc1.get("latitude", 0) - loc2.get("latitude", 0))
        lon_diff = abs(loc1.get("longitude", 0) - loc2.get("longitude", 0))
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111000  # Approximate meters per degree
    
    async def _create_mesh_link(self, device1_id -> None: str, device2_id -> None: str) -> None:
        """Create a mesh link between two devices."""
        link_id = f"{device1_id}_{device2_id}"
        
        if link_id in self.mesh_links:
            return  # Link already exists
        
        # Simulate link quality measurements
        signal_strength = random.uniform(0.5, 1.0)
        latency_ms = random.uniform(1.0, 10.0)
        bandwidth_mbps = random.uniform(10.0, 100.0)
        packet_loss_rate = random.uniform(0.0, 0.05)
        link_quality = signal_strength * (1 - packet_loss_rate) * min(1.0, 50.0 / latency_ms)
        
        # Determine the best common protocol
        device1 = self.devices[device1_id]
        device2 = self.devices[device2_id]
        common_protocols = set(device1.protocols) & set(device2.protocols)
        protocol = list(common_protocols)[0] if common_protocols else CommunicationProtocol.WIFI
        
        mesh_link = MeshLink(
            link_id=link_id,
            source_device_id=device1_id,
            target_device_id=device2_id,
            protocol=protocol,
            signal_strength=signal_strength,
            latency_ms=latency_ms,
            bandwidth_mbps=bandwidth_mbps,
            packet_loss_rate=packet_loss_rate,
            link_quality=link_quality,
            is_active=link_quality >= self.config.link_quality_threshold,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.mesh_links[link_id] = mesh_link
        
        # Update adjacency list
        self.adjacency_list[device1_id].add(device2_id)
        self.adjacency_list[device2_id].add(device1_id)
        
        logger.debug(f"Created mesh link: {device1_id} <-> {device2_id} (quality: {link_quality:.2f})")
    
    async def _find_optimal_route(self, source_id: str, destination_id: str) -> Optional[MeshRoute]:
        """Find optimal route between two devices using Dijkstra's algorithm."""
        if source_id == destination_id:
            return None
        
        # Check if route already exists and is valid
        route_key = f"{source_id}_{destination_id}"
        if route_key in self.routes:
            route = self.routes[route_key]
            if self._is_route_valid(route):
                return route
        
        # Find route using Dijkstra's algorithm
        distances = {device_id: float('inf') for device_id in self.devices}
        distances[source_id] = 0
        previous = {}
        unvisited = set(self.devices.keys())
        
        while unvisited:
            # Find unvisited node with minimum distance
            current = min(unvisited, key=lambda x: distances[x])
            
            if distances[current] == float('inf'):
                break  # No path exists
            
            if current == destination_id:
                # Reconstruct path
                path = []
                node = destination_id
                while node in previous:
                    path.append(node)
                    node = previous[node]
                path.append(source_id)
                path.reverse()
                
                # Calculate route metrics
                total_latency = 0
                total_bandwidth = float('inf')
                
                for i in range(len(path) - 1):
                    link_id = f"{path[i]}_{path[i+1]}"
                    reverse_link_id = f"{path[i+1]}_{path[i]}"
                    
                    link = self.mesh_links.get(link_id) or self.mesh_links.get(reverse_link_id)
                    if link:
                        total_latency += link.latency_ms
                        total_bandwidth = min(total_bandwidth, link.bandwidth_mbps)
                
                route = MeshRoute(
                    route_id=route_key,
                    source_device_id=source_id,
                    destination_device_id=destination_id,
                    path=path,
                    total_hops=len(path) - 1,
                    total_latency_ms=total_latency,
                    total_bandwidth_mbps=total_bandwidth if total_bandwidth != float('inf') else 0,
                    route_quality=1.0 / (1.0 + total_latency / 100.0),  # Simple quality metric
                    is_optimal=True,
                    created_at=datetime.now()
                )
                
                self.routes[route_key] = route
                return route
            
            unvisited.remove(current)
            
            # Update distances to neighbors
            for neighbor_id in self.adjacency_list.get(current, set()):
                if neighbor_id in unvisited:
                    link_id = f"{current}_{neighbor_id}"
                    reverse_link_id = f"{neighbor_id}_{current}"
                    
                    link = self.mesh_links.get(link_id) or self.mesh_links.get(reverse_link_id)
                    if link and link.is_active:
                        distance = distances[current] + link.latency_ms
                        if distance < distances[neighbor_id]:
                            distances[neighbor_id] = distance
                            previous[neighbor_id] = current
        
        return None  # No route found
    
    def _is_route_valid(self, route: MeshRoute) -> bool:
        """Check if a route is still valid."""
        # Check if all devices in the route are still online
        for device_id in route.path:
            if (device_id not in self.devices or
                self.devices[device_id].status != DeviceStatus.ONLINE):
                return False
        
        # Check if all links in the route are still active
        for i in range(len(route.path) - 1):
            link_id = f"{route.path[i]}_{route.path[i+1]}"
            reverse_link_id = f"{route.path[i+1]}_{route.path[i]}"
            
            link = self.mesh_links.get(link_id) or self.mesh_links.get(reverse_link_id)
            if not link or not link.is_active:
                return False
        
        return True
    
    def _select_optimal_device(self, device_ids: List[str], required_capabilities: List[DeviceCapability]) -> str:
        """Select the optimal device for a computation task."""
        if not device_ids:
            return None
        
        # Simple selection based on battery level and device type priority
        device_scores = {}
        
        for device_id in device_ids:
            device = self.devices[device_id]
            score = 1.0
            
            # Prefer devices with more capabilities
            score *= len(device.capabilities) / 10.0
            
            # Prefer devices with higher battery level
            if device.battery_level is not None:
                score *= device.battery_level
            
            # Prefer edge computers and gateways for computation
            if device.device_type in [DeviceType.EDGE_COMPUTER, DeviceType.GATEWAY]:
                score *= 1.5
            
            device_scores[device_id] = score
        
        return max(device_scores, key=device_scores.get)
    
    async def _device_discovery(self) -> None:
        """Continuously discover new devices and update connections."""
        while self.running:
            try:
                # Periodically rediscover neighbors for all devices
                for device_id in list(self.devices.keys()):
                    if self.devices[device_id].status == DeviceStatus.ONLINE:
                        await self._discover_neighbors(device_id)
                
                await asyncio.sleep(60)  # Discovery every minute
                
            except Exception as e:
                logger.error(f"Device discovery error: {e}")
                await asyncio.sleep(60)
    
    async def _route_maintenance(self) -> None:
        """Maintain and update routes periodically."""
        while self.running:
            try:
                # Remove invalid routes
                invalid_routes = [
                    route_id for route_id, route in self.routes.items()
                    if not self._is_route_valid(route)
                ]
                
                for route_id in invalid_routes:
                    self.routes.pop(route_id)
                    logger.debug(f"Removed invalid route: {route_id}")
                
                await asyncio.sleep(self.config.route_discovery_interval_seconds)
                
            except Exception as e:
                logger.error(f"Route maintenance error: {e}")
                await asyncio.sleep(300)
    
    async def _network_monitoring(self) -> None:
        """Monitor network health and performance."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check device heartbeats
                for device_id, device in self.devices.items():
                    time_since_seen = (current_time - device.last_seen).total_seconds()
                    
                    if time_since_seen > self.config.device_heartbeat_interval_seconds * 3:
                        if device.status == DeviceStatus.ONLINE:
                            device.status = DeviceStatus.OFFLINE
                            logger.warning(f"Device {device_id} marked as offline")
                
                # Update link qualities
                for link in self.mesh_links.values():
                    # Simulate quality degradation over time
                    age_hours = (current_time - link.created_at).total_seconds() / 3600
                    quality_degradation = min(0.1, age_hours * 0.01)
                    link.link_quality = max(0.0, link.link_quality - quality_degradation)
                    
                    # Deactivate poor quality links
                    if link.link_quality < self.config.link_quality_threshold:
                        link.is_active = False
                
                await asyncio.sleep(self.config.device_heartbeat_interval_seconds)
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_healing(self) -> None:
        """Perform automatic network healing and optimization."""
        while self.running:
            try:
                if not self.config.auto_healing_enabled:
                    await asyncio.sleep(300)
                    continue
                
                # Identify isolated devices
                for device_id in self.devices:
                    if (self.devices[device_id].status == DeviceStatus.ONLINE and
                        len(self.adjacency_list.get(device_id, set())) == 0):
                        
                        logger.info(f"Attempting to reconnect isolated device: {device_id}")
                        await self._discover_neighbors(device_id)
                
                # Optimize network topology if needed
                await self._optimize_topology()
                
                await asyncio.sleep(300)  # Auto-healing every 5 minutes
                
            except Exception as e:
                logger.error(f"Auto-healing error: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_topology(self) -> None:
        """Optimize network topology for better performance."""
        # This is a placeholder for topology optimization logic
        # In a real implementation, you would analyze the current topology
        # and make improvements like adding redundant links, removing
        # bottlenecks, etc.
        pass


# Convenience function
async def create_iot_mesh_orchestrator(config: Optional[IoTMeshConfig] = None) -> IoTMeshOrchestrator:
    """Create and start an IoT mesh orchestrator."""
    orchestrator = IoTMeshOrchestrator(config)
    await orchestrator.start()
    return orchestrator


# Example usage
async def main() -> None:
    """Example usage of the IoT mesh orchestrator."""
    try:
        # Create configuration
        config = IoTMeshConfig(
            network_name="ainflue-iot-mesh",
            topology=NetworkTopology.MESH,
            auto_healing_enabled=True
        )
        
        # Create and start orchestrator
        orchestrator = await create_iot_mesh_orchestrator(config)
        
        try:
            # Register some devices
            gateway_id = await orchestrator.register_device(
                device_name="iot-gateway-1",
                device_type=DeviceType.GATEWAY,
                capabilities=[DeviceCapability.COMPUTE, DeviceCapability.COMMUNICATION, DeviceCapability.STORAGE],
                protocols=[CommunicationProtocol.WIFI, CommunicationProtocol.ETHERNET],
                hardware_specs={"cpu_cores": 4, "memory_gb": 8},
                location={"latitude": 52.5200, "longitude": 13.4050}
            )
            
            sensor_id = await orchestrator.register_device(
                device_name="temp-sensor-1",
                device_type=DeviceType.SENSOR,
                capabilities=[DeviceCapability.SENSING, DeviceCapability.COMMUNICATION],
                protocols=[CommunicationProtocol.WIFI, CommunicationProtocol.ZIGBEE],
                hardware_specs={"battery_capacity_mah": 3000},
                location={"latitude": 52.5210, "longitude": 13.4060}
            )
            
            # Update device status
            await orchestrator.update_device_status(gateway_id, DeviceStatus.ONLINE)
            await orchestrator.update_device_status(sensor_id, DeviceStatus.ONLINE, battery_level=0.85)
            
            # Create device group
            await orchestrator.create_device_group("sensors", [sensor_id])
            
            # Send a message
            message = {"type": "sensor_reading", "temperature": 23.5, "timestamp": datetime.now().isoformat()}
            await orchestrator.send_message(sensor_id, gateway_id, message)
            
            # Get network status
            status = orchestrator.get_network_status()
            print("IoT Mesh Network Status:")
            print(json.dumps(status, indent=2, default=str))
            
        finally:
            await orchestrator.stop()
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())