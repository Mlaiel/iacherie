# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive Tests for Communication Module

Industrial-grade testing for agent communication protocols, message routing,
inter-agent coordination, and communication infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
import json
import uuid

from ai.ai_agents.communication import (
    AgentCommunicationProtocol,
    MessageRouter,
    CommunicationBus,
    AgentMessage,
    MessageType,
    Priority,
    CommunicationConfig
)

logger = logging.getLogger(__name__)


class TestAgentMessage:
    """Test agent message creation and serialization"""
    
    def test_message_creation(self):
        """Test creating agent messages"""
        message = AgentMessage(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "test_task"},
            priority=Priority.HIGH
        )
        
        assert message.sender_id == "test_sender"
        assert message.recipient_id == "test_recipient"
        assert message.message_type == MessageType.TASK_REQUEST
        assert message.payload == {"task": "test_task"}
        assert message.priority == Priority.HIGH
        assert message.message_id is not None
        assert message.timestamp is not None
        assert message.correlation_id is None
    
    def test_message_serialization(self):
        """Test message serialization and deserialization"""
        original_message = AgentMessage(
            sender_id="sender",
            recipient_id="recipient",
            message_type=MessageType.TASK_RESULT,
            payload={"result": "success", "data": [1, 2, 3]},
            priority=Priority.MEDIUM,
            correlation_id="test_correlation"
        )
        
        # Serialize
        serialized = original_message.to_dict()
        assert isinstance(serialized, dict)
        assert "sender_id" in serialized
        assert "message_id" in serialized
        assert "timestamp" in serialized
        
        # Deserialize
        deserialized = AgentMessage.from_dict(serialized)
        assert deserialized.sender_id == original_message.sender_id
        assert deserialized.recipient_id == original_message.recipient_id
        assert deserialized.message_type == original_message.message_type
        assert deserialized.payload == original_message.payload
        assert deserialized.priority == original_message.priority
        assert deserialized.correlation_id == original_message.correlation_id
    
    def test_message_validation(self):
        """Test message validation"""
        # Valid message
        valid_message = AgentMessage(
            sender_id="sender",
            recipient_id="recipient",
            message_type=MessageType.HEARTBEAT,
            payload={}
        )
        assert valid_message.is_valid()
        
        # Invalid message - missing sender
        with pytest.raises(ValueError):
            AgentMessage(
                sender_id="",
                recipient_id="recipient",
                message_type=MessageType.TASK_REQUEST,
                payload={}
            )
    
    def test_message_expiration(self):
        """Test message expiration logic"""
        # Message with TTL
        message = AgentMessage(
            sender_id="sender",
            recipient_id="recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={},
            ttl_seconds=1
        )
        
        assert not message.is_expired()
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        assert message.is_expired()
    
    def test_message_priority_comparison(self):
        """Test message priority comparison"""
        high_priority = AgentMessage(
            sender_id="sender",
            recipient_id="recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={},
            priority=Priority.HIGH
        )
        
        low_priority = AgentMessage(
            sender_id="sender",
            recipient_id="recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={},
            priority=Priority.LOW
        )
        
        assert high_priority.priority.value > low_priority.priority.value


class TestMessageRouter:
    """Test message routing functionality"""
    
    @pytest.fixture
    async def message_router(self) -> MessageRouter:
        """Create message router for testing"""
        config = CommunicationConfig(
            max_queue_size=1000,
            default_timeout=30,
            retry_attempts=3,
            enable_persistence=False
        )
        router = MessageRouter(config)
        await router.initialize()
        
        yield router
        
        await router.shutdown()
    
    async def test_router_initialization(self):
        """Test message router initialization"""
        config = CommunicationConfig()
        router = MessageRouter(config)
        
        assert not router.initialized
        
        await router.initialize()
        assert router.initialized
        
        await router.shutdown()
        assert not router.initialized
    
    async def test_agent_registration(self, message_router):
        """Test agent registration with router"""
        agent_id = "test_agent_001"
        
        # Register agent
        await message_router.register_agent(agent_id, "test_agent")
        
        # Verify registration
        assert message_router.is_agent_registered(agent_id)
        registered_agents = message_router.get_registered_agents()
        assert agent_id in registered_agents
        
        # Unregister agent
        await message_router.unregister_agent(agent_id)
        assert not message_router.is_agent_registered(agent_id)
    
    async def test_message_routing(self, message_router):
        """Test basic message routing"""
        sender_id = "sender_agent"
        recipient_id = "recipient_agent"
        
        # Register agents
        await message_router.register_agent(sender_id, "sender")
        await message_router.register_agent(recipient_id, "recipient")
        
        # Create message
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "test_routing"}
        )
        
        # Route message
        routing_result = await message_router.route_message(message)
        assert routing_result["success"] is True
        assert routing_result["message_id"] == message.message_id
        
        # Check if message was delivered
        delivered_messages = await message_router.get_messages_for_agent(recipient_id)
        assert len(delivered_messages) == 1
        assert delivered_messages[0].message_id == message.message_id
    
    async def test_broadcast_messaging(self, message_router):
        """Test broadcast messaging"""
        sender_id = "broadcast_sender"
        recipients = ["agent_1", "agent_2", "agent_3"]
        
        # Register agents
        await message_router.register_agent(sender_id, "sender")
        for recipient in recipients:
            await message_router.register_agent(recipient, f"agent_{recipient}")
        
        # Create broadcast message
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id="*",  # Broadcast indicator
            message_type=MessageType.SYSTEM_ANNOUNCEMENT,
            payload={"announcement": "System maintenance scheduled"}
        )
        
        # Broadcast message
        broadcast_result = await message_router.broadcast_message(message, recipients)
        assert broadcast_result["success"] is True
        assert len(broadcast_result["delivered_to"]) == 3
        
        # Verify all recipients received the message
        for recipient in recipients:
            messages = await message_router.get_messages_for_agent(recipient)
            assert len(messages) == 1
            assert messages[0].payload["announcement"] == "System maintenance scheduled"
    
    async def test_message_filtering(self, message_router):
        """Test message filtering by type and priority"""
        agent_id = "filter_test_agent"
        await message_router.register_agent(agent_id, "test")
        
        # Send messages of different types and priorities
        messages = [
            AgentMessage(
                sender_id="sender",
                recipient_id=agent_id,
                message_type=MessageType.TASK_REQUEST,
                payload={},
                priority=Priority.HIGH
            ),
            AgentMessage(
                sender_id="sender",
                recipient_id=agent_id,
                message_type=MessageType.HEARTBEAT,
                payload={},
                priority=Priority.LOW
            ),
            AgentMessage(
                sender_id="sender",
                recipient_id=agent_id,
                message_type=MessageType.TASK_RESULT,
                payload={},
                priority=Priority.MEDIUM
            )
        ]
        
        # Route all messages
        for message in messages:
            await message_router.route_message(message)
        
        # Filter by message type
        task_messages = await message_router.get_messages_for_agent(
            agent_id, 
            message_type=MessageType.TASK_REQUEST
        )
        assert len(task_messages) == 1
        assert task_messages[0].message_type == MessageType.TASK_REQUEST
        
        # Filter by priority
        high_priority_messages = await message_router.get_messages_for_agent(
            agent_id,
            min_priority=Priority.HIGH
        )
        assert len(high_priority_messages) == 1
        assert high_priority_messages[0].priority == Priority.HIGH
    
    async def test_message_acknowledgment(self, message_router):
        """Test message acknowledgment system"""
        sender_id = "ack_sender"
        recipient_id = "ack_recipient"
        
        await message_router.register_agent(sender_id, "sender")
        await message_router.register_agent(recipient_id, "recipient")
        
        # Send message requiring acknowledgment
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "acknowledged_task"},
            requires_ack=True
        )
        
        await message_router.route_message(message)
        
        # Check pending acknowledgments
        pending_acks = await message_router.get_pending_acknowledgments(sender_id)
        assert len(pending_acks) == 1
        assert pending_acks[0]["message_id"] == message.message_id
        
        # Send acknowledgment
        ack_result = await message_router.acknowledge_message(
            message.message_id,
            recipient_id
        )
        assert ack_result["success"] is True
        
        # Verify acknowledgment received
        pending_acks = await message_router.get_pending_acknowledgments(sender_id)
        assert len(pending_acks) == 0
    
    async def test_message_retry_mechanism(self, message_router):
        """Test message retry mechanism for failed deliveries"""
        sender_id = "retry_sender"
        recipient_id = "non_existent_recipient"
        
        await message_router.register_agent(sender_id, "sender")
        # Note: Not registering recipient to simulate failure
        
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "retry_test"},
            retry_attempts=2
        )
        
        # Attempt to route message
        routing_result = await message_router.route_message(message)
        assert routing_result["success"] is False
        assert "retry_scheduled" in routing_result
        
        # Check retry queue
        retry_messages = await message_router.get_retry_queue()
        assert len(retry_messages) >= 1
    
    async def test_priority_queue_ordering(self, message_router):
        """Test priority-based message ordering"""
        agent_id = "priority_test_agent"
        await message_router.register_agent(agent_id, "test")
        
        # Send messages with different priorities
        priorities = [Priority.LOW, Priority.HIGH, Priority.MEDIUM, Priority.CRITICAL]
        messages = []
        
        for i, priority in enumerate(priorities):
            message = AgentMessage(
                sender_id="sender",
                recipient_id=agent_id,
                message_type=MessageType.TASK_REQUEST,
                payload={"order": i},
                priority=priority
            )
            messages.append(message)
            await message_router.route_message(message)
        
        # Retrieve messages (should be ordered by priority)
        delivered_messages = await message_router.get_messages_for_agent(agent_id)
        
        # Verify priority ordering (CRITICAL > HIGH > MEDIUM > LOW)
        assert delivered_messages[0].priority == Priority.CRITICAL
        assert delivered_messages[1].priority == Priority.HIGH
        assert delivered_messages[2].priority == Priority.MEDIUM
        assert delivered_messages[3].priority == Priority.LOW


class TestCommunicationBus:
    """Test communication bus functionality"""
    
    @pytest.fixture
    async def communication_bus(self) -> CommunicationBus:
        """Create communication bus for testing"""
        config = CommunicationConfig(
            enable_event_streaming=True,
            enable_message_persistence=True,
            enable_encryption=False  # Disabled for testing
        )
        bus = CommunicationBus(config)
        await bus.initialize()
        
        yield bus
        
        await bus.shutdown()
    
    async def test_bus_initialization(self):
        """Test communication bus initialization"""
        config = CommunicationConfig()
        bus = CommunicationBus(config)
        
        assert not bus.initialized
        
        await bus.initialize()
        assert bus.initialized
        
        await bus.shutdown()
    
    async def test_event_subscription(self, communication_bus):
        """Test event subscription and notification"""
        events_received = []
        
        async def event_handler(event_type: str, event_data: Dict[str, Any]):
            events_received.append({"type": event_type, "data": event_data})
        
        # Subscribe to events
        subscription_id = await communication_bus.subscribe_to_events(
            event_types=["agent_registered", "message_sent"],
            handler=event_handler
        )
        
        assert subscription_id is not None
        
        # Trigger events
        await communication_bus.publish_event(
            event_type="agent_registered",
            event_data={"agent_id": "test_agent"}
        )
        
        await communication_bus.publish_event(
            event_type="message_sent",
            event_data={"message_id": "test_message"}
        )
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        # Verify events received
        assert len(events_received) == 2
        assert events_received[0]["type"] == "agent_registered"
        assert events_received[1]["type"] == "message_sent"
        
        # Unsubscribe
        await communication_bus.unsubscribe_from_events(subscription_id)
    
    async def test_message_persistence(self, communication_bus):
        """Test message persistence functionality"""
        message = AgentMessage(
            sender_id="persistent_sender",
            recipient_id="persistent_recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "persistent_task"}
        )
        
        # Store message
        storage_result = await communication_bus.store_message(message)
        assert storage_result["success"] is True
        
        # Retrieve message
        retrieved_message = await communication_bus.retrieve_message(message.message_id)
        assert retrieved_message is not None
        assert retrieved_message.message_id == message.message_id
        assert retrieved_message.payload == message.payload
        
        # Query messages by criteria
        query_results = await communication_bus.query_messages(
            sender_id="persistent_sender",
            limit=10
        )
        assert len(query_results) >= 1
        assert any(msg.message_id == message.message_id for msg in query_results)
    
    async def test_communication_metrics(self, communication_bus):
        """Test communication metrics collection"""
        # Generate some activity
        for i in range(5):
            message = AgentMessage(
                sender_id=f"sender_{i}",
                recipient_id=f"recipient_{i}",
                message_type=MessageType.TASK_REQUEST,
                payload={}
            )
            await communication_bus.store_message(message)
        
        # Retrieve metrics
        metrics = await communication_bus.get_communication_metrics()
        
        assert "total_messages" in metrics
        assert "messages_by_type" in metrics
        assert "average_message_size" in metrics
        assert "throughput" in metrics
        assert metrics["total_messages"] >= 5
    
    async def test_health_monitoring(self, communication_bus):
        """Test communication bus health monitoring"""
        health_status = await communication_bus.get_health_status()
        
        assert "status" in health_status
        assert "uptime" in health_status
        assert "message_queue_size" in health_status
        assert "active_connections" in health_status
        assert "last_heartbeat" in health_status
        
        assert health_status["status"] in ["healthy", "degraded", "unhealthy"]


class TestAgentCommunicationProtocol:
    """Test agent communication protocol implementation"""
    
    @pytest.fixture
    async def communication_protocol(self) -> AgentCommunicationProtocol:
        """Create communication protocol for testing"""
        config = CommunicationConfig(
            protocol_version="1.0",
            enable_compression=True,
            enable_encryption=False,
            message_timeout=30
        )
        protocol = AgentCommunicationProtocol(config)
        await protocol.initialize()
        
        yield protocol
        
        await protocol.shutdown()
    
    async def test_protocol_initialization(self):
        """Test protocol initialization"""
        config = CommunicationConfig()
        protocol = AgentCommunicationProtocol(config)
        
        assert not protocol.initialized
        
        await protocol.initialize()
        assert protocol.initialized
        assert protocol.protocol_version is not None
        
        await protocol.shutdown()
    
    async def test_handshake_process(self, communication_protocol):
        """Test agent handshake process"""
        agent_info = {
            "agent_id": "handshake_agent",
            "agent_type": "test_agent",
            "capabilities": ["test_capability"],
            "protocol_version": "1.0"
        }
        
        # Initiate handshake
        handshake_result = await communication_protocol.initiate_handshake(agent_info)
        
        assert handshake_result["success"] is True
        assert "session_id" in handshake_result
        assert "protocol_version" in handshake_result
        
        # Verify agent is connected
        connected_agents = await communication_protocol.get_connected_agents()
        assert "handshake_agent" in connected_agents
    
    async def test_secure_messaging(self, communication_protocol):
        """Test secure messaging capabilities"""
        # Register agents for secure communication
        sender_info = {
            "agent_id": "secure_sender",
            "agent_type": "sender",
            "capabilities": ["secure_messaging"]
        }
        
        recipient_info = {
            "agent_id": "secure_recipient",
            "agent_type": "recipient",
            "capabilities": ["secure_messaging"]
        }
        
        await communication_protocol.initiate_handshake(sender_info)
        await communication_protocol.initiate_handshake(recipient_info)
        
        # Send secure message
        secure_message = AgentMessage(
            sender_id="secure_sender",
            recipient_id="secure_recipient",
            message_type=MessageType.SECURE_DATA,
            payload={"sensitive_data": "confidential_information"},
            encryption_required=True
        )
        
        delivery_result = await communication_protocol.send_secure_message(secure_message)
        assert delivery_result["success"] is True
        assert delivery_result["encrypted"] is True
    
    async def test_protocol_compliance(self, communication_protocol):
        """Test protocol compliance validation"""
        # Valid message according to protocol
        valid_message = AgentMessage(
            sender_id="protocol_sender",
            recipient_id="protocol_recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={"task": "protocol_test"}
        )
        
        compliance_result = await communication_protocol.validate_message_compliance(valid_message)
        assert compliance_result["compliant"] is True
        
        # Invalid message (missing required fields)
        invalid_message_dict = {
            "sender_id": "sender",
            # Missing recipient_id and other required fields
        }
        
        compliance_result = await communication_protocol.validate_compliance(invalid_message_dict)
        assert compliance_result["compliant"] is False
        assert "violations" in compliance_result
    
    async def test_connection_management(self, communication_protocol):
        """Test connection lifecycle management"""
        agent_id = "connection_test_agent"
        
        # Connect agent
        connection_result = await communication_protocol.connect_agent(
            agent_id,
            {"agent_type": "test", "capabilities": []}
        )
        assert connection_result["success"] is True
        
        # Check connection status
        is_connected = await communication_protocol.is_agent_connected(agent_id)
        assert is_connected is True
        
        # Disconnect agent
        disconnection_result = await communication_protocol.disconnect_agent(agent_id)
        assert disconnection_result["success"] is True
        
        # Verify disconnection
        is_connected = await communication_protocol.is_agent_connected(agent_id)
        assert is_connected is False
    
    async def test_protocol_versioning(self, communication_protocol):
        """Test protocol version compatibility"""
        # Agent with compatible version
        compatible_agent = {
            "agent_id": "compatible_agent",
            "protocol_version": "1.0"
        }
        
        compatibility_result = await communication_protocol.check_version_compatibility(
            compatible_agent["protocol_version"]
        )
        assert compatibility_result["compatible"] is True
        
        # Agent with incompatible version
        incompatible_version = "0.5"
        compatibility_result = await communication_protocol.check_version_compatibility(
            incompatible_version
        )
        assert compatibility_result["compatible"] is False
        assert "reason" in compatibility_result


class TestCommunicationIntegration:
    """Integration tests for communication system"""
    
    @pytest.fixture
    async def communication_system(self):
        """Create complete communication system for integration testing"""
        config = CommunicationConfig(
            enable_persistence=True,
            enable_event_streaming=True,
            enable_metrics=True
        )
        
        # Initialize components
        protocol = AgentCommunicationProtocol(config)
        router = MessageRouter(config)
        bus = CommunicationBus(config)
        
        await protocol.initialize()
        await router.initialize()
        await bus.initialize()
        
        system = {
            "protocol": protocol,
            "router": router,
            "bus": bus,
            "config": config
        }
        
        yield system
        
        # Cleanup
        await protocol.shutdown()
        await router.shutdown()
        await bus.shutdown()
    
    async def test_end_to_end_communication(self, communication_system):
        """Test end-to-end communication flow"""
        protocol = communication_system["protocol"]
        router = communication_system["router"]
        bus = communication_system["bus"]
        
        # Register agents
        sender_info = {
            "agent_id": "e2e_sender",
            "agent_type": "content_creator",
            "capabilities": ["content_generation"]
        }
        
        recipient_info = {
            "agent_id": "e2e_recipient", 
            "agent_type": "social_media_manager",
            "capabilities": ["content_posting"]
        }
        
        await protocol.connect_agent(sender_info["agent_id"], sender_info)
        await protocol.connect_agent(recipient_info["agent_id"], recipient_info)
        await router.register_agent(sender_info["agent_id"], sender_info["agent_type"])
        await router.register_agent(recipient_info["agent_id"], recipient_info["agent_type"])
        
        # Send message through the system
        message = AgentMessage(
            sender_id=sender_info["agent_id"],
            recipient_id=recipient_info["agent_id"],
            message_type=MessageType.TASK_REQUEST,
            payload={
                "task": "post_content",
                "content": "Test content for posting",
                "platform": "instagram"
            },
            requires_ack=True
        )
        
        # Route message
        routing_result = await router.route_message(message)
        assert routing_result["success"] is True
        
        # Store in persistent storage
        storage_result = await bus.store_message(message)
        assert storage_result["success"] is True
        
        # Verify message delivery
        delivered_messages = await router.get_messages_for_agent(recipient_info["agent_id"])
        assert len(delivered_messages) >= 1
        assert any(msg.message_id == message.message_id for msg in delivered_messages)
        
        # Send acknowledgment
        ack_result = await router.acknowledge_message(
            message.message_id,
            recipient_info["agent_id"]
        )
        assert ack_result["success"] is True
    
    async def test_system_resilience(self, communication_system):
        """Test system resilience under load"""
        router = communication_system["router"]
        
        # Register multiple agents
        agents = []
        for i in range(10):
            agent_id = f"resilience_agent_{i}"
            await router.register_agent(agent_id, "test_agent")
            agents.append(agent_id)
        
        # Send many messages concurrently
        tasks = []
        for i in range(100):
            sender = agents[i % len(agents)]
            recipient = agents[(i + 1) % len(agents)]
            
            message = AgentMessage(
                sender_id=sender,
                recipient_id=recipient,
                message_type=MessageType.TASK_REQUEST,
                payload={"task_id": i}
            )
            
            tasks.append(router.route_message(message))
        
        # Execute all routing tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify most messages were delivered successfully
        successful_deliveries = sum(1 for result in results 
                                  if isinstance(result, dict) and result.get("success"))
        assert successful_deliveries >= 90  # Allow for some failures under load
    
    @pytest.mark.performance
    async def test_communication_performance(self, communication_system, assert_performance):
        """Test communication system performance"""
        router = communication_system["router"]
        
        # Register test agents
        await router.register_agent("perf_sender", "sender")
        await router.register_agent("perf_recipient", "recipient")
        
        # Test message routing performance
        message = AgentMessage(
            sender_id="perf_sender",
            recipient_id="perf_recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={"performance_test": True}
        )
        
        start_time = datetime.now(timezone.utc)
        result = await router.route_message(message)
        end_time = datetime.now(timezone.utc)
        
        routing_time = (end_time - start_time).total_seconds()
        assert routing_time < 0.1  # Should route within 100ms
        assert result["success"] is True
        
        assert_performance("message_routing", max_time=0.1)
    
    async def test_error_recovery(self, communication_system):
        """Test error recovery mechanisms"""
        router = communication_system["router"]
        bus = communication_system["bus"]
        
        # Test recovery from routing failure
        message = AgentMessage(
            sender_id="error_sender",
            recipient_id="non_existent_recipient",
            message_type=MessageType.TASK_REQUEST,
            payload={"test": "error_recovery"}
        )
        
        # Attempt routing (should fail)
        routing_result = await router.route_message(message)
        assert routing_result["success"] is False
        
        # System should remain operational
        health_status = await bus.get_health_status()
        assert health_status["status"] in ["healthy", "degraded"]
        
        # Register the recipient and retry
        await router.register_agent("non_existent_recipient", "test")
        retry_result = await router.route_message(message)
        assert retry_result["success"] is True
