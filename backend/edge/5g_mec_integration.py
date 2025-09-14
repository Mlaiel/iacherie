"""5G MEC Integration Layer
=========================

Integration layer for 5G Multi-access Edge Computing that extends
the existing MEC orchestrator with enhanced integration capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
import time

# Import from the existing 5G MEC module
import importlib
_mec_module = importlib.import_module('backend.edge.5g_mec')
MECOrchestrator = _mec_module.MECOrchestrator
EdgeNode = _mec_module.EdgeNode
ServiceType = _mec_module.ServiceType
EdgeNodeType = _mec_module.EdgeNodeType
ServiceInstance = _mec_module.ServiceInstance

logger = logging.getLogger(__name__)


class IntegrationProtocol(str, Enum):
    """5G MEC integration protocols."""
    REST_API = "rest_api"
    GRPC = "grpc"
    MQTT = "mqtt"
    WEBSOCKET = "websocket"
    KAFKA = "kafka"
    AMQP = "amqp"


class NetworkFunction(str, Enum):
    """5G network functions."""
    AMF = "amf"  # Access and Mobility Management Function
    SMF = "smf"  # Session Management Function
    UPF = "upf"  # User Plane Function
    PCF = "pcf"  # Policy Control Function
    UDM = "udm"  # Unified Data Management
    NRF = "nrf"  # Network Repository Function
    NSSF = "nssf"  # Network Slice Selection Function


class SliceProfile(str, Enum):
    """5G network slice profiles."""
    EMBB = "enhanced_mobile_broadband"
    URLLC = "ultra_reliable_low_latency"
    MMTC = "massive_machine_type_communications"
    V2X = "vehicle_to_everything"
    INDUSTRIAL_IOT = "industrial_iot"
    AR_VR = "augmented_virtual_reality"


@dataclass
class MECIntegrationConfig:
    """Configuration for 5G MEC integration."""
    integration_protocol: IntegrationProtocol = IntegrationProtocol.REST_API
    mec_platform_endpoint: str = "http://localhost:8080"
    network_slice_support: bool = True
    qos_management_enabled: bool = True
    service_migration_enabled: bool = True
    load_balancing_enabled: bool = True
    auto_scaling_enabled: bool = True
    monitoring_interval_seconds: int = 30
    health_check_timeout_seconds: int = 10
    max_retry_attempts: int = 3
    enable_edge_caching: bool = True
    enable_traffic_steering: bool = True


@dataclass
class NetworkSliceConfig:
    """5G network slice configuration."""
    slice_id: str
    slice_profile: SliceProfile
    sst: int  # Slice/Service Type
    sd: str   # Slice Differentiator
    latency_requirement_ms: int
    bandwidth_requirement_mbps: int
    reliability_requirement: float  # 0.0 to 1.0
    mobility_support: bool = True
    coverage_area: Optional[Dict[str, Any]] = None


@dataclass
class MECServiceRegistration:
    """MEC service registration information."""
    service_id: str
    service_name: str
    service_type: ServiceType
    version: str
    endpoint: str
    capabilities: List[str]
    resource_requirements: Dict[str, Any]
    qos_requirements: Dict[str, Any]
    network_functions: List[NetworkFunction]
    supported_slices: List[str]
    registration_time: datetime


class MECIntegrationLayer:
    """5G MEC integration layer.
    
    Provides enhanced integration capabilities for 5G MEC environments,
    including network slice management, QoS control, and service orchestration.
    """
    
    def __init__(self, config -> None: Optional[MECIntegrationConfig] = None) -> None:
        self.config = config or MECIntegrationConfig()
        
        # Initialize the base MEC orchestrator
        self.mec_orchestrator = MECOrchestrator(
            orchestrator_id=f"mec-integration-{uuid.uuid4().hex[:8]}",
            management_ip="0.0.0.0",
            management_port=8080
        )
        
        # Integration state
        self.running = False
        self.registered_services: Dict[str, MECServiceRegistration] = {}
        self.network_slices: Dict[str, NetworkSliceConfig] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.background_tasks: List[asyncio.Task] = []
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "service_registered": [],
            "service_unregistered": [],
            "slice_created": [],
            "slice_deleted": [],
            "qos_violation": [],
            "migration_started": [],
            "migration_completed": []
        }
        
        logger.info(f"MEC integration layer initialized with protocol: {self.config.integration_protocol}")
    
    async def start(self) -> None:
        """Start the MEC integration layer."""
        if self.running:
            logger.warning("MEC integration layer already running")
            return
        
        self.running = True
        
        # Start the base MEC orchestrator
        await self.mec_orchestrator.start()
        
        # Start background monitoring
        self.background_tasks.append(
            asyncio.create_task(self._integration_monitor())
        )
        
        if self.config.qos_management_enabled:
            self.background_tasks.append(
                asyncio.create_task(self._qos_monitor())
            )
        
        if self.config.service_migration_enabled:
            self.background_tasks.append(
                asyncio.create_task(self._migration_manager())
            )
        
        logger.info("MEC integration layer started")
    
    async def stop(self) -> None:
        """Stop the MEC integration layer."""
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
        
        # Stop the MEC orchestrator
        await self.mec_orchestrator.stop()
        
        logger.info("MEC integration layer stopped")
    
    async def register_mec_service(
        self,
        service_name: str,
        service_type: ServiceType,
        endpoint: str,
        capabilities: List[str],
        resource_requirements: Optional[Dict[str, Any]] = None,
        qos_requirements: Optional[Dict[str, Any]] = None,
        network_functions: Optional[List[NetworkFunction]] = None,
        supported_slices: Optional[List[str]] = None
    ) -> str:
        """Register a MEC service with the integration layer."""
        service_id = str(uuid.uuid4())
        
        registration = MECServiceRegistration(
            service_id=service_id,
            service_name=service_name,
            service_type=service_type,
            version="1.0.0",
            endpoint=endpoint,
            capabilities=capabilities or [],
            resource_requirements=resource_requirements or {},
            qos_requirements=qos_requirements or {},
            network_functions=network_functions or [],
            supported_slices=supported_slices or [],
            registration_time=datetime.now()
        )
        
        self.registered_services[service_id] = registration
        
        # Trigger event
        await self._trigger_event("service_registered", {
            "service_id": service_id,
            "registration": registration
        })
        
        logger.info(f"Registered MEC service: {service_name} (ID: {service_id})")
        return service_id
    
    async def unregister_mec_service(self, service_id: str) -> bool:
        """Unregister a MEC service."""
        if service_id not in self.registered_services:
            logger.warning(f"Service {service_id} not found for unregistration")
            return False
        
        registration = self.registered_services.pop(service_id)
        
        # Trigger event
        await self._trigger_event("service_unregistered", {
            "service_id": service_id,
            "registration": registration
        })
        
        logger.info(f"Unregistered MEC service: {registration.service_name}")
        return True
    
    async def create_network_slice(
        self,
        slice_profile: SliceProfile,
        latency_requirement_ms: int,
        bandwidth_requirement_mbps: int,
        reliability_requirement: float,
        sst: Optional[int] = None,
        sd: Optional[str] = None
    ) -> str:
        """Create a 5G network slice."""
        slice_id = str(uuid.uuid4())
        
        # Generate default SST and SD if not provided
        if sst is None:
            sst = self._get_default_sst(slice_profile)
        if sd is None:
            sd = slice_id[:6]  # Use first 6 chars of UUID
        
        slice_config = NetworkSliceConfig(
            slice_id=slice_id,
            slice_profile=slice_profile,
            sst=sst,
            sd=sd,
            latency_requirement_ms=latency_requirement_ms,
            bandwidth_requirement_mbps=bandwidth_requirement_mbps,
            reliability_requirement=reliability_requirement
        )
        
        self.network_slices[slice_id] = slice_config
        
        # Trigger event
        await self._trigger_event("slice_created", {
            "slice_id": slice_id,
            "config": slice_config
        })
        
        logger.info(f"Created network slice: {slice_profile} (ID: {slice_id})")
        return slice_id
    
    async def delete_network_slice(self, slice_id: str) -> bool:
        """Delete a network slice."""
        if slice_id not in self.network_slices:
            logger.warning(f"Network slice {slice_id} not found")
            return False
        
        slice_config = self.network_slices.pop(slice_id)
        
        # Trigger event
        await self._trigger_event("slice_deleted", {
            "slice_id": slice_id,
            "config": slice_config
        })
        
        logger.info(f"Deleted network slice: {slice_id}")
        return True
    
    async def deploy_service_to_slice(
        self,
        service_id: str,
        slice_id: str,
        target_node_id: Optional[str] = None
    ) -> str:
        """Deploy a registered service to a specific network slice."""
        if service_id not in self.registered_services:
            raise ValueError(f"Service {service_id} not registered")
        
        if slice_id not in self.network_slices:
            raise ValueError(f"Network slice {slice_id} not found")
        
        service_reg = self.registered_services[service_id]
        slice_config = self.network_slices[slice_id]
        
        # Use the underlying MEC orchestrator to deploy the service
        deployment_id = await self.mec_orchestrator.deploy_service(
            service_type=service_reg.service_type,
            image_name=f"{service_reg.service_name}:latest",
            resource_requirements=service_reg.resource_requirements,
            qos_requirements=service_reg.qos_requirements,
            target_node_id=target_node_id
        )
        
        logger.info(f"Deployed service {service_id} to slice {slice_id}")
        return deployment_id
    
    async def setup_qos_flow(
        self,
        session_id: str,
        slice_id: str,
        qos_profile: Dict[str, Any]
    ) -> bool:
        """Setup QoS flow for a session."""
        if slice_id not in self.network_slices:
            logger.error(f"Network slice {slice_id} not found")
            return False
        
        # Store session information
        self.active_sessions[session_id] = {
            "slice_id": slice_id,
            "qos_profile": qos_profile,
            "created_at": datetime.now(),
            "status": "active"
        }
        
        logger.info(f"Setup QoS flow for session {session_id} on slice {slice_id}")
        return True
    
    async def trigger_service_migration(
        self,
        service_instance_id: str,
        target_node_id: str,
        migration_reason: str = "optimization"
    ) -> str:
        """Trigger service migration between edge nodes."""
        # Trigger event
        await self._trigger_event("migration_started", {
            "service_instance_id": service_instance_id,
            "target_node_id": target_node_id,
            "reason": migration_reason
        })
        
        # Use the underlying MEC orchestrator for migration
        migration_id = await self.mec_orchestrator.migrate_service(
            service_instance_id=service_instance_id,
            target_node_id=target_node_id,
            migration_reason=migration_reason
        )
        
        logger.info(f"Triggered service migration: {migration_id}")
        return migration_id
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status."""
        return {
            "integration_layer": {
                "running": self.running,
                "protocol": self.config.integration_protocol,
                "platform_endpoint": self.config.mec_platform_endpoint,
                "registered_services": len(self.registered_services),
                "network_slices": len(self.network_slices),
                "active_sessions": len(self.active_sessions),
                "background_tasks": len(self.background_tasks)
            },
            "services": {
                service_id: {
                    "name": reg.service_name,
                    "type": reg.service_type,
                    "endpoint": reg.endpoint,
                    "registration_time": reg.registration_time.isoformat()
                }
                for service_id, reg in self.registered_services.items()
            },
            "network_slices": {
                slice_id: {
                    "profile": config.slice_profile,
                    "sst": config.sst,
                    "sd": config.sd,
                    "latency_ms": config.latency_requirement_ms,
                    "bandwidth_mbps": config.bandwidth_requirement_mbps
                }
                for slice_id, config in self.network_slices.items()
            },
            "mec_orchestrator": self.mec_orchestrator.get_orchestrator_status() if hasattr(self.mec_orchestrator, 'get_orchestrator_status') else {}
        }
    
    def add_event_handler(self, event_type -> None: str, handler -> None: Callable) -> None:
        """Add an event handler."""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def _get_default_sst(self, slice_profile: SliceProfile) -> int:
        """Get default SST for slice profile."""
        sst_mapping = {
            SliceProfile.EMBB: 1,
            SliceProfile.URLLC: 2,
            SliceProfile.MMTC: 3,
            SliceProfile.V2X: 4,
            SliceProfile.INDUSTRIAL_IOT: 5,
            SliceProfile.AR_VR: 6
        }
        return sst_mapping.get(slice_profile, 1)
    
    async def _trigger_event(self, event_type -> None: str, event_data -> None: Dict[str, Any]) -> None:
        """Trigger event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")
    
    async def _integration_monitor(self) -> None:
        """Monitor integration health and status."""
        while self.running:
            try:
                # Perform health checks on registered services
                for service_id, registration in self.registered_services.items():
                    # This is a placeholder for service health checking
                    # In a real implementation, you would ping the service endpoint
                    pass
                
                await asyncio.sleep(self.config.monitoring_interval_seconds)
                
            except Exception as e:
                logger.error(f"Integration monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _qos_monitor(self) -> None:
        """Monitor QoS and trigger violations."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check active sessions for QoS violations
                for session_id, session_info in self.active_sessions.items():
                    slice_id = session_info["slice_id"]
                    if slice_id in self.network_slices:
                        slice_config = self.network_slices[slice_id]
                        
                        # This is a placeholder for QoS monitoring logic
                        # In a real implementation, you would check actual metrics
                        
                        # Simulate QoS violation detection
                        # if qos_violation_detected:
                        #     await self._trigger_event("qos_violation", {
                        #         "session_id": session_id,
                        #         "slice_id": slice_id,
                        #         "violation_type": "latency"
                        #     })
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"QoS monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _migration_manager(self) -> None:
        """Manage service migrations."""
        while self.running:
            try:
                # This is a placeholder for migration management logic
                # In a real implementation, you would:
                # - Monitor service performance
                # - Detect when migration is needed
                # - Trigger automatic migrations
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Migration manager error: {e}")
                await asyncio.sleep(60)


# Convenience functions
async def create_mec_integration_layer(
    config: Optional[MECIntegrationConfig] = None
) -> MECIntegrationLayer:
    """Create and start a MEC integration layer."""
    integration_layer = MECIntegrationLayer(config)
    await integration_layer.start()
    return integration_layer


# Example usage
async def main() -> None:
    """Example usage of the MEC integration layer."""
    try:
        # Create configuration
        config = MECIntegrationConfig(
            integration_protocol=IntegrationProtocol.REST_API,
            qos_management_enabled=True,
            service_migration_enabled=True
        )
        
        # Create and start integration layer
        integration = await create_mec_integration_layer(config)
        
        try:
            # Register a service
            service_id = await integration.register_mec_service(
                service_name="ai-inference-service",
                service_type=ServiceType.AI_INFERENCE,
                endpoint="http://localhost:8081",
                capabilities=["image_classification", "object_detection"],
                qos_requirements={"latency_ms": 50, "throughput_rps": 100}
            )
            print(f"Registered service: {service_id}")
            
            # Create a network slice
            slice_id = await integration.create_network_slice(
                slice_profile=SliceProfile.URLLC,
                latency_requirement_ms=10,
                bandwidth_requirement_mbps=100,
                reliability_requirement=0.99999
            )
            print(f"Created network slice: {slice_id}")
            
            # Get status
            status = integration.get_integration_status()
            print("MEC Integration Status:")
            print(json.dumps(status, indent=2, default=str))
            
        finally:
            await integration.stop()
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())