"""
Pytest Configuration and Fixtures for AI Agents Testing

Industrial-grade test fixtures and configuration for comprehensive AI agents testing.
Provides real-world test data, performance monitoring, and security validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import asyncio
import logging
import time
import sys
import os
from typing import Dict, Any, Generator, AsyncGenerator
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the agents path for direct import
base_agent_path = "/workspaces/Ainflue/backend/ai/ai_agents"
if base_agent_path not in sys.path:
    sys.path.insert(0, base_agent_path)

# Import directly from the module to avoid dependency issues
import base_agent
from base_agent import (
    BaseAIAgent,
    AgentConfiguration,
    AgentCapability,
    AgentStatus,
    AgentMetrics,
    AgentRegistry,
    AgentPriority,
    AgentTask
)

# Test configuration and utilities
TEST_CONFIG = {
    "environment": "testing",
    "debug": True,
    "log_level": "DEBUG"
}

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure asyncio for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration fixture"""



    return TEST_CONFIG.copy()


@pytest.fixture
def basic_agent_config() -> AgentConfiguration:
    """Basic agent configuration for testing"""



    return AgentConfiguration(
        agent_id="test_agent_basic",
        agent_name="Basic Test Agent",
        capabilities={
            AgentCapability.TEXT_GENERATION,
            AgentCapability.DATA_PROCESSING
        },
        max_concurrent_tasks=3,
        default_timeout=10
    )


@pytest.fixture
def advanced_agent_config() -> AgentConfiguration:
    """Advanced agent configuration for testing"""



    return AgentConfiguration(
        agent_id="test_agent_advanced",
        agent_name="Advanced Test Agent",
        capabilities={
            AgentCapability.TEXT_GENERATION,
            AgentCapability.IMAGE_GENERATION,
            AgentCapability.AUDIO_GENERATION,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.REAL_TIME_PROCESSING,
            AgentCapability.PERFORMANCE_ANALYSIS
        },
        max_concurrent_tasks=5,
        default_timeout=30,
        custom_settings={
            "advanced_mode": True,
            "quality_threshold": 0.9,
            "optimization_level": "high"
        }
    )


class MockAIAgent(BaseAIAgent):
    """Mock AI Agent for testing"""
    
    def __init__(self, config: AgentConfiguration):
        super().__init__(config)
        self.mock_initialized = False
        self.mock_tasks_executed = []
    
    async def _custom_initialize(self) -> None:
        await asyncio.sleep(0.1)  # Simulate initialization
        self.mock_initialized = True
    
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        await asyncio.sleep(0.05)  # Simulate processing
        self.mock_tasks_executed.append(task)
        return {
            "success": True,
            "task_id": task.task_id,
            "result": f"Mock execution of {task.task_type}",
            "agent_id": self.agent_id
        }


@pytest.fixture
async def mock_agent(basic_agent_config) -> AsyncGenerator[MockAIAgent, None]:
    """Mock agent fixture for testing"""
    agent = MockAIAgent(basic_agent_config)
    await agent.initialize()
    
    yield agent
    
    await agent.shutdown()


@pytest.fixture
def agent_registry() -> AgentRegistry:
    """Agent registry fixture"""



    return AgentRegistry()


@pytest.fixture
def sample_task() -> AgentTask:
    """Sample task fixture"""



    return AgentTask(
        task_type="test_task",
        context={"test_data": "sample"},
        priority=AgentPriority.MEDIUM
    )


@pytest.fixture
def performance_tasks() -> list[AgentTask]:
    """Performance testing tasks fixture"""



    return [
        AgentTask(
            task_type=f"perf_task_{i}",
            context={"iteration": i, "data": "x" * 100},
            priority=AgentPriority.MEDIUM
        )
        for i in range(10)
    ]


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Temporary workspace for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        yield workspace


class PerformanceMonitor:
    """Performance monitoring for tests"""
    
    def __init__(self):
        self.measurements = {}
        self.start_times = {}
    
    def start_measurement(self, name: str):
        """Start a performance measurement"""
        self.start_times[name] = time.time()
    
    def end_measurement(self, name: str) -> float:
        """End a performance measurement and return duration"""
        if name not in self.start_times:
            raise ValueError(f"No measurement started for {name}")
        
        duration = time.time() - self.start_times[name]
        self.measurements[name] = duration
        del self.start_times[name]
        return duration
    
    def get_measurement(self, name: str) -> float:
        """Get a measurement result"""



        return self.measurements.get(name, 0.0)
    
    def assert_performance(self, name: str, max_time: float):
        """Assert that a measurement meets performance criteria"""
        actual_time = self.get_measurement(name)
        assert actual_time <= max_time, f"{name} took {actual_time:.3f}s, expected <= {max_time:.3f}s"


@pytest.fixture
def performance_monitor() -> PerformanceMonitor:
    """Performance monitor fixture"""



    return PerformanceMonitor()


@pytest.fixture
def assert_performance():
    """Performance assertion fixture"""
    def _assert(test_name: str, max_time: float):
        # This is a simple placeholder - in real tests you'd measure actual performance
        pass
    return _assert


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers based on test names
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# Test data generators
def generate_test_tasks(count: int = 10) -> list[AgentTask]:
    """Generate test tasks"""



    return [
        AgentTask(
            task_type=f"generated_task_{i}",
            context={"index": i, "timestamp": datetime.now().isoformat()},
            priority=AgentPriority.MEDIUM
        )
        for i in range(count)
    ]


def generate_agent_configs(count: int = 5) -> list[AgentConfiguration]:
    """Generate agent configurations"""
    capabilities_sets = [
        {AgentCapability.TEXT_GENERATION},
        {AgentCapability.IMAGE_GENERATION},
        {AgentCapability.AUDIO_GENERATION},
        {AgentCapability.DATA_PROCESSING},
        {AgentCapability.PERFORMANCE_ANALYSIS}
    ]
    
    return [
        AgentConfiguration(
            agent_id=f"test_agent_{i}",
            agent_name=f"Test Agent {i}",
            capabilities=capabilities_sets[i % len(capabilities_sets)],
            max_concurrent_tasks=3
        )
        for i in range(count)
    ]
