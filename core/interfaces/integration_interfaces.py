"""Integration interfaces for IA Influencer Agent.

Defines interfaces for third-party integrations, API clients,
webhooks, data synchronization and migration operations.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import asyncio


class IntegrationType(Enum):
    """Types of third-party integrations."""
    STREAMING_PLATFORM = "streaming_platform"
    SOCIAL_MEDIA = "social_media"
    PAYMENT_PROCESSOR = "payment_processor"
    CLOUD_STORAGE = "cloud_storage"
    ANALYTICS_PLATFORM = "analytics_platform"
    MESSAGING_SERVICE = "messaging_service"
    AI_SERVICE = "ai_service"
    COLLABORATION_TOOL = "collaboration_tool"
    CONTENT_DELIVERY = "content_delivery"


class SyncStrategy(Enum):
    """Data synchronization strategies."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    INCREMENTAL = "incremental"
    FULL_SYNC = "full_sync"
    BIDIRECTIONAL = "bidirectional"
    UNIDIRECTIONAL = "unidirectional"


class APIMethod(Enum):
    """HTTP API methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class WebhookEvent(Enum):
    """Webhook event types."""
    USER_CREATED = "user_created"
    CONTENT_UPLOADED = "content_uploaded"
    PAYMENT_PROCESSED = "payment_processed"
    COLLABORATION_STARTED = "collaboration_started"
    PROTECTION_ALERT = "protection_alert"
    REVENUE_EARNED = "revenue_earned"
    SYSTEM_ALERT = "system_alert"
    INTEGRATION_ERROR = "integration_error"


class SyncStatus(Enum):
    """Data synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class ThirdPartyIntegrationInterface(ABC):
    """Core interface for third-party service integrations."""
    
    @abstractmethod
    async def register_integration(
        self,
        integration_name: str,
        integration_type: IntegrationType,
        configuration: Dict[str, Any]
    ) -> str:
        """
        Register new third-party integration.
        
        Args:
            integration_name: Name of the integration
            integration_type: Type of integration service
            configuration: Integration configuration settings
            
        Returns:
            Integration registration ID
        """
        pass
    
    @abstractmethod
    async def configure_integration_auth(
        self,
        integration_id: str,
        auth_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure authentication for integration."""
        pass
    
    @abstractmethod
    async def test_integration_connection(
        self,
        integration_id: str
    ) -> Dict[str, Any]:
        """Test connection to third-party service."""
        pass
    
    @abstractmethod
    async def update_integration_config(
        self,
        integration_id: str,
        updated_config: Dict[str, Any]
    ) -> bool:
        """Update integration configuration."""
        pass
    
    @abstractmethod
    async def disable_integration(
        self,
        integration_id: str,
        disable_reason: str
    ) -> bool:
        """Temporarily disable integration."""
        pass
    
    @abstractmethod
    async def remove_integration(
        self,
        integration_id: str,
        cleanup_data: bool = False
    ) -> bool:
        """Permanently remove integration."""
        pass


class APIClientInterface(ABC):
    """Interface for API client operations."""
    
    @abstractmethod
    async def make_api_request(
        self,
        endpoint: str,
        method: APIMethod,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make HTTP API request to external service.
        
        Args:
            endpoint: API endpoint URL
            method: HTTP method to use
            headers: Request headers
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            API response data and metadata
        """
        pass
    
    @abstractmethod
    async def handle_api_rate_limiting(
        self,
        api_name: str,
        rate_limit_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle API rate limiting and backoff strategies."""
        pass
    
    @abstractmethod
    async def retry_failed_request(
        self,
        request_id: str,
        retry_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retry failed API request with exponential backoff."""
        pass
    
    @abstractmethod
    async def validate_api_response(
        self,
        response_data: Dict[str, Any],
        expected_schema: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate API response against expected schema."""
        pass
    
    @abstractmethod
    async def cache_api_response(
        self,
        cache_key: str,
        response_data: Dict[str, Any],
        cache_duration: int
    ) -> bool:
        """Cache API response for performance optimization."""
        pass
    
    @abstractmethod
    async def monitor_api_performance(
        self,
        api_name: str,
        performance_metrics: Dict[str, float]
    ) -> bool:
        """Monitor and log API performance metrics."""
        pass


class WebhookInterface(ABC):
    """Interface for webhook management."""
    
    @abstractmethod
    async def register_webhook_endpoint(
        self,
        webhook_url: str,
        event_types: List[WebhookEvent],
        webhook_config: Dict[str, Any]
    ) -> str:
        """
        Register webhook endpoint for event notifications.
        
        Args:
            webhook_url: URL to receive webhook notifications
            event_types: Types of events to subscribe to
            webhook_config: Webhook configuration settings
            
        Returns:
            Webhook registration ID
        """
        pass
    
    @abstractmethod
    async def send_webhook_notification(
        self,
        webhook_id: str,
        event_type: WebhookEvent,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send webhook notification for event."""
        pass
    
    @abstractmethod
    async def verify_webhook_signature(
        self,
        webhook_payload: bytes,
        signature: str,
        secret_key: str
    ) -> bool:
        """Verify webhook payload signature for security."""
        pass
    
    @abstractmethod
    async def handle_webhook_failure(
        self,
        webhook_id: str,
        failure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle webhook delivery failures and retries."""
        pass
    
    @abstractmethod
    async def update_webhook_config(
        self,
        webhook_id: str,
        updated_config: Dict[str, Any]
    ) -> bool:
        """Update webhook configuration and event subscriptions."""
        pass
    
    @abstractmethod
    async def deactivate_webhook(
        self,
        webhook_id: str,
        deactivation_reason: str
    ) -> bool:
        """Deactivate webhook endpoint."""
        pass


class DataSyncInterface(ABC):
    """Interface for data synchronization operations."""
    
    @abstractmethod
    async def initiate_data_sync(
        self,
        source_system: str,
        target_system: str,
        sync_config: Dict[str, Any]
    ) -> str:
        """
        Initiate data synchronization between systems.
        
        Args:
            source_system: Source system identifier
            target_system: Target system identifier
            sync_config: Synchronization configuration
            
        Returns:
            Synchronization job ID
        """
        pass
    
    @abstractmethod
    async def monitor_sync_progress(
        self,
        sync_job_id: str
    ) -> Dict[str, Any]:
        """Monitor data synchronization progress."""
        pass
    
    @abstractmethod
    async def resolve_sync_conflicts(
        self,
        sync_job_id: str,
        conflict_resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve data conflicts during synchronization."""
        pass
    
    @abstractmethod
    async def validate_sync_integrity(
        self,
        sync_job_id: str,
        validation_rules: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Validate data integrity after synchronization."""
        pass
    
    @abstractmethod
    async def schedule_recurring_sync(
        self,
        sync_schedule: Dict[str, Any],
        sync_targets: List[str]
    ) -> str:
        """Schedule recurring data synchronization."""
        pass
    
    @abstractmethod
    async def rollback_sync_operation(
        self,
        sync_job_id: str,
        rollback_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rollback data synchronization operation."""
        pass


class MigrationInterface(ABC):
    """Interface for data migration operations."""
    
    @abstractmethod
    async def plan_data_migration(
        self,
        migration_scope: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan data migration strategy and execution plan.
        
        Args:
            migration_scope: Scope of data to migrate
            target_schema: Target system schema definition
            
        Returns:
            Migration plan with steps and validation rules
        """
        pass
    
    @abstractmethod
    async def execute_migration_step(
        self,
        migration_plan_id: str,
        step_id: str,
        execution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific migration step."""
        pass
    
    @abstractmethod
    async def validate_migration_results(
        self,
        migration_plan_id: str,
        validation_criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate migration results against criteria."""
        pass
    
    @abstractmethod
    async def handle_migration_errors(
        self,
        migration_plan_id: str,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle and resolve migration errors."""
        pass
    
    @abstractmethod
    async def finalize_migration(
        self,
        migration_plan_id: str,
        finalization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Finalize migration and cleanup temporary resources."""
        pass
    
    @abstractmethod
    async def create_migration_backup(
        self,
        migration_plan_id: str,
        backup_config: Dict[str, Any]
    ) -> str:
        """Create backup before migration execution."""
        pass
