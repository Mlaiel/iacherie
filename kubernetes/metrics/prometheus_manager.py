"""
IA Influencer Agent - Prometheus Metrics Manager
Enterprise-grade metrics collection and monitoring for multi-tenant AI platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiques selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Multi-tenant metrics isolation
- Real-time performance monitoring
- AI model performance tracking
- Content protection metrics
- Revenue tracking metrics
- Resource utilization monitoring
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server, push_to_gateway
)
from prometheus_client.core import MetricWrapperBase
import psutil
import time
import json

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.metrics import MetricsModel, AlertRule
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class MetricDefinition:
    """Metric definition structure"""
    name: str
    metric_type: str  # counter, histogram, gauge, summary, info
    description: str
    labels: List[str]
    buckets: Optional[List[float]] = None  # For histograms
    unit: Optional[str] = None


class PrometheusManager:
    """
    Enterprise Prometheus metrics manager with multi-tenant support
    
    Handles:
    - Application metrics collection
    - Infrastructure monitoring
    - AI model performance tracking
    - Content protection metrics
    - Revenue and business metrics
    - Alert threshold management
    """
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, MetricWrapperBase] = {}
        self.redis_manager = RedisManager()
        self.logger = logger
        self._initialize_core_metrics()
        self._setup_custom_collectors()
        
    def _initialize_core_metrics(self) -> None:
        """Initialize core application metrics"""
        
        # Application Performance Metrics
        self.http_requests_total = Counter(
            'ia_influencer_http_requests_total',
            'Total HTTP requests by method, endpoint, status',
            ['method', 'endpoint', 'status_code', 'tenant_id'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'ia_influencer_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'tenant_id'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # AI Model Performance Metrics
        self.ai_model_predictions_total = Counter(
            'ia_influencer_ai_predictions_total',
            'Total AI model predictions',
            ['model_name', 'model_version', 'prediction_type', 'tenant_id'],
            registry=self.registry
        )
        
        self.ai_model_inference_duration = Histogram(
            'ia_influencer_ai_inference_duration_seconds',
            'AI model inference duration',
            ['model_name', 'model_version', 'tenant_id'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )
        
        self.ai_model_accuracy = Gauge(
            'ia_influencer_ai_model_accuracy',
            'AI model accuracy score',
            ['model_name', 'model_version', 'metric_type', 'tenant_id'],
            registry=self.registry
        )
        
        # Content Protection Metrics
        self.content_fingerprints_created = Counter(
            'ia_influencer_fingerprints_created_total',
            'Total content fingerprints created',
            ['content_type', 'fingerprint_algorithm', 'tenant_id'],
            registry=self.registry
        )
        
        self.content_matches_detected = Counter(
            'ia_influencer_content_matches_total',
            'Total content matches detected',
            ['content_type', 'platform', 'similarity_threshold', 'tenant_id'],
            registry=self.registry
        )
        
        self.fingerprint_processing_duration = Histogram(
            'ia_influencer_fingerprint_processing_seconds',
            'Fingerprint processing duration',
            ['content_type', 'algorithm', 'tenant_id'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        # Revenue and Business Metrics
        self.revenue_tracked = Counter(
            'ia_influencer_revenue_tracked_total',
            'Total revenue tracked in euros',
            ['platform', 'content_type', 'currency', 'tenant_id'],
            registry=self.registry
        )
        
        self.licensing_transactions = Counter(
            'ia_influencer_licensing_transactions_total',
            'Total licensing transactions',
            ['license_type', 'platform', 'status', 'tenant_id'],
            registry=self.registry
        )
        
        self.active_users = Gauge(
            'ia_influencer_active_users',
            'Number of active users',
            ['time_window', 'user_type', 'tenant_id'],
            registry=self.registry
        )
        
        # System Resource Metrics
        self.system_cpu_usage = Gauge(
            'ia_influencer_system_cpu_usage_percent',
            'System CPU usage percentage',
            ['core'],
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'ia_influencer_system_memory_usage_bytes',
            'System memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'ia_influencer_database_connections',
            'Number of database connections',
            ['database', 'state'],
            registry=self.registry
        )
        
        # Cache Performance Metrics
        self.cache_operations = Counter(
            'ia_influencer_cache_operations_total',
            'Total cache operations',
            ['operation', 'cache_type', 'result'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'ia_influencer_cache_hit_rate',
            'Cache hit rate percentage',
            ['cache_type'],
            registry=self.registry
        )
        
        # Background Task Metrics
        self.background_tasks_total = Counter(
            'ia_influencer_background_tasks_total',
            'Total background tasks executed',
            ['task_type', 'status', 'queue'],
            registry=self.registry
        )
        
        self.background_task_duration = Histogram(
            'ia_influencer_background_task_duration_seconds',
            'Background task execution duration',
            ['task_type', 'queue'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry
        )
        
        # Store metrics references
        self.metrics.update({
            'http_requests_total': self.http_requests_total,
            'http_request_duration': self.http_request_duration,
            'ai_model_predictions_total': self.ai_model_predictions_total,
            'ai_model_inference_duration': self.ai_model_inference_duration,
            'ai_model_accuracy': self.ai_model_accuracy,
            'content_fingerprints_created': self.content_fingerprints_created,
            'content_matches_detected': self.content_matches_detected,
            'fingerprint_processing_duration': self.fingerprint_processing_duration,
            'revenue_tracked': self.revenue_tracked,
            'licensing_transactions': self.licensing_transactions,
            'active_users': self.active_users,
            'system_cpu_usage': self.system_cpu_usage,
            'system_memory_usage': self.system_memory_usage,
            'database_connections': self.database_connections,
            'cache_operations': self.cache_operations,
            'cache_hit_rate': self.cache_hit_rate,
            'background_tasks_total': self.background_tasks_total,
            'background_task_duration': self.background_task_duration
        })
    
    def _setup_custom_collectors(self) -> None:
        """Setup custom metric collectors"""
        self.registry.register(SystemResourceCollector())
        self.registry.register(DatabaseMetricsCollector())
    
    async def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        tenant_id: str
    ) -> None:
        """Record HTTP request metrics"""
        try:
            self.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
                tenant_id=tenant_id
            ).inc()
            
            self.http_request_duration.labels(
                method=method,
                endpoint=endpoint,
                tenant_id=tenant_id
            ).observe(duration)
            
        except Exception as e:
            self.logger.error(f"Error recording HTTP request metrics: {e}")
    
    async def record_ai_prediction(
        self,
        model_name: str,
        model_version: str,
        prediction_type: str,
        inference_duration: float,
        accuracy: Optional[float],
        tenant_id: str
    ) -> None:
        """Record AI model prediction metrics"""
        try:
            self.ai_model_predictions_total.labels(
                model_name=model_name,
                model_version=model_version,
                prediction_type=prediction_type,
                tenant_id=tenant_id
            ).inc()
            
            self.ai_model_inference_duration.labels(
                model_name=model_name,
                model_version=model_version,
                tenant_id=tenant_id
            ).observe(inference_duration)
            
            if accuracy is not None:
                self.ai_model_accuracy.labels(
                    model_name=model_name,
                    model_version=model_version,
                    metric_type='accuracy',
                    tenant_id=tenant_id
                ).set(accuracy)
                
        except Exception as e:
            self.logger.error(f"Error recording AI prediction metrics: {e}")
    
    async def record_content_protection(
        self,
        content_type: str,
        fingerprint_algorithm: str,
        processing_duration: float,
        tenant_id: str,
        match_detected: bool = False,
        platform: Optional[str] = None,
        similarity_threshold: Optional[float] = None
    ) -> None:
        """Record content protection metrics"""
        try:
            self.content_fingerprints_created.labels(
                content_type=content_type,
                fingerprint_algorithm=fingerprint_algorithm,
                tenant_id=tenant_id
            ).inc()
            
            self.fingerprint_processing_duration.labels(
                content_type=content_type,
                algorithm=fingerprint_algorithm,
                tenant_id=tenant_id
            ).observe(processing_duration)
            
            if match_detected and platform and similarity_threshold:
                self.content_matches_detected.labels(
                    content_type=content_type,
                    platform=platform,
                    similarity_threshold=str(similarity_threshold),
                    tenant_id=tenant_id
                ).inc()
                
        except Exception as e:
            self.logger.error(f"Error recording content protection metrics: {e}")
    
    async def record_revenue(
        self,
        platform: str,
        content_type: str,
        amount: float,
        currency: str,
        tenant_id: str
    ) -> None:
        """Record revenue tracking metrics"""
        try:
            self.revenue_tracked.labels(
                platform=platform,
                content_type=content_type,
                currency=currency,
                tenant_id=tenant_id
            ).inc(amount)
            
        except Exception as e:
            self.logger.error(f"Error recording revenue metrics: {e}")
    
    async def record_licensing_transaction(
        self,
        license_type: str,
        platform: str,
        status: str,
        tenant_id: str
    ) -> None:
        """Record licensing transaction metrics"""
        try:
            self.licensing_transactions.labels(
                license_type=license_type,
                platform=platform,
                status=status,
                tenant_id=tenant_id
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Error recording licensing transaction metrics: {e}")
    
    async def record_cache_operation(
        self,
        operation: str,
        cache_type: str,
        result: str
    ) -> None:
        """Record cache operation metrics"""
        try:
            self.cache_operations.labels(
                operation=operation,
                cache_type=cache_type,
                result=result
            ).inc()
            
            # Update cache hit rate
            await self._update_cache_hit_rate(cache_type)
            
        except Exception as e:
            self.logger.error(f"Error recording cache operation metrics: {e}")
    
    async def record_background_task(
        self,
        task_type: str,
        queue: str,
        status: str,
        duration: float
    ) -> None:
        """Record background task metrics"""
        try:
            self.background_tasks_total.labels(
                task_type=task_type,
                status=status,
                queue=queue
            ).inc()
            
            self.background_task_duration.labels(
                task_type=task_type,
                queue=queue
            ).observe(duration)
            
        except Exception as e:
            self.logger.error(f"Error recording background task metrics: {e}")
    
    async def update_active_users(
        self,
        time_window: str,
        user_type: str,
        count: int,
        tenant_id: str
    ) -> None:
        """Update active users gauge"""
        try:
            self.active_users.labels(
                time_window=time_window,
                user_type=user_type,
                tenant_id=tenant_id
            ).set(count)
            
        except Exception as e:
            self.logger.error(f"Error updating active users metrics: {e}")
    
    async def _update_cache_hit_rate(self, cache_type: str) -> None:
        """Update cache hit rate based on recent operations"""
        try:
            # Get cache statistics from Redis
            cache_stats = await self.redis_manager.get_cache_stats(cache_type)
            
            if cache_stats:
                total_ops = cache_stats.get('hits', 0) + cache_stats.get('misses', 0)
                if total_ops > 0:
                    hit_rate = (cache_stats.get('hits', 0) / total_ops) * 100
                    self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)
                    
        except Exception as e:
            self.logger.error(f"Error updating cache hit rate: {e}")
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            self.logger.error(f"Error generating metrics: {e}")
            return ""
    
    def start_metrics_server(self, port: int = 8000) -> None:
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Error starting metrics server: {e}")
            raise
    
    async def push_to_gateway(self, gateway_url: str, job_name: str) -> None:
        """Push metrics to Prometheus pushgateway"""
        try:
            push_to_gateway(gateway_url, job=job_name, registry=self.registry)
            self.logger.info(f"Metrics pushed to gateway: {gateway_url}")
        except Exception as e:
            self.logger.error(f"Error pushing metrics to gateway: {e}")
    
    async def create_custom_metric(
        self,
        definition: MetricDefinition,
        tenant_id: Optional[str] = None
    ) -> MetricWrapperBase:
        """Create custom metric dynamically"""
        try:
            labels = definition.labels.copy()
            if tenant_id and 'tenant_id' not in labels:
                labels.append('tenant_id')
            
            if definition.metric_type == 'counter':
                metric = Counter(
                    definition.name,
                    definition.description,
                    labels,
                    registry=self.registry
                )
            elif definition.metric_type == 'histogram':
                metric = Histogram(
                    definition.name,
                    definition.description,
                    labels,
                    buckets=definition.buckets or [],
                    registry=self.registry
                )
            elif definition.metric_type == 'gauge':
                metric = Gauge(
                    definition.name,
                    definition.description,
                    labels,
                    registry=self.registry
                )
            elif definition.metric_type == 'summary':
                metric = Summary(
                    definition.name,
                    definition.description,
                    labels,
                    registry=self.registry
                )
            elif definition.metric_type == 'info':
                metric = Info(
                    definition.name,
                    definition.description,
                    registry=self.registry
                )
            else:
                raise ValueError(f"Unsupported metric type: {definition.metric_type}")
            
            self.metrics[definition.name] = metric
            
            self.logger.info(f"Custom metric created: {definition.name}")
            return metric
            
        except Exception as e:
            self.logger.error(f"Error creating custom metric: {e}")
            raise
    
    async def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get metrics for specific tenant"""
        try:
            # This would require filtering metrics by tenant_id
            # Implementation depends on specific requirements
            pass
        except Exception as e:
            self.logger.error(f"Error getting tenant metrics: {e}")
            return {}
    
    async def export_metrics_to_file(self, file_path: str) -> None:
        """Export metrics to file"""
        try:
            metrics_data = self.get_metrics()
            with open(file_path, 'w') as f:
                f.write(metrics_data)
            self.logger.info(f"Metrics exported to: {file_path}")
        except Exception as e:
            self.logger.error(f"Error exporting metrics to file: {e}")


class SystemResourceCollector:
    """Custom collector for system resource metrics"""
    
    def collect(self):
        """Collect system resource metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            for i, cpu in enumerate(cpu_percent):
                yield Gauge(
                    'system_cpu_usage_percent',
                    'CPU usage percentage',
                    ['core']
                ).labels(core=str(i)).set(cpu)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            yield Gauge(
                'system_memory_usage_bytes',
                'Memory usage in bytes',
                ['type']
            ).labels(type='used').set(memory.used)
            
            yield Gauge(
                'system_memory_usage_bytes',
                'Memory usage in bytes',
                ['type']
            ).labels(type='available').set(memory.available)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            yield Gauge(
                'system_disk_usage_bytes',
                'Disk usage in bytes',
                ['type']
            ).labels(type='used').set(disk.used)
            
            yield Gauge(
                'system_disk_usage_bytes',
                'Disk usage in bytes',
                ['type']
            ).labels(type='free').set(disk.free)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


class DatabaseMetricsCollector:
    """Custom collector for database metrics"""
    
    def collect(self):
        """Collect database metrics"""
        try:
            # Database connection metrics would be implemented here
            # This is a placeholder for the actual implementation
            pass
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
