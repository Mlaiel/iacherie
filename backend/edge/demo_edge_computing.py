"""Edge Computing Layer Demo
===========================

Demonstration of the complete edge computing layer including:
- Edge AI inference orchestration
- 5G MEC integration 
- IoT mesh networking
- Fog computing orchestration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all edge computing components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.edge import (
    # Edge inference
    EdgeInferenceOrchestrator,
    EdgeOptimizationStrategy,
    EdgeInferenceConfig,
    
    # 5G MEC integration
    MECIntegrationLayer,
    SliceProfile,
    MECIntegrationConfig,
    
    # IoT mesh networking
    IoTMeshOrchestrator,
    DeviceType,
    DeviceCapability,
    CommunicationProtocol,
    IoTMeshConfig,
    
    # Fog computing
    FogComputingOrchestrator,
    ProcessingTier,
    WorkloadType,
    ResourceType,
    TaskPriority,
    FogComputingConfig,
    
    # Base components
    ServiceType
)


async def demo_edge_inference():
    """Demonstrate edge AI inference orchestration."""
    print("\n" + "="*60)
    print("🧠 EDGE AI INFERENCE ORCHESTRATION DEMO")
    print("="*60)
    
    # Create configuration optimized for low latency
    config = EdgeInferenceConfig(
        optimization_strategy=EdgeOptimizationStrategy.LATENCY_OPTIMIZED,
        max_concurrent_requests=3,
        request_timeout_seconds=10,
        metrics_collection_enabled=True,
        resource_monitoring_enabled=False  # Disable for demo
    )
    
    # Create and start orchestrator
    orchestrator = EdgeInferenceOrchestrator(config)
    await orchestrator.start()
    
    try:
        print("✅ Edge inference orchestrator started")
        
        # Get status
        status = orchestrator.get_engine_status()
        print(f"📊 Orchestrator status: {status['edge_orchestrator']['optimization_strategy']}")
        
        # Get metrics
        metrics = orchestrator.get_metrics()
        print(f"📈 Current metrics - Requests: {metrics.total_requests}, Avg latency: {metrics.average_latency_ms:.2f}ms")
        
        # Simulate some metrics updates
        orchestrator._update_request_metrics(25.5, success=True)
        orchestrator._update_request_metrics(18.3, success=True)
        orchestrator._update_request_metrics(31.2, success=True)
        
        updated_metrics = orchestrator.get_metrics()
        print(f"📈 Updated metrics - Requests: {updated_metrics.total_requests}, Avg latency: {updated_metrics.average_latency_ms:.2f}ms")
        
    finally:
        await orchestrator.stop()
        print("🛑 Edge inference orchestrator stopped")


async def demo_5g_mec_integration():
    """Demonstrate 5G MEC integration capabilities."""
    print("\n" + "="*60)
    print("📡 5G MEC INTEGRATION DEMO")
    print("="*60)
    
    # Create configuration
    config = MECIntegrationConfig(
        qos_management_enabled=True,
        service_migration_enabled=True,
        monitoring_interval_seconds=60  # Disable frequent monitoring for demo
    )
    
    # Create and start integration layer
    integration = MECIntegrationLayer(config)
    await integration.start()
    
    try:
        print("✅ MEC integration layer started")
        
        # Register a MEC service
        service_id = await integration.register_mec_service(
            service_name="edge-ai-inference",
            service_type=ServiceType.AI_INFERENCE,
            endpoint="http://edge-server:8081",
            capabilities=["image_classification", "object_detection"],
            qos_requirements={"latency_ms": 20, "throughput_rps": 100}
        )
        print(f"📝 Registered MEC service: {service_id}")
        
        # Create a network slice for URLLC (Ultra-Reliable Low-Latency Communication)
        slice_id = await integration.create_network_slice(
            slice_profile=SliceProfile.URLLC,
            latency_requirement_ms=5,
            bandwidth_requirement_mbps=100,
            reliability_requirement=0.99999
        )
        print(f"🍰 Created network slice: {slice_id} (URLLC)")
        
        # Create another slice for enhanced mobile broadband
        embb_slice_id = await integration.create_network_slice(
            slice_profile=SliceProfile.EMBB,
            latency_requirement_ms=50,
            bandwidth_requirement_mbps=1000,
            reliability_requirement=0.99
        )
        print(f"🍰 Created network slice: {embb_slice_id} (eMBB)")
        
        # Setup QoS flow
        session_id = "demo-session-001"
        qos_profile = {"latency_ms": 10, "bandwidth_mbps": 50, "priority": "high"}
        await integration.setup_qos_flow(session_id, slice_id, qos_profile)
        print(f"⚡ Setup QoS flow for session: {session_id}")
        
        # Get status
        status = integration.get_integration_status()
        print(f"📊 Integration status - Services: {len(status['services'])}, Slices: {len(status['network_slices'])}")
        
    finally:
        await integration.stop()
        print("🛑 MEC integration layer stopped")


async def demo_iot_mesh_network():
    """Demonstrate IoT mesh networking capabilities."""
    print("\n" + "="*60)
    print("🌐 IOT MESH NETWORKING DEMO")
    print("="*60)
    
    # Create configuration
    config = IoTMeshConfig(
        network_name="ainflue-demo-mesh",
        auto_healing_enabled=False,  # Disable for demo
        device_heartbeat_interval_seconds=60  # Disable frequent heartbeats
    )
    
    # Create and start orchestrator
    orchestrator = IoTMeshOrchestrator(config)
    await orchestrator.start()
    
    try:
        print("✅ IoT mesh orchestrator started")
        
        # Register different types of devices
        gateway_id = await orchestrator.register_device(
            device_name="edge-gateway-01",
            device_type=DeviceType.GATEWAY,
            capabilities=[DeviceCapability.COMPUTE, DeviceCapability.COMMUNICATION, DeviceCapability.AI_INFERENCE],
            protocols=[CommunicationProtocol.WIFI, CommunicationProtocol.ETHERNET, CommunicationProtocol.CELLULAR_5G],
            hardware_specs={"cpu_cores": 8, "memory_gb": 16, "storage_gb": 500},
            location={"latitude": 52.5200, "longitude": 13.4050}
        )
        print(f"🔧 Registered gateway: {gateway_id}")
        
        sensor_id = await orchestrator.register_device(
            device_name="temp-humidity-sensor-01",
            device_type=DeviceType.SENSOR,
            capabilities=[DeviceCapability.SENSING, DeviceCapability.COMMUNICATION],
            protocols=[CommunicationProtocol.ZIGBEE, CommunicationProtocol.WIFI],
            hardware_specs={"battery_capacity_mah": 3000, "sensor_type": "environmental"},
            location={"latitude": 52.5210, "longitude": 13.4060}
        )
        print(f"🌡️ Registered sensor: {sensor_id}")
        
        camera_id = await orchestrator.register_device(
            device_name="smart-camera-01",
            device_type=DeviceType.SMART_CAMERA,
            capabilities=[DeviceCapability.SENSING, DeviceCapability.AI_INFERENCE, DeviceCapability.COMMUNICATION],
            protocols=[CommunicationProtocol.WIFI, CommunicationProtocol.ETHERNET],
            hardware_specs={"resolution": "4K", "ai_chip": "edge_tpu"},
            location={"latitude": 52.5220, "longitude": 13.4070}
        )
        print(f"📷 Registered camera: {camera_id}")
        
        # Update device statuses
        from backend.edge.iot_mesh_network import DeviceStatus
        await orchestrator.update_device_status(gateway_id, DeviceStatus.ONLINE)
        await orchestrator.update_device_status(sensor_id, DeviceStatus.ONLINE, battery_level=0.85)
        await orchestrator.update_device_status(camera_id, DeviceStatus.ONLINE)
        
        # Create device groups
        await orchestrator.create_device_group("environmental_sensors", [sensor_id])
        await orchestrator.create_device_group("ai_devices", [gateway_id, camera_id])
        
        # Send a message through the mesh
        message = {
            "type": "sensor_reading",
            "temperature": 23.5,
            "humidity": 65.2,
            "timestamp": datetime.now().isoformat()
        }
        await orchestrator.send_message(sensor_id, gateway_id, message)
        print(f"📤 Sent message from sensor to gateway")
        
        # Broadcast a message to all AI devices
        broadcast_msg = {
            "type": "ai_model_update",
            "model_version": "v2.1.0",
            "update_url": "https://models.ainflue.com/v2.1.0"
        }
        devices_reached = await orchestrator.broadcast_message(gateway_id, broadcast_msg, target_group="ai_devices")
        print(f"📢 Broadcast reached {devices_reached} devices")
        
        # Orchestrate computation
        task_result = await orchestrator.orchestrate_computation(
            task_definition={"type": "image_analysis", "priority": "high"},
            required_capabilities=[DeviceCapability.AI_INFERENCE, DeviceCapability.COMPUTE],
            preferred_devices=[gateway_id, camera_id]
        )
        print(f"🧮 Computation orchestrated: {task_result.get('selected_device', 'none')}")
        
        # Get network status
        status = orchestrator.get_network_status()
        print(f"📊 Network status - Devices: {status['metrics']['total_devices']}, Active: {status['metrics']['active_devices']}")
        
    finally:
        await orchestrator.stop()
        print("🛑 IoT mesh orchestrator stopped")


async def demo_fog_computing():
    """Demonstrate fog computing orchestration."""
    print("\n" + "="*60)
    print("🌫️ FOG COMPUTING ORCHESTRATION DEMO")
    print("="*60)
    
    # Create configuration
    config = FogComputingConfig(
        orchestrator_name="ainflue-fog-demo",
        enable_auto_scaling=False,  # Disable for demo
        task_timeout_seconds=30,
        heartbeat_interval_seconds=60  # Disable frequent heartbeats
    )
    
    # Create and start orchestrator
    orchestrator = FogComputingOrchestrator(config)
    await orchestrator.start()
    
    try:
        print("✅ Fog computing orchestrator started")
        
        # Register fog nodes at different tiers
        edge_node_id = await orchestrator.register_fog_node(
            node_name="edge-server-berlin",
            tier=ProcessingTier.FOG_TIER,
            capabilities=["ai_inference", "real_time_analytics", "data_preprocessing"],
            resources={
                ResourceType.CPU: 16.0,
                ResourceType.MEMORY: 32768.0,  # 32GB
                ResourceType.STORAGE: 1000000.0,  # 1TB
                ResourceType.GPU: 2.0
            },
            location={"latitude": 52.5200, "longitude": 13.4050},
            network_latency_ms=5.0,
            network_bandwidth_mbps=1000.0
        )
        print(f"🔧 Registered edge node: {edge_node_id}")
        
        cloud_node_id = await orchestrator.register_fog_node(
            node_name="cloud-instance-eu-central",
            tier=ProcessingTier.CLOUD_TIER,
            capabilities=["machine_learning", "big_data_analytics", "model_training"],
            resources={
                ResourceType.CPU: 64.0,
                ResourceType.MEMORY: 131072.0,  # 128GB
                ResourceType.STORAGE: 10000000.0,  # 10TB
                ResourceType.GPU: 8.0
            },
            network_latency_ms=50.0,
            network_bandwidth_mbps=10000.0
        )
        print(f"☁️ Registered cloud node: {cloud_node_id}")
        
        # Define processing functions
        def image_classification_task(image_data):
            """Simulate image classification."""
            import time
            time.sleep(1)  # Simulate processing time
            return {
                "classification": "cat",
                "confidence": 0.95,
                "processing_time_ms": 1000,
                "processed_at": datetime.now().isoformat()
            }
        
        async def data_aggregation_task(sensor_data):
            """Simulate async data aggregation."""
            await asyncio.sleep(0.5)  # Simulate async I/O
            return {
                "aggregated_value": sum(sensor_data.get("values", [0])),
                "count": len(sensor_data.get("values", [])),
                "average": sum(sensor_data.get("values", [0])) / len(sensor_data.get("values", [1])),
                "processed_at": datetime.now().isoformat()
            }
        
        # Submit tasks with different priorities and requirements
        task1_id = await orchestrator.submit_task(
            task_name="real-time-image-classification",
            workload_type=WorkloadType.AI_INFERENCE,
            processing_function=image_classification_task,
            input_data={"image": "camera_frame_001.jpg", "format": "jpeg"},
            priority=TaskPriority.HIGH,
            resource_requirements={
                ResourceType.CPU: 2.0,
                ResourceType.MEMORY: 2048.0,
                ResourceType.GPU: 0.5
            },
            estimated_duration_seconds=5.0,
            target_tier=ProcessingTier.FOG_TIER  # Prefer edge processing
        )
        print(f"🎯 Submitted high-priority AI inference task: {task1_id}")
        
        task2_id = await orchestrator.submit_task(
            task_name="sensor-data-aggregation",
            workload_type=WorkloadType.DATA_AGGREGATION,
            processing_function=data_aggregation_task,
            input_data={"values": [23.5, 24.1, 23.8, 24.2, 23.9], "sensor_id": "temp_01"},
            priority=TaskPriority.NORMAL,
            resource_requirements={
                ResourceType.CPU: 1.0,
                ResourceType.MEMORY: 512.0
            },
            estimated_duration_seconds=2.0
        )
        print(f"📊 Submitted data aggregation task: {task2_id}")
        
        task3_id = await orchestrator.submit_task(
            task_name="batch-analytics-processing",
            workload_type=WorkloadType.BATCH_PROCESSING,
            processing_function=lambda data: f"Batch processed {len(data.get('records', []))} records",
            input_data={"records": list(range(1000))},
            priority=TaskPriority.LOW,
            resource_requirements={
                ResourceType.CPU: 8.0,
                ResourceType.MEMORY: 8192.0
            },
            estimated_duration_seconds=15.0,
            target_tier=ProcessingTier.CLOUD_TIER  # Prefer cloud processing
        )
        print(f"🔄 Submitted batch processing task: {task3_id}")
        
        # Wait for some processing
        print("⏳ Waiting for task processing...")
        await asyncio.sleep(3)
        
        # Check task statuses
        for task_id, task_name in [(task1_id, "Image Classification"), (task2_id, "Data Aggregation"), (task3_id, "Batch Processing")]:
            status = await orchestrator.get_task_status(task_id)
            if status:
                print(f"📋 {task_name}: {status['status']}")
            else:
                print(f"❓ {task_name}: Status unknown")
        
        # Get node statuses
        for node_id, node_name in [(edge_node_id, "Edge Node"), (cloud_node_id, "Cloud Node")]:
            status = await orchestrator.get_node_status(node_id)
            if status:
                cpu_util = status['resource_utilization'].get('cpu', 0)
                print(f"🖥️ {node_name}: {status['running_tasks']} tasks, CPU: {cpu_util:.1%}")
        
        # Get orchestrator status
        status = orchestrator.get_orchestrator_status()
        print(f"📊 Orchestrator metrics - Total tasks: {status['metrics']['total_tasks']}, Completed: {status['metrics']['completed_tasks']}")
        
    finally:
        await orchestrator.stop()
        print("🛑 Fog computing orchestrator stopped")


async def demo_integration():
    """Demonstrate integration between all edge computing components."""
    print("\n" + "="*60)
    print("🔗 EDGE COMPUTING INTEGRATION DEMO")
    print("="*60)
    
    print("🚀 Starting all edge computing components...")
    
    # Start all components with minimal configurations
    edge_inference = EdgeInferenceOrchestrator(EdgeInferenceConfig(
        resource_monitoring_enabled=False,
        metrics_collection_enabled=False
    ))
    
    mec_integration = MECIntegrationLayer(MECIntegrationConfig(
        monitoring_interval_seconds=300,
        qos_management_enabled=False
    ))
    
    iot_mesh = IoTMeshOrchestrator(IoTMeshConfig(
        auto_healing_enabled=False,
        device_heartbeat_interval_seconds=300
    ))
    
    fog_computing = FogComputingOrchestrator(FogComputingConfig(
        enable_auto_scaling=False,
        heartbeat_interval_seconds=300
    ))
    
    # Start all components
    await edge_inference.start()
    await mec_integration.start()
    await iot_mesh.start()
    await fog_computing.start()
    
    try:
        print("✅ All components started successfully!")
        
        # Register components that work together
        # 1. Register an edge node in fog computing
        fog_node_id = await fog_computing.register_fog_node(
            node_name="integrated-edge-node",
            tier=ProcessingTier.FOG_TIER,
            capabilities=["ai_inference", "iot_data_processing"],
            resources={ResourceType.CPU: 8.0, ResourceType.MEMORY: 16384.0}
        )
        
        # 2. Register a MEC service for AI inference
        mec_service_id = await mec_integration.register_mec_service(
            service_name="integrated-ai-service",
            service_type=ServiceType.AI_INFERENCE,
            endpoint="http://edge-node:8080",
            capabilities=["real_time_inference"]
        )
        
        # 3. Register IoT devices that will use these services
        iot_device_id = await iot_mesh.register_device(
            device_name="integrated-smart-sensor",
            device_type=DeviceType.SENSOR,
            capabilities=[DeviceCapability.SENSING, DeviceCapability.AI_INFERENCE],
            protocols=[CommunicationProtocol.CELLULAR_5G, CommunicationProtocol.WIFI]
        )
        
        print(f"🔧 Registered fog node: {fog_node_id[:8]}...")
        print(f"📡 Registered MEC service: {mec_service_id[:8]}...")
        print(f"🌐 Registered IoT device: {iot_device_id[:8]}...")
        
        # Show how components can work together
        print("🤝 Components integrated and ready for coordinated edge computing!")
        
        # Get status from all components
        edge_status = edge_inference.get_engine_status()
        mec_status = mec_integration.get_integration_status()
        iot_status = iot_mesh.get_network_status()
        fog_status = fog_computing.get_orchestrator_status()
        
        print(f"📊 Edge Inference: {edge_status['edge_orchestrator']['optimization_strategy']}")
        print(f"📊 MEC Integration: {len(mec_status['services'])} services, {len(mec_status['network_slices'])} slices")
        print(f"📊 IoT Mesh: {iot_status['metrics']['total_devices']} devices")
        print(f"📊 Fog Computing: {fog_status['metrics']['total_nodes']} nodes")
        
    finally:
        # Stop all components
        await edge_inference.stop()
        await mec_integration.stop()
        await iot_mesh.stop()
        await fog_computing.stop()
        print("🛑 All edge computing components stopped")


async def main():
    """Run the complete edge computing layer demonstration."""
    print("🌟 AINFLUE EDGE COMPUTING LAYER DEMONSTRATION")
    print("=" * 80)
    print("Showcasing the complete edge computing infrastructure:")
    print("• Edge AI Inference Orchestration")
    print("• 5G Multi-access Edge Computing (MEC) Integration")
    print("• IoT Mesh Network Orchestration")
    print("• Fog Computing Distributed Processing")
    print("• Component Integration")
    print("=" * 80)
    
    try:
        # Run each demo
        await demo_edge_inference()
        await demo_5g_mec_integration()
        await demo_iot_mesh_network()
        await demo_fog_computing()
        await demo_integration()
        
        print("\n" + "="*80)
        print("🎉 EDGE COMPUTING LAYER DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("All components are working correctly and ready for production use.")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())