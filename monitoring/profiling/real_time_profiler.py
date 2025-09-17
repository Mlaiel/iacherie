"""⚡ Real-Time Profiling System
============================

Advanced real-time performance monitoring and profiling for the Ainflue Creator Platform.
Provides live streaming metrics, hot path identification, and dynamic optimization triggers.

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
import json
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

# Try to import real-time communication libraries
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    import asyncio
    HAS_ASYNCIO = True
except ImportError:
    HAS_ASYNCIO = False


class RealTimeMetricType(Enum):
    """Types of real-time metrics"""
    PERFORMANCE = "performance"
    BOTTLENECK = "bottleneck"
    ALERT = "alert"
    OPTIMIZATION = "optimization"
    SYSTEM_HEALTH = "system_health"
    USER_ACTIVITY = "user_activity"
    BUSINESS_KPI = "business_kpi"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StreamingChannel(Enum):
    """Streaming channels for different data types"""
    METRICS = "metrics"
    ALERTS = "alerts"
    BOTTLENECKS = "bottlenecks"
    OPTIMIZATIONS = "optimizations"
    DASHBOARD = "dashboard"
    ADMIN = "admin"


@dataclass
class RealTimeMetric:
    """Real-time metric data structure"""
    metric_id: str
    metric_type: RealTimeMetricType
    source: str
    name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RealTimeAlert:
    """Real-time alert data structure"""
    alert_id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HotPath:
    """Hot path identification"""
    path_id: str
    path_name: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    cpu_usage: float
    memory_usage_mb: float
    last_seen: datetime
    optimization_potential: float


class RealTimeProfiler:
    """
    Real-time profiling system for Creator Economy platform
    """
    
    def __init__(self, 
                 streaming_interval: float = 1.0,
                 max_clients: int = 100):
        self.streaming_interval = streaming_interval
        self.max_clients = max_clients
        self.is_running = False
        
        # Real-time data streams
        self.metric_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.connected_clients: Dict[str, Set[Any]] = defaultdict(set)
        
        # Hot path tracking
        self.hot_paths: Dict[str, HotPath] = {}
        self.path_execution_counts: Dict[str, int] = defaultdict(int)
        self.path_timings: Dict[str, List[float]] = defaultdict(list)
        
        # Alert conditions
        self.alert_conditions: List[Dict] = []
        self.optimization_triggers: List[Dict] = []
        
        # Performance thresholds for real-time alerts
        self.thresholds = {
            'cpu_usage_critical': 90.0,      # 90%
            'memory_usage_critical': 90.0,   # 90%
            'response_time_critical': 5000.0, # 5 seconds
            'error_rate_critical': 10.0,     # 10%
            'queue_depth_critical': 1000,    # 1000 items
            'connection_count_critical': 10000 # 10k connections
        }
        
        # WebSocket server for real-time streaming
        self.websocket_server = None
        self.server_task = None
        
        logger.info("RealTimeProfiler initialized")

    async def start_streaming(self, host: str = "localhost", port: int = 8765):
        """Start real-time streaming server"""
        if not HAS_WEBSOCKETS:
            logger.error("WebSockets not available, cannot start streaming")
            return
        
        self.is_running = True
        
        # Start WebSocket server
        self.websocket_server = await websockets.serve(
            self._handle_websocket_connection,
            host,
            port,
            max_size=None,
            max_queue=None
        )
        
        # Start background streaming task
        self.server_task = asyncio.create_task(self._streaming_loop())
        
        logger.info(f"Real-time streaming started on ws://{host}:{port}")

    async def stop_streaming(self):
        """Stop real-time streaming server"""
        self.is_running = False
        
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        logger.info("Real-time streaming stopped")

    async def _handle_websocket_connection(self, websocket, path):
        """Handle WebSocket client connections"""
        try:
            # Parse connection path to determine channel
            channel = path.strip('/') or StreamingChannel.METRICS.value
            
            # Add client to channel
            if len(self.connected_clients[channel]) >= self.max_clients:
                await websocket.close(code=1013, reason="Too many clients")
                return
            
            self.connected_clients[channel].add(websocket)
            logger.info(f"Client connected to channel: {channel}")
            
            # Send initial data
            await self._send_initial_data(websocket, channel)
            
            # Keep connection alive and handle messages
            async for message in websocket:
                await self._handle_client_message(websocket, channel, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {e}")
        finally:
            # Remove client from all channels
            for channel_clients in self.connected_clients.values():
                channel_clients.discard(websocket)

    async def _send_initial_data(self, websocket, channel: str):
        """Send initial data to newly connected client"""
        try:
            if channel == StreamingChannel.METRICS.value:
                # Send recent metrics
                recent_metrics = list(self.metric_streams[channel])[-50:]
                for metric in recent_metrics:
                    await websocket.send(json.dumps({
                        'type': 'metric',
                        'data': asdict(metric)
                    }))
            
            elif channel == StreamingChannel.ALERTS.value:
                # Send recent alerts
                recent_alerts = list(self.alert_streams[channel])[-20:]
                for alert in recent_alerts:
                    await websocket.send(json.dumps({
                        'type': 'alert',
                        'data': asdict(alert)
                    }))
            
            elif channel == StreamingChannel.DASHBOARD.value:
                # Send dashboard summary
                summary = await self._get_dashboard_summary()
                await websocket.send(json.dumps({
                    'type': 'dashboard_summary',
                    'data': summary
                }))
                
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def _handle_client_message(self, websocket, channel: str, message: str):
        """Handle messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Handle subscription to specific metrics
                metric_names = data.get('metrics', [])
                # Store subscription preferences
                # Implementation would track what each client wants
                
            elif message_type == 'set_threshold':
                # Handle dynamic threshold updates
                threshold_name = data.get('name')
                threshold_value = data.get('value')
                if threshold_name in self.thresholds:
                    self.thresholds[threshold_name] = threshold_value
                    
            elif message_type == 'trigger_optimization':
                # Handle manual optimization triggers
                optimization_type = data.get('optimization_type')
                await self._trigger_optimization(optimization_type)
                
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def _streaming_loop(self):
        """Main streaming loop"""
        while self.is_running:
            try:
                # Collect current metrics
                current_metrics = await self._collect_current_metrics()
                
                # Check for alerts
                alerts = await self._check_alert_conditions(current_metrics)
                
                # Update hot paths
                await self._update_hot_paths()
                
                # Stream data to connected clients
                await self._stream_to_clients(current_metrics, alerts)
                
                # Wait for next interval
                await asyncio.sleep(self.streaming_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                await asyncio.sleep(1.0)

    async def _collect_current_metrics(self) -> List[RealTimeMetric]:
        """Collect current system metrics"""
        metrics = []
        current_time = datetime.utcnow()
        
        try:
            # System metrics
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            metrics.append(RealTimeMetric(
                metric_id=f"cpu_usage_{int(time.time())}",
                metric_type=RealTimeMetricType.PERFORMANCE,
                source="system",
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                tags={"component": "system"}
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics.append(RealTimeMetric(
                metric_id=f"memory_usage_{int(time.time())}",
                metric_type=RealTimeMetricType.PERFORMANCE,
                source="system",
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                tags={"component": "system"}
            ))
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.append(RealTimeMetric(
                    metric_id=f"disk_read_{int(time.time())}",
                    metric_type=RealTimeMetricType.PERFORMANCE,
                    source="system",
                    name="disk_read_rate",
                    value=disk_io.read_bytes,
                    unit="bytes",
                    tags={"component": "storage"}
                ))
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.append(RealTimeMetric(
                    metric_id=f"network_sent_{int(time.time())}",
                    metric_type=RealTimeMetricType.PERFORMANCE,
                    source="system",
                    name="network_sent_rate",
                    value=net_io.bytes_sent,
                    unit="bytes",
                    tags={"component": "network"}
                ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics

    async def _check_alert_conditions(self, metrics: List[RealTimeMetric]) -> List[RealTimeAlert]:
        """Check for alert conditions"""
        alerts = []
        
        for metric in metrics:
            # Check CPU usage
            if metric.name == "cpu_usage" and metric.value > self.thresholds['cpu_usage_critical']:
                alerts.append(RealTimeAlert(
                    alert_id=f"cpu_alert_{int(time.time())}",
                    severity=AlertSeverity.CRITICAL,
                    title="High CPU Usage",
                    message=f"CPU usage is critically high: {metric.value:.1f}%",
                    source="system",
                    metric_value=metric.value,
                    threshold=self.thresholds['cpu_usage_critical'],
                    tags={"component": "system", "metric": "cpu_usage"},
                    actions=["Scale infrastructure", "Optimize CPU-intensive operations"]
                ))
            
            # Check memory usage
            if metric.name == "memory_usage" and metric.value > self.thresholds['memory_usage_critical']:
                alerts.append(RealTimeAlert(
                    alert_id=f"memory_alert_{int(time.time())}",
                    severity=AlertSeverity.CRITICAL,
                    title="High Memory Usage",
                    message=f"Memory usage is critically high: {metric.value:.1f}%",
                    source="system",
                    metric_value=metric.value,
                    threshold=self.thresholds['memory_usage_critical'],
                    tags={"component": "system", "metric": "memory_usage"},
                    actions=["Check for memory leaks", "Scale memory resources"]
                ))
        
        return alerts

    async def _update_hot_paths(self):
        """Update hot path analysis"""
        try:
            current_time = datetime.utcnow()
            
            # Update hot paths based on recent execution data
            for path_name, timings in self.path_timings.items():
                if timings:
                    execution_count = self.path_execution_counts[path_name]
                    total_time = sum(timings)
                    avg_time = statistics.mean(timings)
                    
                    # Calculate optimization potential
                    optimization_potential = min(100.0, (avg_time / 1000.0) * execution_count)
                    
                    hot_path = HotPath(
                        path_id=f"path_{hash(path_name)}",
                        path_name=path_name,
                        execution_count=execution_count,
                        total_time_ms=total_time,
                        avg_time_ms=avg_time,
                        cpu_usage=0.0,  # Would need actual CPU profiling
                        memory_usage_mb=0.0,  # Would need actual memory profiling
                        last_seen=current_time,
                        optimization_potential=optimization_potential
                    )
                    
                    self.hot_paths[path_name] = hot_path
            
            # Clear old timing data to prevent memory growth
            for path_name in list(self.path_timings.keys()):
                if len(self.path_timings[path_name]) > 1000:
                    self.path_timings[path_name] = self.path_timings[path_name][-500:]
                    
        except Exception as e:
            logger.error(f"Error updating hot paths: {e}")

    async def _stream_to_clients(self, metrics: List[RealTimeMetric], alerts: List[RealTimeAlert]):
        """Stream data to connected clients"""
        try:
            # Stream metrics
            if metrics:
                metric_data = json.dumps({
                    'type': 'metrics_batch',
                    'data': [asdict(m) for m in metrics],
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                await self._broadcast_to_channel(StreamingChannel.METRICS.value, metric_data)
                await self._broadcast_to_channel(StreamingChannel.DASHBOARD.value, metric_data)
            
            # Stream alerts
            if alerts:
                for alert in alerts:
                    alert_data = json.dumps({
                        'type': 'alert',
                        'data': asdict(alert)
                    })
                    
                    await self._broadcast_to_channel(StreamingChannel.ALERTS.value, alert_data)
                    await self._broadcast_to_channel(StreamingChannel.DASHBOARD.value, alert_data)
            
            # Stream hot paths periodically
            if int(time.time()) % 10 == 0:  # Every 10 seconds
                hot_paths_data = json.dumps({
                    'type': 'hot_paths',
                    'data': [asdict(hp) for hp in self.hot_paths.values()],
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                await self._broadcast_to_channel(StreamingChannel.DASHBOARD.value, hot_paths_data)
            
            # Store in streams for history
            for metric in metrics:
                self.metric_streams[StreamingChannel.METRICS.value].append(metric)
            
            for alert in alerts:
                self.alert_streams[StreamingChannel.ALERTS.value].append(alert)
                
        except Exception as e:
            logger.error(f"Error streaming to clients: {e}")

    async def _broadcast_to_channel(self, channel: str, data: str):
        """Broadcast data to all clients in a channel"""
        if channel not in self.connected_clients:
            return
        
        disconnected_clients = set()
        
        for client in self.connected_clients[channel].copy():
            try:
                await client.send(data)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.warning(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.connected_clients[channel].discard(client)

    async def _get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary data"""
        try:
            recent_metrics = list(self.metric_streams[StreamingChannel.METRICS.value])[-100:]
            recent_alerts = list(self.alert_streams[StreamingChannel.ALERTS.value])[-10:]
            
            # Calculate summary statistics
            cpu_values = [m.value for m in recent_metrics if m.name == "cpu_usage"]
            memory_values = [m.value for m in recent_metrics if m.name == "memory_usage"]
            
            summary = {
                'total_clients': sum(len(clients) for clients in self.connected_clients.values()),
                'metrics_count': len(recent_metrics),
                'alerts_count': len(recent_alerts),
                'hot_paths_count': len(self.hot_paths),
                'avg_cpu_usage': statistics.mean(cpu_values) if cpu_values else 0,
                'avg_memory_usage': statistics.mean(memory_values) if memory_values else 0,
                'critical_alerts': len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]),
                'top_hot_paths': sorted(
                    self.hot_paths.values(),
                    key=lambda x: x.optimization_potential,
                    reverse=True
                )[:5],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {}

    def track_execution_path(self, path_name: str, execution_time_ms: float):
        """Track execution path for hot path analysis"""
        self.path_execution_counts[path_name] += 1
        self.path_timings[path_name].append(execution_time_ms)

    def add_custom_metric(self, metric: RealTimeMetric):
        """Add a custom metric to the real-time stream"""
        self.metric_streams[StreamingChannel.METRICS.value].append(metric)

    def add_custom_alert(self, alert: RealTimeAlert):
        """Add a custom alert to the real-time stream"""
        self.alert_streams[StreamingChannel.ALERTS.value].append(alert)

    async def _trigger_optimization(self, optimization_type: str):
        """Trigger optimization based on real-time analysis"""
        try:
            logger.info(f"Triggering optimization: {optimization_type}")
            
            # This would integrate with actual optimization systems
            # For now, just log the trigger
            
            optimization_alert = RealTimeAlert(
                alert_id=f"optimization_{int(time.time())}",
                severity=AlertSeverity.INFO,
                title="Optimization Triggered",
                message=f"Automatic optimization triggered: {optimization_type}",
                source="real_time_profiler",
                tags={"optimization_type": optimization_type},
                actions=["Monitor results", "Validate performance improvement"]
            )
            
            await self._broadcast_to_channel(
                StreamingChannel.ALERTS.value,
                json.dumps({'type': 'alert', 'data': asdict(optimization_alert)})
            )
            
        except Exception as e:
            logger.error(f"Error triggering optimization: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get real-time performance summary"""
        recent_metrics = list(self.metric_streams[StreamingChannel.METRICS.value])[-100:]
        recent_alerts = list(self.alert_streams[StreamingChannel.ALERTS.value])[-20:]
        
        return {
            "real_time_status": {
                "is_running": self.is_running,
                "connected_clients": sum(len(clients) for clients in self.connected_clients.values()),
                "streaming_interval": self.streaming_interval,
                "metrics_per_second": len(recent_metrics) / max(1, len(recent_metrics) / 100)
            },
            "current_metrics": {
                "total_metrics": len(recent_metrics),
                "metrics_by_type": {
                    metric_type.value: len([m for m in recent_metrics if m.metric_type == metric_type])
                    for metric_type in RealTimeMetricType
                }
            },
            "alerts": {
                "total_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]),
                "warning_alerts": len([a for a in recent_alerts if a.severity == AlertSeverity.WARNING])
            },
            "hot_paths": {
                "total_paths": len(self.hot_paths),
                "high_potential_paths": len([hp for hp in self.hot_paths.values() if hp.optimization_potential > 50])
            }
        }


# Factory function
def create_real_time_profiler(streaming_interval: float = 1.0,
                            max_clients: int = 100) -> RealTimeProfiler:
    """
    Create and configure a real-time profiler
    
    Args:
        streaming_interval: Streaming interval in seconds
        max_clients: Maximum number of concurrent clients
        
    Returns:
        Configured RealTimeProfiler instance
    """
    return RealTimeProfiler(
        streaming_interval=streaming_interval,
        max_clients=max_clients
    )


# Main execution
if __name__ == "__main__":
    async def main():
        # Example usage
        profiler = create_real_time_profiler()
        
        try:
            # Start streaming server
            await profiler.start_streaming(host="localhost", port=8765)
            
            # Simulate some execution paths
            profiler.track_execution_path("content_upload", 250.0)
            profiler.track_execution_path("user_authentication", 150.0)
            profiler.track_execution_path("video_processing", 2500.0)
            
            # Add custom metric
            custom_metric = RealTimeMetric(
                metric_id="custom_metric_001",
                metric_type=RealTimeMetricType.BUSINESS_KPI,
                source="creator_platform",
                name="active_creators",
                value=1250.0,
                unit="count",
                tags={"region": "us-east-1"}
            )
            profiler.add_custom_metric(custom_metric)
            
            print("Real-time profiler started. Connect to ws://localhost:8765/metrics")
            print("Press Ctrl+C to stop...")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("Stopping real-time profiler...")
        finally:
            await profiler.stop_streaming()

    if HAS_ASYNCIO:
        asyncio.run(main())
    else:
        print("Asyncio not available, cannot run real-time profiler")