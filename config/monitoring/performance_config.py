"""
Performance Monitoring Configuration Module for IA-Influencer Agent Platform
=============================================================================

Professional performance monitoring configuration for comprehensive
system performance tracking, profiling, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PerformanceMetricType(Enum):
    """Performance metric types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"


class ProfilingMode(Enum):
    """Profiling modes"""
    DISABLED = "disabled"
    SAMPLING = "sampling"
    CONTINUOUS = "continuous"
    ON_DEMAND = "on_demand"


class AlertSeverity(Enum):
    """Performance alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    name: str
    metric: str
    operator: str  # >, <, >=, <=, ==
    value: float
    severity: AlertSeverity
    duration: str = "5m"
    description: Optional[str] = None


@dataclass
class ProfilingConfig:
    """Profiling configuration"""
    enabled: bool
    mode: ProfilingMode
    sampling_rate: float = 0.01
    profile_duration: int = 300  # seconds
    max_profiles: int = 100
    output_format: str = "pprof"
    include_stack_traces: bool = True


class PerformanceMonitoringConfig:
    """Professional performance monitoring configuration for IA-Influencer platform"""
    
    def __init__(self):
        self.monitoring_enabled = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
        self.profiling_enabled = os.getenv("PROFILING_ENABLED", "false").lower() == "true"
        self.metrics_collection_interval = int(os.getenv("PERF_METRICS_INTERVAL", "30"))
        self.profiling_sampling_rate = float(os.getenv("PROFILING_SAMPLING_RATE", "0.01"))
        self.alert_thresholds_enabled = os.getenv("PERF_ALERTS_ENABLED", "true").lower() == "true"
        self.performance_data_retention = int(os.getenv("PERF_DATA_RETENTION_DAYS", "90"))
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.service_name = os.getenv("SERVICE_NAME", "ia-influencer-agent")
    
    def get_system_performance_config(self) -> Dict[str, Any]:
        """Get system-level performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "collection_interval": self.metrics_collection_interval,
            "metrics": {
                "cpu_usage": {
                    "enabled": True,
                    "granularity": "per_core",
                    "include_load_average": True,
                    "alert_threshold": 80.0
                },
                "memory_usage": {
                    "enabled": True,
                    "include_swap": True,
                    "include_cache": True,
                    "alert_threshold": 85.0
                },
                "disk_io": {
                    "enabled": True,
                    "include_read_write": True,
                    "include_iops": True,
                    "alert_threshold_utilization": 90.0
                },
                "network_io": {
                    "enabled": True,
                    "include_packets": True,
                    "include_errors": True,
                    "bandwidth_threshold_mbps": 1000
                },
                "file_descriptors": {
                    "enabled": True,
                    "alert_threshold_percent": 80.0
                }
            },
            "system_limits": {
                "max_open_files": 65536,
                "max_processes": 32768,
                "max_memory_mb": 32768
            }
        }
    
    def get_application_performance_config(self) -> Dict[str, Any]:
        """Get application-level performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "metrics": {
                "request_latency": {
                    "enabled": True,
                    "percentiles": [50, 75, 90, 95, 99, 99.9],
                    "buckets": [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
                    "p95_threshold_seconds": 2.0,
                    "p99_threshold_seconds": 5.0
                },
                "throughput": {
                    "enabled": True,
                    "measure_rps": True,
                    "measure_concurrent_requests": True,
                    "min_rps_threshold": 10,
                    "max_concurrent_threshold": 1000
                },
                "error_rates": {
                    "enabled": True,
                    "track_by_endpoint": True,
                    "track_by_status_code": True,
                    "alert_threshold_percent": 5.0
                },
                "database_performance": {
                    "enabled": True,
                    "slow_query_threshold_seconds": 1.0,
                    "connection_pool_usage_threshold": 80.0,
                    "deadlock_detection": True
                },
                "cache_performance": {
                    "enabled": True,
                    "hit_rate_threshold": 80.0,
                    "eviction_rate_threshold": 10.0,
                    "memory_usage_threshold": 85.0
                },
                "queue_performance": {
                    "enabled": True,
                    "queue_depth_threshold": 1000,
                    "processing_time_threshold": 30.0,
                    "failed_job_threshold": 5.0
                }
            }
        }
    
    def get_ai_services_performance_config(self) -> Dict[str, Any]:
        """Get AI services performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "metrics": {
                "inference_latency": {
                    "enabled": True,
                    "track_by_model": True,
                    "track_by_content_type": True,
                    "percentiles": [50, 90, 95, 99],
                    "p95_threshold_seconds": 10.0,
                    "p99_threshold_seconds": 30.0
                },
                "model_accuracy": {
                    "enabled": True,
                    "track_drift": True,
                    "minimum_accuracy_threshold": 0.85,
                    "drift_threshold_percent": 5.0
                },
                "gpu_utilization": {
                    "enabled": True,
                    "track_memory_usage": True,
                    "track_compute_usage": True,
                    "memory_threshold_percent": 90.0,
                    "compute_threshold_percent": 95.0
                },
                "batch_processing": {
                    "enabled": True,
                    "batch_size_optimization": True,
                    "queue_depth_threshold": 500,
                    "processing_time_threshold": 300.0
                },
                "model_loading": {
                    "enabled": True,
                    "loading_time_threshold": 60.0,
                    "memory_footprint_threshold_mb": 1024
                }
            },
            "optimization": {
                "auto_scaling": {
                    "enabled": True,
                    "min_replicas": 1,
                    "max_replicas": 10,
                    "cpu_threshold": 70.0,
                    "queue_threshold": 100
                },
                "model_caching": {
                    "enabled": True,
                    "cache_size_mb": 2048,
                    "ttl_seconds": 3600
                }
            }
        }
    
    def get_content_protection_performance_config(self) -> Dict[str, Any]:
        """Get content protection performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "metrics": {
                "fingerprint_generation": {
                    "enabled": True,
                    "latency_threshold_seconds": 30.0,
                    "throughput_threshold_per_minute": 100,
                    "failure_rate_threshold": 2.0
                },
                "similarity_matching": {
                    "enabled": True,
                    "search_latency_threshold": 5.0,
                    "accuracy_threshold": 0.90,
                    "false_positive_threshold": 0.05
                },
                "crawler_performance": {
                    "enabled": True,
                    "crawl_rate_per_minute": 1000,
                    "success_rate_threshold": 95.0,
                    "response_time_threshold": 10.0
                },
                "database_operations": {
                    "enabled": True,
                    "insert_latency_threshold": 0.1,
                    "query_latency_threshold": 1.0,
                    "index_size_monitoring": True
                }
            }
        }
    
    def get_audio_processing_performance_config(self) -> Dict[str, Any]:
        """Get audio processing performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "metrics": {
                "audio_analysis": {
                    "enabled": True,
                    "processing_latency_threshold": 60.0,
                    "spectral_analysis_threshold": 30.0,
                    "feature_extraction_threshold": 15.0
                },
                "format_conversion": {
                    "enabled": True,
                    "conversion_speed_ratio": 10.0,  # 10x real-time
                    "quality_metrics": True,
                    "file_size_optimization": True
                },
                "real_time_processing": {
                    "enabled": True,
                    "buffer_underrun_threshold": 1.0,
                    "latency_threshold_ms": 100,
                    "cpu_usage_threshold": 80.0
                }
            }
        }
    
    def get_monetization_performance_config(self) -> Dict[str, Any]:
        """Get monetization performance monitoring configuration"""



        return {
            "enabled": self.monitoring_enabled,
            "metrics": {
                "payment_processing": {
                    "enabled": True,
                    "transaction_latency_threshold": 5.0,
                    "success_rate_threshold": 99.5,
                    "fraud_detection_latency": 1.0
                },
                "revenue_calculation": {
                    "enabled": True,
                    "calculation_latency_threshold": 2.0,
                    "accuracy_verification": True,
                    "batch_processing_threshold": 10000
                },
                "reporting_performance": {
                    "enabled": True,
                    "report_generation_threshold": 30.0,
                    "data_freshness_threshold_minutes": 15
                }
            }
        }
    
    def get_performance_thresholds(self) -> List[PerformanceThreshold]:
        """Get performance alert thresholds"""



        return [
            # System thresholds
            PerformanceThreshold(
                name="High CPU Usage",
                metric="system_cpu_usage_percent",
                operator=">",
                value=80.0,
                severity=AlertSeverity.HIGH,
                duration="5m",
                description="System CPU usage above 80% for 5 minutes"
            ),
            PerformanceThreshold(
                name="Critical Memory Usage",
                metric="system_memory_usage_percent",
                operator=">",
                value=90.0,
                severity=AlertSeverity.CRITICAL,
                duration="2m",
                description="System memory usage above 90%"
            ),
            
            # Application thresholds
            PerformanceThreshold(
                name="High Request Latency",
                metric="http_request_duration_p95",
                operator=">",
                value=2.0,
                severity=AlertSeverity.HIGH,
                duration="5m",
                description="95th percentile request latency above 2 seconds"
            ),
            PerformanceThreshold(
                name="High Error Rate",
                metric="http_error_rate",
                operator=">",
                value=0.05,
                severity=AlertSeverity.CRITICAL,
                duration="3m",
                description="Error rate above 5%"
            ),
            
            # AI services thresholds
            PerformanceThreshold(
                name="AI Inference Slow",
                metric="ai_inference_duration_p95",
                operator=">",
                value=10.0,
                severity=AlertSeverity.HIGH,
                duration="10m",
                description="AI inference 95th percentile above 10 seconds"
            ),
            PerformanceThreshold(
                name="Model Accuracy Drop",
                metric="ai_model_accuracy",
                operator="<",
                value=0.85,
                severity=AlertSeverity.CRITICAL,
                duration="5m",
                description="AI model accuracy below 85%"
            ),
            
            # Database thresholds
            PerformanceThreshold(
                name="Database Connection Pool High",
                metric="db_connection_pool_usage",
                operator=">",
                value=0.8,
                severity=AlertSeverity.HIGH,
                duration="5m",
                description="Database connection pool usage above 80%"
            ),
            PerformanceThreshold(
                name="Slow Database Queries",
                metric="db_query_duration_p95",
                operator=">",
                value=1.0,
                severity=AlertSeverity.MEDIUM,
                duration="10m",
                description="Database query 95th percentile above 1 second"
            ),
            
            # Content protection thresholds
            PerformanceThreshold(
                name="Fingerprint Generation Slow",
                metric="fingerprint_generation_duration_p95",
                operator=">",
                value=30.0,
                severity=AlertSeverity.HIGH,
                duration="15m",
                description="Fingerprint generation taking too long"
            ),
            
            # Audio processing thresholds
            PerformanceThreshold(
                name="Audio Processing Queue High",
                metric="audio_processing_queue_size",
                operator=">",
                value=1000,
                severity=AlertSeverity.HIGH,
                duration="5m",
                description="Audio processing queue size above 1000"
            )
        ]
    
    def get_profiling_config(self) -> ProfilingConfig:
        """Get profiling configuration"""
        mode = ProfilingMode.DISABLED
        if self.profiling_enabled:
            if self.environment == "development":
                mode = ProfilingMode.CONTINUOUS
            else:
                mode = ProfilingMode.SAMPLING
        
        return ProfilingConfig(
            enabled=self.profiling_enabled,
            mode=mode,
            sampling_rate=self.profiling_sampling_rate,
            profile_duration=300,
            max_profiles=100,
            output_format="pprof",
            include_stack_traces=True
        )
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get performance optimization recommendations"""



        return {
            "database_optimizations": {
                "connection_pooling": {
                    "min_connections": 5,
                    "max_connections": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 3600
                },
                "query_optimization": {
                    "enable_query_cache": True,
                    "cache_size_mb": 256,
                    "slow_query_logging": True,
                    "explain_analyze_threshold": 1.0
                },
                "indexing_strategy": {
                    "auto_index_creation": True,
                    "index_usage_monitoring": True,
                    "unused_index_cleanup": True
                }
            },
            "caching_strategy": {
                "application_cache": {
                    "type": "redis",
                    "ttl_default": 3600,
                    "max_memory": "2gb",
                    "eviction_policy": "allkeys-lru"
                },
                "query_result_cache": {
                    "enabled": True,
                    "cache_size_mb": 512,
                    "ttl_seconds": 1800
                },
                "static_content_cache": {
                    "enabled": True,
                    "cdn_integration": True,
                    "cache_headers": True
                }
            },
            "concurrency_optimization": {
                "async_processing": {
                    "worker_threads": 4,
                    "max_concurrent_requests": 1000,
                    "queue_size": 10000
                },
                "background_tasks": {
                    "celery_workers": 8,
                    "task_routing": True,
                    "task_prioritization": True
                }
            },
            "resource_optimization": {
                "memory_management": {
                    "gc_threshold": 0.8,
                    "object_pooling": True,
                    "memory_mapped_files": True
                },
                "cpu_optimization": {
                    "process_affinity": True,
                    "thread_pool_size": "auto",
                    "cpu_bound_task_separation": True
                }
            }
        }
    
    def get_performance_testing_config(self) -> Dict[str, Any]:
        """Get performance testing configuration"""



        return {
            "load_testing": {
                "enabled": self.environment != "production",
                "scenarios": {
                    "baseline": {
                        "users": 100,
                        "ramp_up_time": 60,
                        "test_duration": 300
                    },
                    "stress": {
                        "users": 1000,
                        "ramp_up_time": 300,
                        "test_duration": 600
                    },
                    "spike": {
                        "users": 500,
                        "ramp_up_time": 10,
                        "test_duration": 120
                    }
                },
                "sla_requirements": {
                    "response_time_p95": 2.0,
                    "response_time_p99": 5.0,
                    "error_rate_max": 0.01,
                    "throughput_min": 100
                }
            },
            "benchmarking": {
                "enabled": True,
                "frequency": "daily",
                "baseline_comparison": True,
                "regression_detection": True
            }
        }
    
    def get_monitoring_dashboards_config(self) -> Dict[str, Any]:
        """Get performance monitoring dashboards configuration"""



        return {
            "system_performance": {
                "refresh_interval": "30s",
                "time_range": "1h",
                "panels": [
                    "cpu_usage", "memory_usage", "disk_io", "network_io",
                    "load_average", "process_count"
                ]
            },
            "application_performance": {
                "refresh_interval": "15s",
                "time_range": "30m",
                "panels": [
                    "request_latency", "throughput", "error_rate",
                    "active_connections", "queue_sizes"
                ]
            },
            "ai_performance": {
                "refresh_interval": "1m",
                "time_range": "2h",
                "panels": [
                    "inference_latency", "model_accuracy", "gpu_utilization",
                    "batch_processing", "queue_depth"
                ]
            },
            "database_performance": {
                "refresh_interval": "30s",
                "time_range": "1h",
                "panels": [
                    "query_latency", "connection_pool", "slow_queries",
                    "deadlocks", "cache_hit_ratio"
                ]
            }
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete performance monitoring configuration"""



        return {
            "global": {
                "enabled": self.monitoring_enabled,
                "service_name": self.service_name,
                "environment": self.environment,
                "collection_interval": self.metrics_collection_interval,
                "retention_days": self.performance_data_retention
            },
            "system_performance": self.get_system_performance_config(),
            "application_performance": self.get_application_performance_config(),
            "ai_services": self.get_ai_services_performance_config(),
            "content_protection": self.get_content_protection_performance_config(),
            "audio_processing": self.get_audio_processing_performance_config(),
            "monetization": self.get_monetization_performance_config(),
            "thresholds": [threshold.__dict__ for threshold in self.get_performance_thresholds()],
            "profiling": self.get_profiling_config().__dict__,
            "optimization": self.get_optimization_recommendations(),
            "testing": self.get_performance_testing_config(),
            "dashboards": self.get_monitoring_dashboards_config()
        }
