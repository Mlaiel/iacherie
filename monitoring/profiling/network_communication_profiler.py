"""⚡ Network Communication Profiling System
==========================================

Advanced network communication performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for HTTP, WebSocket, gRPC, and other network protocols.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization  
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
import socket
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import psutil

logger = logging.getLogger(__name__)

# Try to import network libraries
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    import grpc
    HAS_GRPC = True
except ImportError:
    HAS_GRPC = False


class NetworkProtocol(Enum):
    """Network communication protocols"""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    FTP = "ftp"
    SMTP = "smtp"


class ConnectionType(Enum):
    """Connection types"""
    CLIENT = "client"
    SERVER = "server"
    PEER_TO_PEER = "peer_to_peer"
    MULTICAST = "multicast"


class NetworkOperation(Enum):
    """Network operations"""
    CONNECT = "connect"
    SEND = "send"
    RECEIVE = "receive"
    DISCONNECT = "disconnect"
    HANDSHAKE = "handshake"
    KEEPALIVE = "keepalive"


@dataclass
class NetworkMetadata:
    """Metadata for network operations"""
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: NetworkProtocol
    connection_type: ConnectionType
    operation: NetworkOperation
    payload_size: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    user_agent: Optional[str] = None
    connection_id: Optional[str] = None


@dataclass
class NetworkMetrics:
    """Network communication performance metrics"""
    operation_id: str
    protocol: NetworkProtocol
    operation: NetworkOperation
    connection_time_ms: float
    transfer_time_ms: float
    total_time_ms: float
    bytes_sent: int
    bytes_received: int
    throughput_mbps: float
    latency_ms: float
    packet_loss: float
    jitter_ms: float
    connection_reused: bool
    ssl_handshake_time_ms: float
    dns_resolution_time_ms: float
    error_count: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkBottleneck:
    """Network communication bottleneck information"""
    bottleneck_type: str
    severity: str
    protocol: NetworkProtocol
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class NetworkCommunicationProfiler:
    """
    Network communication performance profiler for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 2.0,
                 max_history_size: int = 20000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.network_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_connections: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_connection_threshold': 1000.0,  # 1 second
            'high_latency_threshold': 200.0,      # 200ms
            'low_throughput_threshold': 1.0,      # 1 MB/s
            'high_packet_loss_threshold': 2.0,    # 2%
            'ssl_handshake_threshold': 500.0,     # 500ms
            'dns_resolution_threshold': 100.0     # 100ms
        }
        
        # Network monitoring
        self.network_stats_baseline = None
        self._init_network_monitoring()
        
        logger.info("NetworkCommunicationProfiler initialized")

    def _init_network_monitoring(self):
        """Initialize network monitoring"""
        try:
            # Get baseline network statistics
            self.network_stats_baseline = psutil.net_io_counters()
        except Exception as e:
            logger.warning(f"Error initializing network monitoring: {e}")

    def start_monitoring(self):
        """Start background network monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Network communication monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Network communication monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_network_system_metrics()
                self._cleanup_stale_connections()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in network monitoring loop: {e}")

    def _collect_network_system_metrics(self):
        """Collect system-wide network metrics"""
        try:
            # Get current network statistics
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections()
            
            if net_io and self.network_stats_baseline:
                # Calculate deltas
                bytes_sent_delta = net_io.bytes_sent - self.network_stats_baseline.bytes_sent
                bytes_recv_delta = net_io.bytes_recv - self.network_stats_baseline.bytes_recv
                
                # Calculate throughput (rough estimate)
                time_delta = self.monitoring_interval
                throughput_sent = (bytes_sent_delta / time_delta) / (1024 * 1024)  # MB/s
                throughput_recv = (bytes_recv_delta / time_delta) / (1024 * 1024)  # MB/s
                
                # Create system metrics
                metrics = NetworkMetrics(
                    operation_id=f"system_network_{int(time.time())}",
                    protocol=NetworkProtocol.TCP,  # Mixed
                    operation=NetworkOperation.SEND,  # Mixed
                    connection_time_ms=0.0,
                    transfer_time_ms=0.0,
                    total_time_ms=0.0,
                    bytes_sent=bytes_sent_delta,
                    bytes_received=bytes_recv_delta,
                    throughput_mbps=max(throughput_sent, throughput_recv),
                    latency_ms=0.0,
                    packet_loss=0.0,
                    jitter_ms=0.0,
                    connection_reused=False,
                    ssl_handshake_time_ms=0.0,
                    dns_resolution_time_ms=0.0,
                    error_count=net_io.errin + net_io.errout,
                    timestamp=datetime.utcnow(),
                    metadata={
                        'active_connections': len(net_connections),
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv,
                        'packets_drop': net_io.dropin + net_io.dropout,
                        'system_monitoring': True
                    }
                )
                
                self.network_metrics_history.append(metrics)
                
                # Update baseline
                self.network_stats_baseline = net_io
                
        except Exception as e:
            logger.error(f"Error collecting network system metrics: {e}")

    def _cleanup_stale_connections(self):
        """Clean up stale connections"""
        now = time.time()
        stale_threshold = 300  # 5 minutes
        
        stale_connections = [
            conn_id for conn_id, conn_data in self.active_connections.items()
            if now - conn_data.get('start_time', now) > stale_threshold
        ]
        
        for conn_id in stale_connections:
            self.active_connections.pop(conn_id, None)

    def profile_http_request(self,
                           url: str,
                           method: str = "GET",
                           headers: Optional[Dict] = None,
                           data: Optional[bytes] = None,
                           timeout: float = 30.0) -> NetworkMetrics:
        """
        Profile an HTTP request
        
        Args:
            url: Request URL
            method: HTTP method
            headers: Request headers
            data: Request payload
            timeout: Request timeout
            
        Returns:
            NetworkMetrics with profiling results
        """
        operation_id = f"http_{method}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Parse URL
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            protocol = NetworkProtocol.HTTPS if parsed_url.scheme == 'https' else NetworkProtocol.HTTP
            
            # Track connection start
            self.active_connections[operation_id] = {
                'start_time': start_time,
                'url': url,
                'method': method,
                'protocol': protocol
            }
            
            # Perform HTTP request profiling
            if HAS_AIOHTTP:
                result = asyncio.run(self._profile_aiohttp_request(url, method, headers, data, timeout))
            else:
                result = self._profile_requests_request(url, method, headers, data, timeout)
            
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            # Calculate metrics
            payload_size = len(data) if data else 0
            response_size = result.get('response_size', 0)
            throughput_mbps = 0.0
            
            if response_size > 0 and total_time_ms > 0:
                throughput_mbps = (response_size / 1024 / 1024) / (total_time_ms / 1000)
            
            # Create metrics
            metrics = NetworkMetrics(
                operation_id=operation_id,
                protocol=protocol,
                operation=NetworkOperation.SEND,
                connection_time_ms=result.get('connection_time_ms', 0.0),
                transfer_time_ms=result.get('transfer_time_ms', 0.0),
                total_time_ms=total_time_ms,
                bytes_sent=payload_size,
                bytes_received=response_size,
                throughput_mbps=throughput_mbps,
                latency_ms=result.get('latency_ms', total_time_ms),
                packet_loss=0.0,
                jitter_ms=0.0,
                connection_reused=result.get('connection_reused', False),
                ssl_handshake_time_ms=result.get('ssl_handshake_time_ms', 0.0),
                dns_resolution_time_ms=result.get('dns_resolution_time_ms', 0.0),
                error_count=1 if result.get('error') else 0,
                timestamp=datetime.utcnow(),
                metadata={
                    'url': url,
                    'method': method,
                    'status_code': result.get('status_code'),
                    'headers': headers or {},
                    'user_agent': headers.get('User-Agent') if headers else None
                }
            )
            
            # Store metrics
            self.network_metrics_history.append(metrics)
            
            # Check for bottlenecks
            self._analyze_network_bottlenecks(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling HTTP request: {e}")
            raise
        finally:
            # Remove from active connections
            self.active_connections.pop(operation_id, None)

    async def _profile_aiohttp_request(self, url: str, method: str, headers: Optional[Dict],
                                     data: Optional[bytes], timeout: float) -> Dict:
        """Profile HTTP request using aiohttp"""
        result = {'error': False}
        
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                start_time = time.time()
                
                async with session.request(method, url, headers=headers, data=data) as response:
                    end_time = time.time()
                    
                    # Read response
                    response_data = await response.read()
                    
                    result.update({
                        'status_code': response.status,
                        'response_size': len(response_data),
                        'latency_ms': (end_time - start_time) * 1000,
                        'connection_reused': response.connection.is_connected() if response.connection else False
                    })
                    
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def _profile_requests_request(self, url: str, method: str, headers: Optional[Dict],
                                data: Optional[bytes], timeout: float) -> Dict:
        """Profile HTTP request using requests library"""
        result = {'error': False}
        
        try:
            import requests
            
            start_time = time.time()
            response = requests.request(method, url, headers=headers, data=data, timeout=timeout)
            end_time = time.time()
            
            result.update({
                'status_code': response.status_code,
                'response_size': len(response.content),
                'latency_ms': (end_time - start_time) * 1000
            })
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def profile_websocket_connection(self,
                                   uri: str,
                                   message: Optional[str] = None,
                                   timeout: float = 30.0) -> NetworkMetrics:
        """
        Profile a WebSocket connection
        
        Args:
            uri: WebSocket URI
            message: Optional message to send
            timeout: Connection timeout
            
        Returns:
            NetworkMetrics with profiling results
        """
        operation_id = f"websocket_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Track connection start
            self.active_connections[operation_id] = {
                'start_time': start_time,
                'uri': uri,
                'protocol': NetworkProtocol.WEBSOCKET
            }
            
            # Perform WebSocket profiling
            if HAS_WEBSOCKETS:
                result = asyncio.run(self._profile_websocket_connection(uri, message, timeout))
            else:
                result = {'error': True, 'error_message': 'WebSockets library not available'}
            
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            # Create metrics
            metrics = NetworkMetrics(
                operation_id=operation_id,
                protocol=NetworkProtocol.WEBSOCKET,
                operation=NetworkOperation.CONNECT,
                connection_time_ms=result.get('connection_time_ms', total_time_ms),
                transfer_time_ms=result.get('transfer_time_ms', 0.0),
                total_time_ms=total_time_ms,
                bytes_sent=len(message.encode()) if message else 0,
                bytes_received=result.get('bytes_received', 0),
                throughput_mbps=0.0,
                latency_ms=result.get('latency_ms', total_time_ms),
                packet_loss=0.0,
                jitter_ms=0.0,
                connection_reused=False,
                ssl_handshake_time_ms=0.0,
                dns_resolution_time_ms=0.0,
                error_count=1 if result.get('error') else 0,
                timestamp=datetime.utcnow(),
                metadata={
                    'uri': uri,
                    'message_sent': message,
                    'connection_type': 'websocket'
                }
            )
            
            # Store metrics
            self.network_metrics_history.append(metrics)
            
            # Check for bottlenecks
            self._analyze_network_bottlenecks(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling WebSocket connection: {e}")
            raise
        finally:
            # Remove from active connections
            self.active_connections.pop(operation_id, None)

    async def _profile_websocket_connection(self, uri: str, message: Optional[str], timeout: float) -> Dict:
        """Profile WebSocket connection using websockets library"""
        result = {'error': False}
        
        try:
            start_time = time.time()
            
            async with websockets.connect(uri, timeout=timeout) as websocket:
                connection_time = time.time()
                result['connection_time_ms'] = (connection_time - start_time) * 1000
                
                if message:
                    await websocket.send(message)
                    response = await websocket.recv()
                    
                    transfer_time = time.time()
                    result['transfer_time_ms'] = (transfer_time - connection_time) * 1000
                    result['bytes_received'] = len(response.encode()) if isinstance(response, str) else len(response)
                
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def profile_tcp_connection(self,
                             host: str,
                             port: int,
                             data: Optional[bytes] = None,
                             timeout: float = 10.0) -> NetworkMetrics:
        """
        Profile a TCP connection
        
        Args:
            host: Target host
            port: Target port
            data: Optional data to send
            timeout: Connection timeout
            
        Returns:
            NetworkMetrics with profiling results
        """
        operation_id = f"tcp_{host}_{port}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Track connection start
            self.active_connections[operation_id] = {
                'start_time': start_time,
                'host': host,
                'port': port,
                'protocol': NetworkProtocol.TCP
            }
            
            # Perform TCP connection profiling
            result = self._profile_tcp_socket(host, port, data, timeout)
            
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            # Create metrics
            metrics = NetworkMetrics(
                operation_id=operation_id,
                protocol=NetworkProtocol.TCP,
                operation=NetworkOperation.CONNECT,
                connection_time_ms=result.get('connection_time_ms', total_time_ms),
                transfer_time_ms=result.get('transfer_time_ms', 0.0),
                total_time_ms=total_time_ms,
                bytes_sent=len(data) if data else 0,
                bytes_received=result.get('bytes_received', 0),
                throughput_mbps=0.0,
                latency_ms=result.get('latency_ms', total_time_ms),
                packet_loss=0.0,
                jitter_ms=0.0,
                connection_reused=False,
                ssl_handshake_time_ms=0.0,
                dns_resolution_time_ms=result.get('dns_resolution_time_ms', 0.0),
                error_count=1 if result.get('error') else 0,
                timestamp=datetime.utcnow(),
                metadata={
                    'host': host,
                    'port': port,
                    'connection_type': 'tcp'
                }
            )
            
            # Store metrics
            self.network_metrics_history.append(metrics)
            
            # Check for bottlenecks
            self._analyze_network_bottlenecks(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling TCP connection: {e}")
            raise
        finally:
            # Remove from active connections
            self.active_connections.pop(operation_id, None)

    def _profile_tcp_socket(self, host: str, port: int, data: Optional[bytes], timeout: float) -> Dict:
        """Profile TCP socket connection"""
        result = {'error': False}
        
        try:
            # DNS resolution timing
            dns_start = time.time()
            ip = socket.gethostbyname(host)
            dns_end = time.time()
            result['dns_resolution_time_ms'] = (dns_end - dns_start) * 1000
            
            # TCP connection timing
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            connect_start = time.time()
            sock.connect((ip, port))
            connect_end = time.time()
            result['connection_time_ms'] = (connect_end - connect_start) * 1000
            
            # Data transfer timing
            if data:
                transfer_start = time.time()
                sock.send(data)
                
                # Try to receive response
                try:
                    response = sock.recv(4096)
                    transfer_end = time.time()
                    result['transfer_time_ms'] = (transfer_end - transfer_start) * 1000
                    result['bytes_received'] = len(response)
                except socket.timeout:
                    result['bytes_received'] = 0
            
            sock.close()
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def _analyze_network_bottlenecks(self, metrics: NetworkMetrics):
        """Analyze network bottlenecks"""
        bottlenecks = []
        
        # Check connection time
        if metrics.connection_time_ms > self.thresholds['slow_connection_threshold']:
            bottlenecks.append(NetworkBottleneck(
                bottleneck_type="slow_connection",
                severity="high" if metrics.connection_time_ms > 2000 else "medium",
                protocol=metrics.protocol,
                description=f"Network connection too slow: {metrics.connection_time_ms:.1f}ms",
                impact="Poor user experience, connection timeouts",
                recommendations=[
                    "Check network infrastructure",
                    "Optimize server location",
                    "Use connection pooling",
                    "Implement CDN"
                ],
                detected_at=datetime.utcnow(),
                metrics={'connection_time_ms': metrics.connection_time_ms}
            ))
        
        # Check latency
        if metrics.latency_ms > self.thresholds['high_latency_threshold']:
            bottlenecks.append(NetworkBottleneck(
                bottleneck_type="high_latency",
                severity="medium",
                protocol=metrics.protocol,
                description=f"Network latency too high: {metrics.latency_ms:.1f}ms",
                impact="Slow data transfer, poor responsiveness",
                recommendations=[
                    "Optimize network routing",
                    "Use faster network protocols",
                    "Implement data compression",
                    "Cache frequently accessed data"
                ],
                detected_at=datetime.utcnow(),
                metrics={'latency_ms': metrics.latency_ms}
            ))
        
        # Check throughput
        if metrics.throughput_mbps < self.thresholds['low_throughput_threshold'] and metrics.bytes_received > 0:
            bottlenecks.append(NetworkBottleneck(
                bottleneck_type="low_throughput",
                severity="medium",
                protocol=metrics.protocol,
                description=f"Network throughput too low: {metrics.throughput_mbps:.1f}MB/s",
                impact="Slow data transfer, bandwidth limitations",
                recommendations=[
                    "Upgrade network bandwidth",
                    "Optimize data compression",
                    "Use parallel connections",
                    "Implement streaming protocols"
                ],
                detected_at=datetime.utcnow(),
                metrics={'throughput_mbps': metrics.throughput_mbps}
            ))
        
        # Check DNS resolution time
        if metrics.dns_resolution_time_ms > self.thresholds['dns_resolution_threshold']:
            bottlenecks.append(NetworkBottleneck(
                bottleneck_type="slow_dns",
                severity="low",
                protocol=metrics.protocol,
                description=f"DNS resolution too slow: {metrics.dns_resolution_time_ms:.1f}ms",
                impact="Delayed connection establishment",
                recommendations=[
                    "Use faster DNS servers",
                    "Implement DNS caching",
                    "Use DNS prefetching",
                    "Consider local DNS resolution"
                ],
                detected_at=datetime.utcnow(),
                metrics={'dns_resolution_time_ms': metrics.dns_resolution_time_ms}
            ))
        
        # Check for errors
        if metrics.error_count > 0:
            bottlenecks.append(NetworkBottleneck(
                bottleneck_type="network_errors",
                severity="high",
                protocol=metrics.protocol,
                description="Network errors detected",
                impact="Connection failures, data loss",
                recommendations=[
                    "Check network connectivity",
                    "Implement retry mechanisms",
                    "Monitor network health",
                    "Use redundant connections"
                ],
                detected_at=datetime.utcnow(),
                metrics={'error_count': metrics.error_count}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get network performance summary"""
        if not self.network_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.network_metrics_history)[-1000:]  # Last 1000 operations
        
        # Calculate statistics
        connection_times = [m.connection_time_ms for m in recent_metrics if m.connection_time_ms > 0]
        latencies = [m.latency_ms for m in recent_metrics if m.latency_ms > 0]
        throughputs = [m.throughput_mbps for m in recent_metrics if m.throughput_mbps > 0]
        error_count = sum(1 for m in recent_metrics if m.error_count > 0)
        
        return {
            "summary": {
                "total_operations": len(recent_metrics),
                "avg_connection_time_ms": statistics.mean(connection_times) if connection_times else 0,
                "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                "avg_throughput_mbps": statistics.mean(throughputs) if throughputs else 0,
                "p95_connection_time_ms": statistics.quantiles(connection_times, n=20)[18] if len(connection_times) > 20 else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "active_connections": len(self.active_connections)
            },
            "by_protocol": self._get_metrics_by_protocol(),
            "by_operation": self._get_metrics_by_operation(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_network_optimization_recommendations()
        }

    def _get_metrics_by_protocol(self) -> Dict[str, Dict]:
        """Get metrics grouped by protocol"""
        metrics_by_protocol = defaultdict(list)
        
        for metrics in list(self.network_metrics_history)[-1000:]:
            metrics_by_protocol[metrics.protocol.value].append(metrics)
        
        result = {}
        for protocol, metrics_list in metrics_by_protocol.items():
            connection_times = [m.connection_time_ms for m in metrics_list if m.connection_time_ms > 0]
            latencies = [m.latency_ms for m in metrics_list if m.latency_ms > 0]
            
            result[protocol] = {
                "operations": len(metrics_list),
                "avg_connection_time_ms": statistics.mean(connection_times) if connection_times else 0,
                "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_operation(self) -> Dict[str, Dict]:
        """Get metrics grouped by operation type"""
        metrics_by_op = defaultdict(list)
        
        for metrics in list(self.network_metrics_history)[-1000:]:
            metrics_by_op[metrics.operation.value].append(metrics)
        
        result = {}
        for operation, metrics_list in metrics_by_op.items():
            times = [m.total_time_ms for m in metrics_list]
            
            result[operation] = {
                "operations": len(metrics_list),
                "avg_time_ms": statistics.mean(times) if times else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_network_optimization_recommendations(self) -> List[str]:
        """Get network optimization recommendations"""
        recommendations = []
        
        if not self.network_metrics_history:
            return ["Start profiling network operations to get recommendations"]
        
        recent_metrics = list(self.network_metrics_history)[-100:]
        
        if recent_metrics:
            avg_connection_time = statistics.mean([m.connection_time_ms for m in recent_metrics if m.connection_time_ms > 0])
            avg_latency = statistics.mean([m.latency_ms for m in recent_metrics if m.latency_ms > 0])
            error_rate = (sum(1 for m in recent_metrics if m.error_count > 0) / len(recent_metrics)) * 100
            
            if avg_connection_time > 1000:
                recommendations.append("High connection times - optimize network infrastructure")
            if avg_latency > 200:
                recommendations.append("High network latency - consider CDN or closer servers")
            if error_rate > 2:
                recommendations.append("Network errors detected - check connectivity and implement retry logic")
            if len(self.active_connections) > 100:
                recommendations.append("High concurrent connections - consider connection pooling")
        
        if not recommendations:
            recommendations.append("Network performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[NetworkBottleneck]:
        """Get recent network bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def export_metrics(self, format: str = "json") -> str:
        """Export network metrics"""
        data = {
            "network_metrics": [
                {
                    "operation_id": m.operation_id,
                    "protocol": m.protocol.value,
                    "operation": m.operation.value,
                    "connection_time_ms": m.connection_time_ms,
                    "latency_ms": m.latency_ms,
                    "throughput_mbps": m.throughput_mbps,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.network_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "protocol": b.protocol.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ]
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_network_communication_profiler(monitoring_interval: float = 2.0,
                                         max_history_size: int = 20000,
                                         start_monitoring: bool = True) -> NetworkCommunicationProfiler:
    """
    Create and configure a network communication profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured NetworkCommunicationProfiler instance
    """
    profiler = NetworkCommunicationProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_network_communication_profiler()
    
    try:
        # Example: Profile an HTTP request
        metrics = profiler.profile_http_request(
            url="https://httpbin.org/get",
            method="GET",
            headers={"User-Agent": "Ainflue-Profiler/1.0"}
        )
        
        print(f"HTTP request latency: {metrics.latency_ms:.2f}ms")
        print(f"Connection time: {metrics.connection_time_ms:.2f}ms")
        print(f"Throughput: {metrics.throughput_mbps:.2f}MB/s")
        
        # Example: Profile a TCP connection
        tcp_metrics = profiler.profile_tcp_connection(
            host="google.com",
            port=80
        )
        
        print(f"TCP connection time: {tcp_metrics.connection_time_ms:.2f}ms")
        print(f"DNS resolution: {tcp_metrics.dns_resolution_time_ms:.2f}ms")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Network performance summary: {json.dumps(summary, indent=2)}")
        
    finally:
        profiler.stop_monitoring()