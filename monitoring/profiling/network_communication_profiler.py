"""🌐 Network Communication Performance Profiler
================================================

Advanced network communication performance profiling system for the Ainflue Creator Economy platform.
Monitors HTTP requests, WebSocket connections, gRPC calls, and network latency optimization.

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
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import psutil

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class NetworkProtocol(Enum):
    """Network protocols"""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    WEBSOCKET_SECURE = "websocket_secure"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    QUIC = "quic"


class CommunicationType(Enum):
    """Types of network communications"""
    CLIENT_SERVER = "client_server"
    PEER_TO_PEER = "peer_to_peer"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    STREAMING = "streaming"
    REAL_TIME = "real_time"


class NetworkDirection(Enum):
    """Network communication direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class NetworkDomain(Enum):
    """Network communication domains for Creator Economy"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DOWNLOAD = "content_download"
    LIVE_STREAMING = "live_streaming"
    REAL_TIME_CHAT = "real_time_chat"
    API_COMMUNICATION = "api_communication"
    CDN_DELIVERY = "cdn_delivery"
    ANALYTICS_SYNC = "analytics_sync"
    COLLABORATION_SYNC = "collaboration_sync"
    NOTIFICATION_DELIVERY = "notification_delivery"
    PAYMENT_PROCESSING = "payment_processing"


@dataclass
class NetworkEndpoint:
    """Network endpoint information"""
    host: str
    port: int
    protocol: NetworkProtocol
    endpoint_type: str  # "api", "cdn", "streaming", "database", "cache"
    region: Optional[str] = None
    provider: Optional[str] = None  # "aws", "gcp", "azure", "cloudflare"


@dataclass
class NetworkRequestMetadata:
    """Metadata for network requests"""
    request_id: str
    source_endpoint: NetworkEndpoint
    destination_endpoint: NetworkEndpoint
    protocol: NetworkProtocol
    communication_type: CommunicationType
    direction: NetworkDirection
    domain: NetworkDomain
    
    # Request details
    payload_size_bytes: int
    headers_count: int
    compression_enabled: bool = False
    encryption_enabled: bool = True
    
    # Connection details
    connection_reused: bool = False
    keep_alive: bool = True
    
    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    client_ip: Optional[str] = None


@dataclass
class NetworkMetrics:
    """Network communication performance metrics"""
    request_id: str
    metadata: NetworkRequestMetadata
    
    # Timing metrics (all in milliseconds)
    total_time_ms: float
    dns_lookup_time_ms: Optional[float] = None
    tcp_connect_time_ms: Optional[float] = None
    tls_handshake_time_ms: Optional[float] = None
    time_to_first_byte_ms: Optional[float] = None
    data_transfer_time_ms: Optional[float] = None
    
    # Network performance metrics
    throughput_mbps: float = 0.0
    latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_percent: float = 0.0
    
    # Bandwidth metrics
    bytes_sent: int = 0
    bytes_received: int = 0
    bandwidth_utilization_percent: float = 0.0
    
    # Connection metrics
    connection_count: int = 1
    concurrent_connections: int = 1
    connection_pool_size: int = 0
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    status_code: Optional[int] = None
    
    # CDN metrics (for CDN communications)
    cache_hit: Optional[bool] = None
    edge_location: Optional[str] = None
    pop_location: Optional[str] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NetworkBottleneck:
    """Network performance bottleneck detection"""
    bottleneck_id: str
    source_endpoint: NetworkEndpoint
    destination_endpoint: NetworkEndpoint
    domain: NetworkDomain
    
    # Bottleneck details
    bottleneck_type: str  # "high_latency", "low_throughput", "packet_loss", "connection_limit"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected communications
    affected_requests: List[str]
    communication_patterns: List[str]
    
    # Network analysis
    network_path_analysis: Dict[str, Any]
    suggested_optimizations: List[str]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class NetworkCommunicationProfiler:
    """Advanced network communication performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 2.0,
                 max_history_size: int = 10000,
                 enable_packet_analysis: bool = True,
                 enable_path_tracing: bool = False,
                 high_latency_threshold_ms: float = 200.0):
        """
        Initialize network communication profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_packet_analysis: Enable detailed packet analysis
            enable_path_tracing: Enable network path tracing (requires privileges)
            high_latency_threshold_ms: Threshold for high latency detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_packet_analysis = enable_packet_analysis
        self.enable_path_tracing = enable_path_tracing
        self.high_latency_threshold_ms = high_latency_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.active_connections: Dict[str, NetworkMetrics] = {}
        self.bottlenecks: List[NetworkBottleneck] = []
        self.connection_pools: Dict[str, List[NetworkMetrics]] = defaultdict(list)
        
        # Network pattern tracking
        self.endpoint_patterns: Dict[str, List[float]] = defaultdict(list)
        self.bandwidth_usage: Dict[str, List[float]] = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'max_latency_ms': high_latency_threshold_ms,
            'min_throughput_mbps': 1.0,
            'max_packet_loss_percent': 1.0,
            'max_connection_time_ms': 5000.0,
            'max_dns_lookup_time_ms': 100.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Network interface monitoring
        self.network_interfaces = {}
        self.last_network_stats = {}
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("NetworkCommunicationProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'network_request_duration': Histogram(
                'ainflue_network_request_duration_seconds',
                'Duration of network requests',
                ['protocol', 'domain', 'destination']
            ),
            'network_throughput': Gauge(
                'ainflue_network_throughput_mbps',
                'Network throughput in MB/s',
                ['protocol', 'domain', 'direction']
            ),
            'network_latency': Gauge(
                'ainflue_network_latency_ms',
                'Network latency in ms',
                ['protocol', 'domain', 'destination']
            ),
            'network_errors': Counter(
                'ainflue_network_errors_total',
                'Total network errors',
                ['protocol', 'error_type', 'domain']
            ),
            'network_connections': Gauge(
                'ainflue_network_connections_active',
                'Active network connections',
                ['protocol', 'domain']
            ),
            'network_bandwidth_utilization': Gauge(
                'ainflue_network_bandwidth_utilization_percent',
                'Network bandwidth utilization percentage',
                ['interface', 'direction']
            ),
            'network_bottlenecks': Gauge(
                'ainflue_network_bottlenecks_active',
                'Number of active network bottlenecks',
                ['domain', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous network monitoring"""
        if self.is_monitoring:
            logger.warning("Network monitoring already running")
            return
        
        self.is_monitoring = True
        
        # Initialize network interface monitoring
        await self._initialize_network_monitoring()
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Network communication monitoring started")
    
    async def stop_monitoring(self):
        """Stop network monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Network communication monitoring stopped")
    
    async def profile_network_request(self,
                                    metadata: NetworkRequestMetadata,
                                    network_func: Callable,
                                    *args, **kwargs) -> NetworkMetrics:
        """
        Profile a network communication
        
        Args:
            metadata: Network request metadata
            network_func: Function to execute and profile
            *args, **kwargs: Arguments for the network function
        
        Returns:
            NetworkMetrics: Detailed performance metrics
        """
        start_time = time.time()
        
        # Initialize metrics
        metrics = NetworkMetrics(
            request_id=metadata.request_id,
            metadata=metadata,
            total_time_ms=0.0
        )
        
        try:
            # Measure DNS lookup if hostname is used
            if metadata.destination_endpoint.host and not self._is_ip_address(metadata.destination_endpoint.host):
                dns_start = time.time()
                await self._measure_dns_lookup(metadata.destination_endpoint.host)
                dns_end = time.time()
                metrics.dns_lookup_time_ms = (dns_end - dns_start) * 1000
            
            # Measure connection establishment
            if not metadata.connection_reused:
                connect_start = time.time()
                await self._measure_connection_establishment(metadata)
                connect_end = time.time()
                metrics.tcp_connect_time_ms = (connect_end - connect_start) * 1000
                
                # Measure TLS handshake for secure connections
                if metadata.protocol in [NetworkProtocol.HTTPS, NetworkProtocol.WEBSOCKET_SECURE, NetworkProtocol.GRPC]:
                    tls_start = time.time()
                    await self._measure_tls_handshake(metadata)
                    tls_end = time.time()
                    metrics.tls_handshake_time_ms = (tls_end - tls_start) * 1000
            
            # Execute the network operation
            data_start = time.time()
            result = await self._execute_network_operation(network_func, *args, **kwargs)
            data_end = time.time()
            
            metrics.data_transfer_time_ms = (data_end - data_start) * 1000
            
            # Calculate performance metrics
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            
            # Calculate throughput
            if metadata.payload_size_bytes > 0:
                transfer_time_seconds = (data_end - data_start)
                if transfer_time_seconds > 0:
                    metrics.throughput_mbps = (metadata.payload_size_bytes / (1024 * 1024)) / transfer_time_seconds
            
            # Extract response information
            metrics = await self._extract_response_metrics(result, metrics)
            
            # Measure latency (simplified)
            metrics.latency_ms = metrics.total_time_ms / 2  # Simplified RTT calculation
            
            # Set success
            metrics.success = True
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track network patterns
            await self._track_network_patterns(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"Network request profiled: {metadata.request_id} - {metrics.total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle network failure
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            metrics.success = False
            metrics.error_message = str(e)
            metrics.error_type = type(e).__name__
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['network_errors'].labels(
                protocol=metadata.protocol.value,
                error_type=metrics.error_type,
                domain=metadata.domain.value
            ).inc()
            
            logger.error(f"Network request failed: {metadata.request_id} - {e}")
            return metrics
    
    def _is_ip_address(self, host: str) -> bool:
        """Check if host is an IP address"""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
    
    async def _measure_dns_lookup(self, hostname: str):
        """Measure DNS lookup time"""
        try:
            # Simulate DNS lookup
            await asyncio.sleep(0.001)  # Simulated DNS lookup time
        except Exception as e:
            logger.warning(f"DNS lookup failed for {hostname}: {e}")
    
    async def _measure_connection_establishment(self, metadata: NetworkRequestMetadata):
        """Measure connection establishment time"""
        try:
            # Simulate connection establishment
            await asyncio.sleep(0.002)  # Simulated connection time
        except Exception as e:
            logger.warning(f"Connection establishment failed: {e}")
    
    async def _measure_tls_handshake(self, metadata: NetworkRequestMetadata):
        """Measure TLS handshake time"""
        try:
            # Simulate TLS handshake
            await asyncio.sleep(0.005)  # Simulated TLS handshake time
        except Exception as e:
            logger.warning(f"TLS handshake failed: {e}")
    
    async def _execute_network_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute network operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    async def _extract_response_metrics(self, result: Any, metrics: NetworkMetrics) -> NetworkMetrics:
        """Extract response metrics from network operation result"""
        if isinstance(result, dict):
            # Extract status code
            metrics.status_code = result.get('status_code', 200)
            
            # Extract bytes information
            metrics.bytes_received = result.get('bytes_received', 0)
            metrics.bytes_sent = result.get('bytes_sent', 0)
            
            # Extract CDN information
            metrics.cache_hit = result.get('cache_hit')
            metrics.edge_location = result.get('edge_location')
            metrics.pop_location = result.get('pop_location')
        
        return metrics
    
    async def _store_metrics(self, metrics: NetworkMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            
            # Track active connections
            connection_key = f"{metrics.metadata.destination_endpoint.host}:{metrics.metadata.destination_endpoint.port}"
            self.active_connections[connection_key] = metrics
            
            # Update connection pools
            pool_key = f"{metrics.metadata.protocol.value}_{connection_key}"
            self.connection_pools[pool_key].append(metrics)
            
            # Keep connection pool size manageable
            if len(self.connection_pools[pool_key]) > 100:
                self.connection_pools[pool_key] = self.connection_pools[pool_key][-100:]
    
    def _update_prometheus_metrics(self, metrics: NetworkMetrics):
        """Update Prometheus metrics"""
        destination = f"{metrics.metadata.destination_endpoint.host}:{metrics.metadata.destination_endpoint.port}"
        
        # Update request duration
        self.prometheus_metrics['network_request_duration'].labels(
            protocol=metrics.metadata.protocol.value,
            domain=metrics.metadata.domain.value,
            destination=destination
        ).observe(metrics.total_time_ms / 1000)
        
        # Update throughput
        self.prometheus_metrics['network_throughput'].labels(
            protocol=metrics.metadata.protocol.value,
            domain=metrics.metadata.domain.value,
            direction=metrics.metadata.direction.value
        ).set(metrics.throughput_mbps)
        
        # Update latency
        self.prometheus_metrics['network_latency'].labels(
            protocol=metrics.metadata.protocol.value,
            domain=metrics.metadata.domain.value,
            destination=destination
        ).set(metrics.latency_ms)
        
        # Update active connections
        self.prometheus_metrics['network_connections'].labels(
            protocol=metrics.metadata.protocol.value,
            domain=metrics.metadata.domain.value
        ).set(metrics.concurrent_connections)
    
    async def _track_network_patterns(self, metrics: NetworkMetrics):
        """Track network patterns for optimization"""
        endpoint_key = f"{metrics.metadata.destination_endpoint.host}:{metrics.metadata.destination_endpoint.port}"
        
        with self._lock:
            self.endpoint_patterns[endpoint_key].append(metrics.latency_ms)
            self.bandwidth_usage[endpoint_key].append(metrics.throughput_mbps)
            
            # Keep only recent patterns
            if len(self.endpoint_patterns[endpoint_key]) > 100:
                self.endpoint_patterns[endpoint_key] = self.endpoint_patterns[endpoint_key][-100:]
            if len(self.bandwidth_usage[endpoint_key]) > 100:
                self.bandwidth_usage[endpoint_key] = self.bandwidth_usage[endpoint_key][-100:]
    
    async def _detect_bottlenecks(self, metrics: NetworkMetrics):
        """Detect network performance bottlenecks"""
        bottlenecks = []
        
        # High latency detection
        if metrics.latency_ms > self.thresholds['max_latency_ms']:
            bottleneck = NetworkBottleneck(
                bottleneck_id=f"high_latency_{int(time.time())}",
                source_endpoint=metrics.metadata.source_endpoint,
                destination_endpoint=metrics.metadata.destination_endpoint,
                domain=metrics.metadata.domain,
                bottleneck_type="high_latency",
                severity="high" if metrics.latency_ms > self.thresholds['max_latency_ms'] * 2 else "medium",
                description=f"High network latency detected: {metrics.latency_ms:.2f}ms",
                current_performance={"latency_ms": metrics.latency_ms},
                expected_performance={"latency_ms": self.thresholds['max_latency_ms']},
                impact_percentage=(metrics.latency_ms - self.thresholds['max_latency_ms']) / self.thresholds['max_latency_ms'] * 100,
                affected_requests=[metrics.request_id],
                communication_patterns=[f"{metrics.metadata.protocol.value}_{metrics.metadata.domain.value}"],
                network_path_analysis={"hops": "unknown", "bottleneck_location": "unknown"},
                suggested_optimizations=[
                    "Consider using a CDN for content delivery",
                    "Optimize network routing",
                    "Implement connection pooling",
                    "Use regional endpoints closer to users"
                ],
                recommendations=[
                    "Analyze network path for optimization opportunities",
                    "Consider edge computing solutions",
                    "Implement intelligent request routing",
                    "Optimize payload sizes and compression"
                ],
                estimated_improvement={"latency_reduction_percent": 30.0}
            )
            bottlenecks.append(bottleneck)
        
        # Low throughput detection
        if metrics.throughput_mbps < self.thresholds['min_throughput_mbps'] and metrics.throughput_mbps > 0:
            bottleneck = NetworkBottleneck(
                bottleneck_id=f"low_throughput_{int(time.time())}",
                source_endpoint=metrics.metadata.source_endpoint,
                destination_endpoint=metrics.metadata.destination_endpoint,
                domain=metrics.metadata.domain,
                bottleneck_type="low_throughput",
                severity="medium",
                description=f"Low network throughput detected: {metrics.throughput_mbps:.2f} MB/s",
                current_performance={"throughput_mbps": metrics.throughput_mbps},
                expected_performance={"throughput_mbps": self.thresholds['min_throughput_mbps']},
                impact_percentage=(self.thresholds['min_throughput_mbps'] - metrics.throughput_mbps) / self.thresholds['min_throughput_mbps'] * 100,
                affected_requests=[metrics.request_id],
                communication_patterns=[f"{metrics.metadata.protocol.value}_{metrics.metadata.domain.value}"],
                network_path_analysis={"bandwidth_limit": "unknown", "congestion": "possible"},
                suggested_optimizations=[
                    "Implement data compression",
                    "Optimize transfer protocols",
                    "Use parallel connections",
                    "Implement adaptive bitrate streaming"
                ],
                recommendations=[
                    "Review bandwidth allocation and limits",
                    "Implement traffic shaping and QoS",
                    "Consider protocol optimization (HTTP/2, QUIC)",
                    "Optimize data serialization formats"
                ],
                estimated_improvement={"throughput_improvement_percent": 50.0}
            )
            bottlenecks.append(bottleneck)
        
        # DNS lookup bottleneck
        if (metrics.dns_lookup_time_ms is not None and 
            metrics.dns_lookup_time_ms > self.thresholds['max_dns_lookup_time_ms']):
            bottleneck = NetworkBottleneck(
                bottleneck_id=f"dns_slow_{int(time.time())}",
                source_endpoint=metrics.metadata.source_endpoint,
                destination_endpoint=metrics.metadata.destination_endpoint,
                domain=metrics.metadata.domain,
                bottleneck_type="slow_dns",
                severity="low",
                description=f"Slow DNS lookup: {metrics.dns_lookup_time_ms:.2f}ms",
                current_performance={"dns_lookup_time_ms": metrics.dns_lookup_time_ms},
                expected_performance={"dns_lookup_time_ms": self.thresholds['max_dns_lookup_time_ms']},
                impact_percentage=(metrics.dns_lookup_time_ms - self.thresholds['max_dns_lookup_time_ms']) / self.thresholds['max_dns_lookup_time_ms'] * 100,
                affected_requests=[metrics.request_id],
                communication_patterns=[f"dns_{metrics.metadata.destination_endpoint.host}"],
                network_path_analysis={"dns_server": "unknown", "resolution_path": "unknown"},
                suggested_optimizations=[
                    "Implement DNS caching",
                    "Use faster DNS servers",
                    "Implement DNS prefetching",
                    "Consider DNS over HTTPS"
                ],
                recommendations=[
                    "Configure local DNS caching",
                    "Use multiple DNS servers for redundancy",
                    "Implement DNS monitoring and alerting",
                    "Consider using a DNS service provider"
                ],
                estimated_improvement={"dns_time_reduction_percent": 60.0}
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['network_bottlenecks'].labels(
                domain=bottleneck.domain.value,
                severity=bottleneck.severity
            ).inc()
    
    async def _initialize_network_monitoring(self):
        """Initialize network interface monitoring"""
        try:
            # Get initial network interface stats
            self.network_interfaces = psutil.net_if_stats()
            self.last_network_stats = psutil.net_io_counters(pernic=True)
        except Exception as e:
            logger.warning(f"Failed to initialize network monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor network interfaces
                await self._monitor_network_interfaces()
                
                # Monitor endpoint patterns
                await self._monitor_endpoint_patterns()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in network monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_network_interfaces(self):
        """Monitor network interface performance"""
        try:
            current_stats = psutil.net_io_counters(pernic=True)
            
            if self.last_network_stats:
                for interface, stats in current_stats.items():
                    if interface in self.last_network_stats:
                        last_stats = self.last_network_stats[interface]
                        
                        # Calculate bandwidth utilization
                        bytes_sent_diff = stats.bytes_sent - last_stats.bytes_sent
                        bytes_recv_diff = stats.bytes_recv - last_stats.bytes_recv
                        
                        # Update Prometheus metrics
                        if bytes_sent_diff > 0:
                            sent_mbps = (bytes_sent_diff / (1024 * 1024)) / self.monitoring_interval
                            self.prometheus_metrics['network_bandwidth_utilization'].labels(
                                interface=interface,
                                direction='outbound'
                            ).set(min(100.0, sent_mbps))
                        
                        if bytes_recv_diff > 0:
                            recv_mbps = (bytes_recv_diff / (1024 * 1024)) / self.monitoring_interval
                            self.prometheus_metrics['network_bandwidth_utilization'].labels(
                                interface=interface,
                                direction='inbound'
                            ).set(min(100.0, recv_mbps))
            
            self.last_network_stats = current_stats
            
        except Exception as e:
            logger.error(f"Error monitoring network interfaces: {e}")
    
    async def _monitor_endpoint_patterns(self):
        """Monitor endpoint communication patterns"""
        try:
            with self._lock:
                for endpoint, latencies in self.endpoint_patterns.items():
                    if len(latencies) > 10:  # Enough data points
                        avg_latency = statistics.mean(latencies)
                        if avg_latency > self.high_latency_threshold_ms:
                            logger.warning(f"High latency endpoint: {endpoint} - avg {avg_latency:.2f}ms")
                        
                        # Check for high variance (unstable connection)
                        if len(latencies) > 5:
                            variance = statistics.stdev(latencies)
                            if variance > avg_latency * 0.3:  # High variance
                                logger.warning(f"Unstable connection: {endpoint} - stdev {variance:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring endpoint patterns: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old active connections
        old_connections = [conn_id for conn_id, metrics in self.active_connections.items() 
                          if metrics.timestamp < cutoff_time]
        for conn_id in old_connections:
            del self.active_connections[conn_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get network performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 requests
        
        # Calculate averages
        avg_latency = statistics.mean([m.latency_ms for m in recent_metrics])
        avg_throughput = statistics.mean([m.throughput_mbps for m in recent_metrics if m.throughput_mbps > 0])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # Protocol breakdown
        protocol_breakdown = defaultdict(list)
        for metric in recent_metrics:
            protocol_breakdown[metric.metadata.protocol.value].append(metric)
        
        # Domain breakdown
        domain_breakdown = defaultdict(list)
        for metric in recent_metrics:
            domain_breakdown[metric.metadata.domain.value].append(metric)
        
        return {
            "overall_performance": {
                "average_latency_ms": avg_latency,
                "average_throughput_mbps": avg_throughput if avg_throughput > 0 else 0.0,
                "success_rate_percent": success_rate,
                "total_requests": len(recent_metrics),
                "active_connections": len(self.active_connections)
            },
            "protocol_breakdown": {
                protocol: {
                    "request_count": len(metrics),
                    "avg_latency_ms": statistics.mean([m.latency_ms for m in metrics]),
                    "avg_throughput_mbps": statistics.mean([m.throughput_mbps for m in metrics if m.throughput_mbps > 0]) or 0.0
                }
                for protocol, metrics in protocol_breakdown.items()
            },
            "domain_breakdown": {
                domain: {
                    "request_count": len(metrics),
                    "avg_latency_ms": statistics.mean([m.latency_ms for m in metrics])
                }
                for domain, metrics in domain_breakdown.items()
            },
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "source": f"{b.source_endpoint.host}:{b.source_endpoint.port}",
                "destination": f"{b.destination_endpoint.host}:{b.destination_endpoint.port}",
                "domain": b.domain.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_requests": b.affected_requests,
                "communication_patterns": b.communication_patterns,
                "network_path_analysis": b.network_path_analysis,
                "suggested_optimizations": b.suggested_optimizations,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


class NetworkProfiler:
    """Simplified network profiler interface"""
    
    def __init__(self):
        self.profiler = NetworkCommunicationProfiler()
    
    async def start_monitoring(self):
        """Start network monitoring"""
        return await self.profiler.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop network monitoring"""
        return await self.profiler.stop_monitoring()
    
    async def profile_request(self,
                            source_host: str,
                            dest_host: str,
                            dest_port: int,
                            protocol: str,
                            domain: str,
                            network_func: Callable,
                            *args, **kwargs):
        """Profile a network request"""
        # Convert strings to enums
        net_protocol = NetworkProtocol(protocol.lower())
        net_domain = NetworkDomain(domain.lower())
        
        # Create endpoints
        source_endpoint = NetworkEndpoint(
            host=source_host,
            port=0,  # Source port not specified
            protocol=net_protocol,
            endpoint_type="client"
        )
        
        dest_endpoint = NetworkEndpoint(
            host=dest_host,
            port=dest_port,
            protocol=net_protocol,
            endpoint_type="server"
        )
        
        # Create request metadata
        metadata = NetworkRequestMetadata(
            request_id=f"net_{int(time.time() * 1000)}",
            source_endpoint=source_endpoint,
            destination_endpoint=dest_endpoint,
            protocol=net_protocol,
            communication_type=CommunicationType.CLIENT_SERVER,
            direction=NetworkDirection.OUTBOUND,
            domain=net_domain,
            payload_size_bytes=0,  # Would be calculated from actual request
            headers_count=0
        )
        
        return await self.profiler.profile_network_request(
            metadata, network_func, *args, **kwargs
        )


def create_network_communication_profiler(
    monitoring_interval: float = 2.0,
    enable_packet_analysis: bool = True,
    enable_path_tracing: bool = False,
    high_latency_threshold_ms: float = 200.0,
    start_monitoring: bool = False
) -> NetworkCommunicationProfiler:
    """
    Factory function to create network communication profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_packet_analysis: Enable detailed packet analysis
        enable_path_tracing: Enable network path tracing
        high_latency_threshold_ms: Threshold for high latency detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        NetworkCommunicationProfiler: Configured network profiler instance
    """
    profiler = NetworkCommunicationProfiler(
        monitoring_interval=monitoring_interval,
        enable_packet_analysis=enable_packet_analysis,
        enable_path_tracing=enable_path_tracing,
        high_latency_threshold_ms=high_latency_threshold_ms
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_creator_network_profiling():
    """Example of profiling Creator Economy network communications"""
    profiler = create_network_communication_profiler(start_monitoring=True)
    
    # Example: Profile content upload to CDN
    async def upload_to_cdn(file_data: bytes, destination: str):
        # Simulate CDN upload
        await asyncio.sleep(0.1)  # Simulate upload time
        return {
            "status_code": 200,
            "bytes_sent": len(file_data),
            "bytes_received": 64,  # Response metadata
            "cache_hit": False,
            "edge_location": "us-east-1",
            "pop_location": "virginia"
        }
    
    # Create network endpoints
    source_endpoint = NetworkEndpoint(
        host="192.168.1.100",
        port=0,
        protocol=NetworkProtocol.HTTPS,
        endpoint_type="client"
    )
    
    destination_endpoint = NetworkEndpoint(
        host="cdn.ainflue.com",
        port=443,
        protocol=NetworkProtocol.HTTPS,
        endpoint_type="cdn",
        provider="cloudflare"
    )
    
    # Create request metadata
    file_data = b"x" * (5 * 1024 * 1024)  # 5MB file
    metadata = NetworkRequestMetadata(
        request_id="upload_video_123",
        source_endpoint=source_endpoint,
        destination_endpoint=destination_endpoint,
        protocol=NetworkProtocol.HTTPS,
        communication_type=CommunicationType.CLIENT_SERVER,
        direction=NetworkDirection.OUTBOUND,
        domain=NetworkDomain.CONTENT_UPLOAD,
        payload_size_bytes=len(file_data),
        headers_count=8,
        compression_enabled=True,
        user_id="creator_456"
    )
    
    metrics = await profiler.profile_network_request(
        metadata=metadata,
        network_func=upload_to_cdn,
        file_data,
        "cdn://ainflue-content/videos/"
    )
    
    print(f"Network profiling completed:")
    print(f"- Total time: {metrics.total_time_ms:.2f}ms")
    print(f"- Latency: {metrics.latency_ms:.2f}ms")
    print(f"- Throughput: {metrics.throughput_mbps:.2f} MB/s")
    print(f"- DNS lookup: {metrics.dns_lookup_time_ms:.2f}ms" if metrics.dns_lookup_time_ms else "- No DNS lookup")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_creator_network_profiling())