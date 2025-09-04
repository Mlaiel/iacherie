"""Test suite for edge computing layer components.

Tests for edge inference, 5G MEC integration, IoT mesh networking,
and fog computing orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import pytest_asyncio
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import the edge computing components
from backend.edge import (
    EdgeInferenceOrchestrator,
    EdgeOptimizationStrategy,
    EdgeInferenceConfig,
    MECIntegrationLayer,
    MECIntegrationConfig,
    SliceProfile,
    IoTMeshOrchestrator,
    IoTMeshConfig,
    DeviceType,
    DeviceCapability,
    CommunicationProtocol,
    FogComputingOrchestrator,
    FogComputingConfig,
    ProcessingTier,
    WorkloadType,
    ResourceType,
    TaskPriority
)


class TestEdgeInferenceOrchestrator:
    """Test suite for EdgeInferenceOrchestrator."""
    
    @pytest_asyncio.fixture
    async def orchestrator(self):
        """Create and start an edge inference orchestrator for testing."""
        config = EdgeInferenceConfig(
            max_concurrent_requests=2,
            request_timeout_seconds=5,
            metrics_collection_enabled=True
        )
        orchestrator = EdgeInferenceOrchestrator(config)
        await orchestrator.start()
        yield orchestrator
        await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_orchestrator_lifecycle(self):
        """Test orchestrator start and stop lifecycle."""
        config = EdgeInferenceConfig()
        orchestrator = EdgeInferenceOrchestrator(config)
        
        assert not orchestrator.running
        
        await orchestrator.start()
        assert orchestrator.running
        
        await orchestrator.stop()
        assert not orchestrator.running
    
    @pytest.mark.asyncio
    async def test_optimization_strategies(self, orchestrator):
        """Test different optimization strategies."""
        # Test latency optimization
        params = orchestrator._apply_optimization_strategy("test_model", "test_data")
        assert isinstance(params, dict)
        
        # Test different strategies
        orchestrator.config.optimization_strategy = EdgeOptimizationStrategy.LATENCY_OPTIMIZED
        latency_params = orchestrator._apply_optimization_strategy("test_model", "test_data")
        
        orchestrator.config.optimization_strategy = EdgeOptimizationStrategy.ENERGY_EFFICIENT
        energy_params = orchestrator._apply_optimization_strategy("test_model", "test_data")
        
        # Params should be different for different strategies
        assert latency_params != energy_params
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, orchestrator):
        """Test metrics collection and updates."""
        initial_metrics = orchestrator.get_metrics()
        assert initial_metrics.total_requests == 0
        
        # Simulate request metrics update
        orchestrator._update_request_metrics(50.0, success=True)
        
        updated_metrics = orchestrator.get_metrics()
        assert updated_metrics.total_requests == 1
        assert updated_metrics.successful_requests == 1
        assert updated_metrics.average_latency_ms == 50.0
    
    @pytest.mark.asyncio
    async def test_engine_status(self, orchestrator):
        """Test getting engine status."""
        status = orchestrator.get_engine_status()
        
        assert "edge_orchestrator" in status
        assert status["edge_orchestrator"]["running"] is True
        assert "optimization_strategy" in status["edge_orchestrator"]
        assert "metrics" in status["edge_orchestrator"]


class TestMECIntegrationLayer:
    """Test suite for MECIntegrationLayer."""
    
    @pytest_asyncio.fixture
    async def integration_layer(self):
        """Create and start a MEC integration layer for testing."""
        config = MECIntegrationConfig(
            mec_platform_endpoint="http://localhost:8080",
            monitoring_interval_seconds=1
        )
        layer = MECIntegrationLayer(config)
        await layer.start()
        yield layer
        await layer.stop()
    
    @pytest.mark.asyncio
    async def test_integration_layer_lifecycle(self):
        """Test integration layer start and stop lifecycle."""
        config = MECIntegrationConfig()
        layer = MECIntegrationLayer(config)
        
        assert not layer.running
        
        await layer.start()
        assert layer.running
        
        await layer.stop()
        assert not layer.running
    
    @pytest.mark.asyncio
    async def test_service_registration(self, integration_layer):
        """Test MEC service registration and unregistration."""
        from backend.edge import ServiceType
        
        # Register a service
        service_id = await integration_layer.register_mec_service(
            service_name="test-ai-service",
            service_type=ServiceType.AI_INFERENCE,
            endpoint="http://localhost:8081",
            capabilities=["image_classification"],
            qos_requirements={"latency_ms": 50}
        )
        
        assert service_id in integration_layer.registered_services
        assert len(integration_layer.registered_services) == 1
        
        # Unregister the service
        success = await integration_layer.unregister_mec_service(service_id)
        assert success is True
        assert len(integration_layer.registered_services) == 0
    
    @pytest.mark.asyncio
    async def test_network_slice_management(self, integration_layer):
        """Test network slice creation and deletion."""
        # Create a network slice
        slice_id = await integration_layer.create_network_slice(
            slice_profile=SliceProfile.URLLC,
            latency_requirement_ms=10,
            bandwidth_requirement_mbps=100,
            reliability_requirement=0.99999
        )
        
        assert slice_id in integration_layer.network_slices
        assert len(integration_layer.network_slices) == 1
        
        # Delete the network slice
        success = await integration_layer.delete_network_slice(slice_id)
        assert success is True
        assert len(integration_layer.network_slices) == 0
    
    @pytest.mark.asyncio
    async def test_qos_flow_setup(self, integration_layer):
        """Test QoS flow setup."""
        # Create a network slice first
        slice_id = await integration_layer.create_network_slice(
            slice_profile=SliceProfile.EMBB,
            latency_requirement_ms=50,
            bandwidth_requirement_mbps=50,
            reliability_requirement=0.99
        )
        
        # Setup QoS flow
        session_id = "test-session-123"
        qos_profile = {"latency_ms": 30, "bandwidth_mbps": 20}
        
        success = await integration_layer.setup_qos_flow(session_id, slice_id, qos_profile)
        assert success is True
        assert session_id in integration_layer.active_sessions
    
    @pytest.mark.asyncio
    async def test_integration_status(self, integration_layer):
        """Test getting integration status."""
        status = integration_layer.get_integration_status()
        
        assert "integration_layer" in status
        assert "services" in status
        assert "network_slices" in status
        assert status["integration_layer"]["running"] is True


class TestIoTMeshOrchestrator:
    """Test suite for IoTMeshOrchestrator."""
    
    @pytest_asyncio.fixture
    async def mesh_orchestrator(self):
        """Create and start an IoT mesh orchestrator for testing."""
        config = IoTMeshConfig(
            network_name="test-mesh",
            device_heartbeat_interval_seconds=1,
            auto_healing_enabled=False  # Disable for testing
        )
        orchestrator = IoTMeshOrchestrator(config)
        await orchestrator.start()
        yield orchestrator
        await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_orchestrator_lifecycle(self):
        """Test orchestrator start and stop lifecycle."""
        config = IoTMeshConfig()
        orchestrator = IoTMeshOrchestrator(config)
        
        assert not orchestrator.running
        
        await orchestrator.start()
        assert orchestrator.running
        
        await orchestrator.stop()
        assert not orchestrator.running
    
    @pytest.mark.asyncio
    async def test_device_registration(self, mesh_orchestrator):
        """Test device registration and unregistration."""
        # Register a device
        device_id = await mesh_orchestrator.register_device(
            device_name="test-sensor",
            device_type=DeviceType.SENSOR,
            capabilities=[DeviceCapability.SENSING, DeviceCapability.COMMUNICATION],
            protocols=[CommunicationProtocol.WIFI],
            location={"latitude": 52.5200, "longitude": 13.4050}
        )
        
        assert device_id in mesh_orchestrator.devices
        assert len(mesh_orchestrator.devices) == 1
        
        # Unregister the device
        success = await mesh_orchestrator.unregister_device(device_id)
        assert success is True
        assert len(mesh_orchestrator.devices) == 0
    
    @pytest.mark.asyncio
    async def test_device_status_updates(self, mesh_orchestrator):
        """Test device status updates."""
        from backend.edge.iot_mesh_network import DeviceStatus
        
        # Register a device
        device_id = await mesh_orchestrator.register_device(
            device_name="test-device",
            device_type=DeviceType.GATEWAY,
            capabilities=[DeviceCapability.COMPUTE],
            protocols=[CommunicationProtocol.WIFI]
        )
        
        # Update device status
        success = await mesh_orchestrator.update_device_status(
            device_id=device_id,
            status=DeviceStatus.ONLINE,
            battery_level=0.85
        )
        
        assert success is True
        device = mesh_orchestrator.devices[device_id]
        assert device.status == DeviceStatus.ONLINE
        assert device.battery_level == 0.85
    
    @pytest.mark.asyncio
    async def test_device_groups(self, mesh_orchestrator):
        """Test device group creation and management."""
        # Register devices
        sensor_id = await mesh_orchestrator.register_device(
            device_name="sensor-1",
            device_type=DeviceType.SENSOR,
            capabilities=[DeviceCapability.SENSING],
            protocols=[CommunicationProtocol.ZIGBEE]
        )
        
        gateway_id = await mesh_orchestrator.register_device(
            device_name="gateway-1",
            device_type=DeviceType.GATEWAY,
            capabilities=[DeviceCapability.COMPUTE],
            protocols=[CommunicationProtocol.WIFI]
        )
        
        # Create device group
        success = await mesh_orchestrator.create_device_group(
            group_name="sensors",
            device_ids=[sensor_id]
        )
        
        assert success is True
        assert "sensors" in mesh_orchestrator.device_groups
        assert sensor_id in mesh_orchestrator.device_groups["sensors"]
    
    @pytest.mark.asyncio
    async def test_network_status(self, mesh_orchestrator):
        """Test getting network status."""
        status = mesh_orchestrator.get_network_status()
        
        assert "network_info" in status
        assert "metrics" in status
        assert "devices" in status
        assert status["network_info"]["running"] is True


class TestFogComputingOrchestrator:
    """Test suite for FogComputingOrchestrator."""
    
    @pytest_asyncio.fixture
    async def fog_orchestrator(self):
        """Create and start a fog computing orchestrator for testing."""
        config = FogComputingConfig(
            orchestrator_name="test-fog",
            task_timeout_seconds=10,
            heartbeat_interval_seconds=1
        )
        orchestrator = FogComputingOrchestrator(config)
        await orchestrator.start()
        yield orchestrator
        await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_orchestrator_lifecycle(self):
        """Test orchestrator start and stop lifecycle."""
        config = FogComputingConfig()
        orchestrator = FogComputingOrchestrator(config)
        
        assert not orchestrator.running
        
        await orchestrator.start()
        assert orchestrator.running
        
        await orchestrator.stop()
        assert not orchestrator.running
    
    @pytest.mark.asyncio
    async def test_fog_node_registration(self, fog_orchestrator):
        """Test fog node registration and unregistration."""
        # Register a fog node
        node_id = await fog_orchestrator.register_fog_node(
            node_name="test-edge-server",
            tier=ProcessingTier.FOG_TIER,
            capabilities=["ai_inference", "data_processing"],
            resources={
                ResourceType.CPU: 8.0,
                ResourceType.MEMORY: 16384.0,
                ResourceType.STORAGE: 500000.0
            }
        )
        
        assert node_id in fog_orchestrator.fog_nodes
        assert len(fog_orchestrator.fog_nodes) == 1
        
        # Unregister the node
        success = await fog_orchestrator.unregister_fog_node(node_id)
        assert success is True
        assert len(fog_orchestrator.fog_nodes) == 0
    
    @pytest.mark.asyncio
    async def test_task_submission(self, fog_orchestrator):
        """Test task submission and status tracking."""
        # Register a fog node first
        node_id = await fog_orchestrator.register_fog_node(
            node_name="test-node",
            tier=ProcessingTier.FOG_TIER,
            capabilities=["data_processing"],
            resources={ResourceType.CPU: 4.0, ResourceType.MEMORY: 8192.0}
        )
        
        # Define a simple processing function
        def simple_task(data):
            return f"Processed: {data}"
        
        # Submit a task
        task_id = await fog_orchestrator.submit_task(
            task_name="test-processing-task",
            workload_type=WorkloadType.BATCH_PROCESSING,
            processing_function=simple_task,
            input_data="test_data",
            priority=TaskPriority.NORMAL,
            estimated_duration_seconds=5.0
        )
        
        assert task_id in fog_orchestrator.pending_tasks
        
        # Wait a bit for task processing
        await asyncio.sleep(2)
        
        # Check task status
        status = await fog_orchestrator.get_task_status(task_id)
        assert status is not None
        assert status["task_id"] == task_id
    
    @pytest.mark.asyncio
    async def test_node_status(self, fog_orchestrator):
        """Test getting node status."""
        # Register a fog node
        node_id = await fog_orchestrator.register_fog_node(
            node_name="status-test-node",
            tier=ProcessingTier.CLOUD_TIER,
            capabilities=["machine_learning"],
            resources={ResourceType.CPU: 16.0, ResourceType.MEMORY: 32768.0}
        )
        
        # Get node status
        status = await fog_orchestrator.get_node_status(node_id)
        
        assert status is not None
        assert "node_info" in status
        assert "running_tasks" in status
        assert "resource_utilization" in status
    
    @pytest.mark.asyncio
    async def test_orchestrator_status(self, fog_orchestrator):
        """Test getting orchestrator status."""
        status = fog_orchestrator.get_orchestrator_status()
        
        assert "orchestrator_info" in status
        assert "metrics" in status
        assert "task_counts" in status
        assert "node_summary" in status
        assert status["orchestrator_info"]["running"] is True


# Integration tests
class TestEdgeIntegration:
    """Integration tests for edge computing components."""
    
    @pytest.mark.asyncio
    async def test_edge_inference_with_fog_computing(self):
        """Test integration between edge inference and fog computing."""
        # Create minimal configs for testing
        edge_config = EdgeInferenceConfig(
            max_concurrent_requests=1,
            metrics_collection_enabled=False,
            resource_monitoring_enabled=False
        )
        
        fog_config = FogComputingConfig(
            orchestrator_name="integration-test",
            heartbeat_interval_seconds=60  # Disable frequent checks
        )
        
        # Start both orchestrators
        edge_orchestrator = EdgeInferenceOrchestrator(edge_config)
        fog_orchestrator = FogComputingOrchestrator(fog_config)
        
        await edge_orchestrator.start()
        await fog_orchestrator.start()
        
        try:
            # Test that both are running
            assert edge_orchestrator.running
            assert fog_orchestrator.running
            
            # Test getting status from both
            edge_status = edge_orchestrator.get_engine_status()
            fog_status = fog_orchestrator.get_orchestrator_status()
            
            assert edge_status["edge_orchestrator"]["running"]
            assert fog_status["orchestrator_info"]["running"]
            
        finally:
            await edge_orchestrator.stop()
            await fog_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_mec_with_iot_mesh(self):
        """Test integration between MEC and IoT mesh networking."""
        mec_config = MECIntegrationConfig(
            monitoring_interval_seconds=60,  # Disable frequent checks
            qos_management_enabled=False
        )
        
        iot_config = IoTMeshConfig(
            device_heartbeat_interval_seconds=60,  # Disable frequent checks
            auto_healing_enabled=False
        )
        
        # Start both systems
        mec_layer = MECIntegrationLayer(mec_config)
        iot_orchestrator = IoTMeshOrchestrator(iot_config)
        
        await mec_layer.start()
        await iot_orchestrator.start()
        
        try:
            # Test that both are running
            assert mec_layer.running
            assert iot_orchestrator.running
            
            # Test cross-component functionality
            # Register a device in IoT mesh
            device_id = await iot_orchestrator.register_device(
                device_name="mec-enabled-device",
                device_type=DeviceType.EDGE_COMPUTER,
                capabilities=[DeviceCapability.AI_INFERENCE],
                protocols=[CommunicationProtocol.CELLULAR_5G]
            )
            
            # Register a service in MEC
            from backend.edge import ServiceType
            service_id = await mec_layer.register_mec_service(
                service_name="iot-data-processor",
                service_type=ServiceType.IOT_PROCESSING,
                endpoint="http://localhost:8082",
                capabilities=["data_aggregation"]
            )
            
            assert device_id in iot_orchestrator.devices
            assert service_id in mec_layer.registered_services
            
        finally:
            await mec_layer.stop()
            await iot_orchestrator.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])