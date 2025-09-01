"""🎵 Industrial Audio Fingerprinting Performance Monitor
=====================================================
Real-time monitoring and validation system for industrial audio fingerprinting
ensuring compliance with ultra-advanced requirements:
- Real-time processing <50ms guaranteed
- Precision >99.5% validated continuously  
- FAISS 100M+ scale performance tracking
- Modification resistance monitoring
- Industrial SLA compliance validation

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Industrial performance metrics container"""
    # Processing performance
    processing_time_ms: float = 0.0
    realtime_compliant: bool = False  # <50ms requirement
    
    # Precision metrics
    precision_score: float = 0.0
    precision_validated: bool = False  # >99.5% requirement
    
    # Resistance metrics
    pitch_resistance: float = 0.0
    tempo_resistance: float = 0.0
    eq_resistance: float = 0.0
    noise_resistance: float = 0.0
    
    # Scale metrics
    faiss_search_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    index_size: int = 0
    
    # Quality assurance
    industrial_compliant: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IndustrialSLARequirements:
    """Service Level Agreement requirements for industrial deployment"""
    # Performance SLA
    max_processing_time_ms: float = 50.0
    max_search_time_ms: float = 50.0
    target_precision: float = 0.995  # >99.5%
    
    # Scale SLA
    max_memory_usage_gb: float = 64.0
    max_index_size: int = 100_000_000  # 100M fingerprints
    target_throughput_fps: float = 1000.0  # Fingerprints per second
    
    # Resistance SLA
    min_pitch_resistance: float = 0.90
    min_tempo_resistance: float = 0.80
    min_eq_resistance: float = 0.85
    min_noise_resistance: float = 0.75
    
    # Availability SLA
    target_uptime: float = 0.999  # 99.9% uptime
    max_error_rate: float = 0.001  # <0.1% error rate

class IndustrialPerformanceMonitor:
    """
    Real-time performance monitoring system for industrial audio fingerprinting
    
    Features:
    - Continuous SLA compliance monitoring
    - Real-time performance alerting
    - Precision validation framework
    - Scale performance tracking
    - Industrial compliance reporting
    """
    
    def __init__(self, sla_requirements: Optional[IndustrialSLARequirements] = None):
        self.sla = sla_requirements or IndustrialSLARequirements()
        
        # Performance history (rolling window)
        self.window_size = 10000  # Keep last 10K measurements
        self.performance_history = deque(maxlen=self.window_size)
        
        # Real-time metrics
        self.current_metrics = PerformanceMetrics()
        self.cumulative_stats = {
            'total_fingerprints': 0,
            'total_searches': 0,
            'total_processing_time': 0.0,
            'sla_violations': 0,
            'precision_failures': 0,
            'system_errors': 0
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.last_report_time = datetime.now()
        self.alert_callbacks = []
        
        # Performance benchmarks
        self.performance_benchmarks = {
            'baseline_processing_time': 25.0,  # Target 25ms baseline
            'baseline_precision': 0.997,       # Target 99.7% baseline
            'baseline_search_time': 15.0,      # Target 15ms search
        }
        
        logger.info("Industrial Performance Monitor initialized")
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        self.monitoring_active = True
        logger.info("Industrial performance monitoring started")
        
        # Start background monitoring tasks
        asyncio.create_task(self._continuous_monitoring_loop())
        asyncio.create_task(self._sla_compliance_checker())
        
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        logger.info("Industrial performance monitoring stopped")
    
    def record_fingerprint_performance(self, 
                                     processing_time_ms: float,
                                     precision_score: float,
                                     resistance_metrics: Dict[str, float] = None,
                                     memory_usage_mb: float = 0.0,
                                     content_id: str = None) -> PerformanceMetrics:
        """Record performance metrics for a fingerprinting operation"""
        
        metrics = PerformanceMetrics(
            processing_time_ms=processing_time_ms,
            realtime_compliant=processing_time_ms <= self.sla.max_processing_time_ms,
            precision_score=precision_score,
            precision_validated=precision_score >= self.sla.target_precision,
            memory_usage_mb=memory_usage_mb,
            timestamp=datetime.now()
        )
        
        # Add resistance metrics if provided
        if resistance_metrics:
            metrics.pitch_resistance = resistance_metrics.get('pitch_resistance', 0.0)
            metrics.tempo_resistance = resistance_metrics.get('tempo_resistance', 0.0)
            metrics.eq_resistance = resistance_metrics.get('eq_resistance', 0.0)
            metrics.noise_resistance = resistance_metrics.get('noise_resistance', 0.0)
        
        # Check industrial compliance
        metrics.industrial_compliant = self._check_industrial_compliance(metrics)
        
        # Update performance history
        self.performance_history.append(metrics)
        self.current_metrics = metrics
        
        # Update cumulative stats
        self._update_cumulative_stats(metrics)
        
        # Check for SLA violations
        if not metrics.industrial_compliant:
            self._handle_sla_violation(metrics, content_id)
        
        return metrics
    
    def record_search_performance(self,
                                search_time_ms: float,
                                index_size: int,
                                results_count: int,
                                query_id: str = None) -> PerformanceMetrics:
        """Record performance metrics for a search operation"""
        
        metrics = PerformanceMetrics(
            faiss_search_time_ms=search_time_ms,
            index_size=index_size,
            timestamp=datetime.now()
        )
        
        # Check search performance compliance
        search_compliant = search_time_ms <= self.sla.max_search_time_ms
        scale_compliant = index_size <= self.sla.max_index_size
        
        metrics.industrial_compliant = search_compliant and scale_compliant
        
        # Update stats
        self.cumulative_stats['total_searches'] += 1
        
        # Log performance
        if not search_compliant:
            logger.warning(f"Search SLA violation: {search_time_ms:.2f}ms > {self.sla.max_search_time_ms}ms")
        
        return metrics
    
    def _check_industrial_compliance(self, metrics: PerformanceMetrics) -> bool:
        """Check if metrics meet all industrial requirements"""
        
        # Processing time compliance
        processing_compliant = metrics.processing_time_ms <= self.sla.max_processing_time_ms
        
        # Precision compliance
        precision_compliant = metrics.precision_score >= self.sla.target_precision
        
        # Resistance compliance (if available)
        resistance_compliant = True
        if metrics.pitch_resistance > 0:
            resistance_compliant = (
                metrics.pitch_resistance >= self.sla.min_pitch_resistance and
                metrics.tempo_resistance >= self.sla.min_tempo_resistance and
                metrics.eq_resistance >= self.sla.min_eq_resistance and
                metrics.noise_resistance >= self.sla.min_noise_resistance
            )
        
        # Memory compliance
        memory_compliant = metrics.memory_usage_mb <= (self.sla.max_memory_usage_gb * 1024)
        
        return processing_compliant and precision_compliant and resistance_compliant and memory_compliant
    
    def _update_cumulative_stats(self, metrics: PerformanceMetrics):
        """Update cumulative statistics"""
        self.cumulative_stats['total_fingerprints'] += 1
        self.cumulative_stats['total_processing_time'] += metrics.processing_time_ms
        
        if not metrics.realtime_compliant:
            self.cumulative_stats['sla_violations'] += 1
        
        if not metrics.precision_validated:
            self.cumulative_stats['precision_failures'] += 1
    
    def _handle_sla_violation(self, metrics: PerformanceMetrics, content_id: str = None):
        """Handle SLA violation with alerting and logging"""
        violation_details = {
            'timestamp': metrics.timestamp.isoformat(),
            'content_id': content_id,
            'processing_time_ms': metrics.processing_time_ms,
            'precision_score': metrics.precision_score,
            'realtime_compliant': metrics.realtime_compliant,
            'precision_validated': metrics.precision_validated
        }
        
        logger.warning(f"Industrial SLA violation detected: {violation_details}")
        
        # Trigger alerts
        for callback in self.alert_callbacks:
            try:
                callback(violation_details)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current real-time performance statistics"""
        if not self.performance_history:
            return {}
        
        recent_metrics = list(self.performance_history)[-100:]  # Last 100 operations
        
        # Calculate real-time stats
        processing_times = [m.processing_time_ms for m in recent_metrics]
        precision_scores = [m.precision_score for m in recent_metrics if m.precision_score > 0]
        
        stats = {
            'current_performance': {
                'avg_processing_time_ms': np.mean(processing_times) if processing_times else 0.0,
                'max_processing_time_ms': np.max(processing_times) if processing_times else 0.0,
                'avg_precision_score': np.mean(precision_scores) if precision_scores else 0.0,
                'min_precision_score': np.min(precision_scores) if precision_scores else 0.0,
                'realtime_compliance_rate': sum(1 for m in recent_metrics if m.realtime_compliant) / len(recent_metrics),
                'precision_compliance_rate': sum(1 for m in recent_metrics if m.precision_validated) / len(recent_metrics)
            },
            'sla_compliance': {
                'processing_time_sla': all(m.realtime_compliant for m in recent_metrics[-10:]),  # Last 10
                'precision_sla': all(m.precision_validated for m in recent_metrics[-10:]),
                'overall_compliance': all(m.industrial_compliant for m in recent_metrics[-10:])
            },
            'throughput': {
                'total_fingerprints': self.cumulative_stats['total_fingerprints'],
                'total_searches': self.cumulative_stats['total_searches'],
                'sla_violations': self.cumulative_stats['sla_violations'],
                'error_rate': self.cumulative_stats['sla_violations'] / max(1, self.cumulative_stats['total_fingerprints'])
            }
        }
        
        return stats
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.performance_history:
            return {'error': 'No performance data available'}
        
        all_metrics = list(self.performance_history)
        
        # Processing performance analysis
        processing_times = [m.processing_time_ms for m in all_metrics]
        precision_scores = [m.precision_score for m in all_metrics if m.precision_score > 0]
        
        # Resistance analysis
        resistance_data = {
            'pitch': [m.pitch_resistance for m in all_metrics if m.pitch_resistance > 0],
            'tempo': [m.tempo_resistance for m in all_metrics if m.tempo_resistance > 0],
            'eq': [m.eq_resistance for m in all_metrics if m.eq_resistance > 0],
            'noise': [m.noise_resistance for m in all_metrics if m.noise_resistance > 0]
        }
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'monitoring_period': {
                'start_time': all_metrics[0].timestamp.isoformat() if all_metrics else None,
                'end_time': all_metrics[-1].timestamp.isoformat() if all_metrics else None,
                'total_operations': len(all_metrics)
            },
            'performance_summary': {
                'processing_time': {
                    'mean_ms': float(np.mean(processing_times)),
                    'median_ms': float(np.median(processing_times)),
                    'p95_ms': float(np.percentile(processing_times, 95)),
                    'p99_ms': float(np.percentile(processing_times, 99)),
                    'max_ms': float(np.max(processing_times)),
                    'sla_compliance_rate': sum(1 for t in processing_times if t <= self.sla.max_processing_time_ms) / len(processing_times)
                },
                'precision': {
                    'mean_score': float(np.mean(precision_scores)) if precision_scores else 0.0,
                    'median_score': float(np.median(precision_scores)) if precision_scores else 0.0,
                    'min_score': float(np.min(precision_scores)) if precision_scores else 0.0,
                    'sla_compliance_rate': sum(1 for p in precision_scores if p >= self.sla.target_precision) / len(precision_scores) if precision_scores else 0.0
                }
            },
            'resistance_analysis': {},
            'sla_compliance': {
                'overall_compliance_rate': sum(1 for m in all_metrics if m.industrial_compliant) / len(all_metrics),
                'total_violations': self.cumulative_stats['sla_violations'],
                'violation_rate': self.cumulative_stats['sla_violations'] / max(1, len(all_metrics)),
                'meets_industrial_requirements': self._evaluate_industrial_readiness()
            },
            'recommendations': self._generate_performance_recommendations()
        }
        
        # Add resistance analysis
        for resistance_type, values in resistance_data.items():
            if values:
                report['resistance_analysis'][resistance_type] = {
                    'mean_score': float(np.mean(values)),
                    'min_score': float(np.min(values)),
                    'compliance_rate': sum(1 for v in values if v >= getattr(self.sla, f'min_{resistance_type}_resistance')) / len(values)
                }
        
        return report
    
    def _evaluate_industrial_readiness(self) -> bool:
        """Evaluate if system is ready for industrial deployment"""
        if len(self.performance_history) < 100:  # Need sufficient data
            return False
        
        recent_metrics = list(self.performance_history)[-100:]
        
        # Check compliance rates
        realtime_compliance = sum(1 for m in recent_metrics if m.realtime_compliant) / len(recent_metrics)
        precision_compliance = sum(1 for m in recent_metrics if m.precision_validated) / len(recent_metrics)
        overall_compliance = sum(1 for m in recent_metrics if m.industrial_compliant) / len(recent_metrics)
        
        # Industrial readiness thresholds
        return (
            realtime_compliance >= 0.98 and  # 98% real-time compliance
            precision_compliance >= 0.99 and  # 99% precision compliance
            overall_compliance >= 0.95        # 95% overall compliance
        )
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if not self.performance_history:
            return ["Insufficient data for recommendations"]
        
        recent_metrics = list(self.performance_history)[-100:]
        
        # Processing time recommendations
        avg_processing_time = np.mean([m.processing_time_ms for m in recent_metrics])
        if avg_processing_time > self.sla.max_processing_time_ms * 0.8:  # 80% of SLA
            recommendations.append(
                f"Processing time averaging {avg_processing_time:.1f}ms is close to SLA limit. "
                "Consider optimizing feature extraction or using faster algorithms."
            )
        
        # Precision recommendations
        precision_scores = [m.precision_score for m in recent_metrics if m.precision_score > 0]
        if precision_scores:
            avg_precision = np.mean(precision_scores)
            if avg_precision < self.sla.target_precision * 1.001:  # Very close to limit
                recommendations.append(
                    f"Precision averaging {avg_precision:.4f} is close to requirement. "
                    "Consider enhancing ML models or feature extraction quality."
                )
        
        # SLA violation recommendations
        violation_rate = sum(1 for m in recent_metrics if not m.industrial_compliant) / len(recent_metrics)
        if violation_rate > 0.05:  # 5% violation rate
            recommendations.append(
                f"SLA violation rate {violation_rate:.1%} is high. "
                "Review system capacity and consider horizontal scaling."
            )
        
        if not recommendations:
            recommendations.append("System performance meets all industrial requirements. Continue monitoring.")
        
        return recommendations
    
    async def _continuous_monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Log periodic performance summary
                if datetime.now() - self.last_report_time > timedelta(minutes=5):
                    stats = self.get_real_time_stats()
                    if stats:
                        logger.info(f"Performance summary: "
                                  f"Avg processing: {stats['current_performance']['avg_processing_time_ms']:.1f}ms, "
                                  f"Avg precision: {stats['current_performance']['avg_precision_score']:.4f}, "
                                  f"Compliance: {stats['sla_compliance']['overall_compliance']}")
                    
                    self.last_report_time = datetime.now()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _sla_compliance_checker(self):
        """Background SLA compliance checker"""
        while self.monitoring_active:
            try:
                # Check for sustained SLA violations
                if len(self.performance_history) >= 10:
                    recent_metrics = list(self.performance_history)[-10:]
                    violation_count = sum(1 for m in recent_metrics if not m.industrial_compliant)
                    
                    if violation_count >= 5:  # 50% of recent operations failed
                        logger.critical("Sustained SLA violations detected - industrial compliance at risk")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"SLA compliance checker error: {e}")
                await asyncio.sleep(30)
    
    def add_alert_callback(self, callback):
        """Add callback function for SLA violation alerts"""
        self.alert_callbacks.append(callback)
    
    def export_performance_data(self, filepath: str):
        """Export performance data to file"""
        try:
            data = {
                'sla_requirements': {
                    'max_processing_time_ms': self.sla.max_processing_time_ms,
                    'target_precision': self.sla.target_precision,
                    'max_memory_usage_gb': self.sla.max_memory_usage_gb
                },
                'cumulative_stats': self.cumulative_stats,
                'performance_history': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'processing_time_ms': m.processing_time_ms,
                        'precision_score': m.precision_score,
                        'realtime_compliant': m.realtime_compliant,
                        'precision_validated': m.precision_validated,
                        'industrial_compliant': m.industrial_compliant
                    }
                    for m in self.performance_history
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Performance data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export performance data: {e}")

# Factory function for easy initialization
def create_industrial_monitor(custom_sla: Dict[str, Any] = None) -> IndustrialPerformanceMonitor:
    """Create industrial performance monitor with optional custom SLA"""
    sla = IndustrialSLARequirements()
    
    if custom_sla:
        for key, value in custom_sla.items():
            if hasattr(sla, key):
                setattr(sla, key, value)
    
    return IndustrialPerformanceMonitor(sla)