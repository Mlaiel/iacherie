"""
⚠️ CONFIDENTIEL - Ainflue Creator Platform ⚠️

Network Performance Monitor - Enterprise Performance Monitoring
Advanced network performance monitoring for Creator Economy infrastructure

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
import subprocess
import ping3
import socket
import struct
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import statistics
import threading
from prometheus_client import Gauge, Counter, Histogram
import requests
import aiohttp
import dns.resolver
import ipaddress
import traceroute
from urllib.parse import urlparse
import ssl
import certifi

logger = logging.getLogger(__name__)

@dataclass
class NetworkLatencyMetrics:
    """Network latency measurement metrics"""
    target_host: str
    target_ip: str
    latency_ms: float
    packet_loss_percent: float
    jitter_ms: float
    timestamp: datetime
    probe_type: str  # ping, http, tcp, udp
    geographic_region: Optional[str] = None
    isp: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class BandwidthMetrics:
    """Bandwidth measurement metrics"""
    target_endpoint: str
    download_speed_mbps: float
    upload_speed_mbps: float
    test_duration_seconds: float
    data_transferred_mb: float
    concurrent_connections: int
    timestamp: datetime
    cdn_provider: Optional[str] = None
    edge_location: Optional[str] = None

@dataclass
class CDNPerformanceMetrics:
    """CDN performance metrics"""
    cdn_provider: str
    edge_location: str
    cache_hit_ratio: float
    origin_response_time_ms: float
    edge_response_time_ms: float
    cache_miss_rate: float
    bandwidth_savings_percent: float
    timestamp: datetime
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None

@dataclass
class LoadBalancerMetrics:
    """Load balancer performance metrics"""
    lb_name: str
    backend_servers: List[str]
    active_connections: int
    requests_per_second: float
    response_time_ms: float
    health_check_success_rate: float
    failover_count: int
    ssl_termination_time_ms: float
    timestamp: datetime
    algorithm: Optional[str] = None  # round_robin, least_connections, ip_hash

@dataclass
class GeographicPerformanceMetrics:
    """Geographic performance distribution metrics"""
    region: str
    country: str
    city: str
    avg_latency_ms: float
    bandwidth_mbps: float
    cdn_performance_score: float
    user_count: int
    error_rate_percent: float
    timestamp: datetime

class NetworkPerformanceMonitor:
    """
    Enterprise-grade network performance monitor
    Tracks latency, bandwidth, CDN performance, and geographic distribution
    """
    
    def __init__(self,
                 monitoring_targets: List[str] = None,
                 cdn_endpoints: List[str] = None,
                 load_balancers: List[str] = None,
                 geographic_regions: List[str] = None,
                 monitoring_interval: int = 60):
        """
        Initialize network performance monitor
        
        Args:
            monitoring_targets: List of hosts/URLs to monitor
            cdn_endpoints: List of CDN endpoints to test
            load_balancers: List of load balancer endpoints
            geographic_regions: List of geographic regions to test from
            monitoring_interval: Monitoring interval in seconds
        """
        self.monitoring_targets = monitoring_targets or [
            'google.com', 'cloudflare.com', 'aws.amazon.com',
            'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'
        ]
        self.cdn_endpoints = cdn_endpoints or []
        self.load_balancers = load_balancers or []
        self.geographic_regions = geographic_regions or ['us-east-1', 'eu-west-1', 'ap-southeast-1']
        self.monitoring_interval = monitoring_interval
        
        # Metrics storage
        self.latency_metrics: deque = deque(maxlen=10000)
        self.bandwidth_metrics: deque = deque(maxlen=1000)
        self.cdn_metrics: deque = deque(maxlen=5000)
        self.lb_metrics: deque = deque(maxlen=5000)
        self.geographic_metrics: deque = deque(maxlen=5000)
        
        # Real-time tracking
        self.network_health: Dict[str, Dict] = defaultdict(dict)
        self.connection_pools: Dict[str, Any] = {}
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_tasks = []
        
        # DNS resolver
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 10
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.network_latency_histogram = Histogram(
            'network_latency_seconds',
            'Network latency measurements',
            ['target', 'probe_type', 'region'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
        )
        
        self.bandwidth_gauge = Gauge(
            'network_bandwidth_mbps',
            'Network bandwidth measurements',
            ['target', 'direction', 'region']  # direction: download/upload
        )
        
        self.packet_loss_gauge = Gauge(
            'network_packet_loss_percent',
            'Network packet loss percentage',
            ['target', 'region']
        )
        
        self.cdn_cache_hit_ratio_gauge = Gauge(
            'cdn_cache_hit_ratio',
            'CDN cache hit ratio',
            ['provider', 'edge_location']
        )
        
        self.cdn_response_time_histogram = Histogram(
            'cdn_response_time_seconds',
            'CDN response time',
            ['provider', 'edge_location', 'cache_status'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.load_balancer_connections_gauge = Gauge(
            'load_balancer_active_connections',
            'Load balancer active connections',
            ['lb_name']
        )
        
        self.load_balancer_rps_gauge = Gauge(
            'load_balancer_requests_per_second',
            'Load balancer requests per second',
            ['lb_name']
        )
        
        self.dns_resolution_time_histogram = Histogram(
            'dns_resolution_time_seconds',
            'DNS resolution time',
            ['hostname', 'resolver'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
    
    async def measure_network_latency(self, target: str, probe_type: str = 'ping') -> NetworkLatencyMetrics:
        """Measure network latency to target"""
        start_time = time.time()
        
        try:
            # Resolve hostname to IP
            target_ip = socket.gethostbyname(target)
            
            latencies = []
            packet_loss = 0
            
            if probe_type == 'ping':
                # Perform multiple ping measurements
                for _ in range(5):
                    latency = ping3.ping(target, timeout=2)
                    if latency is not None:
                        latencies.append(latency * 1000)  # Convert to ms
                    else:
                        packet_loss += 1
                
                packet_loss_percent = (packet_loss / 5) * 100
                
            elif probe_type == 'http':
                # HTTP latency measurement
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    for _ in range(3):
                        try:
                            start = time.time()
                            async with session.get(f'http://{target}', allow_redirects=False) as response:
                                latency_ms = (time.time() - start) * 1000
                                latencies.append(latency_ms)
                        except:
                            packet_loss += 1
                
                packet_loss_percent = (packet_loss / 3) * 100
                
            elif probe_type == 'tcp':
                # TCP connection latency
                for _ in range(3):
                    try:
                        start = time.time()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        result = sock.connect_ex((target_ip, 80))
                        latency_ms = (time.time() - start) * 1000
                        sock.close()
                        
                        if result == 0:
                            latencies.append(latency_ms)
                        else:
                            packet_loss += 1
                    except:
                        packet_loss += 1
                
                packet_loss_percent = (packet_loss / 3) * 100
            
            if not latencies:
                return NetworkLatencyMetrics(
                    target_host=target,
                    target_ip=target_ip,
                    latency_ms=0.0,
                    packet_loss_percent=100.0,
                    jitter_ms=0.0,
                    timestamp=datetime.utcnow(),
                    probe_type=probe_type,
                    success=False,
                    error_message="All probes failed"
                )
            
            avg_latency = statistics.mean(latencies)
            jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            
            # Get geographic info (simplified)
            geographic_region = await self._get_geographic_region(target_ip)
            
            metrics = NetworkLatencyMetrics(
                target_host=target,
                target_ip=target_ip,
                latency_ms=avg_latency,
                packet_loss_percent=packet_loss_percent,
                jitter_ms=jitter,
                timestamp=datetime.utcnow(),
                probe_type=probe_type,
                geographic_region=geographic_region,
                success=True
            )
            
            # Update Prometheus metrics
            self.network_latency_histogram.labels(
                target=target,
                probe_type=probe_type,
                region=geographic_region or 'unknown'
            ).observe(avg_latency / 1000)
            
            self.packet_loss_gauge.labels(
                target=target,
                region=geographic_region or 'unknown'
            ).set(packet_loss_percent)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error measuring latency to {target}: {e}")
            return NetworkLatencyMetrics(
                target_host=target,
                target_ip='unknown',
                latency_ms=0.0,
                packet_loss_percent=100.0,
                jitter_ms=0.0,
                timestamp=datetime.utcnow(),
                probe_type=probe_type,
                success=False,
                error_message=str(e)
            )
    
    async def measure_bandwidth(self, endpoint: str, test_size_mb: float = 10.0) -> BandwidthMetrics:
        """Measure bandwidth to endpoint"""
        start_time = time.time()
        
        try:
            # Download test
            download_start = time.time()
            async with aiohttp.ClientSession() as session:
                # Create test URL for download
                test_url = f"{endpoint}/test-file-{int(test_size_mb)}mb"
                
                try:
                    async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        data_downloaded = 0
                        async for chunk in response.content.iter_chunked(8192):
                            data_downloaded += len(chunk)
                        
                        download_time = time.time() - download_start
                        download_speed_mbps = (data_downloaded / (1024 * 1024)) / download_time * 8
                        
                except:
                    # Fallback: Use a known file or simulate
                    download_speed_mbps = 0.0
                    download_time = 0.0
                
                # Upload test (simplified - would need actual upload endpoint)
                upload_speed_mbps = 0.0  # Placeholder
            
            total_duration = time.time() - start_time
            
            metrics = BandwidthMetrics(
                target_endpoint=endpoint,
                download_speed_mbps=download_speed_mbps,
                upload_speed_mbps=upload_speed_mbps,
                test_duration_seconds=total_duration,
                data_transferred_mb=test_size_mb,
                concurrent_connections=1,
                timestamp=datetime.utcnow(),
                cdn_provider=self._detect_cdn_provider(endpoint)
            )
            
            # Update Prometheus metrics
            self.bandwidth_gauge.labels(
                target=endpoint,
                direction='download',
                region='unknown'
            ).set(download_speed_mbps)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error measuring bandwidth to {endpoint}: {e}")
            return BandwidthMetrics(
                target_endpoint=endpoint,
                download_speed_mbps=0.0,
                upload_speed_mbps=0.0,
                test_duration_seconds=0.0,
                data_transferred_mb=0.0,
                concurrent_connections=0,
                timestamp=datetime.utcnow(),
                cdn_provider=None
            )
    
    async def measure_cdn_performance(self, cdn_endpoint: str) -> CDNPerformanceMetrics:
        """Measure CDN performance metrics"""
        try:
            cache_hit_tests = []
            origin_times = []
            edge_times = []
            
            async with aiohttp.ClientSession() as session:
                # Test cache hit/miss by requesting same resource multiple times
                test_url = f"{cdn_endpoint}/test-resource-{int(time.time())}"
                
                for i in range(3):
                    start_time = time.time()
                    try:
                        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            response_time = (time.time() - start_time) * 1000
                            
                            # Check cache status from headers
                            cache_status = response.headers.get('cf-cache-status', 
                                         response.headers.get('x-cache', 
                                         response.headers.get('x-served-by', 'unknown')))
                            
                            if 'hit' in cache_status.lower() or i > 0:  # Subsequent requests likely cached
                                cache_hit_tests.append(True)
                                edge_times.append(response_time)
                            else:
                                cache_hit_tests.append(False)
                                origin_times.append(response_time)
                                
                    except Exception as e:
                        logger.debug(f"CDN test failed: {e}")
                        cache_hit_tests.append(False)
            
            # Calculate metrics
            cache_hit_ratio = (sum(cache_hit_tests) / len(cache_hit_tests)) * 100 if cache_hit_tests else 0
            cache_miss_rate = 100 - cache_hit_ratio
            
            avg_origin_time = statistics.mean(origin_times) if origin_times else 0
            avg_edge_time = statistics.mean(edge_times) if edge_times else 0
            
            # Estimate bandwidth savings (simplified)
            bandwidth_savings = cache_hit_ratio * 0.8  # Assume 80% savings on cache hits
            
            cdn_provider = self._detect_cdn_provider(cdn_endpoint)
            edge_location = await self._get_edge_location(cdn_endpoint)
            
            metrics = CDNPerformanceMetrics(
                cdn_provider=cdn_provider,
                edge_location=edge_location,
                cache_hit_ratio=cache_hit_ratio,
                origin_response_time_ms=avg_origin_time,
                edge_response_time_ms=avg_edge_time,
                cache_miss_rate=cache_miss_rate,
                bandwidth_savings_percent=bandwidth_savings,
                timestamp=datetime.utcnow()
            )
            
            # Update Prometheus metrics
            self.cdn_cache_hit_ratio_gauge.labels(
                provider=cdn_provider,
                edge_location=edge_location
            ).set(cache_hit_ratio)
            
            self.cdn_response_time_histogram.labels(
                provider=cdn_provider,
                edge_location=edge_location,
                cache_status='hit'
            ).observe(avg_edge_time / 1000)
            
            if avg_origin_time > 0:
                self.cdn_response_time_histogram.labels(
                    provider=cdn_provider,
                    edge_location=edge_location,
                    cache_status='miss'
                ).observe(avg_origin_time / 1000)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error measuring CDN performance for {cdn_endpoint}: {e}")
            return CDNPerformanceMetrics(
                cdn_provider='unknown',
                edge_location='unknown',
                cache_hit_ratio=0.0,
                origin_response_time_ms=0.0,
                edge_response_time_ms=0.0,
                cache_miss_rate=100.0,
                bandwidth_savings_percent=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def measure_dns_performance(self, hostname: str) -> Dict[str, float]:
        """Measure DNS resolution performance"""
        dns_times = {}
        
        # Test different DNS resolvers
        resolvers = {
            'cloudflare': '1.1.1.1',
            'google': '8.8.8.8',
            'quad9': '9.9.9.9',
            'system': None  # System default
        }
        
        for resolver_name, resolver_ip in resolvers.items():
            try:
                resolver = dns.resolver.Resolver()
                if resolver_ip:
                    resolver.nameservers = [resolver_ip]
                
                start_time = time.time()
                answers = resolver.resolve(hostname, 'A')
                resolution_time = (time.time() - start_time) * 1000
                
                dns_times[resolver_name] = resolution_time
                
                # Update Prometheus metrics
                self.dns_resolution_time_histogram.labels(
                    hostname=hostname,
                    resolver=resolver_name
                ).observe(resolution_time / 1000)
                
            except Exception as e:
                logger.debug(f"DNS resolution failed for {hostname} using {resolver_name}: {e}")
                dns_times[resolver_name] = -1  # Indicate failure
        
        return dns_times
    
    async def perform_traceroute(self, target: str) -> List[Dict[str, Any]]:
        """Perform traceroute to target"""
        try:
            # Use traceroute library or subprocess
            result = subprocess.run(
                ['traceroute', '-n', '-m', '15', target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            hops = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for i, line in enumerate(lines, 1):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        hop_ip = parts[1] if parts[1] != '*' else 'timeout'
                        
                        # Extract timing information
                        timings = []
                        for part in parts[2:]:
                            if part.endswith('ms'):
                                try:
                                    timings.append(float(part[:-2]))
                                except:
                                    pass
                        
                        avg_time = statistics.mean(timings) if timings else None
                        
                        hops.append({
                            'hop': i,
                            'ip': hop_ip,
                            'avg_time_ms': avg_time,
                            'timings': timings
                        })
            
            return hops
            
        except Exception as e:
            logger.error(f"Traceroute failed for {target}: {e}")
            return []
    
    def _detect_cdn_provider(self, endpoint: str) -> str:
        """Detect CDN provider from endpoint"""
        endpoint_lower = endpoint.lower()
        
        if 'cloudflare' in endpoint_lower or 'cf-' in endpoint_lower:
            return 'cloudflare'
        elif 'amazonaws' in endpoint_lower or 'cloudfront' in endpoint_lower:
            return 'aws_cloudfront'
        elif 'googleapis' in endpoint_lower or 'gstatic' in endpoint_lower:
            return 'google_cloud_cdn'
        elif 'fastly' in endpoint_lower:
            return 'fastly'
        elif 'jsdelivr' in endpoint_lower:
            return 'jsdelivr'
        elif 'maxcdn' in endpoint_lower or 'bootstrapcdn' in endpoint_lower:
            return 'maxcdn'
        else:
            return 'unknown'
    
    async def _get_geographic_region(self, ip: str) -> Optional[str]:
        """Get geographic region for IP address (simplified)"""
        try:
            # This would typically use a GeoIP service
            # For now, return a simplified region based on IP ranges
            ip_obj = ipaddress.ip_address(ip)
            
            # Simplified region detection
            if ip_obj.is_private:
                return 'private'
            elif ip_obj.is_loopback:
                return 'loopback'
            else:
                # Would use actual GeoIP lookup here
                return 'unknown'
                
        except:
            return None
    
    async def _get_edge_location(self, endpoint: str) -> str:
        """Get CDN edge location (simplified)"""
        try:
            # This would typically query CDN APIs or use trace headers
            # For now, return a default based on geographic proximity
            return 'unknown'
        except:
            return 'unknown'
    
    async def get_network_health_summary(self) -> Dict[str, Any]:
        """Get overall network health summary"""
        # Recent metrics (last 5 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        recent_latency = [m for m in self.latency_metrics if m.timestamp >= cutoff_time]
        recent_bandwidth = [m for m in self.bandwidth_metrics if m.timestamp >= cutoff_time]
        
        if not recent_latency:
            return {'message': 'No recent network data available'}
        
        # Calculate health scores
        successful_tests = [m for m in recent_latency if m.success]
        success_rate = len(successful_tests) / len(recent_latency) * 100
        
        if successful_tests:
            avg_latency = statistics.mean([m.latency_ms for m in successful_tests])
            avg_packet_loss = statistics.mean([m.packet_loss_percent for m in successful_tests])
        else:
            avg_latency = 0.0
            avg_packet_loss = 100.0
        
        # Network health score (0-100)
        health_score = max(0, 100 - (avg_latency / 10) - (avg_packet_loss * 2))
        
        summary = {
            'health_score': health_score,
            'success_rate': success_rate,
            'avg_latency_ms': avg_latency,
            'avg_packet_loss_percent': avg_packet_loss,
            'total_tests': len(recent_latency),
            'by_target': {}
        }
        
        # Group by target
        by_target = defaultdict(list)
        for metric in recent_latency:
            by_target[metric.target_host].append(metric)
        
        for target, metrics_list in by_target.items():
            successful = [m for m in metrics_list if m.success]
            if successful:
                summary['by_target'][target] = {
                    'success_rate': len(successful) / len(metrics_list) * 100,
                    'avg_latency_ms': statistics.mean([m.latency_ms for m in successful]),
                    'packet_loss_percent': statistics.mean([m.packet_loss_percent for m in successful])
                }
        
        return summary
    
    async def start_monitoring(self):
        """Start continuous network monitoring"""
        if self.monitoring_active:
            logger.warning("Network monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._latency_monitoring_loop(),
            self._bandwidth_monitoring_loop(),
            self._cdn_monitoring_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        logger.info("Network performance monitoring started")
    
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
        logger.info("Network performance monitoring stopped")
    
    async def _latency_monitoring_loop(self):
        """Latency monitoring loop"""
        while self.monitoring_active:
            try:
                for target in self.monitoring_targets:
                    # Test different probe types
                    for probe_type in ['ping', 'http', 'tcp']:
                        try:
                            metrics = await self.measure_network_latency(target, probe_type)
                            self.latency_metrics.append(metrics)
                        except Exception as e:
                            logger.error(f"Error measuring {probe_type} latency to {target}: {e}")
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in latency monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _bandwidth_monitoring_loop(self):
        """Bandwidth monitoring loop"""
        while self.monitoring_active:
            try:
                for endpoint in self.cdn_endpoints:
                    try:
                        metrics = await self.measure_bandwidth(endpoint)
                        self.bandwidth_metrics.append(metrics)
                    except Exception as e:
                        logger.error(f"Error measuring bandwidth to {endpoint}: {e}")
                
                # Run less frequently than latency tests
                await asyncio.sleep(self.monitoring_interval * 5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in bandwidth monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval * 5)
    
    async def _cdn_monitoring_loop(self):
        """CDN monitoring loop"""
        while self.monitoring_active:
            try:
                for cdn_endpoint in self.cdn_endpoints:
                    try:
                        metrics = await self.measure_cdn_performance(cdn_endpoint)
                        self.cdn_metrics.append(metrics)
                    except Exception as e:
                        logger.error(f"Error measuring CDN performance for {cdn_endpoint}: {e}")
                
                await asyncio.sleep(self.monitoring_interval * 2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in CDN monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval * 2)