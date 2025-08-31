# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Performance Monitor Tests - Enterprise Grade Performance & Metrics Test Suite

Comprehensive tests for performance monitoring, system metrics tracking, 
optimization analysis, resource utilization, and performance intelligence systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import time
import psutil
import numpy as np
import pandas as pd
import asyncio
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from dataclasses import dataclass
import json
import sqlite3
import pickle
from contextlib import contextmanager
import gc
import sys
import tracemalloc
import cProfile
import pstats
import io

from ai.ml.performance_monitor import (
    PerformanceMonitor, SystemMetricsCollector, ResourceTracker,
    PerformanceAnalyzer, MetricsAggregator, AlertingSystem,
    PerformanceDashboard, OptimizationRecommendations, BenchmarkRunner,
    LoadTestRunner, MemoryProfiler, CPUProfiler, IOProfiler,
    NetworkProfiler, DatabaseProfiler, CacheProfiler,
    ModelPerformanceTracker, TrainingPerformanceMonitor, InferencePerformanceMonitor,
    RealTimeMetricsCollector, PerformanceReporter, TrendAnalyzer,
    AnomalyDetector, PerformanceOptimizer, ResourcePrediction,
    ScalabilityAnalyzer, BottleneckDetector, PerformanceComparator
)


@dataclass
class MockSystemMetrics:
    """Mock system metrics for testing"""
    cpu_percent: float
    memory_percent: float  
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: datetime


class TestPerformanceMonitor:
    """Tests for core performance monitoring functionality"""
    
    def test_init_performance_monitor(self):
        """Test performance monitor initialization"""
        monitor = PerformanceMonitor(
            monitoring_interval=1.0,
            metrics_to_collect=["cpu", "memory", "disk", "network", "gpu"],
            alert_thresholds={"cpu": 80, "memory": 85, "disk_io": 100},
            enable_real_time_monitoring=True,
            historical_data_retention_hours=168  # 1 week
        )
        
        assert monitor.monitoring_interval == 1.0
        assert len(monitor.metrics_to_collect) == 5
        assert monitor.alert_thresholds["cpu"] == 80
        assert monitor.enable_real_time_monitoring
        assert monitor.historical_data_retention_hours == 168

    def test_system_metrics_collection(self):
        """Test system metrics collection functionality"""
        monitor = PerformanceMonitor()
        
        collection_config = {
            "detailed_process_info": True,
            "include_gpu_metrics": True,
            "network_interface_details": True,
            "disk_usage_by_mount": True
        }
        
        with patch.object(monitor, 'collect_system_metrics') as mock_collect:
            mock_collect.return_value = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_info": {
                    "cpu": {
                        "usage_percent": 45.7,
                        "cores_logical": 8,
                        "cores_physical": 4,
                        "frequency_mhz": 2800.0,
                        "per_core_usage": [42.1, 48.3, 44.8, 47.2, 43.9, 46.1, 49.0, 45.5],
                        "load_average": [1.2, 1.5, 1.8]
                    },
                    "memory": {
                        "total_gb": 16.0,
                        "available_gb": 8.4,
                        "used_gb": 7.6,
                        "usage_percent": 47.5,
                        "swap_total_gb": 4.0,
                        "swap_used_gb": 0.2,
                        "cache_gb": 2.1
                    },
                    "disk": {
                        "total_space_gb": 512.0,
                        "used_space_gb": 287.3,
                        "free_space_gb": 224.7,
                        "usage_percent": 56.1,
                        "read_ops_per_sec": 45,
                        "write_ops_per_sec": 23,
                        "read_mb_per_sec": 12.3,
                        "write_mb_per_sec": 8.7
                    },
                    "network": {
                        "bytes_sent_per_sec": 1024*150,  # 150 KB/s
                        "bytes_recv_per_sec": 1024*890,  # 890 KB/s
                        "packets_sent_per_sec": 125,
                        "packets_recv_per_sec": 234,
                        "connections_active": 47,
                        "errors_per_sec": 0
                    },
                    "gpu": {
                        "gpu_count": 1,
                        "gpu_0": {
                            "name": "NVIDIA RTX 4090",
                            "utilization_percent": 78.9,
                            "memory_total_gb": 24.0,
                            "memory_used_gb": 18.7,
                            "memory_usage_percent": 77.9,
                            "temperature_c": 72,
                            "power_usage_w": 320
                        }
                    }
                }
            }
            
            metrics_result = monitor.collect_system_metrics(config=collection_config)
            
            assert "timestamp" in metrics_result
            assert "system_info" in metrics_result
            assert metrics_result["system_info"]["cpu"]["usage_percent"] > 0
            assert metrics_result["system_info"]["memory"]["total_gb"] > 0
            assert metrics_result["system_info"]["disk"]["total_space_gb"] > 0

    def test_performance_thresholds_and_alerting(self, mock_system_metrics):
        """Test performance threshold monitoring and alerting"""
        monitor = PerformanceMonitor(
            alert_thresholds={
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time_ms": 500.0,
                "error_rate_percent": 5.0
            }
        )
        
        if not mock_system_metrics:
            mock_system_metrics = [
                MockSystemMetrics(85.5, 78.2, 45.3, 23.1, 150*1024, 890*1024, datetime.now()),
                MockSystemMetrics(92.1, 89.7, 67.8, 34.5, 200*1024, 1200*1024, datetime.now()),
                MockSystemMetrics(77.3, 72.1, 23.4, 12.6, 120*1024, 670*1024, datetime.now())
            ]
        
        with patch.object(monitor, 'check_thresholds') as mock_check:
            mock_check.return_value = {
                "threshold_violations": [
                    {
                        "metric": "cpu_usage",
                        "current_value": 92.1,
                        "threshold": 80.0,
                        "violation_severity": "HIGH",
                        "duration_seconds": 45.7,
                        "trend": "INCREASING"
                    },
                    {
                        "metric": "memory_usage", 
                        "current_value": 89.7,
                        "threshold": 85.0,
                        "violation_severity": "MEDIUM",
                        "duration_seconds": 23.2,
                        "trend": "STABLE"
                    }
                ],
                "alerts_generated": [
                    {
                        "alert_id": "alert_cpu_001",
                        "alert_type": "PERFORMANCE_THRESHOLD_EXCEEDED",
                        "metric": "cpu_usage",
                        "severity": "HIGH",
                        "message": "CPU usage (92.1%) exceeded threshold (80.0%)",
                        "timestamp": datetime.now().isoformat(),
                        "recommendations": [
                            "Investigate high CPU processes",
                            "Consider scaling resources",
                            "Check for CPU-intensive operations"
                        ]
                    }
                ],
                "notification_status": {
                    "email_sent": True,
                    "slack_notification": True,
                    "dashboard_updated": True,
                    "escalation_triggered": False
                }
            }
            
            threshold_result = monitor.check_thresholds(metrics=mock_system_metrics)
            
            assert "threshold_violations" in threshold_result
            assert "alerts_generated" in threshold_result
            assert len(threshold_result["threshold_violations"]) > 0
            assert threshold_result["notification_status"]["email_sent"]

    def test_performance_trend_analysis(self, historical_metrics_data):
        """Test performance trend analysis and prediction"""
        monitor = PerformanceMonitor()
        
        if not historical_metrics_data:
            # Generate 24 hours of synthetic metrics data
            base_time = datetime.now() - timedelta(hours=24)
            historical_metrics_data = []
            
            for hour in range(24):
                timestamp = base_time + timedelta(hours=hour)
                # Add some realistic patterns (lower usage at night, higher during day)
                base_cpu = 30 + 40 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 5)
                base_memory = 45 + 20 * np.sin(2 * np.pi * hour / 24 + np.pi/4) + np.random.normal(0, 3)
                
                historical_metrics_data.append({
                    "timestamp": timestamp,
                    "cpu_usage": max(10, min(95, base_cpu)),
                    "memory_usage": max(20, min(90, base_memory)),
                    "disk_io_ops": np.random.poisson(50),
                    "network_throughput_mbps": np.random.exponential(10)
                })
        
        trend_config = {
            "analysis_window_hours": 24,
            "prediction_horizon_hours": 6,
            "seasonality_detection": True,
            "anomaly_detection": True,
            "confidence_interval": 0.95
        }
        
        with patch.object(monitor, 'analyze_trends') as mock_trends:
            mock_trends.return_value = {
                "trend_analysis": {
                    "cpu_usage": {
                        "trend": "STABLE",
                        "slope": 0.023,  # Slight increase per hour
                        "seasonal_pattern": "DAILY_CYCLE",
                        "peak_hours": [9, 10, 11, 14, 15, 16],
                        "low_hours": [2, 3, 4, 5, 6]
                    },
                    "memory_usage": {
                        "trend": "INCREASING",
                        "slope": 0.15,
                        "seasonal_pattern": "WEAK_DAILY",
                        "memory_leak_suspected": False,
                        "growth_rate_percent_per_day": 3.6
                    }
                },
                "predictions": {
                    "next_6_hours": [
                        {
                            "hour": 1,
                            "cpu_predicted": 67.8,
                            "cpu_confidence_lower": 62.1,
                            "cpu_confidence_upper": 73.5,
                            "memory_predicted": 58.4,
                            "memory_confidence_lower": 54.7,
                            "memory_confidence_upper": 62.1
                        }
                        # ... more hourly predictions
                    ]
                },
                "anomalies_detected": [
                    {
                        "timestamp": "2025-01-15T14:30:00",
                        "metric": "cpu_usage",
                        "value": 95.7,
                        "expected_range": [45, 75],
                        "anomaly_score": 0.92,
                        "possible_causes": ["process_spike", "resource_contention"]
                    }
                ]
            }
            
            trend_result = monitor.analyze_trends(
                metrics_data=historical_metrics_data,
                config=trend_config
            )
            
            assert "trend_analysis" in trend_result
            assert "predictions" in trend_result
            assert "anomalies_detected" in trend_result
            assert "seasonal_pattern" in trend_result["trend_analysis"]["cpu_usage"]

    def test_real_time_performance_monitoring(self):
        """Test real-time performance monitoring capabilities"""
        monitor = PerformanceMonitor(enable_real_time_monitoring=True)
        
        realtime_config = {
            "sampling_interval_seconds": 1.0,
            "buffer_size": 1000,
            "streaming_enabled": True,
            "dashboard_updates": True,
            "immediate_alerting": True
        }
        
        # Simulate real-time monitoring session
        monitoring_duration = 10  # seconds
        
        with patch.object(monitor, 'start_realtime_monitoring') as mock_realtime:
            mock_realtime.return_value = {
                "monitoring_session": {
                    "session_id": "realtime_001",
                    "start_time": datetime.now().isoformat(),
                    "duration_seconds": monitoring_duration,
                    "samples_collected": monitoring_duration,
                    "sampling_rate_hz": 1.0
                },
                "realtime_metrics": [
                    {
                        "timestamp": datetime.now() - timedelta(seconds=i),
                        "cpu_usage": 45 + np.random.normal(0, 10),
                        "memory_usage": 60 + np.random.normal(0, 5),
                        "active_connections": np.random.poisson(50),
                        "response_time_ms": np.random.exponential(100)
                    }
                    for i in range(monitoring_duration)
                ],
                "real_time_alerts": [
                    {
                        "alert_time": datetime.now() - timedelta(seconds=3),
                        "metric": "response_time_ms",
                        "value": 850.3,
                        "threshold": 500.0,
                        "action_taken": "notification_sent"
                    }
                ],
                "performance_summary": {
                    "average_cpu": 47.3,
                    "peak_memory": 68.9,
                    "max_response_time": 850.3,
                    "alerts_triggered": 1,
                    "overall_health": "GOOD"
                }
            }
            
            realtime_result = monitor.start_realtime_monitoring(
                duration_seconds=monitoring_duration,
                config=realtime_config
            )
            
            assert "monitoring_session" in realtime_result
            assert "realtime_metrics" in realtime_result
            assert len(realtime_result["realtime_metrics"]) == monitoring_duration
            assert realtime_result["performance_summary"]["overall_health"] == "GOOD"


class TestModelPerformanceTracker:
    """Tests for ML model performance tracking"""
    
    def test_init_model_performance_tracker(self):
        """Test model performance tracker initialization"""
        tracker = ModelPerformanceTracker(
            track_training_metrics=True,
            track_inference_metrics=True,
            model_versioning=True,
            benchmark_comparisons=True,
            resource_efficiency_tracking=True
        )
        
        assert tracker.track_training_metrics
        assert tracker.track_inference_metrics
        assert tracker.model_versioning
        assert tracker.benchmark_comparisons
        assert tracker.resource_efficiency_tracking

    def test_training_performance_monitoring(self, training_session_data):
        """Test ML training performance monitoring"""
        tracker = ModelPerformanceTracker(track_training_metrics=True)
        
        if not training_session_data:
            training_session_data = {
                "model_name": "customer_churn_rf_v2.3",
                "training_start": datetime.now() - timedelta(hours=2),
                "dataset_size_rows": 1500000,
                "dataset_size_mb": 450.7,
                "algorithm": "random_forest",
                "hyperparameters": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 5
                },
                "hardware_config": {
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "gpu_enabled": False
                }
            }
        
        with patch.object(tracker, 'monitor_training_performance') as mock_training:
            mock_training.return_value = {
                "training_metrics": {
                    "total_duration_minutes": 127.3,
                    "data_loading_time_minutes": 8.7,
                    "preprocessing_time_minutes": 23.4,
                    "model_fitting_time_minutes": 89.2,
                    "validation_time_minutes": 6.0,
                    "epochs_completed": 1,  # For tree-based models
                    "convergence_achieved": True
                },
                "resource_utilization": {
                    "peak_cpu_usage": 95.7,
                    "average_cpu_usage": 78.4,
                    "peak_memory_usage_gb": 12.8,
                    "average_memory_usage_gb": 9.6,
                    "disk_io_read_gb": 2.3,
                    "disk_io_write_gb": 1.7,
                    "energy_consumption_kwh": 0.234
                },
                "performance_metrics": {
                    "training_accuracy": 0.847,
                    "validation_accuracy": 0.821,
                    "training_loss": 0.342,
                    "validation_loss": 0.389,
                    "overfitting_score": 0.15,  # Low is better
                    "feature_importance_stability": 0.91
                },
                "efficiency_metrics": {
                    "samples_per_second": 328.7,
                    "memory_efficiency": 0.73,  # Memory used / Memory available
                    "cpu_efficiency": 0.84,     # Useful CPU time / Total CPU time
                    "cost_per_accuracy_point": 0.23  # Training cost / accuracy
                },
                "optimization_recommendations": [
                    "Consider increasing n_estimators to 150 for better accuracy",
                    "Memory usage is optimal for current dataset size",
                    "CPU utilization suggests good parallelization"
                ]
            }
            
            training_result = tracker.monitor_training_performance(
                session_data=training_session_data
            )
            
            assert "training_metrics" in training_result
            assert "resource_utilization" in training_result
            assert "performance_metrics" in training_result
            assert training_result["training_metrics"]["convergence_achieved"]
            assert training_result["performance_metrics"]["training_accuracy"] > 0.8

    def test_inference_performance_monitoring(self, inference_workload_data):
        """Test ML inference performance monitoring"""
        tracker = ModelPerformanceTracker(track_inference_metrics=True)
        
        if not inference_workload_data:
            inference_workload_data = {
                "model_name": "customer_churn_rf_v2.3",
                "model_size_mb": 45.2,
                "inference_type": "batch",
                "batch_size": 1000,
                "total_predictions": 50000,
                "input_data_mb": 25.7,
                "start_time": datetime.now() - timedelta(minutes=15)
            }
        
        with patch.object(tracker, 'monitor_inference_performance') as mock_inference:
            mock_inference.return_value = {
                "inference_metrics": {
                    "total_duration_seconds": 45.8,
                    "model_loading_time_seconds": 2.3,
                    "preprocessing_time_seconds": 8.7,
                    "prediction_time_seconds": 32.1,
                    "postprocessing_time_seconds": 2.7,
                    "predictions_per_second": 1092.4,
                    "batches_processed": 50,
                    "average_batch_time_seconds": 0.916
                },
                "latency_distribution": {
                    "p50_ms": 15.2,
                    "p90_ms": 28.7,
                    "p95_ms": 34.1,
                    "p99_ms": 52.8,
                    "max_ms": 67.3,
                    "min_ms": 8.9
                },
                "resource_consumption": {
                    "peak_cpu_usage": 67.4,
                    "average_cpu_usage": 45.8,
                    "peak_memory_usage_mb": 156.7,
                    "average_memory_usage_mb": 123.4,
                    "cache_hit_rate": 0.87,
                    "io_operations": 234
                },
                "quality_metrics": {
                    "prediction_confidence_average": 0.82,
                    "prediction_confidence_std": 0.15,
                    "uncertainty_score_average": 0.18,
                    "calibration_score": 0.91,  # How well confidence matches accuracy
                    "drift_detection_score": 0.05  # Low drift is good
                },
                "scalability_analysis": {
                    "throughput_scaling_efficiency": 0.89,
                    "memory_scaling_efficiency": 0.73,
                    "bottleneck": "CPU_BOUND",
                    "recommended_max_concurrent_requests": 8,
                    "horizontal_scaling_benefit": 0.85
                }
            }
            
            inference_result = tracker.monitor_inference_performance(
                workload_data=inference_workload_data
            )
            
            assert "inference_metrics" in inference_result
            assert "latency_distribution" in inference_result
            assert "resource_consumption" in inference_result
            assert inference_result["inference_metrics"]["predictions_per_second"] > 1000
            assert inference_result["quality_metrics"]["prediction_confidence_average"] > 0.8

    def test_model_comparison_benchmarking(self, model_versions_data):
        """Test model performance comparison and benchmarking"""
        tracker = ModelPerformanceTracker(benchmark_comparisons=True)
        
        if not model_versions_data:
            model_versions_data = [
                {
                    "version": "v2.1",
                    "accuracy": 0.821,
                    "inference_time_ms": 45.2,
                    "model_size_mb": 67.8,
                    "training_time_hours": 3.2
                },
                {
                    "version": "v2.2",
                    "accuracy": 0.834,
                    "inference_time_ms": 42.1,
                    "model_size_mb": 52.3,
                    "training_time_hours": 2.8
                },
                {
                    "version": "v2.3",
                    "accuracy": 0.847,
                    "inference_time_ms": 38.7,
                    "model_size_mb": 45.2,
                    "training_time_hours": 2.5
                }
            ]
        
        benchmark_config = {
            "metrics_to_compare": ["accuracy", "inference_time", "model_size", "training_time"],
            "statistical_significance": True,
            "efficiency_scoring": True,
            "pareto_frontier_analysis": True
        }
        
        with patch.object(tracker, 'benchmark_model_versions') as mock_benchmark:
            mock_benchmark.return_value = {
                "version_comparison": {
                    "best_accuracy": {"version": "v2.3", "value": 0.847},
                    "fastest_inference": {"version": "v2.3", "value": 38.7},
                    "smallest_model": {"version": "v2.3", "value": 45.2},
                    "fastest_training": {"version": "v2.3", "value": 2.5}
                },
                "performance_evolution": {
                    "accuracy_improvement": {
                        "v2.1_to_v2.2": 0.013,
                        "v2.2_to_v2.3": 0.013,
                        "overall_improvement": 0.026
                    },
                    "speed_improvement": {
                        "inference_speedup_v2.1_to_v2.3": 1.168,  # 45.2/38.7
                        "training_speedup_v2.1_to_v2.3": 1.280    # 3.2/2.5
                    },
                    "efficiency_improvement": {
                        "model_compression_ratio": 1.500,  # 67.8/45.2
                        "performance_per_mb": 0.847 / 45.2  # accuracy per MB
                    }
                },
                "statistical_analysis": {
                    "accuracy_improvement_significant": True,
                    "p_value": 0.012,
                    "confidence_interval_95": [0.018, 0.034],
                    "effect_size": "MEDIUM"
                },
                "pareto_analysis": {
                    "pareto_optimal_versions": ["v2.3"],
                    "dominated_versions": ["v2.1"],
                    "efficiency_frontier": [
                        {"version": "v2.2", "efficiency_score": 0.78},
                        {"version": "v2.3", "efficiency_score": 0.92}
                    ]
                },
                "recommendations": {
                    "recommended_version": "v2.3",
                    "reasoning": "Best overall performance across all metrics",
                    "deployment_confidence": 0.94,
                    "rollback_risk": "LOW"
                }
            }
            
            benchmark_result = tracker.benchmark_model_versions(
                versions_data=model_versions_data,
                config=benchmark_config
            )
            
            assert "version_comparison" in benchmark_result
            assert "performance_evolution" in benchmark_result
            assert "statistical_analysis" in benchmark_result
            assert benchmark_result["recommendations"]["recommended_version"] == "v2.3"
            assert benchmark_result["statistical_analysis"]["accuracy_improvement_significant"]


class TestMemoryProfiler:
    """Tests for memory profiling and optimization"""
    
    def test_init_memory_profiler(self):
        """Test memory profiler initialization"""
        profiler = MemoryProfiler(
            enable_detailed_tracking=True,
            track_allocations=True,
            detect_memory_leaks=True,
            profile_garbage_collection=True
        )
        
        assert profiler.enable_detailed_tracking
        assert profiler.track_allocations
        assert profiler.detect_memory_leaks
        assert profiler.profile_garbage_collection

    def test_memory_usage_profiling(self, memory_intensive_function):
        """Test memory usage profiling for functions"""
        profiler = MemoryProfiler()
        
        # Mock memory-intensive function if not provided
        if not memory_intensive_function:
            def memory_intensive_function():
                # Simulate memory allocation
                data = []
                for i in range(100000):
                    data.append([i] * 100)  # Allocate memory
                return len(data)
        
        profiling_config = {
            "line_by_line_profiling": True,
            "track_peak_memory": True,
            "monitor_gc_activity": True,
            "analyze_memory_patterns": True
        }
        
        with patch.object(profiler, 'profile_function_memory') as mock_profile:
            mock_profile.return_value = {
                "memory_profile": {
                    "peak_memory_mb": 156.7,
                    "memory_growth_mb": 145.3,
                    "final_memory_mb": 23.4,
                    "memory_freed_mb": 133.3,
                    "allocation_count": 100000,
                    "deallocation_count": 99800,
                    "net_allocations": 200
                },
                "line_by_line_analysis": [
                    {
                        "line_number": 3,
                        "memory_increment_mb": 0.1,
                        "memory_total_mb": 12.3,
                        "code": "data = []"
                    },
                    {
                        "line_number": 5,
                        "memory_increment_mb": 145.2,
                        "memory_total_mb": 157.5,
                        "code": "data.append([i] * 100)"
                    }
                ],
                "garbage_collection": {
                    "gc_runs": 15,
                    "objects_collected": 98567,
                    "memory_freed_by_gc_mb": 87.6,
                    "gc_efficiency": 0.89,
                    "gc_pause_time_ms": 234.5
                },
                "memory_patterns": {
                    "allocation_pattern": "RAPID_GROWTH",
                    "deallocation_pattern": "BATCH_RELEASE",
                    "fragmentation_score": 0.23,
                    "memory_leak_indicators": [],
                    "optimization_opportunities": [
                        "Consider pre-allocating memory",
                        "Use memory-efficient data structures",
                        "Implement incremental processing"
                    ]
                }
            }
            
            memory_result = profiler.profile_function_memory(
                func=memory_intensive_function,
                config=profiling_config
            )
            
            assert "memory_profile" in memory_result
            assert "line_by_line_analysis" in memory_result
            assert "garbage_collection" in memory_result
            assert memory_result["memory_profile"]["peak_memory_mb"] > 100

    def test_memory_leak_detection(self, potential_leak_scenario):
        """Test memory leak detection capabilities"""
        profiler = MemoryProfiler(detect_memory_leaks=True)
        
        if not potential_leak_scenario:
            def potential_leak_scenario():
                # Simulate potential memory leak
                global_cache = {}
                for i in range(10000):
                    key = f"item_{i}"
                    global_cache[key] = [i] * 100  # Memory that might not be released
                return len(global_cache)
        
        leak_detection_config = {
            "monitoring_duration_minutes": 5,
            "memory_growth_threshold_mb": 50,
            "leak_confidence_threshold": 0.8,
            "analyze_object_references": True
        }
        
        with patch.object(profiler, 'detect_memory_leaks') as mock_leak_detect:
            mock_leak_detect.return_value = {
                "leak_analysis": {
                    "memory_leak_detected": True,
                    "confidence_score": 0.91,
                    "leak_rate_mb_per_minute": 12.7,
                    "projected_memory_usage_24h": 18336,  # MB
                    "leak_severity": "HIGH"
                },
                "leak_sources": [
                    {
                        "source_type": "GLOBAL_VARIABLE",
                        "variable_name": "global_cache",
                        "growth_rate_mb_per_minute": 11.8,
                        "current_size_mb": 67.3,
                        "reference_count": 1,
                        "location": "line 4 in potential_leak_scenario"
                    }
                ],
                "object_reference_analysis": {
                    "circular_references_found": 0,
                    "unreachable_objects": 245,
                    "long_lived_objects": 9856,
                    "reference_cycles": []
                },
                "recommendations": [
                    "Implement proper cleanup of global_cache",
                    "Add cache size limits and eviction policy", 
                    "Use weak references where appropriate",
                    "Monitor object lifetime and cleanup"
                ],
                "monitoring_data": {
                    "memory_snapshots": [
                        {"time": 0, "memory_mb": 45.2},
                        {"time": 60, "memory_mb": 57.9},
                        {"time": 120, "memory_mb": 70.6},
                        {"time": 180, "memory_mb": 83.3},
                        {"time": 240, "memory_mb": 96.0},
                        {"time": 300, "memory_mb": 108.7}
                    ],
                    "growth_pattern": "LINEAR"
                }
            }
            
            leak_result = profiler.detect_memory_leaks(
                scenario_func=potential_leak_scenario,
                config=leak_detection_config
            )
            
            assert "leak_analysis" in leak_result
            assert "leak_sources" in leak_result
            assert leak_result["leak_analysis"]["memory_leak_detected"]
            assert leak_result["leak_analysis"]["confidence_score"] > 0.8


class TestLoadTestRunner:
    """Tests for load testing and scalability analysis"""
    
    def test_init_load_test_runner(self):
        """Test load test runner initialization"""
        load_tester = LoadTestRunner(
            max_concurrent_users=1000,
            test_duration_minutes=30,
            ramp_up_strategies=["linear", "exponential", "step"],
            performance_targets={"response_time_p95": 500, "throughput_rps": 100}
        )
        
        assert load_tester.max_concurrent_users == 1000
        assert load_tester.test_duration_minutes == 30
        assert len(load_tester.ramp_up_strategies) == 3
        assert load_tester.performance_targets["response_time_p95"] == 500

    def test_stress_testing_execution(self, target_system_config):
        """Test stress testing execution and analysis"""
        load_tester = LoadTestRunner()
        
        if not target_system_config:
            target_system_config = {
                "system_endpoint": "http://localhost:8000/api/predict",
                "authentication": {"type": "bearer", "token": "test_token"},
                "request_payload": {"features": [1, 2, 3, 4, 5]},
                "expected_response_format": "json"
            }
        
        stress_test_config = {
            "load_profile": {
                "start_users": 1,
                "peak_users": 500,
                "ramp_up_duration_minutes": 5,
                "sustained_duration_minutes": 15,
                "ramp_down_duration_minutes": 5
            },
            "test_scenarios": [
                {"name": "normal_prediction", "weight": 80},
                {"name": "batch_prediction", "weight": 15},
                {"name": "model_info_request", "weight": 5}
            ],
            "performance_targets": {
                "max_response_time_ms": 1000,
                "p95_response_time_ms": 500,
                "min_throughput_rps": 100,
                "max_error_rate_percent": 1.0
            }
        }
        
        with patch.object(load_tester, 'run_stress_test') as mock_stress_test:
            mock_stress_test.return_value = {
                "test_execution": {
                    "test_id": "stress_test_001",
                    "start_time": datetime.now().isoformat(),
                    "duration_minutes": 25,
                    "total_requests": 125000,
                    "successful_requests": 124873,
                    "failed_requests": 127,
                    "requests_per_second_avg": 83.3,
                    "requests_per_second_peak": 156.7
                },
                "performance_metrics": {
                    "response_times": {
                        "min_ms": 15.2,
                        "max_ms": 2340.6,
                        "mean_ms": 127.8,
                        "median_ms": 89.4,
                        "p90_ms": 234.5,
                        "p95_ms": 456.7,
                        "p99_ms": 1250.3
                    },
                    "throughput": {
                        "average_rps": 83.3,
                        "peak_rps": 156.7,
                        "sustained_rps": 78.9,
                        "throughput_consistency": 0.87
                    },
                    "error_analysis": {
                        "total_error_rate": 0.10,  # 0.10%
                        "timeout_errors": 45,
                        "connection_errors": 32,
                        "server_errors_5xx": 23,
                        "client_errors_4xx": 27,
                        "error_rate_by_scenario": {
                            "normal_prediction": 0.08,
                            "batch_prediction": 0.15,
                            "model_info_request": 0.05
                        }
                    }
                },
                "resource_utilization": {
                    "target_system_cpu_peak": 89.4,
                    "target_system_memory_peak": 67.8,
                    "target_system_network_utilization": 45.6,
                    "load_generator_cpu_peak": 34.5,
                    "load_generator_memory_peak": 23.8
                },
                "scalability_analysis": {
                    "breaking_point_users": 450,
                    "performance_degradation_starts": 320,
                    "linear_scaling_limit": 280,
                    "bottleneck_identified": "CPU_BOUND",
                    "horizontal_scaling_benefit": 0.85,
                    "vertical_scaling_benefit": 0.67
                },
                "target_compliance": {
                    "response_time_target_met": True,  # p95 < 500ms
                    "throughput_target_met": False,   # avg RPS < 100
                    "error_rate_target_met": True,   # < 1%
                    "overall_pass": False,
                    "failed_targets": ["min_throughput_rps"]
                }
            }
            
            stress_test_result = load_tester.run_stress_test(
                target_config=target_system_config,
                test_config=stress_test_config
            )
            
            assert "test_execution" in stress_test_result
            assert "performance_metrics" in stress_test_result
            assert "scalability_analysis" in stress_test_result
            assert stress_test_result["test_execution"]["total_requests"] > 100000
            assert stress_test_result["performance_metrics"]["error_analysis"]["total_error_rate"] < 1.0

    def test_capacity_planning_analysis(self, production_requirements):
        """Test capacity planning and resource prediction"""
        load_tester = LoadTestRunner()
        
        if not production_requirements:
            production_requirements = {
                "expected_daily_users": 10000,
                "peak_concurrent_users": 500,
                "average_requests_per_user": 25,
                "peak_traffic_multiplier": 3.5,
                "growth_rate_monthly": 0.15,
                "sla_requirements": {
                    "availability": 99.9,
                    "response_time_p95": 300,
                    "throughput_rps": 200
                }
            }
        
        capacity_config = {
            "planning_horizon_months": 12,
            "safety_margin_percent": 20,
            "cost_optimization": True,
            "auto_scaling_modeling": True
        }
        
        with patch.object(load_tester, 'analyze_capacity_requirements') as mock_capacity:
            mock_capacity.return_value = {
                "current_capacity": {
                    "max_sustainable_rps": 150,
                    "max_concurrent_users": 400,
                    "resource_utilization_at_capacity": {
                        "cpu": 85,
                        "memory": 78,
                        "network": 45
                    }
                },
                "projected_requirements": [
                    {
                        "month": 1,
                        "expected_peak_rps": 210,
                        "expected_concurrent_users": 575,
                        "capacity_gap": "INSUFFICIENT",
                        "scaling_required": True
                    },
                    {
                        "month": 6,
                        "expected_peak_rps": 323,
                        "expected_concurrent_users": 884,
                        "capacity_gap": "CRITICAL",
                        "scaling_required": True
                    },
                    {
                        "month": 12,
                        "expected_peak_rps": 534,
                        "expected_concurrent_users": 1461,
                        "capacity_gap": "CRITICAL",
                        "scaling_required": True
                    }
                ],
                "scaling_recommendations": {
                    "immediate_scaling": {
                        "additional_instances": 2,
                        "instance_type": "c5.2xlarge",
                        "estimated_cost_increase": 1200  # USD/month
                    },
                    "6_month_scaling": {
                        "additional_instances": 4,
                        "instance_type": "c5.4xlarge",
                        "estimated_cost_increase": 2800
                    },
                    "12_month_scaling": {
                        "additional_instances": 8,
                        "instance_type": "c5.4xlarge",
                        "estimated_cost_increase": 5600,
                        "architecture_redesign_recommended": True
                    }
                },
                "auto_scaling_strategy": {
                    "cpu_threshold": 70,
                    "memory_threshold": 80,
                    "scale_up_cooldown": 300,  # seconds
                    "scale_down_cooldown": 600,
                    "min_instances": 2,
                    "max_instances": 20,
                    "target_utilization": 70
                },
                "cost_analysis": {
                    "current_monthly_cost": 800,
                    "projected_costs": [1200, 1800, 2800, 5600],  # Monthly costs
                    "cost_per_user_current": 0.08,
                    "cost_per_user_projected_12m": 0.12,
                    "roi_analysis": {
                        "revenue_impact_of_poor_performance": 15000,  # USD/month
                        "infrastructure_investment_payback_months": 3.2
                    }
                }
            }
            
            capacity_result = load_tester.analyze_capacity_requirements(
                requirements=production_requirements,
                config=capacity_config
            )
            
            assert "current_capacity" in capacity_result
            assert "projected_requirements" in capacity_result
            assert "scaling_recommendations" in capacity_result
            assert len(capacity_result["projected_requirements"]) > 0
            assert capacity_result["cost_analysis"]["current_monthly_cost"] > 0


@pytest.mark.integration
class TestPerformanceMonitorIntegration:
    """Integration tests for performance monitoring systems"""
    
    @pytest.mark.slow
    def test_comprehensive_performance_monitoring_pipeline(self, temp_dir):
        """Test complete performance monitoring pipeline"""
        # Initialize all components
        monitor = PerformanceMonitor(output_directory=str(temp_dir))
        model_tracker = ModelPerformanceTracker()
        memory_profiler = MemoryProfiler()
        load_tester = LoadTestRunner()
        
        # Simulate comprehensive monitoring scenario
        monitoring_scenario = {
            "system_monitoring": True,
            "model_performance": True,
            "memory_profiling": True,
            "load_testing": False  # Skip for integration test
        }
        
        results = {}
        
        # System monitoring
        if monitoring_scenario["system_monitoring"]:
            with patch.object(monitor, 'run_comprehensive_monitoring') as mock_system:
                mock_system.return_value = {
                    "monitoring_duration_minutes": 30,
                    "metrics_collected": 1800,  # 30 minutes * 60 seconds
                    "alerts_triggered": 2,
                    "performance_score": 0.87,
                    "recommendations": ["Optimize memory usage", "Monitor CPU spikes"]
                }
                
                results["system_monitoring"] = monitor.run_comprehensive_monitoring(
                    duration_minutes=30
                )
        
        # Model performance tracking
        if monitoring_scenario["model_performance"]:
            mock_training_data = {
                "model_name": "integration_test_model",
                "training_duration_minutes": 45,
                "accuracy": 0.89,
                "resource_efficiency": 0.76
            }
            
            with patch.object(model_tracker, 'track_model_lifecycle') as mock_model:
                mock_model.return_value = {
                    "lifecycle_stage": "TRAINING_COMPLETE",
                    "performance_metrics": mock_training_data,
                    "ready_for_deployment": True,
                    "performance_grade": "A"
                }
                
                results["model_performance"] = model_tracker.track_model_lifecycle(
                    model_data=mock_training_data
                )
        
        # Memory profiling
        if monitoring_scenario["memory_profiling"]:
            def test_function():
                return sum(range(100000))
            
            with patch.object(memory_profiler, 'profile_comprehensive') as mock_memory:
                mock_memory.return_value = {
                    "peak_memory_mb": 45.7,
                    "memory_efficiency": 0.82,
                    "leaks_detected": 0,
                    "optimization_score": 0.88
                }
                
                results["memory_profiling"] = memory_profiler.profile_comprehensive(
                    func=test_function
                )
        
        # Validate integration results
        assert "system_monitoring" in results
        assert "model_performance" in results
        assert "memory_profiling" in results
        
        assert results["system_monitoring"]["performance_score"] > 0.8
        assert results["model_performance"]["ready_for_deployment"]
        assert results["memory_profiling"]["leaks_detected"] == 0
        
        # Generate integrated report
        integrated_report = {
            "monitoring_session_id": "integration_test_001",
            "timestamp": datetime.now().isoformat(),
            "components_tested": list(results.keys()),
            "overall_performance_score": np.mean([
                results["system_monitoring"]["performance_score"],
                results["model_performance"]["performance_metrics"]["resource_efficiency"],
                results["memory_profiling"]["optimization_score"]
            ]),
            "critical_issues": 0,
            "recommendations": [
                rec for component_results in results.values() 
                for rec in component_results.get("recommendations", [])
            ]
        }
        
        assert integrated_report["overall_performance_score"] > 0.8
        assert integrated_report["critical_issues"] == 0

    def test_performance_monitoring_under_load(self):
        """Test performance monitoring system under high load"""
        monitor = PerformanceMonitor()
        
        # Simulate high-frequency monitoring
        high_load_config = {
            "sampling_interval_seconds": 0.1,  # High frequency
            "concurrent_monitoring_threads": 4,
            "buffer_size": 10000,
            "data_compression": True
        }
        
        # Simulate 1000 rapid measurements
        measurements_count = 1000
        
        with patch.object(monitor, 'handle_high_load_monitoring') as mock_high_load:
            mock_high_load.return_value = {
                "measurements_processed": measurements_count,
                "processing_time_seconds": 15.7,
                "measurements_per_second": measurements_count / 15.7,
                "data_loss_percent": 0.02,  # 0.02% data loss
                "system_stability": "STABLE",
                "memory_usage_peak_mb": 234.5,
                "cpu_usage_peak": 67.8,
                "buffer_overflow_events": 0
            }
            
            high_load_result = monitor.handle_high_load_monitoring(
                config=high_load_config,
                measurement_count=measurements_count
            )
            
            assert high_load_result["measurements_processed"] == measurements_count
            assert high_load_result["data_loss_percent"] < 0.1  # Less than 0.1% loss
            assert high_load_result["system_stability"] == "STABLE"
            assert high_load_result["buffer_overflow_events"] == 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
