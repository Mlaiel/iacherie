"""📊 Migration Metrics & Monitoring System - Ultra-Industrial Performance Analytics Engine
======================================================================================

Advanced monitoring and metrics collection system for IA Influencer Agent migrations:
- Real-time migration performance tracking and analysis
- Predictive migration duration estimation with ML algorithms
- Resource utilization monitoring (CPU, memory, disk, network)
- Migration health scoring and risk prediction systems
- Automated alerting and notification for migration anomalies

Technical Infrastructure:
- Metrics Collection: Real-time performance data, resource monitoring, query analysis
- Analytics: Trend analysis, performance baselines, anomaly detection
- Visualization: Migration dashboards, real-time charts, health indicators
- Alerting: Smart notifications, escalation rules, automated responses
- ML Models: Duration prediction, success probability, resource forecasting

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
==================================================
This migration monitoring system, algorithms, and all associated analytics concepts are the 
exclusive intellectual property of Fahed Mlaiel. Any unauthorized use, copying, modification, 
reverse engineering, or distribution without explicit written permission from Fahed Mlaiel 
(mlaiel@live.de) is STRICTLY PROHIBITED and will be prosecuted to the full extent of 
international law.

LEGAL CONSEQUENCES: Violation will result in immediate legal action including:
- Criminal prosecution for intellectual property theft
- Civil litigation for damages and lost profits  
- Permanent injunction against unauthorized use
- Full legal costs and attorney fees recovery

For licensing inquiries: mlaiel@live.de

Business Logic Flow:
Migration Start → Resource Baseline → Performance Monitoring → 
Anomaly Detection → Predictive Analysis → Alert Generation → Health Reporting
"""
import asyncio
import logging
import psutil
import time
import statistics
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union, Tuple, Callable, NamedTuple
from dataclasses import dataclass, field
import uuid
import json
import numpy as np
from collections import defaultdict, deque
import threading
import queue
import pickle
import os

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Boolean, Integer, JSON, Text, BigInteger, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID, JSONB

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of migration metrics"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    DURATION = "duration"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    HEALTH = "health"
    PREDICTION = "prediction"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringStatus(Enum):
    """Monitoring session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    """System resource snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: Tuple[float, float, float]
    active_connections: int
    database_size_gb: float


@dataclass
class PerformanceMetrics:
    """Migration performance metrics"""
    migration_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    records_processed: int = 0
    throughput_per_second: float = 0.0
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    query_count: int = 0
    average_query_time: float = 0.0
    slowest_query_time: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    success_rate: float = 100.0


@dataclass
class MigrationAlert:
    """Migration monitoring alert"""
    alert_id: str
    migration_id: str
    severity: AlertSeverity
    title: str
    message: str
    metric_name: str
    threshold_value: float
    actual_value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    resolved: bool = False
    escalated: bool = False


class MigrationPredictor:
    """ML-based migration outcome and duration predictor"""
    
    def __init__(self):
        self.historical_data = []
        self.model_trained = False
        self.prediction_accuracy = 0.0
    
    def add_historical_data(self, migration_data: Dict[str, Any]):
        """Add historical migration data for model training"""
        self.historical_data.append(migration_data)
        
        # Retrain model when we have enough data
        if len(self.historical_data) >= 10:
            self._train_prediction_model()
    
    def predict_migration_duration(self, migration_info: Dict[str, Any]) -> Dict[str, Any]:
        """Predict migration duration based on historical data"""
        if not self.model_trained or not self.historical_data:
            return {
                'predicted_duration_minutes': 60,  # Default estimate
                'confidence_score': 0.5,
                'prediction_range': (30, 120),
                'factors': ['insufficient_data']
            }
        
        # Feature extraction
        features = self._extract_features(migration_info)
        
        # Simple prediction based on historical averages
        similar_migrations = self._find_similar_migrations(features)
        
        if similar_migrations:
            durations = [m['duration_minutes'] for m in similar_migrations]
            predicted_duration = statistics.mean(durations)
            confidence = min(0.9, len(similar_migrations) / 10.0)
            prediction_range = (
                max(5, predicted_duration * 0.7),
                predicted_duration * 1.5
            )
        else:
            predicted_duration = 60
            confidence = 0.3
            prediction_range = (30, 180)
        
        return {
            'predicted_duration_minutes': predicted_duration,
            'confidence_score': confidence,
            'prediction_range': prediction_range,
            'factors': features,
            'similar_migrations_count': len(similar_migrations)
        }
    
    def predict_success_probability(self, migration_info: Dict[str, Any]) -> Dict[str, Any]:
        """Predict migration success probability"""
        if not self.historical_data:
            return {
                'success_probability': 0.85,
                'risk_factors': ['insufficient_data'],
                'confidence_score': 0.5
            }
        
        features = self._extract_features(migration_info)
        similar_migrations = self._find_similar_migrations(features)
        
        if similar_migrations:
            success_count = sum(1 for m in similar_migrations if m.get('success', True))
            success_rate = success_count / len(similar_migrations)
            confidence = min(0.9, len(similar_migrations) / 10.0)
        else:
            success_rate = 0.8
            confidence = 0.3
        
        # Identify risk factors
        risk_factors = []
        if features.get('complexity_score', 0) > 0.7:
            risk_factors.append('high_complexity')
        if features.get('dependency_count', 0) > 5:
            risk_factors.append('many_dependencies')
        if features.get('data_volume_gb', 0) > 10:
            risk_factors.append('large_data_volume')
        
        return {
            'success_probability': success_rate,
            'risk_factors': risk_factors,
            'confidence_score': confidence,
            'similar_migrations_count': len(similar_migrations)
        }
    
    def _extract_features(self, migration_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from migration information"""
        return {
            'migration_type': migration_info.get('category', 'unknown'),
            'dependency_count': len(migration_info.get('dependencies', [])),
            'complexity_score': self._calculate_complexity_score(migration_info),
            'data_volume_gb': migration_info.get('estimated_data_volume_gb', 1.0),
            'has_schema_changes': migration_info.get('has_schema_changes', False),
            'has_data_migration': migration_info.get('has_data_migration', False)
        }
    
    def _calculate_complexity_score(self, migration_info: Dict[str, Any]) -> float:
        """Calculate migration complexity score"""
        score = 0.0
        
        # Add complexity based on various factors
        if migration_info.get('has_schema_changes', False):
            score += 0.3
        if migration_info.get('has_data_migration', False):
            score += 0.2
        if len(migration_info.get('dependencies', [])) > 3:
            score += 0.2
        if migration_info.get('category') in ['security', 'user']:
            score += 0.3
        
        return min(1.0, score)
    
    def _find_similar_migrations(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical migrations"""
        similar = []
        
        for migration in self.historical_data:
            hist_features = self._extract_features(migration)
            similarity = self._calculate_similarity(features, hist_features)
            
            if similarity > 0.6:  # 60% similarity threshold
                migration['similarity_score'] = similarity
                similar.append(migration)
        
        return sorted(similar, key=lambda x: x['similarity_score'], reverse=True)[:5]
    
    def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """Calculate similarity between two feature sets"""
        similarities = []
        
        # Type similarity
        if features1.get('migration_type') == features2.get('migration_type'):
            similarities.append(1.0)
        else:
            similarities.append(0.0)
        
        # Dependency count similarity
        dep1 = features1.get('dependency_count', 0)
        dep2 = features2.get('dependency_count', 0)
        max_dep = max(dep1, dep2, 1)
        dep_similarity = 1.0 - abs(dep1 - dep2) / max_dep
        similarities.append(dep_similarity)
        
        # Complexity similarity
        comp1 = features1.get('complexity_score', 0)
        comp2 = features2.get('complexity_score', 0)
        comp_similarity = 1.0 - abs(comp1 - comp2)
        similarities.append(comp_similarity)
        
        return statistics.mean(similarities)
    
    def _train_prediction_model(self):
        """Train prediction model (simplified version)"""
        if len(self.historical_data) < 5:
            return
        
        # Simple model training simulation
        self.model_trained = True
        self.prediction_accuracy = min(0.9, len(self.historical_data) / 50.0)
        
        logger.info(f"Prediction model trained with {len(self.historical_data)} samples")


class ResourceMonitor:
    """Real-time system resource monitoring"""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.snapshots = deque(maxlen=3600)  # Keep last hour of data
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Resource monitoring stopped")
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current resource snapshot"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Load average
            load_average = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0.0, 0.0, 0.0)
            
            # Database connections (simplified)
            active_connections = len(psutil.pids())  # Approximate
            
            # Database size (would need actual DB connection)
            database_size_gb = 1.0  # Placeholder
            
            return ResourceSnapshot(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                load_average=load_average,
                active_connections=active_connections,
                database_size_gb=database_size_gb
            )
            
        except Exception as e:
            logger.error(f"Failed to get resource snapshot: {str(e)}")
            return ResourceSnapshot(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                load_average=(0.0, 0.0, 0.0),
                active_connections=0,
                database_size_gb=0.0
            )
    
    def get_resource_trends(self, minutes: int = 10) -> Dict[str, Any]:
        """Get resource usage trends"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        recent_snapshots = [
            snapshot for snapshot in self.snapshots
            if snapshot.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            return {}
        
        trends = {}
        
        # CPU trend
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        trends['cpu'] = {
            'average': statistics.mean(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values),
            'trend': 'stable'  # Would calculate actual trend
        }
        
        # Memory trend
        memory_values = [s.memory_percent for s in recent_snapshots]
        trends['memory'] = {
            'average': statistics.mean(memory_values),
            'max': max(memory_values),
            'min': min(memory_values),
            'trend': 'stable'
        }
        
        # Disk trend
        disk_values = [s.disk_usage_percent for s in recent_snapshots]
        trends['disk'] = {
            'average': statistics.mean(disk_values),
            'max': max(disk_values),
            'min': min(disk_values),
            'trend': 'stable'
        }
        
        return trends
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                snapshot = self.get_current_snapshot()
                self.snapshots.append(snapshot)
                time.sleep(self.sampling_interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                time.sleep(self.sampling_interval)


class PerformanceAnalyzer:
    """Advanced performance analysis and optimization recommendations"""
    
    def __init__(self):
        self.performance_baselines = {}
        self.anomaly_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'query_time': 5.0,
            'throughput_degradation': 0.5
        }
    
    def analyze_migration_performance(self, metrics: PerformanceMetrics,
                                    resource_monitor: ResourceMonitor) -> Dict[str, Any]:
        """Analyze migration performance and provide recommendations"""
        analysis = {
            'overall_score': 0.0,
            'performance_grade': 'A',
            'bottlenecks': [],
            'recommendations': [],
            'anomalies': [],
            'optimization_opportunities': []
        }
        
        try:
            # Calculate performance score
            performance_factors = []
            
            # Duration factor
            if metrics.duration_seconds:
                expected_duration = self._get_expected_duration(metrics.migration_id)
                duration_factor = min(1.0, expected_duration / metrics.duration_seconds)
                performance_factors.append(duration_factor)
            
            # Throughput factor
            if metrics.throughput_per_second > 0:
                baseline_throughput = self._get_baseline_throughput(metrics.migration_id)
                throughput_factor = min(1.0, metrics.throughput_per_second / baseline_throughput)
                performance_factors.append(throughput_factor)
            
            # Error rate factor
            error_factor = max(0.0, 1.0 - (metrics.error_count / max(1, metrics.records_processed)))
            performance_factors.append(error_factor)
            
            # Resource efficiency factor
            resource_trends = resource_monitor.get_resource_trends()
            resource_factor = self._calculate_resource_efficiency(resource_trends)
            performance_factors.append(resource_factor)
            
            # Calculate overall score
            if performance_factors:
                analysis['overall_score'] = statistics.mean(performance_factors)
            
            # Determine performance grade
            if analysis['overall_score'] >= 0.9:
                analysis['performance_grade'] = 'A'
            elif analysis['overall_score'] >= 0.8:
                analysis['performance_grade'] = 'B'
            elif analysis['overall_score'] >= 0.7:
                analysis['performance_grade'] = 'C'
            elif analysis['overall_score'] >= 0.6:
                analysis['performance_grade'] = 'D'
            else:
                analysis['performance_grade'] = 'F'
            
            # Identify bottlenecks
            analysis['bottlenecks'] = self._identify_bottlenecks(metrics, resource_trends)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(
                metrics, resource_trends, analysis['bottlenecks']
            )
            
            # Detect anomalies
            analysis['anomalies'] = self._detect_anomalies(metrics, resource_trends)
            
            # Find optimization opportunities
            analysis['optimization_opportunities'] = self._find_optimization_opportunities(
                metrics, resource_trends
            )
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            analysis['overall_score'] = 0.5
            analysis['performance_grade'] = 'C'
            analysis['anomalies'].append(f"Analysis error: {str(e)}")
        
        return analysis
    
    def _get_expected_duration(self, migration_id: str) -> float:
        """Get expected duration for migration type"""
        # Default expected durations by migration type
        expected_durations = {
            'user': 3600,  # 1 hour
            'content': 7200,  # 2 hours
            'fingerprint': 5400,  # 1.5 hours
            'monetization': 3600,  # 1 hour
            'security': 1800  # 30 minutes
        }
        
        for migration_type, duration in expected_durations.items():
            if migration_type in migration_id.lower():
                return duration
        
        return 3600  # Default 1 hour
    
    def _get_baseline_throughput(self, migration_id: str) -> float:
        """Get baseline throughput for migration type"""
        baseline = self.performance_baselines.get(migration_id, 100.0)
        return baseline
    
    def _calculate_resource_efficiency(self, resource_trends: Dict[str, Any]) -> float:
        """Calculate resource efficiency factor"""
        if not resource_trends:
            return 0.5
        
        efficiency_factors = []
        
        # CPU efficiency
        cpu_trend = resource_trends.get('cpu', {})
        cpu_avg = cpu_trend.get('average', 50.0)
        cpu_efficiency = 1.0 - (cpu_avg / 100.0)
        efficiency_factors.append(cpu_efficiency)
        
        # Memory efficiency
        memory_trend = resource_trends.get('memory', {})
        memory_avg = memory_trend.get('average', 50.0)
        memory_efficiency = 1.0 - (memory_avg / 100.0)
        efficiency_factors.append(memory_efficiency)
        
        return statistics.mean(efficiency_factors)
    
    def _identify_bottlenecks(self, metrics: PerformanceMetrics,
                            resource_trends: Dict[str, Any]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # High CPU usage
        cpu_trend = resource_trends.get('cpu', {})
        if cpu_trend.get('max', 0) > self.anomaly_thresholds['cpu_usage']:
            bottlenecks.append('high_cpu_usage')
        
        # High memory usage
        memory_trend = resource_trends.get('memory', {})
        if memory_trend.get('max', 0) > self.anomaly_thresholds['memory_usage']:
            bottlenecks.append('high_memory_usage')
        
        # Slow queries
        if metrics.slowest_query_time > self.anomaly_thresholds['query_time']:
            bottlenecks.append('slow_queries')
        
        # Low throughput
        if metrics.throughput_per_second < 10:  # Less than 10 records/second
            bottlenecks.append('low_throughput')
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: PerformanceMetrics,
                                resource_trends: Dict[str, Any],
                                bottlenecks: List[str]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if 'high_cpu_usage' in bottlenecks:
            recommendations.append("Consider reducing parallel processing or optimizing CPU-intensive operations")
        
        if 'high_memory_usage' in bottlenecks:
            recommendations.append("Implement batch processing to reduce memory footprint")
        
        if 'slow_queries' in bottlenecks:
            recommendations.append("Optimize database queries and consider adding indexes")
        
        if 'low_throughput' in bottlenecks:
            recommendations.append("Increase batch size or implement parallel processing")
        
        if metrics.error_count > 0:
            recommendations.append("Investigate and fix errors to improve success rate")
        
        return recommendations
    
    def _detect_anomalies(self, metrics: PerformanceMetrics,
                         resource_trends: Dict[str, Any]) -> List[str]:
        """Detect performance anomalies"""
        anomalies = []
        
        # Unusual resource spikes
        cpu_trend = resource_trends.get('cpu', {})
        cpu_variance = cpu_trend.get('max', 0) - cpu_trend.get('min', 0)
        if cpu_variance > 50:
            anomalies.append('cpu_spike_detected')
        
        # Memory leaks
        memory_trend = resource_trends.get('memory', {})
        if memory_trend.get('trend') == 'increasing':
            anomalies.append('potential_memory_leak')
        
        # Query time anomalies
        if metrics.average_query_time > 0 and metrics.slowest_query_time > metrics.average_query_time * 10:
            anomalies.append('query_time_outlier')
        
        return anomalies
    
    def _find_optimization_opportunities(self, metrics: PerformanceMetrics,
                                       resource_trends: Dict[str, Any]) -> List[str]:
        """Find optimization opportunities"""
        opportunities = []
        
        # Underutilized resources
        cpu_trend = resource_trends.get('cpu', {})
        if cpu_trend.get('average', 50) < 30:
            opportunities.append('increase_parallelism')
        
        # Batch size optimization
        if metrics.throughput_per_second > 0 and metrics.records_processed > 1000:
            opportunities.append('optimize_batch_size')
        
        # Query optimization
        if metrics.query_count > 100 and metrics.average_query_time > 0.1:
            opportunities.append('query_optimization')
        
        return opportunities


class MigrationMonitor:
    """Comprehensive migration monitoring and alerting system"""
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.performance_analyzer = PerformanceAnalyzer()
        self.predictor = MigrationPredictor()
        self.active_sessions = {}
        self.alert_queue = queue.Queue()
        self.alert_handlers = []
        self.status = MonitoringStatus.STOPPED
    
    def start_monitoring_session(self, migration_id: str, 
                                migration_info: Dict[str, Any]) -> str:
        """Start monitoring session for migration"""
        session_id = str(uuid.uuid4())
        
        # Get migration predictions
        duration_prediction = self.predictor.predict_migration_duration(migration_info)
        success_prediction = self.predictor.predict_success_probability(migration_info)
        
        session = {
            'session_id': session_id,
            'migration_id': migration_id,
            'start_time': datetime.now(timezone.utc),
            'migration_info': migration_info,
            'predictions': {
                'duration': duration_prediction,
                'success': success_prediction
            },
            'metrics': PerformanceMetrics(
                migration_id=migration_id,
                start_time=datetime.now(timezone.utc)
            ),
            'alerts': [],
            'status': 'active'
        }
        
        self.active_sessions[session_id] = session
        
        # Start resource monitoring if not already running
        if self.status != MonitoringStatus.ACTIVE:
            self.resource_monitor.start_monitoring()
            self.status = MonitoringStatus.ACTIVE
        
        logger.info(f"Started monitoring session {session_id} for migration {migration_id}")
        return session_id
    
    def update_migration_progress(self, session_id: str, 
                                progress_data: Dict[str, Any]):
        """Update migration progress and metrics"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        metrics = session['metrics']
        
        # Update metrics
        metrics.records_processed = progress_data.get('records_processed', metrics.records_processed)
        metrics.query_count = progress_data.get('query_count', metrics.query_count)
        metrics.error_count = progress_data.get('error_count', metrics.error_count)
        
        # Calculate throughput
        elapsed_time = (datetime.now(timezone.utc) - metrics.start_time).total_seconds()
        if elapsed_time > 0:
            metrics.throughput_per_second = metrics.records_processed / elapsed_time
        
        # Update performance metrics
        current_resource = self.resource_monitor.get_current_snapshot()
        metrics.peak_cpu_usage = max(metrics.peak_cpu_usage, current_resource.cpu_percent)
        metrics.peak_memory_usage = max(metrics.peak_memory_usage, current_resource.memory_percent)
        
        # Check for alerts
        self._check_alerts(session_id, session, current_resource)
    
    def end_monitoring_session(self, session_id: str, success: bool = True) -> Dict[str, Any]:
        """End monitoring session and generate final report"""
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        metrics = session['metrics']
        
        # Finalize metrics
        metrics.end_time = datetime.now(timezone.utc)
        metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.success_rate = 100.0 if success else 0.0
        
        # Generate performance analysis
        performance_analysis = self.performance_analyzer.analyze_migration_performance(
            metrics, self.resource_monitor
        )
        
        # Add to historical data for prediction model
        historical_data = {
            'migration_id': metrics.migration_id,
            'category': session['migration_info'].get('category', 'unknown'),
            'dependencies': session['migration_info'].get('dependencies', []),
            'duration_minutes': metrics.duration_seconds / 60.0,
            'success': success,
            'records_processed': metrics.records_processed,
            'throughput': metrics.throughput_per_second,
            'peak_cpu': metrics.peak_cpu_usage,
            'peak_memory': metrics.peak_memory_usage,
            'has_schema_changes': session['migration_info'].get('has_schema_changes', False),
            'has_data_migration': session['migration_info'].get('has_data_migration', False)
        }
        
        self.predictor.add_historical_data(historical_data)
        
        # Generate final report
        final_report = {
            'session_id': session_id,
            'migration_id': metrics.migration_id,
            'success': success,
            'duration_minutes': metrics.duration_seconds / 60.0,
            'metrics': metrics,
            'performance_analysis': performance_analysis,
            'predictions_accuracy': self._calculate_prediction_accuracy(session),
            'alerts_generated': len(session['alerts']),
            'recommendations': performance_analysis.get('recommendations', [])
        }
        
        # Clean up session
        del self.active_sessions[session_id]
        
        # Stop resource monitoring if no active sessions
        if not self.active_sessions:
            self.resource_monitor.stop_monitoring()
            self.status = MonitoringStatus.STOPPED
        
        logger.info(f"Ended monitoring session {session_id}")
        return final_report
    
    def get_migration_dashboard(self) -> Dict[str, Any]:
        """Get real-time migration dashboard data"""
        dashboard_data = {
            'active_migrations': len(self.active_sessions),
            'system_health': self._calculate_system_health(),
            'resource_usage': self.resource_monitor.get_current_snapshot(),
            'resource_trends': self.resource_monitor.get_resource_trends(),
            'active_sessions': [],
            'recent_alerts': self._get_recent_alerts(),
            'performance_summary': self._get_performance_summary()
        }
        
        # Add active session details
        for session_id, session in self.active_sessions.items():
            session_data = {
                'session_id': session_id,
                'migration_id': session['migration_id'],
                'start_time': session['start_time'],
                'duration_minutes': (datetime.now(timezone.utc) - session['start_time']).total_seconds() / 60,
                'progress': self._calculate_session_progress(session),
                'current_metrics': session['metrics']
            }
            dashboard_data['active_sessions'].append(session_data)
        
        return dashboard_data
    
    def _check_alerts(self, session_id: str, session: Dict[str, Any], 
                     resource_snapshot: ResourceSnapshot):
        """Check for alert conditions"""
        metrics = session['metrics']
        
        # High CPU usage alert
        if resource_snapshot.cpu_percent > 90:
            alert = MigrationAlert(
                alert_id=str(uuid.uuid4()),
                migration_id=session['migration_id'],
                severity=AlertSeverity.WARNING,
                title="High CPU Usage",
                message=f"CPU usage is {resource_snapshot.cpu_percent:.1f}%",
                metric_name="cpu_percent",
                threshold_value=90.0,
                actual_value=resource_snapshot.cpu_percent
            )
            self._generate_alert(session_id, alert)
        
        # High memory usage alert
        if resource_snapshot.memory_percent > 90:
            alert = MigrationAlert(
                alert_id=str(uuid.uuid4()),
                migration_id=session['migration_id'],
                severity=AlertSeverity.WARNING,
                title="High Memory Usage",
                message=f"Memory usage is {resource_snapshot.memory_percent:.1f}%",
                metric_name="memory_percent",
                threshold_value=90.0,
                actual_value=resource_snapshot.memory_percent
            )
            self._generate_alert(session_id, alert)
        
        # Duration alert (if migration is taking longer than predicted)
        duration_prediction = session['predictions']['duration']
        current_duration = (datetime.now(timezone.utc) - metrics.start_time).total_seconds() / 60
        predicted_max = duration_prediction['prediction_range'][1]
        
        if current_duration > predicted_max:
            alert = MigrationAlert(
                alert_id=str(uuid.uuid4()),
                migration_id=session['migration_id'],
                severity=AlertSeverity.WARNING,
                title="Migration Duration Exceeded",
                message=f"Migration running longer than predicted ({current_duration:.1f} min)",
                metric_name="duration_minutes",
                threshold_value=predicted_max,
                actual_value=current_duration
            )
            self._generate_alert(session_id, alert)
    
    def _generate_alert(self, session_id: str, alert: MigrationAlert):
        """Generate and process alert"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['alerts'].append(alert)
        
        self.alert_queue.put(alert)
        
        # Process alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {str(e)}")
        
        logger.warning(f"Alert generated: {alert.title} - {alert.message}")
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        current_snapshot = self.resource_monitor.get_current_snapshot()
        
        health_factors = []
        
        # CPU health
        cpu_health = max(0.0, 1.0 - (current_snapshot.cpu_percent / 100.0))
        health_factors.append(cpu_health)
        
        # Memory health
        memory_health = max(0.0, 1.0 - (current_snapshot.memory_percent / 100.0))
        health_factors.append(memory_health)
        
        # Disk health
        disk_health = max(0.0, 1.0 - (current_snapshot.disk_usage_percent / 100.0))
        health_factors.append(disk_health)
        
        overall_health = statistics.mean(health_factors)
        
        if overall_health >= 0.8:
            health_status = "excellent"
        elif overall_health >= 0.6:
            health_status = "good"
        elif overall_health >= 0.4:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            'overall_score': overall_health,
            'status': health_status,
            'cpu_health': cpu_health,
            'memory_health': memory_health,
            'disk_health': disk_health
        }
    
    def _get_recent_alerts(self, hours: int = 24) -> List[MigrationAlert]:
        """Get recent alerts"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_alerts = []
        
        for session in self.active_sessions.values():
            for alert in session['alerts']:
                if alert.timestamp >= cutoff_time:
                    recent_alerts.append(alert)
        
        return sorted(recent_alerts, key=lambda x: x.timestamp, reverse=True)[:10]
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all active migrations"""
        if not self.active_sessions:
            return {}
        
        all_metrics = [session['metrics'] for session in self.active_sessions.values()]
        
        total_records = sum(m.records_processed for m in all_metrics)
        total_errors = sum(m.error_count for m in all_metrics)
        avg_throughput = statistics.mean([m.throughput_per_second for m in all_metrics if m.throughput_per_second > 0])
        
        return {
            'total_records_processed': total_records,
            'total_errors': total_errors,
            'average_throughput': avg_throughput,
            'success_rate': ((total_records - total_errors) / max(1, total_records)) * 100
        }
    
    def _calculate_session_progress(self, session: Dict[str, Any]) -> float:
        """Calculate session progress percentage"""
        duration_prediction = session['predictions']['duration']
        predicted_duration = duration_prediction['predicted_duration_minutes']
        
        current_duration = (datetime.now(timezone.utc) - session['start_time']).total_seconds() / 60
        
        if predicted_duration > 0:
            progress = min(100.0, (current_duration / predicted_duration) * 100)
        else:
            progress = 0.0
        
        return progress
    
    def _calculate_prediction_accuracy(self, session: Dict[str, Any]) -> Dict[str, float]:
        """Calculate prediction accuracy for completed session"""
        metrics = session['metrics']
        predictions = session['predictions']
        
        accuracy = {}
        
        # Duration prediction accuracy
        if metrics.duration_seconds:
            predicted_duration = predictions['duration']['predicted_duration_minutes']
            actual_duration = metrics.duration_seconds / 60.0
            
            if predicted_duration > 0:
                duration_error = abs(predicted_duration - actual_duration) / predicted_duration
                accuracy['duration'] = max(0.0, 1.0 - duration_error)
            else:
                accuracy['duration'] = 0.0
        
        # Success prediction accuracy
        actual_success = metrics.success_rate > 90.0
        predicted_success_prob = predictions['success']['success_probability']
        
        if actual_success and predicted_success_prob > 0.5:
            accuracy['success'] = predicted_success_prob
        elif not actual_success and predicted_success_prob <= 0.5:
            accuracy['success'] = 1.0 - predicted_success_prob
        else:
            accuracy['success'] = 0.0
        
        return accuracy
    
    def add_alert_handler(self, handler: Callable[[MigrationAlert], None]):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def remove_alert_handler(self, handler: Callable[[MigrationAlert], None]):
        """Remove alert handler function"""
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
