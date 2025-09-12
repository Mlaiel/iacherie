#!/usr/bin/env python3
"""
Load Test Coordinator - Ainflue Quality Platform
==============================================

Enterprise-grade load testing and performance analysis system.
Demonstrates ML Engineer + DevOps + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import aiohttp
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Load test configuration."""
    name: str
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    think_time_seconds: float = 1.0
    timeout_seconds: int = 30


@dataclass
class RequestResult:
    """Individual request result."""
    timestamp: float
    status_code: int
    response_time_ms: float
    error: Optional[str] = None
    response_size_bytes: int = 0
    user_id: int = 0


@dataclass
class LoadTestResult:
    """Complete load test execution result."""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    requests_per_second: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p90_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_mb_per_sec: float
    errors: List[str] = field(default_factory=list)
    raw_results: List[RequestResult] = field(default_factory=list)


class SystemMonitor:
    """Monitor system resources during load testing."""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitoring = False
        self.metrics: List[Dict[str, Any]] = []
    
    async def start_monitoring(self):
        """Start system monitoring."""
        self.monitoring = True
        self.metrics = []
        
        while self.monitoring:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_count = psutil.cpu_count()
                
                # Memory metrics
                memory = psutil.virtual_memory()
                
                # Network metrics
                network = psutil.net_io_counters()
                
                # Disk metrics
                disk = psutil.disk_io_counters()
                
                metric = {
                    'timestamp': time.time(),
                    'cpu': {
                        'percent': cpu_percent,
                        'count': cpu_count
                    },
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used
                    },
                    'network': {
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    },
                    'disk': {
                        'read_bytes': disk.read_bytes if disk else 0,
                        'write_bytes': disk.write_bytes if disk else 0,
                        'read_count': disk.read_count if disk else 0,
                        'write_count': disk.write_count if disk else 0
                    }
                }
                
                self.metrics.append(metric)
                
            except Exception as e:
                logger.warning(f"Error collecting system metrics: {e}")
            
            await asyncio.sleep(self.interval)
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics:
            return {}
        
        # Extract time series data
        cpu_usage = [m['cpu']['percent'] for m in self.metrics]
        memory_usage = [m['memory']['percent'] for m in self.metrics]
        
        # Calculate network throughput
        if len(self.metrics) > 1:
            first = self.metrics[0]
            last = self.metrics[-1]
            duration = last['timestamp'] - first['timestamp']
            
            network_in_mbps = (last['network']['bytes_recv'] - first['network']['bytes_recv']) / duration / 1024 / 1024
            network_out_mbps = (last['network']['bytes_sent'] - first['network']['bytes_sent']) / duration / 1024 / 1024
        else:
            network_in_mbps = 0
            network_out_mbps = 0
        
        return {
            'cpu': {
                'avg': statistics.mean(cpu_usage),
                'max': max(cpu_usage),
                'min': min(cpu_usage),
                'p95': np.percentile(cpu_usage, 95)
            },
            'memory': {
                'avg': statistics.mean(memory_usage),
                'max': max(memory_usage),
                'min': min(memory_usage),
                'p95': np.percentile(memory_usage, 95)
            },
            'network': {
                'in_mbps': network_in_mbps,
                'out_mbps': network_out_mbps
            },
            'duration': self.metrics[-1]['timestamp'] - self.metrics[0]['timestamp'] if self.metrics else 0
        }


class LoadGenerator:
    """Generate load for a specific endpoint."""
    
    def __init__(self, config: LoadTestConfig, user_id: int):
        self.config = config
        self.user_id = user_id
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[RequestResult] = []
    
    async def start_session(self):
        """Start HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.config.headers
        )
    
    async def stop_session(self):
        """Stop HTTP session."""
        if self.session:
            await self.session.close()
    
    async def make_request(self) -> RequestResult:
        """Make a single HTTP request."""
        start_time = time.time()
        
        try:
            kwargs = {
                'url': self.config.url,
                'method': self.config.method
            }
            
            if self.config.body:
                if self.config.method.upper() in ['POST', 'PUT', 'PATCH']:
                    kwargs['json'] = self.config.body
            
            async with self.session.request(**kwargs) as response:
                # Read response body to get size
                body = await response.read()
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return RequestResult(
                    timestamp=start_time,
                    status_code=response.status,
                    response_time_ms=response_time,
                    response_size_bytes=len(body),
                    user_id=self.user_id
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return RequestResult(
                timestamp=start_time,
                status_code=0,
                response_time_ms=response_time,
                error="Timeout",
                user_id=self.user_id
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return RequestResult(
                timestamp=start_time,
                status_code=0,
                response_time_ms=response_time,
                error=str(e),
                user_id=self.user_id
            )
    
    async def run_load_test(self, start_time: float, duration: float) -> List[RequestResult]:
        """Run load test for specified duration."""
        await self.start_session()
        
        try:
            end_time = start_time + duration
            
            while time.time() < end_time:
                # Make request
                result = await self.make_request()
                self.results.append(result)
                
                # Think time between requests
                if self.config.think_time_seconds > 0:
                    await asyncio.sleep(self.config.think_time_seconds)
            
        finally:
            await self.stop_session()
        
        return self.results


class PerformanceAnalyzer:
    """Analyze load test results using ML techniques."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
    
    def analyze_response_patterns(self, results: List[RequestResult]) -> Dict[str, Any]:
        """Analyze response time patterns using machine learning."""
        if not results:
            return {}
        
        # Create DataFrame for analysis
        data = []
        for result in results:
            data.append({
                'timestamp': result.timestamp,
                'response_time_ms': result.response_time_ms,
                'status_code': result.status_code,
                'response_size_bytes': result.response_size_bytes,
                'user_id': result.user_id,
                'is_error': 1 if result.error or result.status_code >= 400 else 0
            })
        
        df = pd.DataFrame(data)
        
        # Time-based analysis
        df['time_from_start'] = df['timestamp'] - df['timestamp'].min()
        df['minute'] = (df['time_from_start'] // 60).astype(int)
        
        analysis = {
            'basic_stats': self._calculate_basic_stats(df),
            'time_series_analysis': self._analyze_time_series(df),
            'clustering_analysis': self._cluster_responses(df),
            'error_analysis': self._analyze_errors(df),
            'throughput_analysis': self._analyze_throughput(df)
        }
        
        return analysis
    
    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistical metrics."""
        response_times = df['response_time_ms']
        
        return {
            'count': len(df),
            'mean': response_times.mean(),
            'median': response_times.median(),
            'std': response_times.std(),
            'min': response_times.min(),
            'max': response_times.max(),
            'percentiles': {
                'p50': response_times.quantile(0.5),
                'p90': response_times.quantile(0.9),
                'p95': response_times.quantile(0.95),
                'p99': response_times.quantile(0.99)
            }
        }
    
    def _analyze_time_series(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        # Group by minute for trend analysis
        minute_stats = df.groupby('minute').agg({
            'response_time_ms': ['mean', 'median', 'std', 'count'],
            'is_error': 'mean'
        }).round(2)
        
        minute_stats.columns = ['_'.join(col).strip() for col in minute_stats.columns]
        
        # Detect performance degradation
        response_means = minute_stats['response_time_ms_mean'].values
        if len(response_means) > 1:
            # Simple trend detection using linear regression
            x = np.arange(len(response_means))
            slope = np.polyfit(x, response_means, 1)[0]
            degradation_detected = slope > 10  # More than 10ms increase per minute
        else:
            slope = 0
            degradation_detected = False
        
        return {
            'minute_stats': minute_stats.to_dict('index'),
            'trend_slope_ms_per_minute': slope,
            'performance_degradation_detected': degradation_detected,
            'warmup_period_minutes': self._detect_warmup_period(minute_stats)
        }
    
    def _detect_warmup_period(self, minute_stats: pd.DataFrame) -> int:
        """Detect application warmup period."""
        if len(minute_stats) < 3:
            return 0
        
        response_means = minute_stats['response_time_ms_mean'].values
        stable_threshold = 0.1  # 10% variation
        
        # Find when response times stabilize
        for i in range(1, len(response_means)):
            recent_values = response_means[max(0, i-2):i+1]
            if len(recent_values) >= 3:
                cv = np.std(recent_values) / np.mean(recent_values)  # Coefficient of variation
                if cv < stable_threshold:
                    return i
        
        return len(response_means)
    
    def _cluster_responses(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Cluster response patterns to identify different performance profiles."""
        if len(df) < 10:
            return {'clusters': 'Insufficient data for clustering'}
        
        # Prepare features for clustering
        features = df[['response_time_ms', 'response_size_bytes', 'time_from_start']].copy()
        
        # Handle missing values
        features = features.fillna(features.mean())
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Determine optimal number of clusters (max 5)
        max_clusters = min(5, len(df) // 3)
        if max_clusters < 2:
            return {'clusters': 'Insufficient data for clustering'}
        
        # Use KMeans clustering
        self.kmeans = KMeans(n_clusters=max_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(features_scaled)
        
        # Analyze clusters
        df['cluster'] = clusters
        cluster_analysis = {}
        
        for cluster_id in range(max_clusters):
            cluster_data = df[df['cluster'] == cluster_id]
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'avg_response_time': cluster_data['response_time_ms'].mean(),
                'avg_response_size': cluster_data['response_size_bytes'].mean(),
                'error_rate': cluster_data['is_error'].mean(),
                'characteristics': self._characterize_cluster(cluster_data)
            }
        
        return {
            'num_clusters': max_clusters,
            'cluster_analysis': cluster_analysis
        }
    
    def _characterize_cluster(self, cluster_data: pd.DataFrame) -> str:
        """Characterize a performance cluster."""
        avg_time = cluster_data['response_time_ms'].mean()
        error_rate = cluster_data['is_error'].mean()
        
        if error_rate > 0.1:
            return "High Error Rate"
        elif avg_time < 100:
            return "Fast Response"
        elif avg_time < 500:
            return "Normal Response"
        elif avg_time < 1000:
            return "Slow Response"
        else:
            return "Very Slow Response"
    
    def _analyze_errors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze error patterns."""
        error_data = df[df['is_error'] == 1]
        
        if len(error_data) == 0:
            return {'error_rate': 0, 'error_distribution': {}}
        
        error_rate = len(error_data) / len(df)
        
        # Analyze error distribution by status code
        status_distribution = error_data['status_code'].value_counts().to_dict()
        
        # Analyze error timing
        error_times = error_data['time_from_start'].values
        if len(error_times) > 1:
            error_clustering = len(error_times) > 5 and self._detect_error_clusters(error_times)
        else:
            error_clustering = False
        
        return {
            'error_rate': error_rate,
            'total_errors': len(error_data),
            'error_distribution': status_distribution,
            'error_clustering_detected': error_clustering,
            'first_error_time': error_times.min() if len(error_times) > 0 else None,
            'last_error_time': error_times.max() if len(error_times) > 0 else None
        }
    
    def _detect_error_clusters(self, error_times: np.ndarray) -> bool:
        """Detect if errors cluster in time (indicating cascading failures)."""
        # Sort error times
        sorted_times = np.sort(error_times)
        
        # Calculate gaps between consecutive errors
        gaps = np.diff(sorted_times)
        
        # If median gap is much smaller than max gap, errors are clustered
        if len(gaps) > 2:
            median_gap = np.median(gaps)
            max_gap = np.max(gaps)
            return max_gap > 5 * median_gap
        
        return False
    
    def _analyze_throughput(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze throughput patterns."""
        # Calculate requests per second over time
        df_sorted = df.sort_values('timestamp')
        
        # Group by second
        df_sorted['second'] = df_sorted['timestamp'].astype(int)
        rps_data = df_sorted.groupby('second').size()
        
        return {
            'avg_rps': rps_data.mean(),
            'max_rps': rps_data.max(),
            'min_rps': rps_data.min(),
            'rps_std': rps_data.std(),
            'total_requests': len(df),
            'total_data_mb': df['response_size_bytes'].sum() / 1024 / 1024
        }
    
    def generate_visualizations(self, df: pd.DataFrame, output_dir: str):
        """Generate performance visualizations."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # Response time distribution
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.hist(df['response_time_ms'], bins=50, alpha=0.7)
        plt.xlabel('Response Time (ms)')
        plt.ylabel('Frequency')
        plt.title('Response Time Distribution')
        
        # Response time over time
        plt.subplot(2, 2, 2)
        plt.plot(df['time_from_start'], df['response_time_ms'], alpha=0.6)
        plt.xlabel('Time from Start (seconds)')
        plt.ylabel('Response Time (ms)')
        plt.title('Response Time Over Time')
        
        # Throughput over time
        plt.subplot(2, 2, 3)
        df_sorted = df.sort_values('timestamp')
        df_sorted['second'] = df_sorted['timestamp'].astype(int)
        rps_data = df_sorted.groupby('second').size()
        plt.plot(rps_data.index - rps_data.index.min(), rps_data.values)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Requests per Second')
        plt.title('Throughput Over Time')
        
        # Error rate over time
        plt.subplot(2, 2, 4)
        df_sorted['minute'] = (df_sorted['time_from_start'] // 60).astype(int)
        error_rate_by_minute = df_sorted.groupby('minute')['is_error'].mean()
        plt.plot(error_rate_by_minute.index, error_rate_by_minute.values * 100)
        plt.xlabel('Time (minutes)')
        plt.ylabel('Error Rate (%)')
        plt.title('Error Rate Over Time')
        
        plt.tight_layout()
        plt.savefig(output_path / 'load_test_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualizations saved to {output_path}")


class LoadTestCoordinator:
    """
    Enterprise Load Testing Coordination Engine
    =========================================
    
    Comprehensive load testing with ML-powered performance analysis.
    Demonstrates ML Engineer + DevOps + Backend Senior expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.system_monitor = SystemMonitor()
        self.analyzer = PerformanceAnalyzer()
        self.test_results: List[LoadTestResult] = []
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load load testing configuration."""
        default_config = {
            'load_tests': {},
            'global_settings': {
                'ramp_up_strategy': 'linear',  # linear, exponential, step
                'monitoring_interval': 1.0,
                'analysis_enabled': True,
                'visualizations_enabled': True,
                'output_dir': 'load_test_results'
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def execute_load_test(self, test_config: LoadTestConfig) -> LoadTestResult:
        """Execute a single load test."""
        logger.info(f"Starting load test: {test_config.name}")
        
        start_time = datetime.now()
        
        # Start system monitoring
        monitoring_task = asyncio.create_task(self.system_monitor.start_monitoring())
        
        try:
            # Calculate ramp-up schedule
            ramp_schedule = self._calculate_ramp_schedule(test_config)
            
            # Create load generators
            generators = []
            all_results = []
            
            test_start_time = time.time()
            
            # Execute ramp-up
            for step_time, num_users in ramp_schedule:
                # Wait for ramp step time
                while time.time() - test_start_time < step_time:
                    await asyncio.sleep(0.1)
                
                # Add new users
                new_generators = []
                for i in range(len(generators), num_users):
                    generator = LoadGenerator(test_config, i)
                    new_generators.append(generator)
                    generators.append(generator)
                
                # Start new generators
                if new_generators:
                    logger.info(f"Ramping up to {num_users} concurrent users")
                    tasks = [
                        generator.run_load_test(test_start_time, test_config.duration_seconds)
                        for generator in new_generators
                    ]
                    asyncio.create_task(self._collect_results(tasks, all_results))
            
            # Wait for test completion
            remaining_time = test_config.duration_seconds - (time.time() - test_start_time)
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)
            
            # Collect all results
            for generator in generators:
                all_results.extend(generator.results)
            
        finally:
            # Stop monitoring
            self.system_monitor.stop_monitoring()
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
        
        end_time = datetime.now()
        
        # Analyze results
        result = self._analyze_load_test_results(test_config.name, start_time, end_time, all_results)
        
        # Add system metrics
        result.system_metrics = self.system_monitor.get_summary()
        
        # Perform ML analysis if enabled
        if self.config['global_settings']['analysis_enabled']:
            result.ml_analysis = self.analyzer.analyze_response_patterns(all_results)
        
        # Generate visualizations if enabled
        if self.config['global_settings']['visualizations_enabled'] and all_results:
            output_dir = Path(self.config['global_settings']['output_dir']) / test_config.name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert results to DataFrame for visualization
            data = []
            for r in all_results:
                data.append({
                    'timestamp': r.timestamp,
                    'response_time_ms': r.response_time_ms,
                    'status_code': r.status_code,
                    'response_size_bytes': r.response_size_bytes,
                    'user_id': r.user_id,
                    'is_error': 1 if r.error or r.status_code >= 400 else 0,
                    'time_from_start': r.timestamp - all_results[0].timestamp
                })
            
            df = pd.DataFrame(data)
            self.analyzer.generate_visualizations(df, str(output_dir))
        
        return result
    
    def _calculate_ramp_schedule(self, test_config: LoadTestConfig) -> List[Tuple[float, int]]:
        """Calculate user ramp-up schedule."""
        strategy = self.config['global_settings']['ramp_up_strategy']
        ramp_time = test_config.ramp_up_seconds
        max_users = test_config.concurrent_users
        
        schedule = [(0, 1)]  # Start with 1 user
        
        if strategy == 'linear':
            # Linear ramp-up
            steps = min(10, max_users)
            for i in range(1, steps + 1):
                time_point = (i / steps) * ramp_time
                users = int((i / steps) * max_users)
                schedule.append((time_point, max(1, users)))
        
        elif strategy == 'exponential':
            # Exponential ramp-up
            steps = min(8, max_users)
            for i in range(1, steps + 1):
                time_point = (i / steps) * ramp_time
                users = int(max_users * (2 ** i - 1) / (2 ** steps - 1))
                schedule.append((time_point, max(1, users)))
        
        elif strategy == 'step':
            # Step ramp-up
            steps = min(5, max_users)
            users_per_step = max_users // steps
            for i in range(1, steps + 1):
                time_point = (i / steps) * ramp_time
                users = min(i * users_per_step, max_users)
                schedule.append((time_point, users))
        
        # Ensure we reach max users
        if schedule[-1][1] < max_users:
            schedule.append((ramp_time, max_users))
        
        return schedule
    
    async def _collect_results(self, tasks: List, all_results: List):
        """Collect results from async tasks."""
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            for results in results_list:
                if isinstance(results, list):
                    all_results.extend(results)
        except Exception as e:
            logger.error(f"Error collecting results: {e}")
    
    def _analyze_load_test_results(self, test_name: str, start_time: datetime, end_time: datetime, 
                                 results: List[RequestResult]) -> LoadTestResult:
        """Analyze load test results and create summary."""
        if not results:
            return LoadTestResult(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                error_rate=0.0,
                requests_per_second=0.0,
                avg_response_time_ms=0.0,
                min_response_time_ms=0.0,
                max_response_time_ms=0.0,
                p50_response_time_ms=0.0,
                p90_response_time_ms=0.0,
                p95_response_time_ms=0.0,
                p99_response_time_ms=0.0,
                throughput_mb_per_sec=0.0
            )
        
        # Calculate basic metrics
        successful_results = [r for r in results if not r.error and r.status_code < 400]
        failed_results = [r for r in results if r.error or r.status_code >= 400]
        
        response_times = [r.response_time_ms for r in successful_results]
        if not response_times:
            response_times = [0]
        
        total_bytes = sum(r.response_size_bytes for r in results)
        duration_seconds = (end_time - start_time).total_seconds()
        
        return LoadTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            error_rate=len(failed_results) / len(results) * 100,
            requests_per_second=len(results) / duration_seconds,
            avg_response_time_ms=statistics.mean(response_times),
            min_response_time_ms=min(response_times),
            max_response_time_ms=max(response_times),
            p50_response_time_ms=np.percentile(response_times, 50),
            p90_response_time_ms=np.percentile(response_times, 90),
            p95_response_time_ms=np.percentile(response_times, 95),
            p99_response_time_ms=np.percentile(response_times, 99),
            throughput_mb_per_sec=total_bytes / duration_seconds / 1024 / 1024,
            raw_results=results
        )
    
    async def run_load_tests(self, test_configs: List[LoadTestConfig]) -> Dict[str, Any]:
        """Run multiple load tests."""
        logger.info(f"Starting {len(test_configs)} load tests")
        
        results = []
        
        for config in test_configs:
            try:
                result = await self.execute_load_test(config)
                results.append(result)
                self.test_results.append(result)
                
                logger.info(f"Load test completed: {config.name}")
                logger.info(f"  Requests: {result.total_requests}")
                logger.info(f"  Success Rate: {100 - result.error_rate:.2f}%")
                logger.info(f"  Avg Response Time: {result.avg_response_time_ms:.2f}ms")
                logger.info(f"  RPS: {result.requests_per_second:.2f}")
                
            except Exception as e:
                logger.error(f"Load test failed: {config.name}: {e}")
        
        # Generate comprehensive report
        return self._generate_report(results)
    
    def _generate_report(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Generate comprehensive load test report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'total_requests': sum(r.total_requests for r in results),
                'total_successful_requests': sum(r.successful_requests for r in results),
                'total_failed_requests': sum(r.failed_requests for r in results),
                'overall_error_rate': 0.0,
                'avg_requests_per_second': 0.0,
                'avg_response_time_ms': 0.0
            },
            'tests': [],
            'performance_insights': {},
            'recommendations': []
        }
        
        # Calculate overall metrics
        total_requests = report['summary']['total_requests']
        if total_requests > 0:
            report['summary']['overall_error_rate'] = (
                report['summary']['total_failed_requests'] / total_requests * 100
            )
            report['summary']['avg_requests_per_second'] = statistics.mean([r.requests_per_second for r in results])
            report['summary']['avg_response_time_ms'] = statistics.mean([r.avg_response_time_ms for r in results])
        
        # Process each test result
        for result in results:
            test_report = {
                'name': result.test_name,
                'duration_seconds': (result.end_time - result.start_time).total_seconds(),
                'total_requests': result.total_requests,
                'successful_requests': result.successful_requests,
                'failed_requests': result.failed_requests,
                'error_rate': result.error_rate,
                'requests_per_second': result.requests_per_second,
                'response_time_ms': {
                    'avg': result.avg_response_time_ms,
                    'min': result.min_response_time_ms,
                    'max': result.max_response_time_ms,
                    'p50': result.p50_response_time_ms,
                    'p90': result.p90_response_time_ms,
                    'p95': result.p95_response_time_ms,
                    'p99': result.p99_response_time_ms
                },
                'throughput_mb_per_sec': result.throughput_mb_per_sec
            }
            
            # Add system metrics if available
            if hasattr(result, 'system_metrics'):
                test_report['system_metrics'] = result.system_metrics
            
            # Add ML analysis if available
            if hasattr(result, 'ml_analysis'):
                test_report['ml_analysis'] = result.ml_analysis
            
            report['tests'].append(test_report)
        
        # Generate performance insights
        report['performance_insights'] = self._generate_insights(results)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(results)
        
        return report
    
    def _generate_insights(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Generate performance insights using ML analysis."""
        insights = {
            'performance_trends': [],
            'bottleneck_analysis': {},
            'scalability_assessment': {}
        }
        
        if not results:
            return insights
        
        # Analyze performance trends
        for result in results:
            if hasattr(result, 'ml_analysis') and result.ml_analysis:
                ml_data = result.ml_analysis
                
                # Check for performance degradation
                if 'time_series_analysis' in ml_data:
                    ts_analysis = ml_data['time_series_analysis']
                    if ts_analysis.get('performance_degradation_detected', False):
                        insights['performance_trends'].append({
                            'test': result.test_name,
                            'issue': 'Performance degradation detected',
                            'details': f"Response time increased by {ts_analysis.get('trend_slope_ms_per_minute', 0):.2f}ms per minute"
                        })
                
                # Analyze error patterns
                if 'error_analysis' in ml_data:
                    error_analysis = ml_data['error_analysis']
                    if error_analysis.get('error_clustering_detected', False):
                        insights['performance_trends'].append({
                            'test': result.test_name,
                            'issue': 'Cascading failures detected',
                            'details': 'Errors appear to cluster in time, suggesting cascading failures'
                        })
        
        return insights
    
    def _generate_recommendations(self, results: List[LoadTestResult]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        for result in results:
            # High error rate
            if result.error_rate > 5:
                recommendations.append(
                    f"{result.test_name}: High error rate ({result.error_rate:.1f}%) - "
                    "Check application logs and increase resource allocation"
                )
            
            # Slow response times
            if result.p95_response_time_ms > 2000:
                recommendations.append(
                    f"{result.test_name}: Slow P95 response time ({result.p95_response_time_ms:.0f}ms) - "
                    "Consider optimizing database queries and adding caching"
                )
            
            # Low throughput
            if result.requests_per_second < 10:
                recommendations.append(
                    f"{result.test_name}: Low throughput ({result.requests_per_second:.1f} RPS) - "
                    "Consider horizontal scaling or performance optimization"
                )
            
            # High system resource usage
            if hasattr(result, 'system_metrics'):
                sys_metrics = result.system_metrics
                if sys_metrics.get('cpu', {}).get('max', 0) > 80:
                    recommendations.append(
                        f"{result.test_name}: High CPU usage ({sys_metrics['cpu']['max']:.1f}%) - "
                        "Consider CPU optimization or adding more CPU resources"
                    )
                
                if sys_metrics.get('memory', {}).get('max', 0) > 85:
                    recommendations.append(
                        f"{result.test_name}: High memory usage ({sys_metrics['memory']['max']:.1f}%) - "
                        "Check for memory leaks or increase available memory"
                    )
        
        if not recommendations:
            recommendations.append("All tests performed within acceptable parameters. No immediate optimizations required.")
        
        return recommendations
    
    async def save_report(self, report: Dict[str, Any], output_path: str = "load_test_report.json"):
        """Save test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Load test report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for load testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load Test Coordination Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--url", help="Target URL for quick test")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--output", default="load_test_report.json", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize coordinator
    coordinator = LoadTestCoordinator(args.config)
    
    try:
        test_configs = []
        
        if args.url:
            # Quick test mode
            config = LoadTestConfig(
                name="quick_test",
                url=args.url,
                concurrent_users=args.users,
                duration_seconds=args.duration
            )
            test_configs.append(config)
        else:
            # Load from configuration
            for name, test_config in coordinator.config.get('load_tests', {}).items():
                config = LoadTestConfig(
                    name=name,
                    **test_config
                )
                test_configs.append(config)
        
        if not test_configs:
            logger.error("No test configurations found")
            return
        
        # Run tests
        report = await coordinator.run_load_tests(test_configs)
        
        # Save report
        await coordinator.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n⚡ Load Test Results")
        print(f"{'='*50}")
        print(f"Tests Executed: {summary['total_tests']}")
        print(f"Total Requests: {summary['total_requests']:,}")
        print(f"Success Rate: {100 - summary['overall_error_rate']:.2f}%")
        print(f"Average RPS: {summary['avg_requests_per_second']:.2f}")
        print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations'][:3]:  # Show first 3 recommendations
                print(f"  - {rec}")
    
    except Exception as e:
        logger.error(f"Load test execution failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())