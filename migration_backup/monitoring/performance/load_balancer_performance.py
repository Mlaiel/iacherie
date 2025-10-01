"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Load Balancer Performance Monitor - Enterprise Performance Monitoring
Advanced load balancer performance monitoring for Creator Economy infrastructure

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import json
import statistics
import requests
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import threading
from prometheus_client import Gauge, Counter, Histogram
from urllib.parse import urljoin, urlparse
import socket
import ssl
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class LoadBalancerMetrics:
    """Load balancer performance metrics"""
    lb_name: str
    lb_type: str  # haproxy, nginx, aws_alb, aws_nlb, gcp_lb
    active_connections: int
    total_requests: int
    requests_per_second: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    error_count: int
    error_rate_percent: float
    ssl_handshake_time_ms: float
    backend_server_count: int
    healthy_backends: int
    timestamp: datetime

@dataclass
class BackendServerMetrics:
    """Backend server performance metrics"""
    lb_name: str
    server_name: str
    server_address: str
    server_port: int
    status: str  # up, down, maintenance
    active_connections: int
    total_requests: int
    response_time_ms: float
    error_count: int
    health_check_status: str  # passing, failing, unknown
    last_health_check: datetime
    weight: int
    timestamp: datetime

@dataclass
class HealthCheckMetrics:
    """Health check performance metrics"""
    lb_name: str
    backend_server: str
    check_type: str  # http, tcp, ssl
    check_interval_seconds: int
    check_timeout_seconds: int
    success: bool
    response_time_ms: float
    status_code: Optional[int]
    error_message: Optional[str]
    consecutive_failures: int
    timestamp: datetime

@dataclass
class FailoverMetrics:
    """Failover event metrics"""
    lb_name: str
    failed_backend: str
    failover_target: str
    failover_reason: str
    failover_time_ms: float
    impact_duration_seconds: int
    affected_connections: int
    automatic_recovery: bool
    timestamp: datetime

@dataclass
class TrafficDistributionMetrics:
    """Traffic distribution analytics"""
    lb_name: str
    algorithm: str  # round_robin, least_connections, ip_hash, weighted
    backend_distributions: Dict[str, float]  # server -> percentage of traffic
    distribution_balance_score: float  # 0-100, higher is more balanced
    hot_spot_servers: List[str]
    underutilized_servers: List[str]
    timestamp: datetime

@dataclass
class SSLPerformanceMetrics:
    """SSL/TLS performance metrics"""
    lb_name: str
    ssl_version: str
    cipher_suite: str
    handshake_time_ms: float
    certificate_validation_time_ms: float
    ssl_session_reuse_rate: float
    ssl_errors_count: int
    certificate_expiry_days: int
    timestamp: datetime

class LoadBalancerPerformance:
    """
    Enterprise-grade load balancer performance monitor
    Tracks HAProxy, NGINX, AWS ALB/NLB, and other load balancer metrics
    """
    
    def __init__(self,
                 load_balancers: List[Dict] = None,
                 health_check_interval: int = 30,
                 enable_ssl_monitoring: bool = True,
                 enable_automatic_failover_detection: bool = True):
        """
        Initialize load balancer performance monitor
        
        Args:
            load_balancers: List of load balancer configurations
            health_check_interval: Health check interval in seconds
            enable_ssl_monitoring: Enable SSL/TLS performance monitoring
            enable_automatic_failover_detection: Enable automatic failover detection
        """
        self.load_balancers = load_balancers or []
        self.health_check_interval = health_check_interval
        self.enable_ssl_monitoring = enable_ssl_monitoring
        self.enable_automatic_failover_detection = enable_automatic_failover_detection
        
        # Metrics storage
        self.lb_metrics: deque = deque(maxlen=10000)
        self.backend_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        self.health_check_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.failover_metrics: deque = deque(maxlen=1000)
        self.traffic_distribution_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.ssl_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # State tracking
        self.backend_states: Dict[str, Dict] = defaultdict(dict)
        self.failover_history: Dict[str, List] = defaultdict(list)
        self.health_check_history: Dict[str, Dict] = defaultdict(dict)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_tasks = []
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.lb_active_connections_gauge = Gauge(
            'load_balancer_active_connections',
            'Load balancer active connections',
            ['lb_name', 'lb_type']
        )
        
        self.lb_requests_per_second_gauge = Gauge(
            'load_balancer_requests_per_second',
            'Load balancer requests per second',
            ['lb_name', 'lb_type']
        )
        
        self.lb_response_time_histogram = Histogram(
            'load_balancer_response_time_seconds',
            'Load balancer response time',
            ['lb_name', 'lb_type'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.lb_error_rate_gauge = Gauge(
            'load_balancer_error_rate_percent',
            'Load balancer error rate percentage',
            ['lb_name', 'lb_type']
        )
        
        self.backend_status_gauge = Gauge(
            'load_balancer_backend_status',
            'Backend server status (1=up, 0=down)',
            ['lb_name', 'backend_server']
        )
        
        self.backend_connections_gauge = Gauge(
            'load_balancer_backend_connections',
            'Backend server active connections',
            ['lb_name', 'backend_server']
        )
        
        self.health_check_success_rate_gauge = Gauge(
            'load_balancer_health_check_success_rate',
            'Health check success rate',
            ['lb_name', 'backend_server']
        )
        
        self.failover_count_counter = Counter(
            'load_balancer_failover_events_total',
            'Total failover events',
            ['lb_name', 'reason']
        )
        
        self.ssl_handshake_time_histogram = Histogram(
            'load_balancer_ssl_handshake_seconds',
            'SSL handshake time',
            ['lb_name'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.traffic_distribution_balance_gauge = Gauge(
            'load_balancer_traffic_balance_score',
            'Traffic distribution balance score (0-100)',
            ['lb_name', 'algorithm']
        )
    
    async def collect_haproxy_metrics(self, lb_config: Dict) -> LoadBalancerMetrics:
        """Collect HAProxy metrics"""
        try:
            stats_url = lb_config.get('stats_url')
            if not stats_url:
                logger.warning(f"No stats URL configured for HAProxy {lb_config['name']}")
                return None
            
            # Fetch HAProxy stats
            async with aiohttp.ClientSession() as session:
                auth = None
                if 'username' in lb_config and 'password' in lb_config:
                    auth = aiohttp.BasicAuth(lb_config['username'], lb_config['password'])
                
                async with session.get(f"{stats_url};csv", auth=auth) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch HAProxy stats: HTTP {response.status}")
                        return None
                    
                    csv_data = await response.text()
                    
                    # Parse HAProxy CSV stats
                    lines = csv_data.strip().split('\n')
                    if len(lines) < 2:
                        return None
                    
                    headers = lines[0].split(',')
                    stats_data = []
                    
                    for line in lines[1:]:
                        if line.strip():
                            values = line.split(',')
                            if len(values) >= len(headers):
                                stats_data.append(dict(zip(headers, values)))
                    
                    # Aggregate metrics
                    total_requests = 0
                    total_connections = 0
                    total_errors = 0
                    response_times = []
                    healthy_backends = 0
                    total_backends = 0
                    
                    for stat in stats_data:
                        if stat.get('type') == '2':  # Server type
                            total_backends += 1
                            if stat.get('status') == 'UP':
                                healthy_backends += 1
                            
                            # Accumulate metrics
                            try:
                                total_requests += int(stat.get('stot', 0))
                                total_connections += int(stat.get('scur', 0))
                                total_errors += int(stat.get('eresp', 0))
                                
                                rtime = stat.get('rtime', '')
                                if rtime and rtime.isdigit():
                                    response_times.append(int(rtime))
                            except (ValueError, TypeError):
                                pass
                    
                    # Calculate derived metrics
                    avg_response_time = statistics.mean(response_times) if response_times else 0
                    p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0
                    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
                    
                    metrics = LoadBalancerMetrics(
                        lb_name=lb_config['name'],
                        lb_type='haproxy',
                        active_connections=total_connections,
                        total_requests=total_requests,
                        requests_per_second=0,  # Would need to calculate from time series
                        avg_response_time_ms=avg_response_time,
                        p95_response_time_ms=p95_response_time,
                        error_count=total_errors,
                        error_rate_percent=error_rate,
                        ssl_handshake_time_ms=0,  # Not available in basic stats
                        backend_server_count=total_backends,
                        healthy_backends=healthy_backends,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Update Prometheus metrics
                    self._update_prometheus_metrics(metrics)
                    
                    return metrics
        
        except Exception as e:
            logger.error(f"Error collecting HAProxy metrics: {e}")
            return None
    
    async def collect_nginx_metrics(self, lb_config: Dict) -> LoadBalancerMetrics:
        """Collect NGINX metrics"""
        try:
            stats_url = lb_config.get('stats_url', f"http://{lb_config['address']}/nginx_status")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(stats_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch NGINX stats: HTTP {response.status}")
                        return None
                    
                    stats_text = await response.text()
                    
                    # Parse NGINX status format
                    lines = stats_text.strip().split('\n')
                    
                    active_connections = 0
                    total_requests = 0
                    
                    for line in lines:
                        if 'Active connections:' in line:
                            active_connections = int(line.split(':')[1].strip())
                        elif line.strip() and line.split()[0].isdigit():
                            # Server accepts handled requests format
                            parts = line.split()
                            if len(parts) >= 3:
                                total_requests = int(parts[2])
                    
                    metrics = LoadBalancerMetrics(
                        lb_name=lb_config['name'],
                        lb_type='nginx',
                        active_connections=active_connections,
                        total_requests=total_requests,
                        requests_per_second=0,  # Would need time series calculation
                        avg_response_time_ms=0,  # Not available in basic stats
                        p95_response_time_ms=0,
                        error_count=0,
                        error_rate_percent=0,
                        ssl_handshake_time_ms=0,
                        backend_server_count=0,  # Not available in basic stats
                        healthy_backends=0,
                        timestamp=datetime.utcnow()
                    )
                    
                    self._update_prometheus_metrics(metrics)
                    return metrics
        
        except Exception as e:
            logger.error(f"Error collecting NGINX metrics: {e}")
            return None
    
    async def collect_aws_alb_metrics(self, lb_config: Dict) -> LoadBalancerMetrics:
        """Collect AWS Application Load Balancer metrics"""
        try:
            # This would use boto3 to collect CloudWatch metrics
            # For demonstration, we'll return simulated metrics
            
            metrics = LoadBalancerMetrics(
                lb_name=lb_config['name'],
                lb_type='aws_alb',
                active_connections=0,  # ALB doesn't expose this directly
                total_requests=0,  # Would come from CloudWatch
                requests_per_second=0,
                avg_response_time_ms=0,
                p95_response_time_ms=0,
                error_count=0,
                error_rate_percent=0,
                ssl_handshake_time_ms=0,
                backend_server_count=0,
                healthy_backends=0,
                timestamp=datetime.utcnow()
            )
            
            self._update_prometheus_metrics(metrics)
            return metrics
        
        except Exception as e:
            logger.error(f"Error collecting AWS ALB metrics: {e}")
            return None
    
    async def perform_backend_health_checks(self, lb_config: Dict) -> List[HealthCheckMetrics]:
        """Perform health checks on backend servers"""
        health_metrics = []
        
        backends = lb_config.get('backends', [])
        
        for backend in backends:
            backend_name = backend['name']
            backend_address = backend['address']
            backend_port = backend['port']
            health_check_config = backend.get('health_check', {})
            
            check_type = health_check_config.get('type', 'http')
            check_path = health_check_config.get('path', '/health')
            check_timeout = health_check_config.get('timeout', 5)
            
            start_time = time.time()
            success = False
            status_code = None
            error_message = None
            
            try:
                if check_type == 'http':
                    health_url = f"http://{backend_address}:{backend_port}{check_path}"
                    
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=check_timeout)) as session:
                        async with session.get(health_url) as response:
                            status_code = response.status
                            success = 200 <= status_code < 400
                            
                elif check_type == 'tcp':
                    # TCP socket check
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(check_timeout)
                    result = sock.connect_ex((backend_address, backend_port))
                    sock.close()
                    success = result == 0
                    
                elif check_type == 'ssl':
                    # SSL handshake check
                    context = ssl.create_default_context()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(check_timeout)
                    
                    with context.wrap_socket(sock, server_hostname=backend_address) as ssock:
                        ssock.connect((backend_address, backend_port))
                        success = True
                        
            except Exception as e:
                error_message = str(e)
                success = False
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Track consecutive failures
            backend_key = f"{lb_config['name']}-{backend_name}"
            if backend_key not in self.health_check_history:
                self.health_check_history[backend_key] = {'consecutive_failures': 0}
            
            if success:
                self.health_check_history[backend_key]['consecutive_failures'] = 0
            else:
                self.health_check_history[backend_key]['consecutive_failures'] += 1
            
            health_check_metrics = HealthCheckMetrics(
                lb_name=lb_config['name'],
                backend_server=backend_name,
                check_type=check_type,
                check_interval_seconds=self.health_check_interval,
                check_timeout_seconds=check_timeout,
                success=success,
                response_time_ms=response_time_ms,
                status_code=status_code,
                error_message=error_message,
                consecutive_failures=self.health_check_history[backend_key]['consecutive_failures'],
                timestamp=datetime.utcnow()
            )
            
            health_metrics.append(health_check_metrics)
            
            # Store metrics
            self.health_check_metrics[backend_key].append(health_check_metrics)
            
            # Update Prometheus metrics
            success_rate = self._calculate_health_check_success_rate(backend_key)
            self.health_check_success_rate_gauge.labels(
                lb_name=lb_config['name'],
                backend_server=backend_name
            ).set(success_rate)
            
            self.backend_status_gauge.labels(
                lb_name=lb_config['name'],
                backend_server=backend_name
            ).set(1 if success else 0)
            
            # Check for failover conditions
            if self.enable_automatic_failover_detection:
                await self._check_failover_conditions(lb_config, backend, health_check_metrics)
        
        return health_metrics
    
    def _calculate_health_check_success_rate(self, backend_key: str, window_minutes: int = 5) -> float:
        """Calculate health check success rate for backend"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_checks = [
            check for check in self.health_check_metrics[backend_key]
            if check.timestamp >= cutoff_time
        ]
        
        if not recent_checks:
            return 100.0
        
        successful_checks = len([check for check in recent_checks if check.success])
        return (successful_checks / len(recent_checks)) * 100
    
    async def _check_failover_conditions(self, lb_config: Dict, backend: Dict, health_metrics: HealthCheckMetrics):
        """Check if failover conditions are met"""
        backend_key = f"{lb_config['name']}-{backend['name']}"
        
        # Failover if consecutive failures exceed threshold
        failure_threshold = backend.get('failure_threshold', 3)
        
        if health_metrics.consecutive_failures >= failure_threshold:
            # Trigger failover
            await self._trigger_failover(lb_config, backend, 'health_check_failure')
    
    async def _trigger_failover(self, lb_config: Dict, failed_backend: Dict, reason: str):
        """Trigger failover for failed backend"""
        start_time = time.time()
        
        # Find healthy backend for failover
        healthy_backends = []
        for backend in lb_config.get('backends', []):
            if backend['name'] != failed_backend['name']:
                backend_key = f"{lb_config['name']}-{backend['name']}"
                success_rate = self._calculate_health_check_success_rate(backend_key)
                if success_rate > 80:  # Healthy threshold
                    healthy_backends.append(backend)
        
        if not healthy_backends:
            logger.error(f"No healthy backends available for failover in {lb_config['name']}")
            return
        
        # Select failover target (simple round-robin)
        failover_target = healthy_backends[0]['name']
        
        # In a real implementation, this would reconfigure the load balancer
        # For now, we'll just log and record the failover event
        
        failover_time_ms = (time.time() - start_time) * 1000
        
        failover_metrics = FailoverMetrics(
            lb_name=lb_config['name'],
            failed_backend=failed_backend['name'],
            failover_target=failover_target,
            failover_reason=reason,
            failover_time_ms=failover_time_ms,
            impact_duration_seconds=0,  # Would track actual impact
            affected_connections=0,  # Would count affected connections
            automatic_recovery=True,
            timestamp=datetime.utcnow()
        )
        
        self.failover_metrics.append(failover_metrics)
        self.failover_history[lb_config['name']].append(failover_metrics)
        
        # Update Prometheus metrics
        self.failover_count_counter.labels(
            lb_name=lb_config['name'],
            reason=reason
        ).inc()
        
        logger.warning(f"Failover triggered: {failed_backend['name']} -> {failover_target} in {lb_config['name']}")
    
    async def analyze_traffic_distribution(self, lb_config: Dict) -> TrafficDistributionMetrics:
        """Analyze traffic distribution across backends"""
        try:
            # This would typically analyze request logs or stats
            # For demonstration, we'll simulate traffic distribution analysis
            
            backends = lb_config.get('backends', [])
            if not backends:
                return None
            
            # Simulate traffic distribution (would come from actual metrics)
            total_requests = 1000
            backend_distributions = {}
            
            # Simple simulation based on backend weights
            total_weight = sum(backend.get('weight', 1) for backend in backends)
            
            for backend in backends:
                weight = backend.get('weight', 1)
                distribution_percent = (weight / total_weight) * 100
                backend_distributions[backend['name']] = distribution_percent
            
            # Calculate balance score
            ideal_distribution = 100 / len(backends)
            distribution_variance = statistics.variance(backend_distributions.values())
            balance_score = max(0, 100 - distribution_variance)
            
            # Identify hot spots and underutilized servers
            hot_spot_threshold = ideal_distribution * 1.5
            underutilized_threshold = ideal_distribution * 0.5
            
            hot_spot_servers = [
                name for name, percent in backend_distributions.items()
                if percent > hot_spot_threshold
            ]
            
            underutilized_servers = [
                name for name, percent in backend_distributions.items()
                if percent < underutilized_threshold
            ]
            
            metrics = TrafficDistributionMetrics(
                lb_name=lb_config['name'],
                algorithm=lb_config.get('algorithm', 'round_robin'),
                backend_distributions=backend_distributions,
                distribution_balance_score=balance_score,
                hot_spot_servers=hot_spot_servers,
                underutilized_servers=underutilized_servers,
                timestamp=datetime.utcnow()
            )
            
            self.traffic_distribution_metrics[lb_config['name']].append(metrics)
            
            # Update Prometheus metrics
            self.traffic_distribution_balance_gauge.labels(
                lb_name=lb_config['name'],
                algorithm=lb_config.get('algorithm', 'round_robin')
            ).set(balance_score)
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error analyzing traffic distribution: {e}")
            return None
    
    async def monitor_ssl_performance(self, lb_config: Dict) -> SSLPerformanceMetrics:
        """Monitor SSL/TLS performance"""
        if not self.enable_ssl_monitoring:
            return None
        
        try:
            ssl_endpoint = lb_config.get('ssl_endpoint')
            if not ssl_endpoint:
                return None
            
            parsed_url = urlparse(ssl_endpoint)
            host = parsed_url.hostname
            port = parsed_url.port or 443
            
            # Measure SSL handshake time
            start_time = time.time()
            
            context = ssl.create_default_context()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.connect((host, port))
                
                # Get SSL information
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                ssl_version = ssock.version()
                
                handshake_time_ms = (time.time() - start_time) * 1000
                
                # Calculate certificate expiry
                import datetime as dt
                expiry_date = dt.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                expiry_days = (expiry_date - dt.datetime.utcnow()).days
                
                metrics = SSLPerformanceMetrics(
                    lb_name=lb_config['name'],
                    ssl_version=ssl_version,
                    cipher_suite=cipher[0] if cipher else 'unknown',
                    handshake_time_ms=handshake_time_ms,
                    certificate_validation_time_ms=0,  # Would measure separately
                    ssl_session_reuse_rate=0,  # Would track from session data
                    ssl_errors_count=0,  # Would track from error logs
                    certificate_expiry_days=expiry_days,
                    timestamp=datetime.utcnow()
                )
                
                self.ssl_metrics[lb_config['name']].append(metrics)
                
                # Update Prometheus metrics
                self.ssl_handshake_time_histogram.labels(
                    lb_name=lb_config['name']
                ).observe(handshake_time_ms / 1000)
                
                return metrics
        
        except Exception as e:
            logger.error(f"Error monitoring SSL performance: {e}")
            return None
    
    def _update_prometheus_metrics(self, metrics: LoadBalancerMetrics):
        """Update Prometheus metrics"""
        self.lb_active_connections_gauge.labels(
            lb_name=metrics.lb_name,
            lb_type=metrics.lb_type
        ).set(metrics.active_connections)
        
        self.lb_requests_per_second_gauge.labels(
            lb_name=metrics.lb_name,
            lb_type=metrics.lb_type
        ).set(metrics.requests_per_second)
        
        self.lb_response_time_histogram.labels(
            lb_name=metrics.lb_name,
            lb_type=metrics.lb_type
        ).observe(metrics.avg_response_time_ms / 1000)
        
        self.lb_error_rate_gauge.labels(
            lb_name=metrics.lb_name,
            lb_type=metrics.lb_type
        ).set(metrics.error_rate_percent)
    
    def get_load_balancer_summary(self, lb_name: Optional[str] = None) -> Dict[str, Any]:
        """Get load balancer performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        if lb_name:
            recent_metrics = [m for m in self.lb_metrics 
                           if m.lb_name == lb_name and m.timestamp >= cutoff_time]
        else:
            recent_metrics = [m for m in self.lb_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No recent load balancer data available'}
        
        # Group by load balancer
        by_lb = defaultdict(list)
        for metric in recent_metrics:
            by_lb[metric.lb_name].append(metric)
        
        summary = {}
        
        for lb_name_key, metrics_list in by_lb.items():
            latest_metrics = metrics_list[-1]
            
            response_times = [m.avg_response_time_ms for m in metrics_list]
            error_rates = [m.error_rate_percent for m in metrics_list]
            
            # Calculate recent failovers
            recent_failovers = len([
                f for f in self.failover_history[lb_name_key]
                if f.timestamp >= cutoff_time
            ])
            
            summary[lb_name_key] = {
                'lb_type': latest_metrics.lb_type,
                'status': 'healthy' if latest_metrics.error_rate_percent < 5 else 'degraded',
                'active_connections': latest_metrics.active_connections,
                'avg_response_time_ms': statistics.mean(response_times),
                'avg_error_rate_percent': statistics.mean(error_rates),
                'backend_servers': latest_metrics.backend_server_count,
                'healthy_backends': latest_metrics.healthy_backends,
                'recent_failovers': recent_failovers,
                'health_score': min(100, 100 - latest_metrics.error_rate_percent * 10)
            }
        
        return {
            'time_window_minutes': 15,
            'load_balancers': summary,
            'total_failovers': sum(len(history) for history in self.failover_history.values())
        }
    
    async def start_monitoring(self):
        """Start continuous load balancer monitoring"""
        if self.monitoring_active:
            logger.warning("Load balancer monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._metrics_collection_loop(),
            self._health_check_loop(),
            self._traffic_analysis_loop(),
            self._ssl_monitoring_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        logger.info("Load balancer performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._monitoring_tasks.clear()
        logger.info("Load balancer performance monitoring stopped")
    
    async def _metrics_collection_loop(self):
        """Metrics collection loop"""
        while self.monitoring_active:
            try:
                for lb_config in self.load_balancers:
                    lb_type = lb_config.get('type', 'unknown')
                    
                    if lb_type == 'haproxy':
                        metrics = await self.collect_haproxy_metrics(lb_config)
                    elif lb_type == 'nginx':
                        metrics = await self.collect_nginx_metrics(lb_config)
                    elif lb_type == 'aws_alb':
                        metrics = await self.collect_aws_alb_metrics(lb_config)
                    else:
                        logger.warning(f"Unsupported load balancer type: {lb_type}")
                        continue
                    
                    if metrics:
                        self.lb_metrics.append(metrics)
                
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(30)
    
    async def _health_check_loop(self):
        """Health check monitoring loop"""
        while self.monitoring_active:
            try:
                for lb_config in self.load_balancers:
                    await self.perform_backend_health_checks(lb_config)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _traffic_analysis_loop(self):
        """Traffic distribution analysis loop"""
        while self.monitoring_active:
            try:
                for lb_config in self.load_balancers:
                    await self.analyze_traffic_distribution(lb_config)
                
                await asyncio.sleep(120)  # Analyze traffic every 2 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in traffic analysis loop: {e}")
                await asyncio.sleep(120)
    
    async def _ssl_monitoring_loop(self):
        """SSL performance monitoring loop"""
        while self.monitoring_active:
            try:
                if self.enable_ssl_monitoring:
                    for lb_config in self.load_balancers:
                        if 'ssl_endpoint' in lb_config:
                            await self.monitor_ssl_performance(lb_config)
                
                await asyncio.sleep(300)  # Monitor SSL every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SSL monitoring loop: {e}")
                await asyncio.sleep(300)