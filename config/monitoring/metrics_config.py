"""
Metrics Configuration Module for IA-Influencer Agent Platform
=============================================================

Professional metrics collection and instrumentation configuration for
comprehensive monitoring of content creators platform with AI processing.

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
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
import psutil
import threading


class MetricCategory(Enum):
    """Metric categories for organization"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    AI_SERVICES = "ai_services"
    CONTENT_PROTECTION = "content_protection"
    AUDIO_PROCESSING = "audio_processing"
    SECURITY = "security"
    MONETIZATION = "monetization"


@dataclass
class MetricDefinition:
    """Metric definition with metadata"""
    name: str
    metric_type: str
    description: str
    category: MetricCategory
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
    unit: Optional[str] = None


class MetricsRegistry:
    """Professional metrics registry with automatic instrumentation"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._metrics = {}
        self._background_collectors = []
        self._collection_interval = int(os.getenv("METRICS_COLLECTION_INTERVAL", "15"))
        self._setup_standard_metrics()
        self._start_background_collection()
    
    def _setup_standard_metrics(self):
        """Setup standard platform metrics"""
        # System metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            ['mount_point'],
            registry=self.registry
        )
        
        # Application metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status', 'service'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'service'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'active_connections_total',
            'Number of active connections',
            ['service'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections',
            ['database'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type', 'database'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        # AI/ML metrics
        self.ai_inference_duration = Histogram(
            'ai_inference_duration_seconds',
            'AI model inference duration in seconds',
            ['model_type', 'content_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.ai_model_accuracy = Gauge(
            'ai_model_accuracy',
            'AI model accuracy score',
            ['model_name', 'model_version'],
            registry=self.registry
        )
        
        self.ai_gpu_utilization = Gauge(
            'ai_gpu_utilization_percent',
            'GPU utilization percentage',
            ['device_id'],
            registry=self.registry
        )
        
        self.ai_processing_queue_size = Gauge(
            'ai_processing_queue_size',
            'AI processing queue size',
            ['queue_type'],
            registry=self.registry
        )
        
        # Content protection metrics
        self.content_uploads_total = Counter(
            'content_uploads_total',
            'Total content uploads',
            ['user_id', 'content_type', 'platform'],
            registry=self.registry
        )
        
        self.protection_matches_total = Counter(
            'protection_matches_total',
            'Total content protection matches',
            ['content_type', 'match_confidence', 'platform'],
            registry=self.registry
        )
        
        self.fingerprint_generation_duration = Histogram(
            'fingerprint_generation_duration_seconds',
            'Fingerprint generation duration in seconds',
            ['content_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.fingerprint_database_size = Gauge(
            'fingerprint_database_size',
            'Size of fingerprint database',
            ['content_type', 'database_shard'],
            registry=self.registry
        )
        
        # Audio processing metrics
        self.audio_processing_duration = Histogram(
            'audio_processing_duration_seconds',
            'Audio processing duration in seconds',
            ['processing_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.audio_fingerprints_generated_total = Counter(
            'audio_fingerprints_generated_total',
            'Total audio fingerprints generated',
            ['audio_format'],
            registry=self.registry
        )
        
        self.spectral_analysis_queue_size = Gauge(
            'spectral_analysis_queue_size',
            'Spectral analysis queue size',
            registry=self.registry
        )
        
        # Security metrics
        self.auth_attempts_total = Counter(
            'auth_attempts_total',
            'Total authentication attempts',
            ['status', 'method'],
            registry=self.registry
        )
        
        self.suspicious_activity_score = Gauge(
            'suspicious_activity_score',
            'Suspicious activity score',
            ['source_ip', 'activity_type'],
            registry=self.registry
        )
        
        self.api_rate_limit_exceeded_total = Counter(
            'api_rate_limit_exceeded_total',
            'Total API rate limit violations',
            ['endpoint', 'user_id'],
            registry=self.registry
        )
        
        self.security_incidents_total = Counter(
            'security_incidents_total',
            'Total security incidents',
            ['severity', 'incident_type'],
            registry=self.registry
        )
        
        # Business metrics
        self.revenue_generated_total = Counter(
            'revenue_generated_total',
            'Total revenue generated',
            ['user_id', 'platform', 'content_type'],
            registry=self.registry
        )
        
        self.active_users_count = Gauge(
            'active_users_count',
            'Number of active users',
            registry=self.registry
        )
        
        self.platform_usage_count = Gauge(
            'platform_usage_count',
            'Platform usage statistics',
            ['platform'],
            registry=self.registry
        )
        
        self.collaboration_matches_total = Counter(
            'collaboration_matches_total',
            'Total collaboration matches',
            ['match_type', 'success'],
            registry=self.registry
        )
        
        # Monetization metrics
        self.payment_processing_duration = Histogram(
            'payment_processing_duration_seconds',
            'Payment processing duration in seconds',
            ['provider', 'payment_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.license_agreements_active = Gauge(
            'license_agreements_active',
            'Number of active license agreements',
            ['license_type'],
            registry=self.registry
        )
        
        self.platform_revenue_total = Counter(
            'platform_revenue_total',
            'Total revenue by platform',
            ['platform', 'revenue_type'],
            registry=self.registry
        )
    
    def _start_background_collection(self):
        """Start background metric collection"""
        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.system_cpu_usage.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.system_memory_usage.set(memory.percent)
                    
                    # Disk usage
                    for disk in psutil.disk_partitions():
                        try:
                            usage = psutil.disk_usage(disk.mountpoint)
                            self.system_disk_usage.labels(mount_point=disk.mountpoint).set(usage.percent)
                        except (PermissionError, OSError):
                            pass
                    
                    time.sleep(self._collection_interval)
                except Exception as e:
                    print(f"Error collecting system metrics: {e}")
                    time.sleep(self._collection_interval)
        
        collector_thread = threading.Thread(target=collect_system_metrics, daemon=True)
        collector_thread.start()
    
    def record_http_request(self, method: str, endpoint: str, status: str, 
                           service: str, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status=status, service=service
        ).inc()
        
        self.http_request_duration.labels(
            method=method, endpoint=endpoint, service=service
        ).observe(duration)
    
    def record_db_query(self, query_type: str, database: str, duration: float):
        """Record database query metrics"""
        self.db_query_duration.labels(
            query_type=query_type, database=database
        ).observe(duration)
    
    def record_ai_inference(self, model_type: str, content_type: str, 
                           duration: float, accuracy: Optional[float] = None):
        """Record AI inference metrics"""
        self.ai_inference_duration.labels(
            model_type=model_type, content_type=content_type
        ).observe(duration)
        
        if accuracy is not None:
            self.ai_model_accuracy.labels(
                model_name=model_type, model_version="latest"
            ).set(accuracy)
    
    def record_content_upload(self, user_id: str, content_type: str, platform: str):
        """Record content upload metrics"""
        self.content_uploads_total.labels(
            user_id=user_id, content_type=content_type, platform=platform
        ).inc()
    
    def record_protection_match(self, content_type: str, confidence: str, platform: str):
        """Record content protection match metrics"""
        self.protection_matches_total.labels(
            content_type=content_type, match_confidence=confidence, platform=platform
        ).inc()
    
    def record_audio_processing(self, processing_type: str, duration: float):
        """Record audio processing metrics"""
        self.audio_processing_duration.labels(
            processing_type=processing_type
        ).observe(duration)
    
    def record_fingerprint_generation(self, content_type: str, audio_format: str, duration: float):
        """Record fingerprint generation metrics"""
        self.fingerprint_generation_duration.labels(
            content_type=content_type
        ).observe(duration)
        
        if content_type == "audio":
            self.audio_fingerprints_generated_total.labels(
                audio_format=audio_format
            ).inc()
    
    def record_auth_attempt(self, status: str, method: str):
        """Record authentication attempt metrics"""
        self.auth_attempts_total.labels(status=status, method=method).inc()
    
    def record_security_incident(self, severity: str, incident_type: str):
        """Record security incident metrics"""
        self.security_incidents_total.labels(
            severity=severity, incident_type=incident_type
        ).inc()
    
    def record_revenue(self, user_id: str, platform: str, content_type: str, amount: float):
        """Record revenue metrics"""
        self.revenue_generated_total.labels(
            user_id=user_id, platform=platform, content_type=content_type
        ).inc(amount)
    
    def record_payment_processing(self, provider: str, payment_type: str, duration: float):
        """Record payment processing metrics"""
        self.payment_processing_duration.labels(
            provider=provider, payment_type=payment_type
        ).observe(duration)
    
    def update_active_users(self, count: int):
        """Update active users count"""
        self.active_users_count.set(count)
    
    def update_platform_usage(self, platform: str, count: int):
        """Update platform usage statistics"""
        self.platform_usage_count.labels(platform=platform).set(count)
    
    def update_gpu_utilization(self, device_id: str, utilization: float):
        """Update GPU utilization metrics"""
        self.ai_gpu_utilization.labels(device_id=device_id).set(utilization)
    
    def update_queue_size(self, queue_type: str, size: int):
        """Update queue size metrics"""
        if queue_type.startswith("ai_"):
            self.ai_processing_queue_size.labels(queue_type=queue_type).set(size)
        elif queue_type == "spectral_analysis":
            self.spectral_analysis_queue_size.set(size)
    
    def update_fingerprint_database_size(self, content_type: str, shard: str, size: int):
        """Update fingerprint database size"""
        self.fingerprint_database_size.labels(
            content_type=content_type, database_shard=shard
        ).set(size)
    
    def update_license_agreements(self, license_type: str, count: int):
        """Update active license agreements"""
        self.license_agreements_active.labels(license_type=license_type).set(count)
    
    def set_suspicious_activity_score(self, source_ip: str, activity_type: str, score: float):
        """Set suspicious activity score"""
        self.suspicious_activity_score.labels(
            source_ip=source_ip, activity_type=activity_type
        ).set(score)
    
    def increment_collaboration_matches(self, match_type: str, success: bool):
        """Increment collaboration matches"""
        self.collaboration_matches_total.labels(
            match_type=match_type, success=str(success).lower()
        ).inc()
    
    def get_metrics_export(self) -> str:
        """Export metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')


class MetricsConfig:
    """Professional metrics configuration for IA-Influencer platform"""
    
    def __init__(self):
        self.metrics_port = int(os.getenv("METRICS_PORT", "8000"))
        self.metrics_path = os.getenv("METRICS_PATH", "/metrics")
        self.collection_interval = int(os.getenv("METRICS_COLLECTION_INTERVAL", "15"))
        self.retention_days = int(os.getenv("METRICS_RETENTION_DAYS", "30"))
        self.registry = MetricsRegistry()
    
    def get_metric_definitions(self) -> List[MetricDefinition]:
        """Get all metric definitions"""
        return [
            # System metrics
            MetricDefinition(
                name="system_cpu_usage_percent",
                metric_type="gauge",
                description="System CPU usage percentage",
                category=MetricCategory.SYSTEM,
                unit="percent"
            ),
            MetricDefinition(
                name="system_memory_usage_percent",
                metric_type="gauge",
                description="System memory usage percentage",
                category=MetricCategory.SYSTEM,
                unit="percent"
            ),
            
            # Application metrics
            MetricDefinition(
                name="http_requests_total",
                metric_type="counter",
                description="Total HTTP requests",
                category=MetricCategory.APPLICATION,
                labels=["method", "endpoint", "status", "service"]
            ),
            MetricDefinition(
                name="http_request_duration_seconds",
                metric_type="histogram",
                description="HTTP request duration",
                category=MetricCategory.APPLICATION,
                labels=["method", "endpoint", "service"],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
                unit="seconds"
            ),
            
            # AI service metrics
            MetricDefinition(
                name="ai_inference_duration_seconds",
                metric_type="histogram",
                description="AI model inference duration",
                category=MetricCategory.AI_SERVICES,
                labels=["model_type", "content_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
                unit="seconds"
            ),
            MetricDefinition(
                name="ai_model_accuracy",
                metric_type="gauge",
                description="AI model accuracy score",
                category=MetricCategory.AI_SERVICES,
                labels=["model_name", "model_version"],
                unit="ratio"
            ),
            
            # Content protection metrics
            MetricDefinition(
                name="content_uploads_total",
                metric_type="counter",
                description="Total content uploads",
                category=MetricCategory.CONTENT_PROTECTION,
                labels=["user_id", "content_type", "platform"]
            ),
            MetricDefinition(
                name="protection_matches_total",
                metric_type="counter",
                description="Total content protection matches",
                category=MetricCategory.CONTENT_PROTECTION,
                labels=["content_type", "match_confidence", "platform"]
            ),
            
            # Audio processing metrics
            MetricDefinition(
                name="audio_processing_duration_seconds",
                metric_type="histogram",
                description="Audio processing duration",
                category=MetricCategory.AUDIO_PROCESSING,
                labels=["processing_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
                unit="seconds"
            ),
            
            # Security metrics
            MetricDefinition(
                name="auth_attempts_total",
                metric_type="counter",
                description="Total authentication attempts",
                category=MetricCategory.SECURITY,
                labels=["status", "method"]
            ),
            MetricDefinition(
                name="suspicious_activity_score",
                metric_type="gauge",
                description="Suspicious activity score",
                category=MetricCategory.SECURITY,
                labels=["source_ip", "activity_type"],
                unit="score"
            ),
            
            # Business metrics
            MetricDefinition(
                name="revenue_generated_total",
                metric_type="counter",
                description="Total revenue generated",
                category=MetricCategory.BUSINESS,
                labels=["user_id", "platform", "content_type"],
                unit="currency"
            ),
            MetricDefinition(
                name="active_users_count",
                metric_type="gauge",
                description="Number of active users",
                category=MetricCategory.BUSINESS,
                unit="count"
            ),
            
            # Monetization metrics
            MetricDefinition(
                name="payment_processing_duration_seconds",
                metric_type="histogram",
                description="Payment processing duration",
                category=MetricCategory.MONETIZATION,
                labels=["provider", "payment_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
                unit="seconds"
            )
        ]
    
    def get_configuration_dict(self) -> Dict[str, Any]:
        """Get metrics configuration as dictionary"""
        return {
            "metrics_port": self.metrics_port,
            "metrics_path": self.metrics_path,
            "collection_interval": self.collection_interval,
            "retention_days": self.retention_days,
            "categories": [category.value for category in MetricCategory],
            "total_metrics": len(self.get_metric_definitions())
        }
