"""
Real-time Monitoring Dashboard for Crawlers
==========================================

Advanced real-time monitoring and analytics dashboard for crawler operations.
Provides comprehensive insights, performance metrics, and violation alerts
for content protection and surveillance systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import statistics

from .orchestrator import CrawlerOrchestrator, CrawlingJobResult, CrawlerType
from ..database.models import CrawlResult as DBCrawlResult
from ..utils.metrics_collector import MetricsCollector
from ..utils.alert_manager import AlertManager

logger = logging.getLogger(__name__)

@dataclass
class CrawlerMetrics:
    """Performance metrics for crawler operations."""
    
    crawler_type: CrawlerType
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    success_rate: float
    avg_execution_time: float
    avg_results_per_job: float
    total_violations_detected: int
    last_activity: Optional[datetime]
    
    # Performance metrics
    avg_response_time: float = 0.0
    peak_memory_usage: float = 0.0
    cpu_utilization: float = 0.0
    
    # Error analysis
    common_errors: List[str] = None
    error_frequency: Dict[str, int] = None

@dataclass
class ViolationTrend:
    """Trend analysis for violation detection."""
    
    platform: str
    date: datetime
    violation_count: int
    total_content_scanned: int
    violation_rate: float
    severity_breakdown: Dict[str, int]
    top_violation_types: List[str]

@dataclass
class SystemHealth:
    """Overall system health indicators."""
    
    overall_status: str  # healthy, warning, critical
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    
    # Service status
    database_healthy: bool
    redis_healthy: bool
    crawler_services: Dict[str, bool]
    
    # Performance indicators
    response_times: Dict[str, float]
    throughput: Dict[str, float]
    error_rates: Dict[str, float]

class RealTimeMonitor:
    """Real-time monitoring system for crawler operations."""
    
    def __init__(self, orchestrator: CrawlerOrchestrator):
        """Initialize real-time monitor."""
        self.orchestrator = orchestrator
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        
        # Real-time data storage
        self.metrics_history: Dict[CrawlerType, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.violation_trends: deque = deque(maxlen=10000)
        self.system_health_history: deque = deque(maxlen=1000)
        
        # Alert thresholds
        self.alert_thresholds = {
            'success_rate_threshold': 0.8,
            'response_time_threshold': 30.0,
            'violation_rate_threshold': 0.1,
            'memory_threshold': 0.85,
            'cpu_threshold': 0.9
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_interval = 30  # seconds
    
    async def start_monitoring(self):
        """Start real-time monitoring."""
        self.is_monitoring = True
        logger.info("Real-time monitor started")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_crawler_performance(),
            self._monitor_system_health(),
            self._analyze_violation_trends(),
            self._check_alert_conditions()
        )
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.is_monitoring = False
        logger.info("Real-time monitor stopped")
    
    async def _monitor_crawler_performance(self):
        """Monitor crawler performance metrics."""
        while self.is_monitoring:
            try:
                # Collect metrics for each crawler type
                for crawler_type in CrawlerType:
                    metrics = await self._calculate_crawler_metrics(crawler_type)
                    if metrics:
                        self.metrics_history[crawler_type].append({
                            'timestamp': datetime.now(),
                            'metrics': metrics
                        })
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Crawler performance monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_system_health(self):
        """Monitor overall system health."""
        while self.is_monitoring:
            try:
                health_data = await self._collect_system_health()
                self.system_health_history.append({
                    'timestamp': datetime.now(),
                    'health': health_data
                })
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"System health monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _analyze_violation_trends(self):
        """Analyze violation detection trends."""
        while self.is_monitoring:
            try:
                # Analyze trends for each platform
                platforms = ['youtube', 'tiktok', 'instagram', 'twitter', 'web']
                
                for platform in platforms:
                    trend = await self._calculate_violation_trend(platform)
                    if trend:
                        self.violation_trends.append(trend)
                
                await asyncio.sleep(self.monitoring_interval * 2)  # Less frequent
                
            except Exception as e:
                logger.error(f"Violation trend analysis error: {e}")
                await asyncio.sleep(self.monitoring_interval * 2)
    
    async def _check_alert_conditions(self):
        """Check for alert conditions."""
        while self.is_monitoring:
            try:
                await self._check_performance_alerts()
                await self._check_violation_alerts()
                await self._check_system_alerts()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Alert checking error: {e}")
                await asyncio.sleep(60)
    
    async def _calculate_crawler_metrics(self, crawler_type: CrawlerType) -> Optional[CrawlerMetrics]:
        """Calculate performance metrics for a specific crawler type."""
        try:
            # Get recent job results for this crawler type
            recent_jobs = [
                job for job in self.orchestrator.job_results
                if job.crawler_type == crawler_type and 
                job.start_time > datetime.now() - timedelta(hours=24)
            ]
            
            if not recent_jobs:
                return None
            
            # Calculate basic metrics
            total_jobs = len(recent_jobs)
            successful_jobs = sum(1 for job in recent_jobs if job.status == 'success')
            failed_jobs = total_jobs - successful_jobs
            success_rate = successful_jobs / total_jobs if total_jobs > 0 else 0
            
            # Execution time metrics
            execution_times = [job.execution_time for job in recent_jobs if job.execution_time]
            avg_execution_time = statistics.mean(execution_times) if execution_times else 0
            
            # Results metrics
            results_counts = [job.results_count for job in recent_jobs]
            avg_results_per_job = statistics.mean(results_counts) if results_counts else 0
            
            # Violation metrics
            total_violations = sum(job.violations_detected for job in recent_jobs)
            
            # Last activity
            last_activity = max(job.start_time for job in recent_jobs) if recent_jobs else None
            
            # Error analysis
            error_jobs = [job for job in recent_jobs if job.status == 'error']
            common_errors = [job.error_message for job in error_jobs if job.error_message]
            error_frequency = {}
            for error in common_errors:
                error_key = error[:50]  # Truncate for grouping
                error_frequency[error_key] = error_frequency.get(error_key, 0) + 1
            
            return CrawlerMetrics(
                crawler_type=crawler_type,
                total_jobs=total_jobs,
                successful_jobs=successful_jobs,
                failed_jobs=failed_jobs,
                success_rate=success_rate,
                avg_execution_time=avg_execution_time,
                avg_results_per_job=avg_results_per_job,
                total_violations_detected=total_violations,
                last_activity=last_activity,
                common_errors=list(set(common_errors))[:5],  # Top 5 unique errors
                error_frequency=dict(sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:5])
            )
            
        except Exception as e:
            logger.error(f"Metrics calculation error for {crawler_type}: {e}")
            return None
    
    async def _collect_system_health(self) -> SystemHealth:
        """Collect system health metrics."""
        try:
            # Get system metrics from metrics collector
            system_metrics = await self.metrics_collector.get_system_metrics()
            
            # Determine overall status
            overall_status = "healthy"
            if (system_metrics.get('cpu_usage', 0) > self.alert_thresholds['cpu_threshold'] or
                system_metrics.get('memory_usage', 0) > self.alert_thresholds['memory_threshold']):
                overall_status = "warning"
            
            # Check service health
            crawler_services = {}
            for crawler_type in self.orchestrator.crawlers:
                crawler_services[crawler_type.value] = True  # Would implement actual health checks
            
            return SystemHealth(
                overall_status=overall_status,
                cpu_usage=system_metrics.get('cpu_usage', 0),
                memory_usage=system_metrics.get('memory_usage', 0),
                disk_usage=system_metrics.get('disk_usage', 0),
                network_io=system_metrics.get('network_io', {}),
                active_connections=system_metrics.get('active_connections', 0),
                database_healthy=True,  # Would implement actual checks
                redis_healthy=True,
                crawler_services=crawler_services,
                response_times=system_metrics.get('response_times', {}),
                throughput=system_metrics.get('throughput', {}),
                error_rates=system_metrics.get('error_rates', {})
            )
            
        except Exception as e:
            logger.error(f"System health collection error: {e}")
            return SystemHealth(
                overall_status="error",
                cpu_usage=0, memory_usage=0, disk_usage=0,
                network_io={}, active_connections=0,
                database_healthy=False, redis_healthy=False,
                crawler_services={}, response_times={},
                throughput={}, error_rates={}
            )
    
    async def _calculate_violation_trend(self, platform: str) -> Optional[ViolationTrend]:
        """Calculate violation trends for a platform."""
        try:
            # Get recent job results for this platform
            recent_jobs = [
                job for job in self.orchestrator.job_results
                if any(result.platform == platform for result in (job.crawl_results or []))
                and job.start_time > datetime.now() - timedelta(hours=1)
            ]
            
            if not recent_jobs:
                return None
            
            # Calculate metrics
            total_violations = sum(job.violations_detected for job in recent_jobs)
            total_content = sum(job.results_count for job in recent_jobs)
            violation_rate = total_violations / total_content if total_content > 0 else 0
            
            return ViolationTrend(
                platform=platform,
                date=datetime.now(),
                violation_count=total_violations,
                total_content_scanned=total_content,
                violation_rate=violation_rate,
                severity_breakdown={'high': 0, 'medium': 0, 'low': 0},  # Would implement
                top_violation_types=['unauthorized_copy', 'copyright_infringement']  # Would analyze
            )
            
        except Exception as e:
            logger.error(f"Violation trend calculation error for {platform}: {e}")
            return None
    
    async def _check_performance_alerts(self):
        """Check for performance-related alerts."""
        try:
            for crawler_type, history in self.metrics_history.items():
                if not history:
                    continue
                
                latest_metrics = history[-1]['metrics']
                
                # Check success rate
                if latest_metrics.success_rate < self.alert_thresholds['success_rate_threshold']:
                    await self.alert_manager.send_alert({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f'{crawler_type.value} success rate dropped to {latest_metrics.success_rate:.2%}',
                        'data': asdict(latest_metrics)
                    })
                
                # Check execution time
                if latest_metrics.avg_execution_time > self.alert_thresholds['response_time_threshold']:
                    await self.alert_manager.send_alert({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f'{crawler_type.value} execution time increased to {latest_metrics.avg_execution_time:.2f}s',
                        'data': asdict(latest_metrics)
                    })
                    
        except Exception as e:
            logger.error(f"Performance alert check error: {e}")
    
    async def _check_violation_alerts(self):
        """Check for violation-related alerts."""
        try:
            if not self.violation_trends:
                return
            
            # Check for sudden spikes in violations
            recent_trends = list(self.violation_trends)[-10:]  # Last 10 data points
            
            for platform in set(trend.platform for trend in recent_trends):
                platform_trends = [t for t in recent_trends if t.platform == platform]
                
                if len(platform_trends) >= 2:
                    latest_rate = platform_trends[-1].violation_rate
                    previous_rate = platform_trends[-2].violation_rate
                    
                    # Alert on significant increase
                    if latest_rate > previous_rate * 2 and latest_rate > self.alert_thresholds['violation_rate_threshold']:
                        await self.alert_manager.send_alert({
                            'type': 'violation_spike',
                            'severity': 'high',
                            'message': f'Violation rate spike on {platform}: {latest_rate:.2%}',
                            'data': asdict(platform_trends[-1])
                        })
                        
        except Exception as e:
            logger.error(f"Violation alert check error: {e}")
    
    async def _check_system_alerts(self):
        """Check for system-related alerts."""
        try:
            if not self.system_health_history:
                return
            
            latest_health = self.system_health_history[-1]['health']
            
            # Check CPU usage
            if latest_health.cpu_usage > self.alert_thresholds['cpu_threshold']:
                await self.alert_manager.send_alert({
                    'type': 'system',
                    'severity': 'critical',
                    'message': f'High CPU usage: {latest_health.cpu_usage:.1%}',
                    'data': asdict(latest_health)
                })
            
            # Check memory usage
            if latest_health.memory_usage > self.alert_thresholds['memory_threshold']:
                await self.alert_manager.send_alert({
                    'type': 'system',
                    'severity': 'critical',
                    'message': f'High memory usage: {latest_health.memory_usage:.1%}',
                    'data': asdict(latest_health)
                })
                
        except Exception as e:
            logger.error(f"System alert check error: {e}")
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for real-time display."""
        try:
            # Current metrics for each crawler
            crawler_metrics = {}
            for crawler_type, history in self.metrics_history.items():
                if history:
                    crawler_metrics[crawler_type.value] = asdict(history[-1]['metrics'])
            
            # Recent violation trends
            recent_violations = list(self.violation_trends)[-50:]  # Last 50 data points
            violation_summary = {}
            for platform in set(trend.platform for trend in recent_violations):
                platform_trends = [t for t in recent_violations if t.platform == platform]
                if platform_trends:
                    latest = platform_trends[-1]
                    violation_summary[platform] = {
                        'current_rate': latest.violation_rate,
                        'total_violations': sum(t.violation_count for t in platform_trends),
                        'trend': 'increasing' if len(platform_trends) > 1 and latest.violation_rate > platform_trends[-2].violation_rate else 'stable'
                    }
            
            # Current system health
            current_health = None
            if self.system_health_history:
                current_health = asdict(self.system_health_history[-1]['health'])
            
            # Active tasks summary
            orchestrator_status = self.orchestrator.get_system_status()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system_health': current_health,
                'crawler_metrics': crawler_metrics,
                'violation_summary': violation_summary,
                'orchestrator_status': orchestrator_status,
                'active_alerts': len(self.alert_manager.active_alerts) if hasattr(self.alert_manager, 'active_alerts') else 0,
                'monitoring_status': 'active' if self.is_monitoring else 'inactive'
            }
            
        except Exception as e:
            logger.error(f"Dashboard data generation error: {e}")
            return {}
    
    def get_historical_metrics(
        self,
        crawler_type: Optional[CrawlerType] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get historical metrics for analysis."""
        try:
            cutoff_time = datetime.now() - time_range
            
            if crawler_type:
                # Get metrics for specific crawler
                history = self.metrics_history.get(crawler_type, deque())
                filtered_history = [
                    entry for entry in history
                    if entry['timestamp'] > cutoff_time
                ]
                
                return {
                    'crawler_type': crawler_type.value,
                    'time_range': str(time_range),
                    'data_points': len(filtered_history),
                    'metrics': [entry['metrics'] for entry in filtered_history]
                }
            else:
                # Get metrics for all crawlers
                all_metrics = {}
                for ct, history in self.metrics_history.items():
                    filtered_history = [
                        entry for entry in history
                        if entry['timestamp'] > cutoff_time
                    ]
                    all_metrics[ct.value] = [entry['metrics'] for entry in filtered_history]
                
                return {
                    'time_range': str(time_range),
                    'all_crawler_metrics': all_metrics
                }
                
        except Exception as e:
            logger.error(f"Historical metrics error: {e}")
            return {}
    
    def get_violation_analytics(self, time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Get comprehensive violation analytics."""
        try:
            cutoff_time = datetime.now() - time_range
            
            # Filter recent violation trends
            recent_trends = [
                trend for trend in self.violation_trends
                if trend.date > cutoff_time
            ]
            
            # Analytics by platform
            platform_analytics = {}
            for platform in set(trend.platform for trend in recent_trends):
                platform_trends = [t for t in recent_trends if t.platform == platform]
                
                total_violations = sum(t.violation_count for t in platform_trends)
                total_scanned = sum(t.total_content_scanned for t in platform_trends)
                avg_rate = total_violations / total_scanned if total_scanned > 0 else 0
                
                platform_analytics[platform] = {
                    'total_violations': total_violations,
                    'total_content_scanned': total_scanned,
                    'average_violation_rate': avg_rate,
                    'data_points': len(platform_trends),
                    'peak_violation_rate': max(t.violation_rate for t in platform_trends) if platform_trends else 0
                }
            
            # Overall statistics
            overall_stats = {
                'total_violations': sum(t.violation_count for t in recent_trends),
                'total_content_scanned': sum(t.total_content_scanned for t in recent_trends),
                'platforms_monitored': len(platform_analytics),
                'time_range': str(time_range),
                'data_points': len(recent_trends)
            }
            
            return {
                'overall_statistics': overall_stats,
                'platform_analytics': platform_analytics,
                'trend_data': [asdict(trend) for trend in recent_trends[-100:]]  # Last 100 points
            }
            
        except Exception as e:
            logger.error(f"Violation analytics error: {e}")
            return {}
    
    async def cleanup(self):
        """Clean up monitoring resources."""
        try:
            self.stop_monitoring()
            
            if hasattr(self.metrics_collector, 'cleanup'):
                await self.metrics_collector.cleanup()
            
            if hasattr(self.alert_manager, 'cleanup'):
                await self.alert_manager.cleanup()
            
            logger.info("Real-time monitor cleaned up")
            
        except Exception as e:
            logger.error(f"Monitor cleanup error: {e}")
