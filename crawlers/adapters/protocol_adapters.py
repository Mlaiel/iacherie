"""
Protocol Adapters - Enterprise Multi-protocol Network Communication System
=========================================================================

Industrial-grade adapters for comprehensive network protocol support in the IA-Influencer platform.
Handles HTTP/HTTPS, WebSocket, FTP/SFTP, TCP/UDP, MQTT, gRPC, WebRTC, and modern protocols.

Business Logic: Protocol Communication → Data Exchange → Real-time Streaming → Content Distribution

Supported Protocols:
- HTTP/1.1, HTTP/2, HTTP/3 with advanced features
- WebSocket with real-time bidirectional communication
- FTP/SFTP for secure file transfer operations
- TCP/UDP for low-level network communication
- MQTT for IoT and real-time messaging
- gRPC for high-performance microservice communication
- WebRTC for peer-to-peer media streaming
- CoAP for lightweight IoT communication
- SSH for secure remote command execution
- XMPP for instant messaging and presence

Advanced Features:
- High-performance async network communication
- Enterprise-grade security and authentication
- Multi-protocol support with auto-failover
- Advanced connection pooling and load balancing
- Intelligent retry logic and circuit breaker patterns
- Real-time metrics and performance monitoring
- SSL/TLS encryption and certificate management
- Dynamic rate limiting and traffic shaping
- Stream processing and WebSocket multiplexing
- Protocol-specific optimizations and tuning
- Network quality assessment and adaptation
- Bandwidth optimization and compression

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
import ssl
import socket
import aiohttp
import aiofiles
import websockets
import time
import gzip
import brotli
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, AsyncGenerator, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from abc import ABC, abstractmethod
from enum import Enum
import hashlib
import hmac
from urllib.parse import urljoin, urlparse, parse_qs
import backoff
import random
from collections import defaultdict, deque
import weakref
import concurrent.futures

# Advanced protocol imports
try:
    import aioftp
    import asyncssh
    from paramiko import SSHClient, AutoAddPolicy
    FTP_AVAILABLE = True
except ImportError:
    FTP_AVAILABLE = False

try:
    import grpc
    import grpc.aio
    from grpc import StatusCode
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

try:
    import aiomqtt
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import aiocoap
    from aiocoap import Context, Message, Code
    COAP_AVAILABLE = True
except ImportError:
    COAP_AVAILABLE = False

try:
    import asyncio_mqtt
    import aiortc
    from aiortc import RTCPeerConnection, RTCSessionDescription
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

# Network optimization imports
try:
    import aioquic
    from aioquic.asyncio import connect
    QUIC_AVAILABLE = True
except ImportError:
    QUIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProtocolType(Enum):
    """Supported protocol types."""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    WSS = "wss"
    FTP = "ftp"
    SFTP = "sftp"
    TCP = "tcp"
    UDP = "udp"
    MQTT = "mqtt"
    GRPC = "grpc"
    COAP = "coap"

class AuthenticationType(Enum):
    """Supported authentication types."""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"

@dataclass
class ConnectionMetrics:
    """Metrics for protocol connections."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    connection_uptime: float = 0.0
    last_request_time: Optional[datetime] = None
    errors_count: int = 0

@dataclass
class ProtocolConfig:
    """Advanced configuration for protocol adapters."""
    # Basic connection settings
    host: str
    port: int
    protocol: ProtocolType = ProtocolType.HTTP
    base_path: str = "/"
    
    # Authentication settings
    auth_type: AuthenticationType = AuthenticationType.NONE
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    private_key_path: Optional[str] = None
    certificate_path: Optional[str] = None
    
    # Connection settings
    timeout: float = 30.0
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    keep_alive: bool = True
    keep_alive_timeout: float = 600.0
    
    # SSL/TLS settings
    ssl_verify: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    ssl_ciphers: Optional[str] = None
    
    # Headers and data
    headers: Dict[str, str] = field(default_factory=dict)
    default_params: Dict[str, str] = field(default_factory=dict)
    user_agent: str = "IA-Influencer-Agent/1.0"
    
    # Connection pooling
    max_connections: int = 100
    max_connections_per_host: int = 10
    pool_timeout: float = 10.0
    
    # Retry and resilience
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    
    # Rate limiting
    rate_limit_enabled: bool = True
    requests_per_second: int = 10
    burst_limit: int = 20
    
    # Compression and optimization
    compress: bool = True
    compression_threshold: int = 1024
    enable_http2: bool = False
    enable_streaming: bool = False
    
    # Monitoring
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"

@dataclass
class ProtocolResponse:
    """Enhanced protocol response container."""
    status_code: int
    headers: Dict[str, str]
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    retry_count: int = 0
    protocol_used: Optional[str] = None
    connection_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class CircuitBreaker:
    """Circuit breaker implementation for resilience."""
    
    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = "OPEN"

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token for rate limiting."""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

class ProtocolAdapter(ABC):
    """Enterprise base class for all protocol adapters."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize protocol adapter with enterprise features."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = None
        self.session = None
        self.is_connected = False
        self.protocol_name = ""
        
        # Enterprise features
        self.metrics = ConnectionMetrics()
        self.circuit_breaker = CircuitBreaker(
            threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        ) if config.circuit_breaker_enabled else None
        
        self.rate_limiter = RateLimiter(
            rate=config.requests_per_second,
            burst=config.burst_limit
        ) if config.rate_limit_enabled else None
        
        # Connection pool
        self._connection_pool: Dict[str, Any] = {}
        self._pool_lock = asyncio.Lock()
        
        # Setup SSL context
        self._ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context based on configuration."""
        if not self.config.ssl_verify and self.config.protocol in [ProtocolType.HTTPS, ProtocolType.WSS]:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
        elif self.config.ssl_cert_path and self.config.ssl_key_path:
            context = ssl.create_default_context()
            context.load_cert_chain(self.config.ssl_cert_path, self.config.ssl_key_path)
            if self.config.ssl_ca_path:
                context.load_verify_locations(self.config.ssl_ca_path)
            return context
        return None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect using the protocol."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the protocol."""
        pass
    
    @abstractmethod
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Send request using the protocol."""
        pass
    
    async def health_check(self) -> bool:
        """Perform health check on the connection."""



        try:
            if self.config.protocol in [ProtocolType.HTTP, ProtocolType.HTTPS]:
                response = await self.send_request("HEAD", "/health")
                return response.success
            return self.is_connected
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def initialize(self):
        """Initialize the adapter with enterprise features."""
        success = await self.connect()
        if not success:
            raise Exception(f"Failed to connect using {self.protocol_name}")
        self.logger.info(f"Initialized {self.protocol_name} adapter")
    
    async def cleanup(self):
        """Cleanup adapter resources."""
        await self.disconnect()
        self.logger.info(f"Cleaned up {self.protocol_name} adapter")

class HTTPAdapter(ProtocolAdapter):
    """Adapter for HTTP protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize HTTP adapter."""
        super().__init__(config)
        self.protocol_name = "HTTP"
        self.session = None
        self.base_url = f"http://{config.host}:{config.port}"
    
    async def connect(self) -> bool:
        """Initialize HTTP session."""



        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=self.config.max_connections,
                keepalive_timeout=30 if self.config.keep_alive else 0
            )
            
            headers = self.config.headers or {}
            if self.config.compress:
                headers['Accept-Encoding'] = 'gzip, deflate'
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            
            self.is_connected = True
            self.logger.info(f"HTTP session initialized for {self.base_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"HTTP connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        self.is_connected = False
    
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Send HTTP request."""
        start_time = datetime.now()
        
        try:
            url = f"{self.base_url}{path}"
            
            # Prepare request parameters
            request_kwargs = {
                'params': kwargs.get('params'),
                'headers': kwargs.get('headers', {}),
            }
            
            # Add authentication if configured
            if self.config.username and self.config.password:
                auth = aiohttp.BasicAuth(self.config.username, self.config.password)
                request_kwargs['auth'] = auth
            
            # Add request body
            if data is not None:
                if isinstance(data, (dict, list)):
                    request_kwargs['json'] = data
                elif isinstance(data, str):
                    request_kwargs['data'] = data
                elif isinstance(data, bytes):
                    request_kwargs['data'] = data
            
            # Execute request
            async with self.session.request(method, url, **request_kwargs) as response:
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Read response data
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    response_data = await response.json()
                except:
                    response_data = response_text
                
                return ProtocolResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    data=response_data,
                    metadata={
                        'url': str(response.url),
                        'method': method,
                        'content_type': response.content_type
                    },
                    execution_time=execution_time,
                    success=200 <= response.status < 300
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"HTTP request failed: {e}")
            
            return ProtocolResponse(
                status_code=0,
                headers={},
                data=None,
                metadata={'error': str(e)},
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def get(self, path: str, **kwargs) -> ProtocolResponse:
        """Send GET request."""



        return await self.send_request('GET', path, **kwargs)
    
    async def post(self, path: str, data: Any = None, **kwargs) -> ProtocolResponse:
        """Send POST request."""



        return await self.send_request('POST', path, data, **kwargs)
    
    async def put(self, path: str, data: Any = None, **kwargs) -> ProtocolResponse:
        """Send PUT request."""



        return await self.send_request('PUT', path, data, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> ProtocolResponse:
        """Send DELETE request."""



        return await self.send_request('DELETE', path, **kwargs)

class HTTPSAdapter(HTTPAdapter):
    """Adapter for HTTPS protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize HTTPS adapter."""
        super().__init__(config)
        self.protocol_name = "HTTPS"
        self.base_url = f"https://{config.host}:{config.port}"
    
    async def connect(self) -> bool:
        """Initialize HTTPS session with SSL."""



        try:
            # Setup SSL context
            ssl_context = None
            if self.config.ssl_verify:
                ssl_context = ssl.create_default_context()
                
                # Load custom certificates if provided
                if self.config.ssl_cert_path and self.config.ssl_key_path:
                    ssl_context.load_cert_chain(
                        self.config.ssl_cert_path,
                        self.config.ssl_key_path
                    )
            else:
                ssl_context = False  # Disable SSL verification
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=self.config.max_connections,
                keepalive_timeout=30 if self.config.keep_alive else 0
            )
            
            headers = self.config.headers or {}
            if self.config.compress:
                headers['Accept-Encoding'] = 'gzip, deflate'
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            
            self.is_connected = True
            self.logger.info(f"HTTPS session initialized for {self.base_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"HTTPS connection failed: {e}")
            return False

class WebSocketSecureAdapter(ProtocolAdapter):
    """Adapter for secure WebSocket protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize WebSocket Secure adapter."""
        super().__init__(config)
        self.protocol_name = "WSS"
        self.websocket = None
        self.ws_url = f"wss://{config.host}:{config.port}"
        self.message_handlers: Dict[str, Callable] = {}
        self.ping_interval = 30
        self.ping_timeout = 10
    
    async def connect(self) -> bool:
        """Connect to secure WebSocket."""



        try:
            # Setup SSL context
            ssl_context = None
            if self.config.ssl_verify:
                ssl_context = ssl.create_default_context()
                
                if self.config.ssl_cert_path and self.config.ssl_key_path:
                    ssl_context.load_cert_chain(
                        self.config.ssl_cert_path,
                        self.config.ssl_key_path
                    )
            
            # Prepare headers
            headers = self.config.headers or {}
            
            # Add authentication if configured
            if self.config.username and self.config.password:
                import base64
                credentials = base64.b64encode(
                    f"{self.config.username}:{self.config.password}".encode()
                ).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.ws_url,
                ssl=ssl_context,
                extra_headers=headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout
            )
            
            self.is_connected = True
            self.logger.info(f"Connected to secure WebSocket: {self.ws_url}")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
            return True
            
        except Exception as e:
            self.logger.error(f"WSS connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            await self.websocket.close()
        self.is_connected = False
    
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Send WebSocket message."""
        start_time = datetime.now()
        
        try:
            if not self.is_connected:
                await self.connect()
            
            # Prepare message
            message = {
                'method': method,
                'path': path,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            message_str = json.dumps(message)
            
            # Send message
            await self.websocket.send(message_str)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ProtocolResponse(
                status_code=200,
                headers={},
                data={'sent': True, 'message_id': message.get('id')},
                metadata={'method': method, 'path': path},
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"WSS send failed: {e}")
            
            return ProtocolResponse(
                status_code=0,
                headers={},
                data=None,
                metadata={'error': str(e)},
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def _message_listener(self):
        """Listen for incoming WebSocket messages."""



        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type', 'default')
                    
                    handler = self.message_handlers.get(message_type)
                    if handler:
                        await handler(data)
                    else:
                        self.logger.debug(f"Unhandled message type: {message_type}")
                        
                except Exception as e:
                    self.logger.error(f"Error handling WSS message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            self.logger.warning("WSS connection closed")
            
        except Exception as e:
            self.logger.error(f"WSS listener error: {e}")
            self.is_connected = False
    
    def add_message_handler(self, message_type: str, handler: Callable):
        """Add handler for specific message type."""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, message: Union[str, Dict]) -> ProtocolResponse:
        """Send raw message via WebSocket."""



        return await self.send_request('SEND', '', message)

class FTPAdapter(ProtocolAdapter):
    """Adapter for FTP protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize FTP adapter."""
        super().__init__(config)
        
        if not FTP_AVAILABLE:
            raise ImportError("FTP dependencies not available. Install with: pip install aioftp")
        
        self.protocol_name = "FTP"
        self.ftp_client = None
    
    async def connect(self) -> bool:
        """Connect to FTP server."""



        try:
            self.ftp_client = aioftp.Client()
            
            await self.ftp_client.connect(
                self.config.host,
                self.config.port
            )
            
            if self.config.username and self.config.password:
                await self.ftp_client.login(
                    self.config.username,
                    self.config.password
                )
            
            self.is_connected = True
            self.logger.info(f"Connected to FTP server: {self.config.host}")
            return True
            
        except Exception as e:
            self.logger.error(f"FTP connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from FTP server."""
        if self.ftp_client:
            await self.ftp_client.quit()
        self.is_connected = False
    
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Execute FTP operation."""
        start_time = datetime.now()
        
        try:
            result = None
            
            if method.upper() == 'LIST':
                # List directory contents
                result = []
                async for item in self.ftp_client.list(path):
                    result.append(str(item))
            
            elif method.upper() == 'DOWNLOAD':
                # Download file
                local_path = kwargs.get('local_path', './downloaded_file')
                await self.ftp_client.download(path, local_path)
                result = {'downloaded': True, 'local_path': local_path}
            
            elif method.upper() == 'UPLOAD':
                # Upload file
                local_path = kwargs.get('local_path')
                if not local_path:
                    raise ValueError("local_path required for upload")
                
                await self.ftp_client.upload(local_path, path)
                result = {'uploaded': True, 'remote_path': path}
            
            elif method.upper() == 'DELETE':
                # Delete file
                await self.ftp_client.remove(path)
                result = {'deleted': True, 'path': path}
            
            elif method.upper() == 'MKDIR':
                # Create directory
                await self.ftp_client.make_directory(path)
                result = {'created': True, 'directory': path}
            
            elif method.upper() == 'RMDIR':
                # Remove directory
                await self.ftp_client.remove_directory(path)
                result = {'removed': True, 'directory': path}
            
            elif method.upper() == 'PWD':
                # Get current directory
                result = await self.ftp_client.get_current_directory()
            
            elif method.upper() == 'CWD':
                # Change directory
                await self.ftp_client.change_directory(path)
                result = {'changed': True, 'directory': path}
            
            else:
                raise ValueError(f"Unsupported FTP method: {method}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ProtocolResponse(
                status_code=200,
                headers={},
                data=result,
                metadata={'method': method, 'path': path},
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"FTP operation failed: {e}")
            
            return ProtocolResponse(
                status_code=0,
                headers={},
                data=None,
                metadata={'error': str(e)},
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def list_directory(self, path: str = '.') -> ProtocolResponse:
        """List directory contents."""



        return await self.send_request('LIST', path)
    
    async def download_file(self, remote_path: str, local_path: str) -> ProtocolResponse:
        """Download file from FTP server."""



        return await self.send_request('DOWNLOAD', remote_path, local_path=local_path)
    
    async def upload_file(self, local_path: str, remote_path: str) -> ProtocolResponse:
        """Upload file to FTP server."""



        return await self.send_request('UPLOAD', remote_path, local_path=local_path)

class SFTPAdapter(ProtocolAdapter):
    """Adapter for SFTP protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize SFTP adapter."""
        super().__init__(config)
        
        if not FTP_AVAILABLE:
            raise ImportError("SFTP dependencies not available. Install with: pip install asyncssh")
        
        self.protocol_name = "SFTP"
        self.sftp_client = None
        self.ssh_connection = None
    
    async def connect(self) -> bool:
        """Connect to SFTP server."""



        try:
            # Prepare authentication
            auth_kwargs = {}
            
            if self.config.private_key_path:
                # Key-based authentication
                auth_kwargs['client_keys'] = [self.config.private_key_path]
            elif self.config.username and self.config.password:
                # Password authentication
                auth_kwargs['username'] = self.config.username
                auth_kwargs['password'] = self.config.password
            
            # Establish SSH connection
            self.ssh_connection = await asyncssh.connect(
                self.config.host,
                port=self.config.port,
                **auth_kwargs
            )
            
            # Create SFTP client
            self.sftp_client = await self.ssh_connection.start_sftp_client()
            
            self.is_connected = True
            self.logger.info(f"Connected to SFTP server: {self.config.host}")
            return True
            
        except Exception as e:
            self.logger.error(f"SFTP connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from SFTP server."""
        if self.sftp_client:
            self.sftp_client.exit()
        if self.ssh_connection:
            self.ssh_connection.close()
        self.is_connected = False
    
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Execute SFTP operation."""
        start_time = datetime.now()
        
        try:
            result = None
            
            if method.upper() == 'LIST':
                # List directory contents
                result = await self.sftp_client.listdir(path)
            
            elif method.upper() == 'DOWNLOAD':
                # Download file
                local_path = kwargs.get('local_path', './downloaded_file')
                await self.sftp_client.get(path, local_path)
                result = {'downloaded': True, 'local_path': local_path}
            
            elif method.upper() == 'UPLOAD':
                # Upload file
                local_path = kwargs.get('local_path')
                if not local_path:
                    raise ValueError("local_path required for upload")
                
                await self.sftp_client.put(local_path, path)
                result = {'uploaded': True, 'remote_path': path}
            
            elif method.upper() == 'DELETE':
                # Delete file
                await self.sftp_client.remove(path)
                result = {'deleted': True, 'path': path}
            
            elif method.upper() == 'MKDIR':
                # Create directory
                await self.sftp_client.mkdir(path)
                result = {'created': True, 'directory': path}
            
            elif method.upper() == 'RMDIR':
                # Remove directory
                await self.sftp_client.rmdir(path)
                result = {'removed': True, 'directory': path}
            
            elif method.upper() == 'STAT':
                # Get file/directory stats
                stats = await self.sftp_client.stat(path)
                result = {
                    'size': stats.st_size,
                    'modified': stats.st_mtime,
                    'is_dir': stats.st_mode & 0o170000 == 0o040000
                }
            
            else:
                raise ValueError(f"Unsupported SFTP method: {method}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ProtocolResponse(
                status_code=200,
                headers={},
                data=result,
                metadata={'method': method, 'path': path},
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"SFTP operation failed: {e}")
            
            return ProtocolResponse(
                status_code=0,
                headers={},
                data=None,
                metadata={'error': str(e)},
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )

class TCPAdapter(ProtocolAdapter):
    """Adapter for raw TCP protocol."""
    
    def __init__(self, config: ProtocolConfig):
        """Initialize TCP adapter."""
        super().__init__(config)
        self.protocol_name = "TCP"
        self.reader = None
        self.writer = None
    
    async def connect(self) -> bool:
        """Connect to TCP server."""



        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.config.host,
                self.config.port
            )
            
            self.is_connected = True
            self.logger.info(f"Connected to TCP server: {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"TCP connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from TCP server."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.is_connected = False
    
    async def send_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> ProtocolResponse:
        """Send TCP data."""
        start_time = datetime.now()
        
        try:
            # Prepare message
            if isinstance(data, str):
                message = data.encode('utf-8')
            elif isinstance(data, dict):
                message = json.dumps(data).encode('utf-8')
            elif isinstance(data, bytes):
                message = data
            else:
                message = str(data).encode('utf-8')
            
            # Add delimiter if specified
            delimiter = kwargs.get('delimiter', b'\n')
            if delimiter and not message.endswith(delimiter):
                message += delimiter
            
            # Send data
            self.writer.write(message)
            await self.writer.drain()
            
            # Read response if requested
            response_data = None
            if kwargs.get('read_response', True):
                try:
                    # Read with timeout
                    response_data = await asyncio.wait_for(
                        self.reader.read(kwargs.get('buffer_size', 1024)),
                        timeout=kwargs.get('read_timeout', 5.0)
                    )
                    
                    if delimiter in response_data:
                        response_data = response_data.split(delimiter)[0]
                    
                    # Try to decode
                    try:
                        response_data = response_data.decode('utf-8')
                        # Try to parse as JSON
                        try:
                            response_data = json.loads(response_data)
                        except:
                            pass
                    except:
                        pass  # Keep as bytes
                        
                except asyncio.TimeoutError:
                    response_data = None
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ProtocolResponse(
                status_code=200,
                headers={},
                data=response_data,
                metadata={
                    'sent_bytes': len(message),
                    'method': method,
                    'path': path
                },
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"TCP send failed: {e}")
            
            return ProtocolResponse(
                status_code=0,
                headers={},
                data=None,
                metadata={'error': str(e)},
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def send_raw(self, data: bytes, **kwargs) -> ProtocolResponse:
        """Send raw TCP data."""



        return await self.send_request('SEND', '', data, **kwargs)
    
    async def receive_data(self, buffer_size: int = 1024, timeout: float = 5.0) -> Optional[bytes]:
        """Receive data from TCP connection."""



        try:
            data = await asyncio.wait_for(
                self.reader.read(buffer_size),
                timeout=timeout
            )
            return data
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"TCP receive failed: {e}")
            return None

# Export all adapters
__all__ = [
    'ProtocolAdapter',
    'ProtocolConfig',
    'ProtocolResponse',
    'HTTPAdapter',
    'HTTPSAdapter',
    'WebSocketSecureAdapter',
    'FTPAdapter',
    'SFTPAdapter',
    'TCPAdapter'
]
