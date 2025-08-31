"""Stream Connector Manager for IA Influencer Agent Platform
========================================================

Universal connector management system for integrating with various
data sources, APIs, databases, and external services.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

from pydantic import BaseModel, Field
from redis.asyncio import Redis

from ...core.config import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ConnectorType(str, Enum):
    """Connector type enumeration"""    DATABASE = "database"
    API = "api"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    CLOUD_STORAGE = "cloud_storage"
    WEBHOOK = "webhook"
    STREAMING = "streaming"
    CACHE = "cache"


class ConnectionStatus(str, Enum):
    """Connection status enumeration"""    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class DataFormat(str, Enum):
    """Data format types"""    JSON = "json"
    XML = "xml"
    CSV = "csv"
    BINARY = "binary"
    TEXT = "text"
    AVRO = "avro"
    PARQUET = "parquet"


@dataclass
class ConnectorConfig:
    """Connector configuration"""    connector_id: str
    connector_type: ConnectorType
    name: str
    connection_params: Dict[str, Any]
    data_format: DataFormat = DataFormat.JSON
    enabled: bool = True
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    timeout_seconds: float = 30.0
    health_check_interval: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectionMetrics(BaseModel):
    """Connection performance metrics"""    total_requests: int = Field(default=0, description="Total requests made")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    avg_response_time: float = Field(default=0.0, description="Average response time")
    last_success: Optional[datetime] = Field(default=None, description="Last successful request")
    last_failure: Optional[datetime] = Field(default=None, description="Last failed request")
    uptime_percentage: float = Field(default=100.0, description="Uptime percentage")
    data_transferred_mb: float = Field(default=0.0, description="Data transferred in MB")


class BaseConnector(ABC):
    """Abstract base class for all connectors"""    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.status = ConnectionStatus.DISCONNECTED
        self.metrics = ConnectionMetrics()
        self.last_health_check = None
        self._connection = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection"""        pass
        
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection"""        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check connection health"""        pass
        
    @abstractmethod
    async def send_data(self, data: Any, **kwargs) -> bool:
        """Send data through connector"""        pass
        
    @abstractmethod
    async def receive_data(self, **kwargs) -> Optional[Any]:
        """Receive data through connector"""        pass
        
    async def get_status(self) -> ConnectionStatus:
        """Get connection status"""        return self.status
        
    async def get_metrics(self) -> ConnectionMetrics:
        """Get performance metrics"""        return self.metrics
        
    def _update_metrics(self, success: bool, response_time: float = 0, data_size: int = 0):
        """Update connection metrics"""        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
            self.metrics.last_success = datetime.now(timezone.utc)
        else:
            self.metrics.failed_requests += 1
            self.metrics.last_failure = datetime.now(timezone.utc)
            
        # Update average response time
        total_requests = self.metrics.total_requests
        current_avg = self.metrics.avg_response_time
        self.metrics.avg_response_time = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update data transferred
        self.metrics.data_transferred_mb += data_size / (1024 * 1024)
        
        # Update uptime percentage
        if total_requests > 0:
            self.metrics.uptime_percentage = (
                self.metrics.successful_requests / total_requests * 100
            )


class DatabaseConnector(BaseConnector):
    """Database connector implementation"""    
    async def connect(self) -> bool:
        try:
            self.status = ConnectionStatus.CONNECTING
            
            # Database connection logic here
            # This would use SQLAlchemy, asyncpg, etc.
            
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"Database connector {self.config.connector_id} connected")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"Database connection failed: {e}")
            return False
            
    async def disconnect(self) -> bool:
        try:
            if self._connection:
                await self._connection.close()
            self.status = ConnectionStatus.DISCONNECTED
            return True
        except Exception as e:
            logger.error(f"Database disconnect failed: {e}")
            return False
            
    async def health_check(self) -> bool:
        try:
            # Execute simple query to check health
            start_time = datetime.now(timezone.utc)
            # result = await self._connection.execute("SELECT 1")
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self._update_metrics(True, response_time)
            return True
            
        except Exception as e:
            self._update_metrics(False)
            logger.warning(f"Database health check failed: {e}")
            return False
            
    async def send_data(self, data: Any, **kwargs) -> bool:
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute database operation
            # await self._connection.execute(query, data)
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(json.dumps(data).encode()) if isinstance(data, dict) else len(str(data))
            
            self._update_metrics(True, response_time, data_size)
            return True
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"Database send failed: {e}")
            return False
            
    async def receive_data(self, **kwargs) -> Optional[Any]:
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute query
            # result = await self._connection.fetch(query)
            result = {}  # Placeholder
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(json.dumps(result).encode()) if result else 0
            
            self._update_metrics(True, response_time, data_size)
            return result
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"Database receive failed: {e}")
            return None


class APIConnector(BaseConnector):
    """REST API connector implementation"""    
    async def connect(self) -> bool:
        try:
            self.status = ConnectionStatus.CONNECTING
            
            # Initialize HTTP client
            import aiohttp
            self._connection = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"API connector {self.config.connector_id} connected")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"API connection failed: {e}")
            return False
            
    async def disconnect(self) -> bool:
        try:
            if self._connection:
                await self._connection.close()
            self.status = ConnectionStatus.DISCONNECTED
            return True
        except Exception as e:
            logger.error(f"API disconnect failed: {e}")
            return False
            
    async def health_check(self) -> bool:
        try:
            base_url = self.config.connection_params.get("base_url")
            health_endpoint = self.config.connection_params.get("health_endpoint", "/health")
            
            start_time = datetime.now(timezone.utc)
            async with self._connection.get(f"{base_url}{health_endpoint}") as response:
                success = response.status == 200
                
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_metrics(success, response_time)
            
            return success
            
        except Exception as e:
            self._update_metrics(False)
            logger.warning(f"API health check failed: {e}")
            return False
            
    async def send_data(self, data: Any, **kwargs) -> bool:
        try:
            endpoint = kwargs.get("endpoint", "/")
            method = kwargs.get("method", "POST")
            headers = kwargs.get("headers", {})
            
            base_url = self.config.connection_params.get("base_url")
            url = f"{base_url}{endpoint}"
            
            start_time = datetime.now(timezone.utc)
            
            async with self._connection.request(
                method, url, json=data, headers=headers
            ) as response:
                success = 200 <= response.status < 300
                
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(json.dumps(data).encode()) if isinstance(data, dict) else len(str(data))
            
            self._update_metrics(success, response_time, data_size)
            return success
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"API send failed: {e}")
            return False
            
    async def receive_data(self, **kwargs) -> Optional[Any]:
        try:
            endpoint = kwargs.get("endpoint", "/")
            method = kwargs.get("method", "GET")
            params = kwargs.get("params", {})
            headers = kwargs.get("headers", {})
            
            base_url = self.config.connection_params.get("base_url")
            url = f"{base_url}{endpoint}"
            
            start_time = datetime.now(timezone.utc)
            
            async with self._connection.request(
                method, url, params=params, headers=headers
            ) as response:
                if 200 <= response.status < 300:
                    result = await response.json()
                else:
                    result = None
                    
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(json.dumps(result).encode()) if result else 0
            
            self._update_metrics(result is not None, response_time, data_size)
            return result
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"API receive failed: {e}")
            return None


class RedisConnector(BaseConnector):
    """Redis connector implementation"""    
    async def connect(self) -> bool:
        try:
            self.status = ConnectionStatus.CONNECTING
            
            redis_url = self.config.connection_params.get("url", "redis://localhost:6379")
            self._connection = Redis.from_url(redis_url)
            
            # Test connection
            await self._connection.ping()
            
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"Redis connector {self.config.connector_id} connected")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"Redis connection failed: {e}")
            return False
            
    async def disconnect(self) -> bool:
        try:
            if self._connection:
                await self._connection.close()
            self.status = ConnectionStatus.DISCONNECTED
            return True
        except Exception as e:
            logger.error(f"Redis disconnect failed: {e}")
            return False
            
    async def health_check(self) -> bool:
        try:
            start_time = datetime.now(timezone.utc)
            await self._connection.ping()
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self._update_metrics(True, response_time)
            return True
            
        except Exception as e:
            self._update_metrics(False)
            logger.warning(f"Redis health check failed: {e}")
            return False
            
    async def send_data(self, data: Any, **kwargs) -> bool:
        try:
            key = kwargs.get("key")
            ttl = kwargs.get("ttl")
            
            if not key:
                raise ValueError("Redis key is required")
                
            start_time = datetime.now(timezone.utc)
            
            # Store data
            serialized_data = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            await self._connection.set(key, serialized_data)
            
            if ttl:
                await self._connection.expire(key, ttl)
                
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(serialized_data.encode())
            
            self._update_metrics(True, response_time, data_size)
            return True
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"Redis send failed: {e}")
            return False
            
    async def receive_data(self, **kwargs) -> Optional[Any]:
        try:
            key = kwargs.get("key")
            if not key:
                raise ValueError("Redis key is required")
                
            start_time = datetime.now(timezone.utc)
            
            result = await self._connection.get(key)
            if result:
                try:
                    result = json.loads(result.decode())
                except json.JSONDecodeError:
                    result = result.decode()
                    
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            data_size = len(str(result).encode()) if result else 0
            
            self._update_metrics(True, response_time, data_size)
            return result
            
        except Exception as e:
            self._update_metrics(False)
            logger.error(f"Redis receive failed: {e}")
            return None


class StreamConnector:
    """    Universal connector management system for integrating with various
    data sources, APIs, databases, and external services.
    """    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.connector_types: Dict[ConnectorType, Type[BaseConnector]] = {
            ConnectorType.DATABASE: DatabaseConnector,
            ConnectorType.API: APIConnector,
            ConnectorType.CACHE: RedisConnector,
        }
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize stream connector manager"""        try:
            # Start health check task
            asyncio.create_task(self._health_check_loop())
            
            logger.info("StreamConnector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamConnector: {e}")
            raise
            
    async def register_connector(self, config: ConnectorConfig) -> bool:
        """        Register new connector
        
        Args:
            config: Connector configuration
            
        Returns:
            Success status
        """        try:
            if config.connector_type not in self.connector_types:
                logger.error(f"Unsupported connector type: {config.connector_type}")
                return False
                
            # Create connector instance
            connector_class = self.connector_types[config.connector_type]
            connector = connector_class(config)
            
            # Connect if enabled
            if config.enabled:
                if await connector.connect():
                    self.connectors[config.connector_id] = connector
                    logger.info(f"Registered connector {config.connector_id}")
                    return True
                else:
                    logger.error(f"Failed to connect {config.connector_id}")
                    return False
            else:
                self.connectors[config.connector_id] = connector
                logger.info(f"Registered disabled connector {config.connector_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register connector {config.connector_id}: {e}")
            return False
            
    async def unregister_connector(self, connector_id: str) -> bool:
        """        Unregister connector
        
        Args:
            connector_id: Connector identifier
            
        Returns:
            Success status
        """        try:
            if connector_id in self.connectors:
                connector = self.connectors[connector_id]
                await connector.disconnect()
                del self.connectors[connector_id]
                
                logger.info(f"Unregistered connector {connector_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister connector {connector_id}: {e}")
            return False
            
    async def send_data(
        self,
        connector_id: str,
        data: Any,
        **kwargs
    ) -> bool:
        """        Send data through connector
        
        Args:
            connector_id: Connector identifier
            data: Data to send
            **kwargs: Additional parameters
            
        Returns:
            Success status
        """        try:
            if connector_id not in self.connectors:
                logger.error(f"Connector {connector_id} not found")
                return False
                
            connector = self.connectors[connector_id]
            
            if connector.status != ConnectionStatus.CONNECTED:
                # Try to reconnect
                if not await connector.connect():
                    logger.error(f"Connector {connector_id} not connected")
                    return False
                    
            return await connector.send_data(data, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to send data through {connector_id}: {e}")
            return False
            
    async def receive_data(
        self,
        connector_id: str,
        **kwargs
    ) -> Optional[Any]:
        """        Receive data through connector
        
        Args:
            connector_id: Connector identifier
            **kwargs: Additional parameters
            
        Returns:
            Received data or None
        """        try:
            if connector_id not in self.connectors:
                logger.error(f"Connector {connector_id} not found")
                return None
                
            connector = self.connectors[connector_id]
            
            if connector.status != ConnectionStatus.CONNECTED:
                # Try to reconnect
                if not await connector.connect():
                    logger.error(f"Connector {connector_id} not connected")
                    return None
                    
            return await connector.receive_data(**kwargs)
            
        except Exception as e:
            logger.error(f"Failed to receive data from {connector_id}: {e}")
            return None
            
    async def get_connector_status(self, connector_id: str) -> Optional[ConnectionStatus]:
        """Get connector status"""        if connector_id in self.connectors:
            return await self.connectors[connector_id].get_status()
        return None
        
    async def get_connector_metrics(self, connector_id: str) -> Optional[ConnectionMetrics]:
        """Get connector performance metrics"""        if connector_id in self.connectors:
            return await self.connectors[connector_id].get_metrics()
        return None
        
    async def list_connectors(self) -> List[Dict[str, Any]]:
        """List all registered connectors"""        connectors = []
        
        for connector_id, connector in self.connectors.items():
            status = await connector.get_status()
            metrics = await connector.get_metrics()
            
            connectors.append({
                "connector_id": connector_id,
                "type": connector.config.connector_type.value,
                "name": connector.config.name,
                "status": status.value,
                "enabled": connector.config.enabled,
                "metrics": metrics.dict()
            })
            
        return connectors
        
    async def enable_connector(self, connector_id: str) -> bool:
        """Enable connector"""        try:
            if connector_id not in self.connectors:
                return False
                
            connector = self.connectors[connector_id]
            connector.config.enabled = True
            
            if connector.status != ConnectionStatus.CONNECTED:
                return await connector.connect()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable connector {connector_id}: {e}")
            return False
            
    async def disable_connector(self, connector_id: str) -> bool:
        """Disable connector"""        try:
            if connector_id not in self.connectors:
                return False
                
            connector = self.connectors[connector_id]
            connector.config.enabled = False
            
            if connector.status == ConnectionStatus.CONNECTED:
                await connector.disconnect()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable connector {connector_id}: {e}")
            return False
            
    async def reconnect_connector(self, connector_id: str) -> bool:
        """Reconnect specific connector"""        try:
            if connector_id not in self.connectors:
                return False
                
            connector = self.connectors[connector_id]
            
            # Disconnect and reconnect
            await connector.disconnect()
            return await connector.connect()
            
        except Exception as e:
            logger.error(f"Failed to reconnect connector {connector_id}: {e}")
            return False
            
    async def _health_check_loop(self) -> None:
        """Background health check loop"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for connector_id, connector in self.connectors.items():
                    if not connector.config.enabled:
                        continue
                        
                    # Perform health check
                    if await connector.health_check():
                        if connector.status != ConnectionStatus.CONNECTED:
                            connector.status = ConnectionStatus.CONNECTED
                            logger.info(f"Connector {connector_id} health check passed")
                    else:
                        if connector.status == ConnectionStatus.CONNECTED:
                            connector.status = ConnectionStatus.ERROR
                            logger.warning(f"Connector {connector_id} health check failed")
                            
                            # Try to reconnect
                            await self.reconnect_connector(connector_id)
                            
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown connector manager"""        try:
            self._shutdown_event.set()
            
            # Disconnect all connectors
            for connector_id, connector in list(self.connectors.items()):
                await connector.disconnect()
                
            self.connectors.clear()
            
            logger.info("StreamConnector shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during connector shutdown: {e}")
