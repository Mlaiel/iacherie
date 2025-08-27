"""
Performance Testing & Load Optimization Engine - IA Influencer Agent Platform
============================================================================

Industrial-grade performance testing system for load optimization, stress testing,
and scalability analysis with real-time monitoring and auto-scaling capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import asyncio
import json
import logging
import psutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from uuid import UUID, uuid4
import aiohttp
import numpy as np
import pandas as pd
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns

from ...core.config import get_settings
from ...core.database import get_database
from ...core.exceptions import PerformanceTestError
from ...core.logging import get_logger
from ...models.performance import (
    LoadTestResult, PerformanceMetrics, ScalabilityReport,
    OptimizationRecommendation, ResourceUsage
)
from ...services.monitoring_service import MonitoringService
from ...utils.metrics_collector import MetricsCollector
from ...utils.load_generator import LoadGenerator
from ...utils.resource_monitor import ResourceMonitor

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class TestConfiguration:
    """Configuration for performance tests."""
    test_type: str
    duration_seconds: int
    concurrent_users: int
    ramp_up_duration: int
    target_endpoints: List[str]
    test_data: Dict[str, Any]
    success_criteria: Dict[str, float]
    monitoring_interval: int = 5


@dataclass
class LoadTestMetrics:
    """Metrics collected during load testing."""
    timestamp: datetime
    response_time_ms: float
    throughput_rps: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    queue_length: int


class PerformanceTestEngine:
    """Industrial performance testing and optimization engine."""
    
    def __init__(self):
        self.db = get_database()
        self.monitoring_service = MonitoringService()
        self.metrics_collector = MetricsCollector()
        self.load_generator = LoadGenerator()
        self.resource_monitor = ResourceMonitor()
        
        # Test configurations
        self.test_profiles = {
            'smoke_test': {
                'duration': 60,
                'users': 5,
                'ramp_up': 10,
                'description': 'Basic functionality verification'
            },
            'load_test': {
                'duration': 300,
                'users': 50,
                'ramp_up': 60,
                'description': 'Normal expected load simulation'
            },
            'stress_test': {
                'duration': 600,
                'users': 200,
                'ramp_up': 120,
                'description': 'Beyond normal capacity testing'
            },
            'spike_test': {
                'duration': 180,
                'users': 500,
                'ramp_up': 30,
                'description': 'Sudden load increase simulation'
            },
            'volume_test': {
                'duration': 1800,
                'users': 100,
                'ramp_up': 300,
                'description': 'Large data volume processing'
            },
            'endurance_test': {
                'duration': 3600,
                'users': 75,
                'ramp_up': 180,
                'description': 'Long-term stability testing'
            }
        }
        
        # Performance benchmarks
        self.performance_benchmarks = {
            'api_response_time': {
                'excellent': 200,    # ms
                'good': 500,
                'acceptable': 1000,
                'poor': 2000
            },
            'throughput': {
                'excellent': 1000,   # requests per second
                'good': 500,
                'acceptable': 200,
                'poor': 100
            },
            'error_rate': {
                'excellent': 0.01,   # 1%
                'good': 0.05,        # 5%
                'acceptable': 0.10,  # 10%
                'poor': 0.20         # 20%
            },
            'cpu_usage': {
                'excellent': 60,     # %
                'good': 75,
                'acceptable': 85,
                'poor': 95
            },
            'memory_usage': {
                'excellent': 60,     # %
                'good': 75,
                'acceptable': 85,
                'poor': 95
            }
        }
        
        # Active test sessions
        self.active_tests = {}
        
        # Optimization strategies
        self.optimization_strategies = {
            'database': [
                'query_optimization', 'connection_pooling', 'index_optimization',
                'read_replicas', 'query_caching', 'database_partitioning'
            ],
            'application': [
                'code_optimization', 'caching_layer', 'async_processing',
                'connection_pooling', 'resource_pooling', 'batch_processing'
            ],
            'infrastructure': [
                'load_balancing', 'auto_scaling', 'cdn_optimization',
                'resource_scaling', 'network_optimization', 'server_tuning'
            ],
            'content': [
                'compression', 'minification', 'lazy_loading',
                'image_optimization', 'cdn_caching', 'content_preprocessing'
            ]
        }
    
    async def execute_performance_test(
        self,
        test_config: TestConfiguration,
        project_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Execute comprehensive performance test suite.
        
        Args:
            test_config: Test configuration parameters
            project_id: Optional project identifier
            
        Returns:
            Detailed performance test results and analysis
        """
        try:
            test_id = uuid4()
            test_start_time = datetime.utcnow()
            
            logger.info(f"Starting performance test: {test_id} - {test_config.test_type}")
            
            # Initialize test session
            test_session = {
                'test_id': test_id,
                'config': test_config,
                'start_time': test_start_time,
                'status': 'running',
                'metrics': [],
                'errors': [],
                'warnings': []
            }
            
            self.active_tests[test_id] = test_session
            
            # Pre-test system state capture
            baseline_metrics = await self._capture_baseline_metrics()
            
            # Start resource monitoring
            monitoring_task = asyncio.create_task(
                self._monitor_system_resources(test_id, test_config.monitoring_interval)
            )
            
            # Execute load test
            load_test_results = await self._execute_load_test(test_config, test_id)
            
            # Stop monitoring
            monitoring_task.cancel()
            
            # Post-test analysis
            test_end_time = datetime.utcnow()
            test_duration = (test_end_time - test_start_time).total_seconds()
            
            # Collect final metrics
            final_metrics = await self._capture_final_metrics()
            
            # Analyze results
            performance_analysis = await self._analyze_performance_results(
                load_test_results, baseline_metrics, final_metrics, test_config
            )
            
            # Generate recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                performance_analysis, test_config
            )
            
            # Create comprehensive test report
            test_report = {
                'test_id': str(test_id),
                'project_id': str(project_id) if project_id else None,
                'test_configuration': {
                    'test_type': test_config.test_type,
                    'duration_seconds': test_config.duration_seconds,
                    'concurrent_users': test_config.concurrent_users,
                    'ramp_up_duration': test_config.ramp_up_duration,
                    'target_endpoints': test_config.target_endpoints,
                    'success_criteria': test_config.success_criteria
                },
                'execution_summary': {
                    'start_time': test_start_time.isoformat(),
                    'end_time': test_end_time.isoformat(),
                    'total_duration_seconds': test_duration,
                    'test_status': 'completed',
                    'total_requests': load_test_results['total_requests'],
                    'successful_requests': load_test_results['successful_requests'],
                    'failed_requests': load_test_results['failed_requests'],
                    'overall_success_rate': load_test_results['success_rate']
                },
                'performance_metrics': {
                    'response_time_statistics': {
                        'average_ms': performance_analysis['avg_response_time'],
                        'median_ms': performance_analysis['median_response_time'],
                        'p95_ms': performance_analysis['p95_response_time'],
                        'p99_ms': performance_analysis['p99_response_time'],
                        'min_ms': performance_analysis['min_response_time'],
                        'max_ms': performance_analysis['max_response_time']
                    },
                    'throughput_statistics': {
                        'average_rps': performance_analysis['avg_throughput'],
                        'peak_rps': performance_analysis['peak_throughput'],
                        'sustained_rps': performance_analysis['sustained_throughput']
                    },
                    'error_statistics': {
                        'total_errors': load_test_results['failed_requests'],
                        'error_rate': load_test_results['error_rate'],
                        'error_types': load_test_results['error_breakdown'],
                        'error_timeline': load_test_results['error_timeline']
                    },
                    'resource_utilization': {
                        'cpu_usage': {
                            'average': performance_analysis['avg_cpu_usage'],
                            'peak': performance_analysis['peak_cpu_usage'],
                            'baseline': baseline_metrics['cpu_usage']
                        },
                        'memory_usage': {
                            'average': performance_analysis['avg_memory_usage'],
                            'peak': performance_analysis['peak_memory_usage'],
                            'baseline': baseline_metrics['memory_usage']
                        },
                        'network_io': performance_analysis['network_stats'],
                        'disk_io': performance_analysis['disk_stats']
                    }
                },
                'benchmark_comparison': {
                    'response_time_rating': self._rate_performance(
                        performance_analysis['avg_response_time'], 
                        'api_response_time'
                    ),
                    'throughput_rating': self._rate_performance(
                        performance_analysis['avg_throughput'], 
                        'throughput'
                    ),
                    'error_rate_rating': self._rate_performance(
                        load_test_results['error_rate'], 
                        'error_rate'
                    ),
                    'cpu_usage_rating': self._rate_performance(
                        performance_analysis['avg_cpu_usage'], 
                        'cpu_usage'
                    ),
                    'memory_usage_rating': self._rate_performance(
                        performance_analysis['avg_memory_usage'], 
                        'memory_usage'
                    )
                },
                'scalability_analysis': await self._analyze_scalability(
                    load_test_results, test_config
                ),
                'bottleneck_identification': await self._identify_bottlenecks(
                    performance_analysis, load_test_results
                ),
                'optimization_recommendations': optimization_recommendations,
                'detailed_timeline': load_test_results['timeline_data'],
                'test_artifacts': {
                    'charts_generated': await self._generate_performance_charts(
                        load_test_results, test_id
                    ),
                    'raw_data_file': f"performance_test_{test_id}_raw_data.json",
                    'report_file': f"performance_test_{test_id}_report.pdf"
                }
            }
            
            # Store test results
            await self.db.performance_tests.create({
                'id': test_id,
                'project_id': project_id,
                'test_type': test_config.test_type,
                'configuration': test_config.__dict__,
                'results': test_report,
                'created_at': test_start_time,
                'completed_at': test_end_time
            })
            
            # Clean up active test session
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            
            logger.info(f"Performance test completed: {test_id} - Duration: {test_duration:.2f}s")
            return test_report
            
        except Exception as e:
            logger.error(f"Performance test execution failed: {str(e)}")
            if test_id in self.active_tests:
                self.active_tests[test_id]['status'] = 'failed'
                self.active_tests[test_id]['error'] = str(e)
            raise PerformanceTestError(f"Test execution failed: {str(e)}")
    
    async def run_continuous_performance_monitoring(
        self,
        monitoring_config: Dict[str, Any],
        project_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Run continuous performance monitoring with alerting.
        
        Args:
            monitoring_config: Monitoring configuration
            project_id: Optional project identifier
            
        Returns:
            Monitoring session details and real-time metrics access
        """
        try:
            monitoring_id = uuid4()
            start_time = datetime.utcnow()
            
            # Configure monitoring parameters
            monitoring_interval = monitoring_config.get('interval_seconds', 30)
            alert_thresholds = monitoring_config.get('alert_thresholds', {})
            endpoints_to_monitor = monitoring_config.get('endpoints', [])
            duration_hours = monitoring_config.get('duration_hours', 24)
            
            # Initialize monitoring session
            monitoring_session = {
                'monitoring_id': monitoring_id,
                'project_id': project_id,
                'start_time': start_time,
                'end_time': start_time + timedelta(hours=duration_hours),
                'status': 'active',
                'config': monitoring_config,
                'metrics_collected': 0,
                'alerts_triggered': 0
            }
            
            # Start background monitoring task
            monitoring_task = asyncio.create_task(
                self._run_continuous_monitoring_loop(
                    monitoring_session, alert_thresholds, endpoints_to_monitor
                )
            )
            
            result = {
                'monitoring_id': str(monitoring_id),
                'project_id': str(project_id) if project_id else None,
                'status': 'started',
                'start_time': start_time.isoformat(),
                'scheduled_end_time': monitoring_session['end_time'].isoformat(),
                'monitoring_interval_seconds': monitoring_interval,
                'endpoints_monitored': len(endpoints_to_monitor),
                'alert_thresholds_configured': len(alert_thresholds),
                'real_time_dashboard_url': f"/monitoring/dashboard/{monitoring_id}",
                'api_endpoint_for_metrics': f"/api/monitoring/{monitoring_id}/metrics",
                'stop_monitoring_endpoint': f"/api/monitoring/{monitoring_id}/stop"
            }
            
            # Store monitoring session
            await self.db.monitoring_sessions.create({
                'id': monitoring_id,
                'project_id': project_id,
                'configuration': monitoring_config,
                'session_data': monitoring_session,
                'created_at': start_time
            })
            
            logger.info(f"Started continuous performance monitoring: {monitoring_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start continuous monitoring: {str(e)}")
            raise PerformanceTestError(f"Monitoring startup failed: {str(e)}")
    
    async def optimize_system_performance(
        self,
        optimization_request: Dict[str, Any],
        project_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Execute automated system performance optimization.
        
        Args:
            optimization_request: Optimization parameters and targets
            project_id: Optional project identifier
            
        Returns:
            Optimization results and applied changes
        """
        try:
            optimization_id = uuid4()
            start_time = datetime.utcnow()
            
            # Parse optimization request
            target_areas = optimization_request.get('target_areas', ['all'])
            optimization_level = optimization_request.get('level', 'moderate')  # conservative, moderate, aggressive
            dry_run = optimization_request.get('dry_run', False)
            
            # Collect current system state
            current_state = await self._collect_system_state()
            
            # Analyze performance issues
            performance_issues = await self._analyze_performance_issues(current_state)
            
            # Generate optimization plan
            optimization_plan = await self._generate_optimization_plan(
                performance_issues, target_areas, optimization_level
            )
            
            # Execute optimizations (if not dry run)
            applied_optimizations = []
            if not dry_run:
                applied_optimizations = await self._execute_optimization_plan(
                    optimization_plan
                )
            
            # Measure impact
            post_optimization_state = None
            performance_improvement = None
            
            if applied_optimizations:
                # Wait for changes to take effect
                await asyncio.sleep(30)
                
                post_optimization_state = await self._collect_system_state()
                performance_improvement = await self._measure_performance_improvement(
                    current_state, post_optimization_state
                )
            
            end_time = datetime.utcnow()
            
            result = {
                'optimization_id': str(optimization_id),
                'project_id': str(project_id) if project_id else None,
                'execution_summary': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': (end_time - start_time).total_seconds(),
                    'optimization_level': optimization_level,
                    'dry_run_mode': dry_run,
                    'target_areas': target_areas
                },
                'performance_analysis': {
                    'issues_identified': len(performance_issues),
                    'critical_issues': len([i for i in performance_issues if i['severity'] == 'critical']),
                    'major_issues': len([i for i in performance_issues if i['severity'] == 'major']),
                    'minor_issues': len([i for i in performance_issues if i['severity'] == 'minor']),
                    'issues_breakdown': performance_issues
                },
                'optimization_plan': {
                    'total_optimizations_planned': len(optimization_plan),
                    'database_optimizations': len([o for o in optimization_plan if o['category'] == 'database']),
                    'application_optimizations': len([o for o in optimization_plan if o['category'] == 'application']),
                    'infrastructure_optimizations': len([o for o in optimization_plan if o['category'] == 'infrastructure']),
                    'planned_optimizations': optimization_plan
                },
                'applied_optimizations': {
                    'total_applied': len(applied_optimizations),
                    'successful_applications': len([o for o in applied_optimizations if o['status'] == 'success']),
                    'failed_applications': len([o for o in applied_optimizations if o['status'] == 'failed']),
                    'applied_changes': applied_optimizations
                },
                'performance_impact': performance_improvement if performance_improvement else {
                    'note': 'No impact measured - dry run mode or no optimizations applied'
                },
                'system_state_comparison': {
                    'before_optimization': current_state,
                    'after_optimization': post_optimization_state
                } if post_optimization_state else None,
                'recommendations': {
                    'immediate_actions': await self._recommend_immediate_actions(performance_issues),
                    'long_term_improvements': await self._recommend_long_term_improvements(performance_issues),
                    'monitoring_recommendations': await self._recommend_monitoring_improvements(current_state)
                }
            }
            
            # Store optimization results
            await self.db.performance_optimizations.create({
                'id': optimization_id,
                'project_id': project_id,
                'optimization_request': optimization_request,
                'results': result,
                'created_at': start_time,
                'completed_at': end_time
            })
            
            logger.info(f"Performance optimization completed: {optimization_id} - Applied {len(applied_optimizations)} changes")
            return result
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")
            raise PerformanceTestError(f"Optimization failed: {str(e)}")
    
    # Private methods for test execution and analysis
    
    async def _execute_load_test(
        self,
        test_config: TestConfiguration,
        test_id: UUID
    ) -> Dict[str, Any]:
        """Execute load test with specified configuration."""
        try:
            results = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'throughput_data': [],
                'error_breakdown': {},
                'error_timeline': [],
                'timeline_data': [],
                'success_rate': 0.0,
                'error_rate': 0.0
            }
            
            # Calculate test parameters
            total_duration = test_config.duration_seconds
            ramp_up_duration = test_config.ramp_up_duration
            concurrent_users = test_config.concurrent_users
            
            # Generate load using thread pool
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                # Submit load generation tasks
                futures = []
                
                for user_id in range(concurrent_users):
                    # Calculate start delay for ramp-up
                    start_delay = (user_id / concurrent_users) * ramp_up_duration
                    
                    future = executor.submit(
                        self._simulate_user_load,
                        test_config,
                        user_id,
                        start_delay,
                        total_duration
                    )
                    futures.append(future)
                
                # Collect results from all users
                for future in as_completed(futures):
                    try:
                        user_results = future.result()
                        
                        results['total_requests'] += user_results['requests']
                        results['successful_requests'] += user_results['successful']
                        results['failed_requests'] += user_results['failed']
                        results['response_times'].extend(user_results['response_times'])
                        results['timeline_data'].extend(user_results['timeline'])
                        
                        # Merge error breakdown
                        for error_type, count in user_results['errors'].items():
                            results['error_breakdown'][error_type] = results['error_breakdown'].get(error_type, 0) + count
                    
                    except Exception as e:
                        logger.error(f"Load test user failed: {str(e)}")
                        continue
            
            # Calculate final statistics
            if results['total_requests'] > 0:
                results['success_rate'] = results['successful_requests'] / results['total_requests']
                results['error_rate'] = results['failed_requests'] / results['total_requests']
            
            return results
            
        except Exception as e:
            logger.error(f"Load test execution failed: {str(e)}")
            raise
    
    def _simulate_user_load(
        self,
        test_config: TestConfiguration,
        user_id: int,
        start_delay: float,
        duration: int
    ) -> Dict[str, Any]:
        """Simulate individual user load."""
        import requests
        import random
        
        user_results = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'response_times': [],
            'timeline': [],
            'errors': {}
        }
        
        # Wait for ramp-up delay
        time.sleep(start_delay)
        
        start_time = time.time()
        session = requests.Session()
        
        try:
            while time.time() - start_time < duration - start_delay:
                # Select random endpoint
                endpoint = random.choice(test_config.target_endpoints)
                request_start = time.time()
                
                try:
                    # Make request
                    response = session.get(
                        endpoint,
                        timeout=30,
                        headers={'User-Agent': f'LoadTest-User-{user_id}'}
                    )
                    
                    request_end = time.time()
                    response_time = (request_end - request_start) * 1000  # Convert to ms
                    
                    user_results['requests'] += 1
                    user_results['response_times'].append(response_time)
                    
                    if response.status_code < 400:
                        user_results['successful'] += 1
                    else:
                        user_results['failed'] += 1
                        error_key = f"HTTP_{response.status_code}"
                        user_results['errors'][error_key] = user_results['errors'].get(error_key, 0) + 1
                    
                    # Record timeline data
                    user_results['timeline'].append({
                        'timestamp': request_start,
                        'user_id': user_id,
                        'endpoint': endpoint,
                        'response_time': response_time,
                        'status_code': response.status_code
                    })
                    
                    # Random think time
                    time.sleep(random.uniform(0.1, 1.0))
                    
                except requests.exceptions.RequestException as e:
                    user_results['failed'] += 1
                    user_results['requests'] += 1
                    error_key = f"EXCEPTION_{type(e).__name__}"
                    user_results['errors'][error_key] = user_results['errors'].get(error_key, 0) + 1
                    
                    time.sleep(1)  # Brief pause on error
                    
        except Exception as e:
            logger.error(f"User {user_id} simulation failed: {str(e)}")
        
        finally:
            session.close()
        
        return user_results
    
    async def _capture_baseline_metrics(self) -> Dict[str, Any]:
        """Capture system baseline metrics before testing."""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                'network_io': psutil.net_io_counters()._asdict(),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                'active_connections': len(psutil.net_connections()),
                'process_count': len(psutil.pids()),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to capture baseline metrics: {str(e)}")
            return {}
    
    async def _capture_final_metrics(self) -> Dict[str, Any]:
        """Capture system metrics after testing."""
        return await self._capture_baseline_metrics()
    
    async def _monitor_system_resources(
        self,
        test_id: UUID,
        monitoring_interval: int
    ):
        """Monitor system resources during test execution."""
        try:
            while test_id in self.active_tests and self.active_tests[test_id]['status'] == 'running':
                metrics = {
                    'timestamp': datetime.utcnow(),
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_io_read': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    'disk_io_write': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                    'network_io_sent': psutil.net_io_counters().bytes_sent,
                    'network_io_recv': psutil.net_io_counters().bytes_recv,
                    'active_connections': len(psutil.net_connections())
                }
                
                if test_id in self.active_tests:
                    self.active_tests[test_id]['metrics'].append(metrics)
                
                await asyncio.sleep(monitoring_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Resource monitoring cancelled for test {test_id}")
        except Exception as e:
            logger.error(f"Resource monitoring failed: {str(e)}")
    
    async def _analyze_performance_results(
        self,
        load_results: Dict[str, Any],
        baseline_metrics: Dict[str, Any],
        final_metrics: Dict[str, Any],
        test_config: TestConfiguration
    ) -> Dict[str, Any]:
        """Analyze performance test results."""
        try:
            response_times = load_results['response_times']
            
            if not response_times:
                return self._get_default_analysis()
            
            analysis = {
                'avg_response_time': float(np.mean(response_times)),
                'median_response_time': float(np.median(response_times)),
                'p95_response_time': float(np.percentile(response_times, 95)),
                'p99_response_time': float(np.percentile(response_times, 99)),
                'min_response_time': float(np.min(response_times)),
                'max_response_time': float(np.max(response_times)),
                'std_response_time': float(np.std(response_times)),
                'avg_throughput': load_results['total_requests'] / test_config.duration_seconds,
                'peak_throughput': 0.0,  # Would need timeline analysis
                'sustained_throughput': 0.0,  # Would need timeline analysis
                'avg_cpu_usage': 0.0,
                'peak_cpu_usage': 0.0,
                'avg_memory_usage': 0.0,
                'peak_memory_usage': 0.0,
                'network_stats': {},
                'disk_stats': {}
            }
            
            # Add resource usage analysis if available
            if baseline_metrics and final_metrics:
                analysis['avg_cpu_usage'] = (baseline_metrics.get('cpu_usage', 0) + final_metrics.get('cpu_usage', 0)) / 2
                analysis['avg_memory_usage'] = (baseline_metrics.get('memory_usage', 0) + final_metrics.get('memory_usage', 0)) / 2
                analysis['peak_cpu_usage'] = max(baseline_metrics.get('cpu_usage', 0), final_metrics.get('cpu_usage', 0))
                analysis['peak_memory_usage'] = max(baseline_metrics.get('memory_usage', 0), final_metrics.get('memory_usage', 0))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when data is insufficient."""
        return {
            'avg_response_time': 0.0,
            'median_response_time': 0.0,
            'p95_response_time': 0.0,
            'p99_response_time': 0.0,
            'min_response_time': 0.0,
            'max_response_time': 0.0,
            'std_response_time': 0.0,
            'avg_throughput': 0.0,
            'peak_throughput': 0.0,
            'sustained_throughput': 0.0,
            'avg_cpu_usage': 0.0,
            'peak_cpu_usage': 0.0,
            'avg_memory_usage': 0.0,
            'peak_memory_usage': 0.0,
            'network_stats': {},
            'disk_stats': {}
        }
    
    def _rate_performance(self, value: float, metric_type: str) -> str:
        """Rate performance based on benchmarks."""
        benchmarks = self.performance_benchmarks.get(metric_type, {})
        
        if not benchmarks:
            return 'unknown'
        
        if metric_type == 'error_rate':
            # Lower is better for error rate
            if value <= benchmarks['excellent']:
                return 'excellent'
            elif value <= benchmarks['good']:
                return 'good'
            elif value <= benchmarks['acceptable']:
                return 'acceptable'
            else:
                return 'poor'
        else:
            # Higher is better for response time, throughput, etc.
            if value <= benchmarks['excellent']:
                return 'excellent'
            elif value <= benchmarks['good']:
                return 'good'
            elif value <= benchmarks['acceptable']:
                return 'acceptable'
            else:
                return 'poor'
