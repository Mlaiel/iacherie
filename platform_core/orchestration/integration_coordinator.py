"""
Integration Coordinator - Platform Core Enterprise Architecture
External system integration management for Ainflue AI Creator Platform

© 2025 Fahed Mlaiel. All rights reserved.
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import ssl
import time

# Platform Core Imports
from ..utils.base_classes import EnterpriseComponent
from ..utils.exceptions import IntegrationError, ValidationError
from ..utils.metrics import MetricsCollector
from ..security.auth_manager import AuthenticationManager

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Integration type classifications."""
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    STREAMING = "streaming"
    BLOCKCHAIN = "blockchain"
    THIRD_PARTY_SERVICE = "third_party_service"

class IntegrationStatus(Enum):
    """Integration status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    TESTING = "testing"

class SynchronizationMode(Enum):
    """Data synchronization modes."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"

@dataclass
class IntegrationConfig:
    """Integration configuration."""
    name: str
    type: IntegrationType
    endpoint: Optional[str] = None
    credentials: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 100  # requests per minute
    timeout: int = 30      # seconds
    retry_attempts: int = 3
    sync_mode: SynchronizationMode = SynchronizationMode.EVENT_DRIVEN
    health_check_interval: int = 300  # 5 minutes
    data_mapping: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationSession:
    """Integration session tracking."""
    id: str
    config: IntegrationConfig
    status: IntegrationStatus
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0
    last_error: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class SyncTask:
    """Data synchronization task."""
    id: str
    integration_id: str
    source: str
    destination: str
    data_type: str
    sync_mode: SynchronizationMode
    status: str = "pending"
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    records_processed: int = 0
    errors: List[str] = field(default_factory=list)

class IntegrationCoordinator(EnterpriseComponent):
    """
    Enterprise integration management and coordination system.
    
    Features:
    - External system integration management
    - API gateway coordination
    - Third-party service integration
    - Data synchronization coordination
    - Real-time monitoring and health checks
    - Rate limiting and throttling
    - Error handling and retry logic
    - Performance optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.integrations: Dict[str, IntegrationSession] = {}
        self.sync_tasks: Dict[str, SyncTask] = {}
        self.active_connections: Dict[str, Any] = {}
        self.metrics_collector = MetricsCollector("integration_coordinator")
        self.auth_manager = AuthenticationManager()
        
        # Configuration
        self.max_concurrent_syncs = config.get("max_concurrent_syncs", 10)
        self.default_timeout = config.get("default_timeout", 30)
        self.health_check_interval = config.get("health_check_interval", 300)
        self.rate_limit_window = config.get("rate_limit_window", 60)  # seconds
        
        # Rate limiting
        self.rate_limit_counters: Dict[str, Dict[str, int]] = {}
        
        logger.info("IntegrationCoordinator initialized successfully")

    async def register_integration(
        self,
        config: IntegrationConfig,
        user_id: str = None
    ) -> str:
        """Register a new integration."""
        try:
            # Validate configuration
            await self._validate_integration_config(config)
            
            # Check authorization
            if user_id and not await self.auth_manager.authorize_integration(user_id, config.name):
                raise ValidationError(f"User {user_id} not authorized for integration")
            
            # Generate integration ID
            integration_id = f"integration_{config.name}_{int(time.time())}"
            
            # Create integration session
            session = IntegrationSession(
                id=integration_id,
                config=config,
                status=IntegrationStatus.TESTING
            )
            
            # Test connection
            connection_test = await self._test_connection(session)
            if not connection_test:
                session.status = IntegrationStatus.FAILED
                session.last_error = "Connection test failed"
            else:
                session.status = IntegrationStatus.ACTIVE
            
            self.integrations[integration_id] = session
            
            # Start health monitoring
            if session.status == IntegrationStatus.ACTIVE:
                await self._start_health_monitoring(integration_id)
            
            self.metrics_collector.increment("integrations_registered")
            logger.info(f"Integration registered: {integration_id}")
            
            return integration_id
            
        except Exception as e:
            logger.error(f"Failed to register integration: {str(e)}")
            raise IntegrationError(f"Integration registration failed: {str(e)}")

    async def create_sync_task(
        self,
        integration_id: str,
        source: str,
        destination: str,
        data_type: str,
        sync_mode: SynchronizationMode = SynchronizationMode.EVENT_DRIVEN
    ) -> str:
        """Create a data synchronization task."""
        try:
            # Validate integration exists
            if integration_id not in self.integrations:
                raise IntegrationError(f"Integration {integration_id} not found")
            
            session = self.integrations[integration_id]
            if session.status != IntegrationStatus.ACTIVE:
                raise IntegrationError(f"Integration {integration_id} is not active")
            
            # Generate task ID
            task_id = f"sync_{integration_id}_{int(time.time())}"
            
            # Create sync task
            task = SyncTask(
                id=task_id,
                integration_id=integration_id,
                source=source,
                destination=destination,
                data_type=data_type,
                sync_mode=sync_mode
            )
            
            self.sync_tasks[task_id] = task
            
            # Execute based on sync mode
            if sync_mode == SynchronizationMode.REAL_TIME:
                await self._execute_sync_task(task_id)
            elif sync_mode == SynchronizationMode.SCHEDULED:
                await self._schedule_sync_task(task_id)
            
            self.metrics_collector.increment("sync_tasks_created")
            logger.info(f"Sync task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create sync task: {str(e)}")
            raise IntegrationError(f"Sync task creation failed: {str(e)}")

    async def execute_integration_call(
        self,
        integration_id: str,
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Execute an API call through an integration."""
        try:
            session = self.integrations.get(integration_id)
            if not session:
                raise IntegrationError(f"Integration {integration_id} not found")
            
            if session.status != IntegrationStatus.ACTIVE:
                raise IntegrationError(f"Integration {integration_id} is not active")
            
            # Check rate limiting
            if not await self._check_rate_limit(integration_id):
                raise IntegrationError("Rate limit exceeded")
            
            # Execute the call
            start_time = time.time()
            response = await self._make_api_call(session, endpoint, method, data, headers)
            execution_time = time.time() - start_time
            
            # Update metrics
            session.success_count += 1
            session.performance_metrics["avg_response_time"] = execution_time
            
            self.metrics_collector.record("api_call_duration", execution_time)
            self.metrics_collector.increment("api_calls_successful")
            
            logger.info(f"API call executed successfully for integration {integration_id}")
            return response
            
        except Exception as e:
            # Update error metrics
            if integration_id in self.integrations:
                self.integrations[integration_id].error_count += 1
                self.integrations[integration_id].last_error = str(e)
            
            self.metrics_collector.increment("api_calls_failed")
            logger.error(f"API call failed: {str(e)}")
            raise IntegrationError(f"API call failed: {str(e)}")

    async def synchronize_data(
        self,
        integration_id: str,
        data_type: str,
        source_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synchronize data with external system."""
        try:
            session = self.integrations.get(integration_id)
            if not session:
                raise IntegrationError(f"Integration {integration_id} not found")
            
            # Apply data mapping
            mapped_data = await self._apply_data_mapping(source_data, session.config.data_mapping)
            
            # Apply filters
            filtered_data = await self._apply_filters(mapped_data, session.config.filters)
            
            # Execute synchronization
            result = await self._execute_data_sync(session, filtered_data, data_type)
            
            # Update session
            session.last_sync = datetime.now()
            
            self.metrics_collector.increment("data_syncs_completed")
            logger.info(f"Data synchronization completed for integration {integration_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Data synchronization failed: {str(e)}")
            raise IntegrationError(f"Data synchronization failed: {str(e)}")

    async def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """Get integration status and metrics."""
        try:
            session = self.integrations.get(integration_id)
            if not session:
                raise IntegrationError(f"Integration {integration_id} not found")
            
            return {
                "id": session.id,
                "name": session.config.name,
                "type": session.config.type.value,
                "status": session.status.value,
                "last_sync": session.last_sync.isoformat() if session.last_sync else None,
                "next_sync": session.next_sync.isoformat() if session.next_sync else None,
                "success_count": session.success_count,
                "error_count": session.error_count,
                "last_error": session.last_error,
                "performance_metrics": session.performance_metrics,
                "health_score": await self._calculate_health_score(session)
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status: {str(e)}")
            raise IntegrationError(f"Status retrieval failed: {str(e)}")

    async def list_integrations(self, status_filter: IntegrationStatus = None) -> List[Dict[str, Any]]:
        """List all integrations with optional status filter."""
        try:
            integrations_list = []
            
            for integration_id, session in self.integrations.items():
                if status_filter and session.status != status_filter:
                    continue
                
                integrations_list.append({
                    "id": session.id,
                    "name": session.config.name,
                    "type": session.config.type.value,
                    "status": session.status.value,
                    "last_sync": session.last_sync.isoformat() if session.last_sync else None,
                    "success_count": session.success_count,
                    "error_count": session.error_count
                })
            
            return integrations_list
            
        except Exception as e:
            logger.error(f"Failed to list integrations: {str(e)}")
            raise IntegrationError(f"Failed to list integrations: {str(e)}")

    async def deactivate_integration(self, integration_id: str) -> bool:
        """Deactivate an integration."""
        try:
            session = self.integrations.get(integration_id)
            if not session:
                raise IntegrationError(f"Integration {integration_id} not found")
            
            session.status = IntegrationStatus.INACTIVE
            
            # Stop health monitoring
            await self._stop_health_monitoring(integration_id)
            
            # Close active connections
            if integration_id in self.active_connections:
                await self._close_connection(integration_id)
            
            self.metrics_collector.increment("integrations_deactivated")
            logger.info(f"Integration deactivated: {integration_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate integration: {str(e)}")
            raise IntegrationError(f"Integration deactivation failed: {str(e)}")

    # Private Methods
    
    async def _validate_integration_config(self, config: IntegrationConfig) -> None:
        """Validate integration configuration."""
        if not config.name:
            raise ValidationError("Integration name is required")
        
        if config.rate_limit <= 0:
            raise ValidationError("Rate limit must be positive")
        
        if config.timeout <= 0:
            raise ValidationError("Timeout must be positive")
        
        if config.retry_attempts < 0:
            raise ValidationError("Retry attempts cannot be negative")

    async def _test_connection(self, session: IntegrationSession) -> bool:
        """Test integration connection."""
        try:
            if session.config.type == IntegrationType.API:
                return await self._test_api_connection(session)
            elif session.config.type == IntegrationType.DATABASE:
                return await self._test_database_connection(session)
            elif session.config.type == IntegrationType.MESSAGE_QUEUE:
                return await self._test_message_queue_connection(session)
            else:
                # Default connection test
                return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    async def _test_api_connection(self, session: IntegrationSession) -> bool:
        """Test API connection."""
        try:
            if not session.config.endpoint:
                return False
            
            timeout = aiohttp.ClientTimeout(total=session.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as client:
                async with client.get(session.config.endpoint) as response:
                    return response.status < 500
                    
        except Exception:
            return False

    async def _test_database_connection(self, session: IntegrationSession) -> bool:
        """Test database connection."""
        # Simulate database connection test
        await asyncio.sleep(0.1)
        return True

    async def _test_message_queue_connection(self, session: IntegrationSession) -> bool:
        """Test message queue connection."""
        # Simulate message queue connection test
        await asyncio.sleep(0.1)
        return True

    async def _start_health_monitoring(self, integration_id: str) -> None:
        """Start health monitoring for integration."""
        logger.info(f"Starting health monitoring for integration {integration_id}")
        # In real implementation, would start background monitoring task

    async def _stop_health_monitoring(self, integration_id: str) -> None:
        """Stop health monitoring for integration."""
        logger.info(f"Stopping health monitoring for integration {integration_id}")
        # In real implementation, would stop background monitoring task

    async def _check_rate_limit(self, integration_id: str) -> bool:
        """Check if integration is within rate limits."""
        session = self.integrations.get(integration_id)
        if not session:
            return False
        
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # Initialize counter if not exists
        if integration_id not in self.rate_limit_counters:
            self.rate_limit_counters[integration_id] = {}
        
        # Clean old entries
        self.rate_limit_counters[integration_id] = {
            timestamp: count for timestamp, count in self.rate_limit_counters[integration_id].items()
            if timestamp > window_start
        }
        
        # Count current requests
        total_requests = sum(self.rate_limit_counters[integration_id].values())
        
        if total_requests >= session.config.rate_limit:
            return False
        
        # Increment counter
        self.rate_limit_counters[integration_id][current_time] = \
            self.rate_limit_counters[integration_id].get(current_time, 0) + 1
        
        return True

    async def _make_api_call(
        self,
        session: IntegrationSession,
        endpoint: str,
        method: str,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Make API call with retry logic."""
        last_exception = None
        
        for attempt in range(session.config.retry_attempts + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=session.config.timeout)
                
                # Prepare headers
                call_headers = {"Content-Type": "application/json"}
                if headers:
                    call_headers.update(headers)
                
                # Add authentication if configured
                if "api_key" in session.config.credentials:
                    call_headers["Authorization"] = f"Bearer {session.config.credentials['api_key']}"
                
                async with aiohttp.ClientSession(timeout=timeout) as client:
                    if method.upper() == "GET":
                        async with client.get(endpoint, headers=call_headers) as response:
                            return await response.json()
                    elif method.upper() == "POST":
                        async with client.post(endpoint, json=data, headers=call_headers) as response:
                            return await response.json()
                    elif method.upper() == "PUT":
                        async with client.put(endpoint, json=data, headers=call_headers) as response:
                            return await response.json()
                    elif method.upper() == "DELETE":
                        async with client.delete(endpoint, headers=call_headers) as response:
                            return await response.json()
                    else:
                        raise IntegrationError(f"Unsupported HTTP method: {method}")
                        
            except Exception as e:
                last_exception = e
                if attempt < session.config.retry_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    logger.warning(f"API call attempt {attempt + 1} failed, retrying...")
                else:
                    logger.error(f"API call failed after {attempt + 1} attempts")
        
        raise last_exception

    async def _apply_data_mapping(
        self,
        data: List[Dict[str, Any]],
        mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Apply data field mapping."""
        if not mapping:
            return data
        
        mapped_data = []
        for record in data:
            mapped_record = {}
            for source_field, target_field in mapping.items():
                if source_field in record:
                    mapped_record[target_field] = record[source_field]
            mapped_data.append(mapped_record)
        
        return mapped_data

    async def _apply_filters(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply data filters."""
        if not filters:
            return data
        
        filtered_data = []
        for record in data:
            include_record = True
            for field, filter_value in filters.items():
                if field in record and record[field] != filter_value:
                    include_record = False
                    break
            
            if include_record:
                filtered_data.append(record)
        
        return filtered_data

    async def _execute_data_sync(
        self,
        session: IntegrationSession,
        data: List[Dict[str, Any]],
        data_type: str
    ) -> Dict[str, Any]:
        """Execute data synchronization."""
        try:
            # Simulate data synchronization
            await asyncio.sleep(0.5)
            
            return {
                "status": "success",
                "records_processed": len(data),
                "data_type": data_type,
                "sync_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data sync execution failed: {str(e)}")
            raise IntegrationError(f"Data sync failed: {str(e)}")

    async def _execute_sync_task(self, task_id: str) -> None:
        """Execute a sync task."""
        task = self.sync_tasks.get(task_id)
        if not task:
            return
        
        try:
            task.status = "running"
            task.start_time = datetime.now()
            
            # Simulate sync execution
            await asyncio.sleep(1)
            task.progress = 100.0
            task.records_processed = 100  # Simulated
            
            task.status = "completed"
            task.end_time = datetime.now()
            
        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            task.end_time = datetime.now()

    async def _schedule_sync_task(self, task_id: str) -> None:
        """Schedule a sync task for later execution."""
        task = self.sync_tasks.get(task_id)
        if not task:
            return
        
        # In real implementation, would schedule task in task queue
        logger.info(f"Sync task {task_id} scheduled for execution")

    async def _calculate_health_score(self, session: IntegrationSession) -> float:
        """Calculate integration health score."""
        if session.success_count + session.error_count == 0:
            return 1.0
        
        success_rate = session.success_count / (session.success_count + session.error_count)
        
        # Adjust for recent errors
        if session.last_error and session.error_count > 0:
            success_rate *= 0.9
        
        return min(1.0, max(0.0, success_rate))

    async def _close_connection(self, integration_id: str) -> None:
        """Close active connection."""
        if integration_id in self.active_connections:
            # Close connection resources
            del self.active_connections[integration_id]
            logger.info(f"Connection closed for integration {integration_id}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get coordinator health status."""
        active_integrations = sum(1 for session in self.integrations.values() 
                                 if session.status == IntegrationStatus.ACTIVE)
        
        total_success = sum(session.success_count for session in self.integrations.values())
        total_errors = sum(session.error_count for session in self.integrations.values())
        
        return {
            "status": "healthy",
            "active_integrations": active_integrations,
            "total_integrations": len(self.integrations),
            "active_sync_tasks": len([task for task in self.sync_tasks.values() if task.status == "running"]),
            "success_rate": total_success / (total_success + total_errors) if (total_success + total_errors) > 0 else 1.0,
            "metrics": await self.metrics_collector.get_summary()
        }

    async def cleanup(self) -> None:
        """Cleanup coordinator resources."""
        try:
            # Deactivate all integrations
            for integration_id in list(self.integrations.keys()):
                await self.deactivate_integration(integration_id)
            
            logger.info("IntegrationCoordinator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")