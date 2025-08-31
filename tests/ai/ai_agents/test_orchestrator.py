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
Comprehensive Tests for Orchestrator

Industrial-grade testing for AI agent orchestration, coordination,
system management, and multi-agent workflow execution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
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
import uuid

from ai.ai_agents.orchestrator import (
    Orchestrator,
    AgentOrchestrator,
    OrchestratorConfig,
    AgentRegistry,
    OrchestratorStatus,
    ExecutionPlan,
    ResourceManager,
    LoadBalancer,
    SystemMonitor,
    FaultHandler
)

logger = logging.getLogger(__name__)


class TestAgentRegistry:
    """Test agent registry functionality"""
    
    @pytest.fixture
    def agent_registry(self) -> AgentRegistry:
        """Create agent registry for testing"""
        config = OrchestratorConfig(
            max_agents=100,
            registration_timeout=30,
            health_check_interval=60
        )
        return AgentRegistry(config)
    
    def test_registry_initialization(self):
        """Test agent registry initialization"""
        config = OrchestratorConfig()
        registry = AgentRegistry(config)
        
        assert registry.agent_count == 0
        assert len(registry.get_all_agents()) == 0
        assert registry.max_agents > 0
    
    def test_agent_registration(self, agent_registry):
        """Test agent registration process"""
        agent_info = {
            "agent_id": "test_content_creator",
            "agent_type": "ContentCreatorAgent",
            "capabilities": [
                "content_generation", "image_creation", "video_editing"
            ],
            "version": "1.0.0",
            "status": "active",
            "resource_requirements": {
                "cpu": 2,
                "memory": "4GB",
                "gpu": False
            }
        }
        
        # Register agent
        registration_result = agent_registry.register_agent(agent_info)
        
        assert registration_result["success"] is True
        assert registration_result["agent_id"] == "test_content_creator"
        assert agent_registry.agent_count == 1
        
        # Verify agent is registered
        registered_agent = agent_registry.get_agent("test_content_creator")
        assert registered_agent is not None
        assert registered_agent["agent_type"] == "ContentCreatorAgent"
        assert "content_generation" in registered_agent["capabilities"]
    
    def test_duplicate_registration(self, agent_registry):
        """Test handling of duplicate agent registration"""
        agent_info = {
            "agent_id": "duplicate_agent",
            "agent_type": "TestAgent",
            "capabilities": ["test_capability"]
        }
        
        # First registration should succeed
        result1 = agent_registry.register_agent(agent_info)
        assert result1["success"] is True
        
        # Duplicate registration should fail
        result2 = agent_registry.register_agent(agent_info)
        assert result2["success"] is False
        assert "already registered" in result2["error"].lower()
    
    def test_agent_deregistration(self, agent_registry):
        """Test agent deregistration"""
        # Register agent first
        agent_info = {
            "agent_id": "temp_agent",
            "agent_type": "TemporaryAgent",
            "capabilities": ["temp_capability"]
        }
        agent_registry.register_agent(agent_info)
        
        # Deregister agent
        deregistration_result = agent_registry.deregister_agent("temp_agent")
        
        assert deregistration_result["success"] is True
        assert agent_registry.agent_count == 0
        assert agent_registry.get_agent("temp_agent") is None
    
    def test_agent_capability_queries(self, agent_registry):
        """Test querying agents by capabilities"""
        # Register multiple agents with different capabilities
        agents = [
            {
                "agent_id": "content_creator_1",
                "agent_type": "ContentCreatorAgent",
                "capabilities": ["content_generation", "image_creation"]
            },
            {
                "agent_id": "social_manager_1",
                "agent_type": "SocialMediaManagerAgent", 
                "capabilities": ["social_posting", "analytics"]
            },
            {
                "agent_id": "content_creator_2",
                "agent_type": "ContentCreatorAgent",
                "capabilities": ["content_generation", "video_editing"]
            }
        ]
        
        for agent in agents:
            agent_registry.register_agent(agent)
        
        # Query by capability
        content_agents = agent_registry.get_agents_by_capability("content_generation")
        assert len(content_agents) == 2
        
        social_agents = agent_registry.get_agents_by_capability("social_posting")
        assert len(social_agents) == 1
        
        # Query by agent type
        content_creator_agents = agent_registry.get_agents_by_type("ContentCreatorAgent")
        assert len(content_creator_agents) == 2
    
    def test_agent_health_status(self, agent_registry):
        """Test agent health status tracking"""
        agent_info = {
            "agent_id": "health_test_agent",
            "agent_type": "TestAgent",
            "capabilities": ["test"]
        }
        agent_registry.register_agent(agent_info)
        
        # Update health status
        health_update = agent_registry.update_agent_health("health_test_agent", {
            "status": "healthy",
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "active_tasks": 3
        })
        
        assert health_update["success"] is True
        
        # Get health status
        health_status = agent_registry.get_agent_health("health_test_agent")
        assert health_status["status"] == "healthy"
        assert "cpu_usage" in health_status
        assert "memory_usage" in health_status
    
    def test_registry_capacity_limits(self, agent_registry):
        """Test registry capacity management"""
        # Set low limit for testing
        agent_registry.max_agents = 2
        
        # Register up to capacity
        for i in range(2):
            agent_info = {
                "agent_id": f"capacity_agent_{i}",
                "agent_type": "TestAgent",
                "capabilities": ["test"]
            }
            result = agent_registry.register_agent(agent_info)
            assert result["success"] is True
        
        # Try to exceed capacity
        overflow_agent = {
            "agent_id": "overflow_agent",
            "agent_type": "TestAgent",
            "capabilities": ["test"]
        }
        result = agent_registry.register_agent(overflow_agent)
        assert result["success"] is False
        assert "capacity" in result["error"].lower()


class TestResourceManager:
    """Test resource management functionality"""
    
    @pytest.fixture
    def resource_manager(self) -> ResourceManager:
        """Create resource manager for testing"""
        config = OrchestratorConfig(
            total_cpu_cores=16,
            total_memory_gb=64,
            total_gpu_count=4,
            resource_allocation_strategy="dynamic"
        )
        return ResourceManager(config)
    
    def test_resource_manager_initialization(self):
        """Test resource manager initialization"""
        config = OrchestratorConfig(
            total_cpu_cores=8,
            total_memory_gb=32,
            total_gpu_count=2
        )
        manager = ResourceManager(config)
        
        assert manager.total_resources["cpu"] == 8
        assert manager.total_resources["memory"] == 32
        assert manager.total_resources["gpu"] == 2
        assert manager.available_resources["cpu"] == 8
        assert manager.available_resources["memory"] == 32
        assert manager.available_resources["gpu"] == 2
    
    def test_resource_allocation(self, resource_manager):
        """Test resource allocation for agents"""
        # Allocate resources for agent
        allocation_request = {
            "agent_id": "resource_agent_1",
            "cpu": 4,
            "memory": 16,
            "gpu": 1
        }
        
        allocation_result = resource_manager.allocate_resources(allocation_request)
        
        assert allocation_result["success"] is True
        assert allocation_result["allocation_id"] is not None
        
        # Verify resource consumption
        available = resource_manager.get_available_resources()
        assert available["cpu"] == 12  # 16 - 4
        assert available["memory"] == 48  # 64 - 16
        assert available["gpu"] == 3  # 4 - 1
    
    def test_resource_deallocation(self, resource_manager):
        """Test resource deallocation"""
        # Allocate resources first
        allocation_request = {
            "agent_id": "dealloc_agent",
            "cpu": 2,
            "memory": 8,
            "gpu": 0
        }
        allocation_result = resource_manager.allocate_resources(allocation_request)
        allocation_id = allocation_result["allocation_id"]
        
        # Deallocate resources
        deallocation_result = resource_manager.deallocate_resources(allocation_id)
        
        assert deallocation_result["success"] is True
        
        # Verify resources are returned
        available = resource_manager.get_available_resources()
        assert available["cpu"] == 16  # Back to original
        assert available["memory"] == 64
        assert available["gpu"] == 4
    
    def test_resource_over_allocation(self, resource_manager):
        """Test handling of resource over-allocation"""
        # Try to allocate more resources than available
        excessive_request = {
            "agent_id": "excessive_agent",
            "cpu": 32,  # More than total 16
            "memory": 128,  # More than total 64
            "gpu": 8  # More than total 4
        }
        
        allocation_result = resource_manager.allocate_resources(excessive_request)
        
        assert allocation_result["success"] is False
        assert "insufficient" in allocation_result["error"].lower()
    
    def test_resource_utilization_monitoring(self, resource_manager):
        """Test resource utilization monitoring"""
        # Allocate some resources
        allocations = [
            {"agent_id": "monitor_agent_1", "cpu": 4, "memory": 16, "gpu": 1},
            {"agent_id": "monitor_agent_2", "cpu": 2, "memory": 8, "gpu": 0}
        ]
        
        for allocation in allocations:
            resource_manager.allocate_resources(allocation)
        
        # Get utilization metrics
        utilization = resource_manager.get_resource_utilization()
        
        assert "cpu_utilization" in utilization
        assert "memory_utilization" in utilization
        assert "gpu_utilization" in utilization
        
        # Verify utilization calculations
        assert utilization["cpu_utilization"] == 0.375  # (4+2)/16
        assert utilization["memory_utilization"] == 0.375  # (16+8)/64
        assert utilization["gpu_utilization"] == 0.25  # 1/4
    
    def test_dynamic_resource_scaling(self, resource_manager):
        """Test dynamic resource scaling"""
        # Simulate high load requiring scaling
        scaling_request = {
            "trigger": "high_cpu_utilization",
            "current_utilization": 0.85,
            "requested_scaling": 1.5  # 50% increase
        }
        
        scaling_result = resource_manager.request_scaling(scaling_request)
        
        # Note: Actual scaling might not be implemented in test environment
        assert "scaling_decision" in scaling_result
        assert scaling_result["scaling_decision"] in ["approved", "denied", "pending"]


class TestLoadBalancer:
    """Test load balancing functionality"""
    
    @pytest.fixture
    def load_balancer(self) -> LoadBalancer:
        """Create load balancer for testing"""
        config = OrchestratorConfig(
            load_balancing_algorithm="weighted_round_robin",
            health_check_interval=30,
            failover_enabled=True
        )
        return LoadBalancer(config)
    
    def test_load_balancer_initialization(self):
        """Test load balancer initialization"""
        config = OrchestratorConfig()
        balancer = LoadBalancer(config)
        
        assert balancer.algorithm is not None
        assert balancer.active_agents == 0
        assert len(balancer.get_agent_loads()) == 0
    
    def test_agent_load_tracking(self, load_balancer):
        """Test agent load tracking"""
        # Add agents to load balancer
        agents = [
            {"agent_id": "load_agent_1", "capacity": 100, "current_load": 25},
            {"agent_id": "load_agent_2", "capacity": 100, "current_load": 50},
            {"agent_id": "load_agent_3", "capacity": 100, "current_load": 75}
        ]
        
        for agent in agents:
            load_balancer.add_agent(agent)
        
        # Get load distribution
        loads = load_balancer.get_agent_loads()
        
        assert len(loads) == 3
        assert loads["load_agent_1"]["load_percentage"] == 0.25
        assert loads["load_agent_2"]["load_percentage"] == 0.50
        assert loads["load_agent_3"]["load_percentage"] == 0.75
    
    def test_task_distribution(self, load_balancer):
        """Test task distribution across agents"""
        # Setup agents with different loads
        agents = [
            {"agent_id": "dist_agent_1", "capacity": 100, "current_load": 20},
            {"agent_id": "dist_agent_2", "capacity": 100, "current_load": 60},
            {"agent_id": "dist_agent_3", "capacity": 100, "current_load": 40}
        ]
        
        for agent in agents:
            load_balancer.add_agent(agent)
        
        # Distribute tasks
        task_requests = [
            {"task_id": "task_1", "resource_requirement": 10, "agent_type": "any"},
            {"task_id": "task_2", "resource_requirement": 15, "agent_type": "any"},
            {"task_id": "task_3", "resource_requirement": 20, "agent_type": "any"}
        ]
        
        distributions = []
        for task in task_requests:
            distribution = load_balancer.select_agent_for_task(task)
            distributions.append(distribution)
        
        # Verify load balancing (should prefer less loaded agents)
        assert len(distributions) == 3
        for dist in distributions:
            assert dist["success"] is True
            assert "selected_agent" in dist
    
    def test_load_balancing_algorithms(self, load_balancer):
        """Test different load balancing algorithms"""
        algorithms = ["round_robin", "least_connections", "weighted_round_robin", "resource_aware"]
        
        # Setup test agents
        agents = [
            {"agent_id": "algo_agent_1", "capacity": 100, "current_load": 30},
            {"agent_id": "algo_agent_2", "capacity": 100, "current_load": 50},
            {"agent_id": "algo_agent_3", "capacity": 100, "current_load": 20}
        ]
        
        for agent in agents:
            load_balancer.add_agent(agent)
        
        # Test each algorithm
        for algorithm in algorithms:
            load_balancer.set_algorithm(algorithm)
            
            task = {"task_id": f"algo_test_{algorithm}", "resource_requirement": 10}
            selection = load_balancer.select_agent_for_task(task)
            
            assert selection["success"] is True
            assert "selected_agent" in selection
            assert "algorithm_used" in selection
            assert selection["algorithm_used"] == algorithm
    
    def test_failover_mechanism(self, load_balancer):
        """Test agent failover handling"""
        # Add agents
        agents = [
            {"agent_id": "failover_agent_1", "capacity": 100, "current_load": 40, "status": "healthy"},
            {"agent_id": "failover_agent_2", "capacity": 100, "current_load": 30, "status": "healthy"}
        ]
        
        for agent in agents:
            load_balancer.add_agent(agent)
        
        # Mark one agent as unhealthy
        load_balancer.mark_agent_unhealthy("failover_agent_1")
        
        # Verify failover behavior
        task = {"task_id": "failover_test", "resource_requirement": 20}
        selection = load_balancer.select_agent_for_task(task)
        
        assert selection["success"] is True
        assert selection["selected_agent"] == "failover_agent_2"  # Only healthy agent
    
    def test_load_redistribution(self, load_balancer):
        """Test load redistribution when agents become unavailable"""
        # Setup agents with tasks
        agents = [
            {"agent_id": "redist_agent_1", "capacity": 100, "current_load": 80},
            {"agent_id": "redist_agent_2", "capacity": 100, "current_load": 60},
            {"agent_id": "redist_agent_3", "capacity": 100, "current_load": 40}
        ]
        
        for agent in agents:
            load_balancer.add_agent(agent)
        
        # Remove heavily loaded agent
        redistribution_result = load_balancer.remove_agent("redist_agent_1")
        
        assert redistribution_result["success"] is True
        assert "redistributed_tasks" in redistribution_result
        
        # Verify remaining agents are available for new tasks
        remaining_agents = load_balancer.get_available_agents()
        assert len(remaining_agents) == 2
        assert "redist_agent_1" not in [agent["agent_id"] for agent in remaining_agents]


class TestOrchestrator:
    """Test complete orchestrator functionality"""
    
    @pytest.fixture
    async def orchestrator(self) -> Orchestrator:
        """Create orchestrator for testing"""
        config = OrchestratorConfig(
            max_agents=50,
            max_concurrent_workflows=20,
            enable_monitoring=True,
            enable_fault_tolerance=True,
            resource_management=True,
            load_balancing=True
        )
        orch = Orchestrator(config)
        await orch.initialize()
        
        yield orch
        
        await orch.shutdown()
    
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        config = OrchestratorConfig()
        orch = Orchestrator(config)
        
        assert not orch.initialized
        assert orch.status == OrchestratorStatus.STOPPED
        
        await orch.initialize()
        assert orch.initialized
        assert orch.status == OrchestratorStatus.RUNNING
        
        await orch.shutdown()
        assert not orch.initialized
        assert orch.status == OrchestratorStatus.STOPPED
    
    async def test_agent_lifecycle_management(self, orchestrator):
        """Test complete agent lifecycle management"""
        # Register multiple agents
        agents = [
            {
                "agent_id": "lifecycle_content_creator",
                "agent_type": "ContentCreatorAgent",
                "capabilities": ["content_generation", "image_creation"],
                "resource_requirements": {"cpu": 2, "memory": 4, "gpu": 0}
            },
            {
                "agent_id": "lifecycle_social_manager", 
                "agent_type": "SocialMediaManagerAgent",
                "capabilities": ["social_posting", "analytics"],
                "resource_requirements": {"cpu": 1, "memory": 2, "gpu": 0}
            },
            {
                "agent_id": "lifecycle_audio_specialist",
                "agent_type": "AudioSpecialistAgent",
                "capabilities": ["audio_processing", "voice_synthesis"],
                "resource_requirements": {"cpu": 3, "memory": 8, "gpu": 1}
            }
        ]
        
        # Register agents
        for agent in agents:
            registration_result = await orchestrator.register_agent(agent)
            assert registration_result["success"] is True
        
        # Verify registration
        registered_agents = await orchestrator.get_registered_agents()
        assert len(registered_agents) == 3
        
        # Start agents
        for agent in agents:
            start_result = await orchestrator.start_agent(agent["agent_id"])
            assert start_result["success"] is True
        
        # Verify agents are running
        for agent in agents:
            status = await orchestrator.get_agent_status(agent["agent_id"])
            assert status["status"] == "running"
        
        # Stop and deregister agents
        for agent in agents:
            stop_result = await orchestrator.stop_agent(agent["agent_id"])
            assert stop_result["success"] is True
            
            deregister_result = await orchestrator.deregister_agent(agent["agent_id"])
            assert deregister_result["success"] is True
    
    async def test_workflow_orchestration(self, orchestrator):
        """Test multi-agent workflow orchestration"""
        # Register agents for workflow
        content_agent = {
            "agent_id": "workflow_content_creator",
            "agent_type": "ContentCreatorAgent",
            "capabilities": ["content_generation"]
        }
        
        social_agent = {
            "agent_id": "workflow_social_manager",
            "agent_type": "SocialMediaManagerAgent", 
            "capabilities": ["social_posting"]
        }
        
        analytics_agent = {
            "agent_id": "workflow_analytics",
            "agent_type": "AnalyticsAgent",
            "capabilities": ["performance_analysis"]
        }
        
        await orchestrator.register_agent(content_agent)
        await orchestrator.register_agent(social_agent)
        await orchestrator.register_agent(analytics_agent)
        
        # Define workflow
        workflow_definition = {
            "workflow_id": "content_creation_workflow",
            "name": "Content Creation and Publishing",
            "steps": [
                {
                    "step_id": "generate_content",
                    "agent_type": "ContentCreatorAgent",
                    "task_type": "content_generation",
                    "parameters": {"content_type": "video", "duration": 60}
                },
                {
                    "step_id": "publish_content",
                    "agent_type": "SocialMediaManagerAgent",
                    "task_type": "social_posting",
                    "parameters": {"platform": "tiktok"},
                    "dependencies": ["generate_content"]
                },
                {
                    "step_id": "analyze_performance",
                    "agent_type": "AnalyticsAgent",
                    "task_type": "performance_analysis",
                    "dependencies": ["publish_content"]
                }
            ]
        }
        
        # Execute workflow
        execution_result = await orchestrator.execute_workflow(workflow_definition)
        
        assert execution_result["success"] is True
        assert "workflow_execution_id" in execution_result
        
        # Monitor workflow execution
        workflow_id = execution_result["workflow_execution_id"]
        max_wait_time = 120
        wait_time = 0
        
        while wait_time < max_wait_time:
            status = await orchestrator.get_workflow_status(workflow_id)
            
            if status["status"] in ["completed", "failed"]:
                break
                
            await asyncio.sleep(2)
            wait_time += 2
        
        # Verify workflow completion
        final_status = await orchestrator.get_workflow_status(workflow_id)
        assert final_status["status"] in ["completed", "failed"]
        
        if final_status["status"] == "completed":
            assert "completed_steps" in final_status
            assert len(final_status["completed_steps"]) == 3
    
    async def test_dynamic_scaling(self, orchestrator):
        """Test dynamic scaling of agents"""
        # Register base agent configuration
        agent_template = {
            "agent_type": "ContentCreatorAgent",
            "capabilities": ["content_generation"],
            "resource_requirements": {"cpu": 2, "memory": 4, "gpu": 0}
        }
        
        # Request scaling up
        scaling_request = {
            "agent_type": "ContentCreatorAgent",
            "action": "scale_up",
            "target_count": 3,
            "reason": "high_demand"
        }
        
        scaling_result = await orchestrator.handle_scaling_request(scaling_request)
        
        assert scaling_result["success"] is True
        assert "scaled_agents" in scaling_result
        
        # Verify agents were created
        content_agents = await orchestrator.get_agents_by_type("ContentCreatorAgent")
        assert len(content_agents) >= 3
        
        # Request scaling down
        scale_down_request = {
            "agent_type": "ContentCreatorAgent",
            "action": "scale_down",
            "target_count": 1,
            "reason": "low_demand"
        }
        
        scale_down_result = await orchestrator.handle_scaling_request(scale_down_request)
        assert scale_down_result["success"] is True
    
    async def test_fault_tolerance(self, orchestrator):
        """Test fault tolerance and recovery"""
        # Register agents
        agent_info = {
            "agent_id": "fault_test_agent",
            "agent_type": "TestAgent",
            "capabilities": ["test_capability"]
        }
        
        await orchestrator.register_agent(agent_info)
        await orchestrator.start_agent("fault_test_agent")
        
        # Simulate agent failure
        failure_simulation = await orchestrator.simulate_agent_failure("fault_test_agent")
        assert failure_simulation["success"] is True
        
        # Verify fault detection
        await asyncio.sleep(2)  # Allow time for detection
        
        fault_status = await orchestrator.get_fault_status()
        assert "detected_faults" in fault_status
        
        # Verify recovery mechanism
        recovery_result = await orchestrator.trigger_recovery("fault_test_agent")
        assert recovery_result["success"] is True
        
        # Verify agent is back online
        agent_status = await orchestrator.get_agent_status("fault_test_agent")
        assert agent_status["status"] in ["running", "recovering"]
    
    async def test_performance_monitoring(self, orchestrator):
        """Test system performance monitoring"""
        # Generate some activity
        agent_info = {
            "agent_id": "monitoring_test_agent",
            "agent_type": "TestAgent",
            "capabilities": ["test"]
        }
        
        await orchestrator.register_agent(agent_info)
        await orchestrator.start_agent("monitoring_test_agent")
        
        # Execute some tasks to generate metrics
        task_requests = [
            {"task_type": "test_task", "agent_id": "monitoring_test_agent"},
            {"task_type": "test_task", "agent_id": "monitoring_test_agent"}
        ]
        
        for task in task_requests:
            await orchestrator.submit_task(task)
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Get performance metrics
        performance_metrics = await orchestrator.get_performance_metrics()
        
        assert "system_metrics" in performance_metrics
        assert "agent_metrics" in performance_metrics
        assert "resource_utilization" in performance_metrics
        assert "throughput" in performance_metrics
        
        # Verify metric values
        system_metrics = performance_metrics["system_metrics"]
        assert "total_agents" in system_metrics
        assert "active_workflows" in system_metrics
        assert "tasks_processed" in system_metrics
    
    async def test_concurrent_workflow_execution(self, orchestrator):
        """Test concurrent workflow execution"""
        # Register agents for multiple workflows
        agents = [
            {"agent_id": "concurrent_content_1", "agent_type": "ContentCreatorAgent", "capabilities": ["content_generation"]},
            {"agent_id": "concurrent_content_2", "agent_type": "ContentCreatorAgent", "capabilities": ["content_generation"]},
            {"agent_id": "concurrent_social_1", "agent_type": "SocialMediaManagerAgent", "capabilities": ["social_posting"]},
            {"agent_id": "concurrent_social_2", "agent_type": "SocialMediaManagerAgent", "capabilities": ["social_posting"]}
        ]
        
        for agent in agents:
            await orchestrator.register_agent(agent)
        
        # Define multiple workflows
        workflows = [
            {
                "workflow_id": "concurrent_workflow_1",
                "name": "Workflow 1",
                "steps": [
                    {"step_id": "step1", "agent_type": "ContentCreatorAgent", "task_type": "content_generation"},
                    {"step_id": "step2", "agent_type": "SocialMediaManagerAgent", "task_type": "social_posting", "dependencies": ["step1"]}
                ]
            },
            {
                "workflow_id": "concurrent_workflow_2",
                "name": "Workflow 2", 
                "steps": [
                    {"step_id": "step1", "agent_type": "ContentCreatorAgent", "task_type": "content_generation"},
                    {"step_id": "step2", "agent_type": "SocialMediaManagerAgent", "task_type": "social_posting", "dependencies": ["step1"]}
                ]
            }
        ]
        
        # Execute workflows concurrently
        execution_tasks = [orchestrator.execute_workflow(workflow) for workflow in workflows]
        execution_results = await asyncio.gather(*execution_tasks)
        
        # Verify both workflows started successfully
        assert len(execution_results) == 2
        for result in execution_results:
            assert result["success"] is True
        
        # Monitor concurrent execution
        workflow_ids = [result["workflow_execution_id"] for result in execution_results]
        
        max_wait_time = 60
        wait_time = 0
        completed_workflows = 0
        
        while wait_time < max_wait_time and completed_workflows < 2:
            completed_workflows = 0
            
            for workflow_id in workflow_ids:
                status = await orchestrator.get_workflow_status(workflow_id)
                if status["status"] in ["completed", "failed"]:
                    completed_workflows += 1
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # Verify workflows completed
        assert completed_workflows >= 1  # At least one should complete
    
    @pytest.mark.performance
    async def test_orchestrator_performance(self, orchestrator, assert_performance):
        """Test orchestrator performance under load"""
        # Test agent registration performance
        start_time = datetime.now(timezone.utc)
        
        registration_tasks = []
        for i in range(10):
            agent_info = {
                "agent_id": f"perf_agent_{i}",
                "agent_type": "TestAgent",
                "capabilities": ["test"]
            }
            registration_tasks.append(orchestrator.register_agent(agent_info))
        
        await asyncio.gather(*registration_tasks)
        
        registration_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        assert registration_time < 10.0  # Should register 10 agents within 10 seconds
        
        assert_performance("agent_registration", max_time=10.0)
    
    async def test_system_health_checks(self, orchestrator):
        """Test system health monitoring"""
        # Get overall system health
        health_status = await orchestrator.get_system_health()
        
        assert "overall_status" in health_status
        assert "component_health" in health_status
        assert "resource_status" in health_status
        assert "performance_indicators" in health_status
        
        # Verify health status values
        assert health_status["overall_status"] in ["healthy", "degraded", "critical"]
        
        # Check component health
        component_health = health_status["component_health"]
        assert "agent_registry" in component_health
        assert "resource_manager" in component_health
        assert "load_balancer" in component_health
        
        # Check resource status
        resource_status = health_status["resource_status"]
        assert "cpu_utilization" in resource_status
        assert "memory_utilization" in resource_status
        assert "available_agents" in resource_status
    
    async def test_configuration_updates(self, orchestrator):
        """Test dynamic configuration updates"""
        # Get current configuration
        current_config = await orchestrator.get_configuration()
        assert current_config is not None
        
        # Update configuration
        config_updates = {
            "max_concurrent_workflows": 30,
            "load_balancing_algorithm": "least_connections",
            "health_check_interval": 45
        }
        
        update_result = await orchestrator.update_configuration(config_updates)
        assert update_result["success"] is True
        
        # Verify configuration was updated
        updated_config = await orchestrator.get_configuration()
        assert updated_config["max_concurrent_workflows"] == 30
        assert updated_config["load_balancing_algorithm"] == "least_connections"
        assert updated_config["health_check_interval"] == 45
    
    async def test_emergency_shutdown(self, orchestrator):
        """Test emergency shutdown procedures"""
        # Register some agents
        agents = [
            {"agent_id": "emergency_agent_1", "agent_type": "TestAgent", "capabilities": ["test"]},
            {"agent_id": "emergency_agent_2", "agent_type": "TestAgent", "capabilities": ["test"]}
        ]
        
        for agent in agents:
            await orchestrator.register_agent(agent)
            await orchestrator.start_agent(agent["agent_id"])
        
        # Trigger emergency shutdown
        shutdown_result = await orchestrator.emergency_shutdown()
        
        assert shutdown_result["success"] is True
        assert "shutdown_reason" in shutdown_result
        assert "agents_stopped" in shutdown_result
        
        # Verify system is in shutdown state
        system_status = await orchestrator.get_system_status()
        assert system_status["status"] in ["shutting_down", "stopped"]
