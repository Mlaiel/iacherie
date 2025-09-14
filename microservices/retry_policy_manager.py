"""
Retry Policy Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔄 RETRY POLICY MANAGER
======================

Advanced retry mechanism orchestration service for the Ainflue platform.
Provides intelligent retry policies, exponential backoff, jitter, and failure analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Type
from dataclasses import dataclass, asdict
from enum import Enum
import functools
import inspect
from collections import deque, defaultdict
import json
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Retry strategy enumeration"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    CUSTOM = "custom"

class StopCondition(Enum):
    """Stop condition for retries"""
    MAX_ATTEMPTS = "max_attempts"
    MAX_DELAY = "max_delay"
    MAX_TOTAL_TIME = "max_total_time"
    CUSTOM = "custom"

@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    name: str
    max_attempts: int = 3
    base_delay: float = 1.0                    # Base delay in seconds
    max_delay: float = 60.0                    # Maximum delay in seconds
    backoff_multiplier: float = 2.0            # Multiplier for exponential backoff
    jitter: bool = True                        # Add random jitter
    jitter_range: float = 0.1                  # Jitter range (0.0 to 1.0)
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: List[Type[Exception]] = None
    non_retryable_exceptions: List[Type[Exception]] = None
    timeout_per_attempt: float = 30.0          # Timeout for each attempt
    total_timeout: float = 300.0               # Total timeout for all attempts
    retry_on_result: Optional[Callable] = None  # Function to check if result should trigger retry

@dataclass
class RetryAttempt:
    """Retry attempt information"""
    attempt_number: int
    delay: float
    timestamp: datetime
    exception: Optional[Exception] = None
    result: Any = None
    success: bool = False
    response_time: float = 0.0

@dataclass
class RetryExecution:
    """Retry execution record"""
    id: str
    policy_name: str
    function_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_attempts: int = 0
    success: bool = False
    final_result: Any = None
    final_exception: Optional[Exception] = None
    attempts: List[RetryAttempt] = None
    total_delay: float = 0.0
    total_execution_time: float = 0.0

class BackoffCalculator:
    """Calculate backoff delays for different strategies"""
    
    @staticmethod
    def fixed_delay(attempt: int, base_delay: float, **kwargs) -> float:
        """Fixed delay strategy"""
        return base_delay
    
    @staticmethod
    def exponential_backoff(attempt: int, base_delay: float, 
                           backoff_multiplier: float = 2.0, **kwargs) -> float:
        """Exponential backoff strategy"""
        return base_delay * (backoff_multiplier ** (attempt - 1))
    
    @staticmethod
    def linear_backoff(attempt: int, base_delay: float, **kwargs) -> float:
        """Linear backoff strategy"""
        return base_delay * attempt
    
    @staticmethod
    def fibonacci_backoff(attempt: int, base_delay: float, **kwargs) -> float:
        """Fibonacci backoff strategy"""
        def fibonacci(n) -> None:
            if n <= 1:
                return 1
            return fibonacci(n - 1) + fibonacci(n - 2)
        
        return base_delay * fibonacci(attempt)
    
    @staticmethod
    def apply_jitter(delay: float, jitter_range: float = 0.1) -> float:
        """Apply jitter to delay"""
        jitter = random.uniform(-jitter_range, jitter_range)
        return delay * (1 + jitter)
    
    @staticmethod
    def calculate_delay(policy: RetryPolicy, attempt: int) -> float:
        """Calculate delay for a specific attempt"""
        if policy.strategy == RetryStrategy.FIXED_DELAY:
            delay = BackoffCalculator.fixed_delay(attempt, policy.base_delay)
        elif policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = BackoffCalculator.exponential_backoff(
                attempt, policy.base_delay, policy.backoff_multiplier
            )
        elif policy.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = BackoffCalculator.linear_backoff(attempt, policy.base_delay)
        elif policy.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = BackoffCalculator.fibonacci_backoff(attempt, policy.base_delay)
        else:
            delay = policy.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, policy.max_delay)
        
        # Apply jitter if enabled
        if policy.jitter:
            delay = BackoffCalculator.apply_jitter(delay, policy.jitter_range)
        
        return max(0, delay)  # Ensure non-negative delay

class RetryException(Exception):
    """Base exception for retry operations"""
    pass

class MaxAttemptsExceededException(RetryException):
    """Exception raised when maximum attempts are exceeded"""
    pass

class TotalTimeoutExceededException(RetryException):
    """Exception raised when total timeout is exceeded"""
    pass

class RetryPolicyManager:
    """Advanced retry mechanism orchestration service"""
    
    def __init__(self) -> None:
        self.service_name = "RetryPolicyManager"
        self.version = "1.0.0"
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.retry_executions: Dict[str, RetryExecution] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.monitoring_enabled = True
        self.monitoring_task: Optional[asyncio.Task] = None
        self.execution_history: deque = deque(maxlen=1000)
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(self, redis_url -> None: str = "redis -> None://localhost -> None:6379/0") -> None:
        """Initialize the retry policy manager"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Create default retry policies
            self._create_default_policies()
            
            # Start monitoring
            await self.start_monitoring()
            
            logger.info(f"🔄 {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.service_name}: {str(e)}")
            return False
    
    def _create_default_policies(self) -> None:
        """Create default retry policies"""
        default_policies = [
            RetryPolicy(
                name="default",
                max_attempts=3,
                base_delay=1.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                retryable_exceptions=[ConnectionError, TimeoutError]
            ),
            RetryPolicy(
                name="aggressive",
                max_attempts=5,
                base_delay=0.5,
                max_delay=30.0,
                backoff_multiplier=1.5,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            RetryPolicy(
                name="conservative",
                max_attempts=2,
                base_delay=2.0,
                max_delay=10.0,
                strategy=RetryStrategy.FIXED_DELAY,
                jitter=False
            ),
            RetryPolicy(
                name="database",
                max_attempts=3,
                base_delay=1.0,
                max_delay=60.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                timeout_per_attempt=10.0,
                retryable_exceptions=[ConnectionError]
            ),
            RetryPolicy(
                name="api_call",
                max_attempts=4,
                base_delay=2.0,
                max_delay=120.0,
                strategy=RetryStrategy.FIBONACCI_BACKOFF,
                timeout_per_attempt=30.0
            )
        ]
        
        for policy in default_policies:
            self.add_retry_policy(policy)
        
        logger.info(f"🔧 Created {len(default_policies)} default retry policies")
    
    def add_retry_policy(self, policy -> None: RetryPolicy) -> None:
        """Add a retry policy"""
        # Set default retryable exceptions if none specified
        if policy.retryable_exceptions is None:
            policy.retryable_exceptions = [Exception]
        
        if policy.non_retryable_exceptions is None:
            policy.non_retryable_exceptions = []
        
        self.retry_policies[policy.name] = policy
        logger.info(f"➕ Added retry policy: {policy.name}")
    
    def get_retry_policy(self, name: str) -> Optional[RetryPolicy]:
        """Get a retry policy by name"""
        return self.retry_policies.get(name)
    
    def retry(self, policy_name -> None: str = "default") -> None:
        """Decorator for retry functionality"""
        def decorator(func -> None: Callable) -> None:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> None:
                return await self.execute_with_retry(policy_name, func, *args, **kwargs)
            return wrapper
        return decorator
    
    async def execute_with_retry(self, policy_name: str, func: Callable, 
                                *args, **kwargs) -> Any:
        """Execute a function with retry policy"""
        policy = self.get_retry_policy(policy_name)
        if not policy:
            raise ValueError(f"Retry policy '{policy_name}' not found")
        
        execution_id = f"retry_{int(time.time())}_{hash(func.__name__) % 10000}"
        execution = RetryExecution(
            id=execution_id,
            policy_name=policy_name,
            function_name=func.__name__,
            start_time=datetime.now(),
            attempts=[]
        )
        
        self.retry_executions[execution_id] = execution
        
        try:
            result = await self._execute_with_retries(policy, func, execution, *args, **kwargs)
            execution.success = True
            execution.final_result = result
            return result
            
        except Exception as e:
            execution.success = False
            execution.final_exception = e
            raise
            
        finally:
            execution.end_time = datetime.now()
            execution.total_execution_time = (
                execution.end_time - execution.start_time
            ).total_seconds()
            
            self.execution_history.append(execution)
            await self._save_execution_to_storage(execution)
    
    async def _execute_with_retries(self, policy: RetryPolicy, func: Callable,
                                   execution: RetryExecution, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt_number in range(1, policy.max_attempts + 1):
            # Check total timeout
            if execution.start_time:
                elapsed_time = (datetime.now() - execution.start_time).total_seconds()
                if elapsed_time >= policy.total_timeout:
                    raise TotalTimeoutExceededException(
                        f"Total timeout of {policy.total_timeout}s exceeded"
                    )
            
            attempt_start_time = datetime.now()
            attempt = RetryAttempt(
                attempt_number=attempt_number,
                delay=0.0,
                timestamp=attempt_start_time
            )
            
            try:
                # Execute the function with timeout
                if inspect.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=policy.timeout_per_attempt
                    )
                else:
                    # Run sync function in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, functools.partial(func, *args, **kwargs)
                    )
                
                attempt.success = True
                attempt.result = result
                attempt.response_time = (datetime.now() - attempt_start_time).total_seconds()
                execution.attempts.append(attempt)
                execution.total_attempts = attempt_number
                
                # Check if result should trigger retry
                if policy.retry_on_result and policy.retry_on_result(result):
                    logger.warning(f"⚠️ Result triggered retry for attempt {attempt_number}")
                    if attempt_number < policy.max_attempts:
                        await self._apply_delay(policy, attempt_number + 1, execution)
                        continue
                
                logger.info(f"✅ Retry execution succeeded on attempt {attempt_number}")
                return result
                
            except Exception as e:
                attempt.success = False
                attempt.exception = e
                attempt.response_time = (datetime.now() - attempt_start_time).total_seconds()
                execution.attempts.append(attempt)
                execution.total_attempts = attempt_number
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(policy, e):
                    logger.error(f"❌ Non-retryable exception: {type(e).__name__}")
                    raise e
                
                logger.warning(f"⚠️ Attempt {attempt_number} failed: {str(e)}")
                
                # If this is the last attempt, raise the exception
                if attempt_number >= policy.max_attempts:
                    break
                
                # Apply delay before next attempt
                await self._apply_delay(policy, attempt_number + 1, execution)
        
        # All attempts failed
        raise MaxAttemptsExceededException(
            f"Maximum attempts ({policy.max_attempts}) exceeded. "
            f"Last exception: {str(last_exception)}"
        ) from last_exception
    
    def _is_retryable_exception(self, policy: RetryPolicy, exception: Exception) -> bool:
        """Check if an exception is retryable based on policy"""
        # Check non-retryable exceptions first
        for non_retryable in policy.non_retryable_exceptions:
            if isinstance(exception, non_retryable):
                return False
        
        # Check retryable exceptions
        for retryable in policy.retryable_exceptions:
            if isinstance(exception, retryable):
                return True
        
        return False
    
    async def _apply_delay(self, policy -> None: RetryPolicy, next_attempt -> None: int, 
                          execution -> None: RetryExecution) -> None:
        """Apply delay before next retry attempt"""
        delay = BackoffCalculator.calculate_delay(policy, next_attempt)
        execution.total_delay += delay
        
        logger.info(f"⏳ Waiting {delay:.2f}s before attempt {next_attempt}")
        await asyncio.sleep(delay)
    
    async def start_monitoring(self) -> None:
        """Start monitoring retry operations"""
        if self.monitoring_task is None and self.monitoring_enabled:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("📊 Retry policy monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring retry operations"""
        self.monitoring_enabled = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("📊 Retry policy monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Monitor retry operations and store metrics"""
        while self.monitoring_enabled:
            try:
                # Collect retry statistics
                stats = self._calculate_statistics()
                
                # Store metrics in Redis
                if self.redis_client and stats:
                    metrics_data = {
                        'timestamp': datetime.now().isoformat(),
                        'retry_statistics': stats
                    }
                    
                    await self.redis_client.set(
                        'retry_policy:metrics',
                        json.dumps(metrics_data)
                    )
                    
                    # Store metrics history
                    await self.redis_client.lpush(
                        'retry_policy:metrics_history',
                        json.dumps(metrics_data)
                    )
                    await self.redis_client.ltrim('retry_policy:metrics_history', 0, 999)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate retry operation statistics"""
        if not self.execution_history:
            return {}
        
        # Overall statistics
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for ex in self.execution_history if ex.success)
        
        # Per-policy statistics
        policy_stats = defaultdict(lambda: {
            'executions': 0,
            'successes': 0,
            'failures': 0,
            'total_attempts': 0,
            'average_attempts': 0.0,
            'success_rate': 0.0
        })
        
        for execution in self.execution_history:
            stats = policy_stats[execution.policy_name]
            stats['executions'] += 1
            stats['total_attempts'] += execution.total_attempts
            
            if execution.success:
                stats['successes'] += 1
            else:
                stats['failures'] += 1
        
        # Calculate derived metrics
        for policy_name, stats in policy_stats.items():
            if stats['executions'] > 0:
                stats['average_attempts'] = stats['total_attempts'] / stats['executions']
                stats['success_rate'] = stats['successes'] / stats['executions'] * 100
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'overall_success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0,
            'policy_statistics': dict(policy_stats)
        }
    
    async def _save_execution_to_storage(self, execution -> None: RetryExecution) -> None:
        """Save retry execution to Redis storage"""
        if self.redis_client:
            try:
                execution_data = asdict(execution)
                
                # Convert datetime objects to ISO strings
                execution_data['start_time'] = execution.start_time.isoformat()
                if execution.end_time:
                    execution_data['end_time'] = execution.end_time.isoformat()
                
                # Convert attempts
                if execution.attempts:
                    for attempt_data in execution_data['attempts']:
                        attempt_data['timestamp'] = attempt_data['timestamp'].isoformat()
                        if attempt_data.get('exception'):
                            attempt_data['exception'] = str(attempt_data['exception'])
                
                # Convert final exception
                if execution.final_exception:
                    execution_data['final_exception'] = str(execution.final_exception)
                
                await self.redis_client.hset(
                    'retry_policy:executions',
                    execution.id,
                    json.dumps(execution_data)
                )
                
            except Exception as e:
                logger.error(f"❌ Failed to save execution to storage: {str(e)}")
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry operation statistics"""
        return self._calculate_statistics()
    
    def get_execution_history(self, limit: int = 100) -> List[RetryExecution]:
        """Get retry execution history"""
        return list(self.execution_history)[-limit:]
    
    def get_policy_list(self) -> List[str]:
        """Get list of available retry policies"""
        return list(self.retry_policies.keys())
    
    def get_policy_details(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific retry policy"""
        policy = self.get_retry_policy(policy_name)
        if policy:
            policy_dict = asdict(policy)
            # Convert enums to strings
            policy_dict['strategy'] = policy.strategy.value
            # Convert exception types to strings
            if policy.retryable_exceptions:
                policy_dict['retryable_exceptions'] = [
                    exc.__name__ for exc in policy.retryable_exceptions
                ]
            if policy.non_retryable_exceptions:
                policy_dict['non_retryable_exceptions'] = [
                    exc.__name__ for exc in policy.non_retryable_exceptions
                ]
            return policy_dict
        return None
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get retry policy manager health status"""
        stats = self._calculate_statistics()
        
        return {
            'service': self.service_name,
            'version': self.version,
            'total_policies': len(self.retry_policies),
            'total_executions': len(self.execution_history),
            'recent_success_rate': stats.get('overall_success_rate', 0),
            'monitoring_enabled': self.monitoring_enabled,
            'redis_connected': self.redis_client is not None,
            'timestamp': datetime.now().isoformat()
        }

# Service instance
retry_policy_manager = RetryPolicyManager()

# Example functions to test retry policies
async def unreliable_function() -> None:
    """Simulate an unreliable function"""
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError("Connection failed")
    
    await asyncio.sleep(0.1)
    return "Success!"

async def timeout_function() -> None:
    """Simulate a function that might timeout"""
    delay = random.uniform(0.1, 5.0)
    await asyncio.sleep(delay)
    return f"Completed after {delay:.2f}s"

def sync_unreliable_function() -> None:
    """Simulate an unreliable sync function"""
    if random.random() < 0.5:  # 50% failure rate
        raise ValueError("Random error")
    return "Sync success!"

# Example usage
async def main() -> None:
    """Example usage of the retry policy manager"""
    try:
        # Initialize service
        await retry_policy_manager.initialize()
        
        # Test direct execution with retry
        print("Testing direct execution with retry...")
        try:
            result = await retry_policy_manager.execute_with_retry(
                "aggressive", unreliable_function
            )
            print(f"Direct execution result: {result}")
        except Exception as e:
            print(f"Direct execution failed: {str(e)}")
        
        # Test with decorator
        @retry_policy_manager.retry("default")
        async def decorated_function() -> None:
            return await unreliable_function()
        
        print("\nTesting with decorator...")
        try:
            result = await decorated_function()
            print(f"Decorated execution result: {result}")
        except Exception as e:
            print(f"Decorated execution failed: {str(e)}")
        
        # Test sync function
        print("\nTesting sync function...")
        try:
            result = await retry_policy_manager.execute_with_retry(
                "conservative", sync_unreliable_function
            )
            print(f"Sync execution result: {result}")
        except Exception as e:
            print(f"Sync execution failed: {str(e)}")
        
        # Create custom policy
        custom_policy = RetryPolicy(
            name="custom_test",
            max_attempts=5,
            base_delay=0.5,
            strategy=RetryStrategy.FIBONACCI_BACKOFF,
            retryable_exceptions=[ConnectionError, ValueError]
        )
        retry_policy_manager.add_retry_policy(custom_policy)
        
        print("\nTesting custom policy...")
        try:
            result = await retry_policy_manager.execute_with_retry(
                "custom_test", unreliable_function
            )
            print(f"Custom policy result: {result}")
        except Exception as e:
            print(f"Custom policy failed: {str(e)}")
        
        # Get statistics
        print("\nRetry statistics:")
        stats = retry_policy_manager.get_retry_statistics()
        print(json.dumps(stats, indent=2))
        
        # Get service health
        health = await retry_policy_manager.get_service_health()
        print(f"\nService health: {json.dumps(health, indent=2)}")
        
        # List policies
        policies = retry_policy_manager.get_policy_list()
        print(f"\nAvailable policies: {policies}")
        
        # Get policy details
        for policy_name in policies[:3]:  # Show first 3 policies
            details = retry_policy_manager.get_policy_details(policy_name)
            print(f"\nPolicy '{policy_name}': {json.dumps(details, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    finally:
        await retry_policy_manager.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())