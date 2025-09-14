"""🎭 Mock Service Manager - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + TESTING_ARCHITECT + BACKEND_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive mocking service for external dependencies, APIs, databases,
and third-party services to enable isolated testing environments.
================================================================
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from contextlib import contextmanager, asynccontextmanager
import inspect
import redis
from pathlib import Path

logger = logging.getLogger(__name__)

class MockType(Enum):
    """Types of mocks available"""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    ASYNC_FUNCTION = "async_function"
    ASYNC_METHOD = "async_method"
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    REDIS_CACHE = "redis_cache"
    AI_MODEL = "ai_model"

class MockBehavior(Enum):
    """Mock behavior types"""
    RETURN_VALUE = "return_value"
    RETURN_FUNCTION = "return_function"
    SIDE_EFFECT = "side_effect"
    EXCEPTION = "exception"
    ASYNC_RETURN = "async_return"
    SEQUENCE = "sequence"
    CONDITIONAL = "conditional"

@dataclass
class MockConfiguration:
    """Mock configuration definition"""
    name: str
    mock_type: MockType
    target: str  # Module path or target identifier
    behavior: MockBehavior
    return_value: Any = None
    side_effect: Optional[Union[Callable, Exception, List]] = None
    call_count: int = 0
    max_calls: Optional[int] = None
    delay: float = 0.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

@dataclass
class MockInteraction:
    """Record of mock interaction"""
    mock_name: str
    call_args: tuple
    call_kwargs: Dict[str, Any]
    return_value: Any
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    exception: Optional[str] = None

@dataclass
class MockSession:
    """Mock session for grouped mocking"""
    session_id: str
    mocks: Dict[str, MockConfiguration] = field(default_factory=dict)
    interactions: List[MockInteraction] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    active: bool = True

class MockServiceManager:
    """
    Comprehensive mock service manager for testing isolation
    """
    
    def __init__(self, project_root -> None: Optional[str] = None) -> None:
        """Initialize mock service manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.active_mocks: Dict[str, Mock] = {}
        self.mock_configs: Dict[str, MockConfiguration] = {}
        self.mock_sessions: Dict[str, MockSession] = {}
        self.interactions: List[MockInteraction] = []
        self.patches: List[Any] = []
        
        # Initialize predefined mocks
        self._initialize_platform_mocks()

    def _initialize_platform_mocks(self) -> None:
        """Initialize platform-specific mock configurations"""
        
        # Database mocks
        self.register_mock(MockConfiguration(
            name="mongodb_client",
            mock_type=MockType.DATABASE,
            target="motor.motor_asyncio.AsyncIOMotorClient",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_mongodb_client
        ))
        
        self.register_mock(MockConfiguration(
            name="redis_client",
            mock_type=MockType.REDIS_CACHE,
            target="redis.Redis",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_redis_client
        ))
        
        # API mocks
        self.register_mock(MockConfiguration(
            name="openai_client",
            mock_type=MockType.EXTERNAL_SERVICE,
            target="openai.OpenAI",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_openai_client
        ))
        
        self.register_mock(MockConfiguration(
            name="stripe_client",
            mock_type=MockType.EXTERNAL_SERVICE,
            target="stripe.api_requestor",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_stripe_client
        ))
        
        # AI Model mocks
        self.register_mock(MockConfiguration(
            name="torch_model",
            mock_type=MockType.AI_MODEL,
            target="torch.nn.Module.forward",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_torch_forward
        ))
        
        # File system mocks
        self.register_mock(MockConfiguration(
            name="file_operations",
            mock_type=MockType.FUNCTION,
            target="builtins.open",
            behavior=MockBehavior.RETURN_FUNCTION,
            return_value=self._mock_file_operations
        ))

    def register_mock(self, config -> None: MockConfiguration) -> None:
        """Register a mock configuration"""
        self.mock_configs[config.name] = config
        self.logger.info(f"Registered mock configuration: {config.name}")

    def create_session(self, session_id: str) -> MockSession:
        """Create a new mock session"""
        session = MockSession(session_id=session_id)
        self.mock_sessions[session_id] = session
        self.logger.info(f"Created mock session: {session_id}")
        return session

    @contextmanager
    def mock_context(self, mock_names -> None: List[str], session_id -> None: Optional[str] = None) -> None:
        """Context manager for temporary mocking"""
        session = None
        if session_id:
            session = self.mock_sessions.get(session_id) or self.create_session(session_id)
        
        activated_mocks = []
        
        try:
            # Activate mocks
            for mock_name in mock_names:
                if mock_name in self.mock_configs:
                    mock_obj = self.activate_mock(mock_name, session)
                    activated_mocks.append((mock_name, mock_obj))
            
            yield {name: mock_obj for name, mock_obj in activated_mocks}
            
        finally:
            # Deactivate mocks
            for mock_name, _ in activated_mocks:
                self.deactivate_mock(mock_name)

    @asynccontextmanager
    async def async_mock_context(self, mock_names -> None: List[str], session_id -> None: Optional[str] = None) -> None:
        """Async context manager for temporary mocking"""
        session = None
        if session_id:
            session = self.mock_sessions.get(session_id) or self.create_session(session_id)
        
        activated_mocks = []
        
        try:
            # Activate mocks
            for mock_name in mock_names:
                if mock_name in self.mock_configs:
                    mock_obj = self.activate_mock(mock_name, session)
                    activated_mocks.append((mock_name, mock_obj))
            
            yield {name: mock_obj for name, mock_obj in activated_mocks}
            
        finally:
            # Deactivate mocks
            for mock_name, _ in activated_mocks:
                self.deactivate_mock(mock_name)

    def activate_mock(self, mock_name: str, session: Optional[MockSession] = None) -> Mock:
        """Activate a specific mock"""
        if mock_name not in self.mock_configs:
            raise ValueError(f"Mock configuration '{mock_name}' not found")
        
        config = self.mock_configs[mock_name]
        
        if not config.active:
            self.logger.warning(f"Mock '{mock_name}' is disabled")
            return None
        
        # Create the appropriate mock object
        mock_obj = self._create_mock_object(config)
        
        # Apply the mock using patch
        if config.target:
            patcher = patch(config.target, mock_obj)
            patcher.start()
            self.patches.append(patcher)
        
        # Store active mock
        self.active_mocks[mock_name] = mock_obj
        
        # Add to session if provided
        if session:
            session.mocks[mock_name] = config
        
        self.logger.info(f"Activated mock: {mock_name}")
        return mock_obj

    def deactivate_mock(self, mock_name -> None: str) -> None:
        """Deactivate a specific mock"""
        if mock_name in self.active_mocks:
            del self.active_mocks[mock_name]
        
        # Stop patches (simplified - in production would track individual patches)
        for patcher in self.patches:
            try:
                patcher.stop()
            except:
                pass
        self.patches.clear()
        
        self.logger.info(f"Deactivated mock: {mock_name}")

    def deactivate_all_mocks(self) -> None:
        """Deactivate all active mocks"""
        for mock_name in list(self.active_mocks.keys()):
            self.deactivate_mock(mock_name)

    def _create_mock_object(self, config: MockConfiguration) -> Mock:
        """Create appropriate mock object based on configuration"""
        
        if config.mock_type in [MockType.ASYNC_FUNCTION, MockType.ASYNC_METHOD]:
            mock_obj = AsyncMock()
        else:
            mock_obj = Mock()
        
        # Configure behavior
        if config.behavior == MockBehavior.RETURN_VALUE:
            if config.mock_type in [MockType.ASYNC_FUNCTION, MockType.ASYNC_METHOD]:
                mock_obj.return_value = asyncio.coroutine(lambda: config.return_value)()
            else:
                mock_obj.return_value = config.return_value
                
        elif config.behavior == MockBehavior.RETURN_FUNCTION:
            if callable(config.return_value):
                mock_obj.side_effect = self._wrap_mock_function(config)
            else:
                mock_obj.return_value = config.return_value
                
        elif config.behavior == MockBehavior.SIDE_EFFECT:
            mock_obj.side_effect = config.side_effect
            
        elif config.behavior == MockBehavior.EXCEPTION:
            mock_obj.side_effect = config.side_effect or Exception("Mock exception")
            
        elif config.behavior == MockBehavior.SEQUENCE:
            if isinstance(config.side_effect, list):
                mock_obj.side_effect = config.side_effect
                
        # Add tracking
        mock_obj.side_effect = self._wrap_with_tracking(mock_obj.side_effect or mock_obj.return_value, config)
        
        return mock_obj

    def _wrap_mock_function(self, config: MockConfiguration) -> Callable:
        """Wrap mock function with tracking and delay"""
        original_func = config.return_value
        
        def wrapped_function(*args, **kwargs) -> None:
            start_time = time.time()
            
            # Add delay if specified
            if config.delay > 0:
                time.sleep(config.delay)
            
            # Check call count limits
            if config.max_calls and config.call_count >= config.max_calls:
                raise Exception(f"Mock '{config.name}' exceeded maximum calls ({config.max_calls})")
            
            # Call original function
            try:
                if inspect.iscoroutinefunction(original_func):
                    # Handle async functions
                    async def async_wrapper() -> None:
                        result = await original_func(*args, **kwargs)
                        self._record_interaction(config, args, kwargs, result, time.time() - start_time)
                        return result
                    return async_wrapper()
                else:
                    result = original_func(*args, **kwargs)
                    self._record_interaction(config, args, kwargs, result, time.time() - start_time)
                    return result
                    
            except Exception as e:
                self._record_interaction(config, args, kwargs, None, time.time() - start_time, str(e))
                raise
        
        return wrapped_function

    def _wrap_with_tracking(self, original_behavior: Any, config: MockConfiguration) -> Callable:
        """Wrap any mock behavior with tracking"""
        def tracking_wrapper(*args, **kwargs) -> None:
            start_time = time.time()
            config.call_count += 1
            
            try:
                if callable(original_behavior):
                    result = original_behavior(*args, **kwargs)
                else:
                    result = original_behavior
                
                self._record_interaction(config, args, kwargs, result, time.time() - start_time)
                return result
                
            except Exception as e:
                self._record_interaction(config, args, kwargs, None, time.time() - start_time, str(e))
                raise
        
        return tracking_wrapper

    def _record_interaction(
        self, 
        config -> None: MockConfiguration, 
        args -> None: tuple, 
        kwargs -> None: Dict[str, Any], 
        result -> None: Any, 
        execution_time -> None: float,
        exception -> None: Optional[str] = None
    ) -> None:
        """Record mock interaction"""
        interaction = MockInteraction(
            mock_name=config.name,
            call_args=args,
            call_kwargs=kwargs,
            return_value=result,
            execution_time=execution_time,
            exception=exception
        )
        
        self.interactions.append(interaction)

    # Platform-specific mock implementations
    def _mock_mongodb_client(self, *args, **kwargs) -> None:
        """Mock MongoDB client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        # Configure database and collection access
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Configure common operations
        mock_collection.find_one = AsyncMock(return_value={"_id": "test", "data": "mock_data"})
        mock_collection.find = AsyncMock(return_value=[{"_id": "test", "data": "mock_data"}])
        mock_collection.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
        mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        mock_collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        
        return mock_client

    def _mock_redis_client(self, *args, **kwargs) -> None:
        """Mock Redis client"""
        mock_redis = Mock()
        
        # In-memory storage for testing
        mock_storage = {}
        
        def mock_get(key) -> None:
            return mock_storage.get(key)
        
        def mock_set(key, value, **kwargs) -> None:
            mock_storage[key] = value
            return True
        
        def mock_delete(key) -> None:
            return mock_storage.pop(key, None) is not None
        
        def mock_exists(key) -> None:
            return key in mock_storage
        
        mock_redis.get = mock_get
        mock_redis.set = mock_set
        mock_redis.delete = mock_delete
        mock_redis.exists = mock_exists
        mock_redis.flushall = lambda: mock_storage.clear()
        
        return mock_redis

    def _mock_openai_client(self, *args, **kwargs) -> None:
        """Mock OpenAI client"""
        mock_client = Mock()
        mock_completions = Mock()
        mock_embeddings = Mock()
        
        # Mock chat completions
        mock_completions.create = Mock(return_value=Mock(
            choices=[Mock(
                message=Mock(content="This is a mock AI response"),
                finish_reason="stop"
            )],
            usage=Mock(total_tokens=50)
        ))
        
        # Mock embeddings
        mock_embeddings.create = Mock(return_value=Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        ))
        
        mock_client.chat = Mock(completions=mock_completions)
        mock_client.embeddings = mock_embeddings
        
        return mock_client

    def _mock_stripe_client(self, *args, **kwargs) -> None:
        """Mock Stripe client"""
        mock_stripe = Mock()
        
        # Mock payment methods
        mock_stripe.PaymentIntent.create = Mock(return_value=Mock(
            id="pi_test_123",
            status="succeeded",
            amount=1000,
            currency="usd"
        ))
        
        mock_stripe.Customer.create = Mock(return_value=Mock(
            id="cus_test_123",
            email="test@example.com"
        ))
        
        return mock_stripe

    def _mock_torch_forward(self, *args, **kwargs) -> None:
        """Mock PyTorch model forward pass"""
        import torch
        # Return a mock tensor
        return torch.randn(1, 10)  # Assuming output shape

    def _mock_file_operations(self, filename, mode='r', **kwargs) -> None:
        """Mock file operations"""
        mock_file = Mock()
        
        if 'r' in mode:
            mock_file.read.return_value = "Mock file content"
            mock_file.readline.return_value = "Mock line"
            mock_file.readlines.return_value = ["Mock line 1\n", "Mock line 2\n"]
        
        mock_file.write.return_value = 10
        mock_file.close.return_value = None
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        return mock_file

    # Utility methods
    def get_mock_stats(self, mock_name: str) -> Dict[str, Any]:
        """Get statistics for a specific mock"""
        if mock_name not in self.mock_configs:
            return {}
        
        config = self.mock_configs[mock_name]
        interactions = [i for i in self.interactions if i.mock_name == mock_name]
        
        return {
            "call_count": config.call_count,
            "total_interactions": len(interactions),
            "average_execution_time": sum(i.execution_time for i in interactions) / len(interactions) if interactions else 0,
            "exceptions": len([i for i in interactions if i.exception]),
            "last_call": interactions[-1].timestamp if interactions else None
        }

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a mock session"""
        if session_id not in self.mock_sessions:
            return {}
        
        session = self.mock_sessions[session_id]
        session_interactions = [i for i in self.interactions 
                              if i.mock_name in session.mocks and 
                              i.timestamp >= session.start_time]
        
        return {
            "session_id": session_id,
            "active_mocks": len(session.mocks),
            "total_interactions": len(session_interactions),
            "session_duration": (datetime.utcnow() - session.start_time).total_seconds(),
            "mocks": list(session.mocks.keys())
        }

    def verify_mock_calls(self, mock_name: str, expected_calls: int) -> bool:
        """Verify number of calls to a mock"""
        if mock_name not in self.mock_configs:
            return False
        
        actual_calls = self.mock_configs[mock_name].call_count
        return actual_calls == expected_calls

    def verify_mock_called_with(self, mock_name: str, *args, **kwargs) -> bool:
        """Verify mock was called with specific arguments"""
        interactions = [i for i in self.interactions if i.mock_name == mock_name]
        
        for interaction in interactions:
            if interaction.call_args == args and interaction.call_kwargs == kwargs:
                return True
        
        return False

    def reset_mock(self, mock_name -> None: str) -> None:
        """Reset a specific mock's state"""
        if mock_name in self.mock_configs:
            self.mock_configs[mock_name].call_count = 0
        
        # Remove interactions for this mock
        self.interactions = [i for i in self.interactions if i.mock_name != mock_name]
        
        # Reset the mock object if active
        if mock_name in self.active_mocks:
            self.active_mocks[mock_name].reset_mock()

    def reset_all_mocks(self) -> None:
        """Reset all mocks"""
        for mock_name in self.mock_configs:
            self.reset_mock(mock_name)

    def export_interactions(self, format: str = "json") -> str:
        """Export mock interactions"""
        if format == "json":
            return self._export_json_interactions()
        elif format == "csv":
            return self._export_csv_interactions()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json_interactions(self) -> str:
        """Export interactions as JSON"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_interactions": len(self.interactions),
            "interactions": [
                {
                    "mock_name": i.mock_name,
                    "call_args": str(i.call_args),
                    "call_kwargs": i.call_kwargs,
                    "return_value": str(i.return_value),
                    "execution_time": i.execution_time,
                    "timestamp": i.timestamp.isoformat(),
                    "exception": i.exception
                }
                for i in self.interactions
            ]
        }
        return json.dumps(data, indent=2)

    def _export_csv_interactions(self) -> str:
        """Export interactions as CSV"""
        lines = ["Mock Name,Timestamp,Execution Time,Exception,Args,Kwargs"]
        for interaction in self.interactions:
            lines.append(
                f"{interaction.mock_name},"
                f"{interaction.timestamp.isoformat()},"
                f"{interaction.execution_time:.3f},"
                f"{interaction.exception or ''},"
                f"\"{str(interaction.call_args)}\","
                f"\"{str(interaction.call_kwargs)}\""
            )
        return "\n".join(lines)

    def create_smart_mock(self, target_class: type, **kwargs) -> Mock:
        """Create a smart mock that mimics the target class interface"""
        mock_obj = Mock(spec=target_class)
        
        # Auto-mock methods based on the class
        for attr_name in dir(target_class):
            if not attr_name.startswith('_'):
                attr = getattr(target_class, attr_name)
                if callable(attr):
                    if inspect.iscoroutinefunction(attr):
                        setattr(mock_obj, attr_name, AsyncMock())
                    else:
                        setattr(mock_obj, attr_name, Mock())
        
        return mock_obj

# Global mock service manager instance
mock_service_manager = MockServiceManager()

__all__ = [
    "MockServiceManager",
    "MockConfiguration",
    "MockInteraction",
    "MockSession",
    "MockType",
    "MockBehavior",
    "mock_service_manager"
]