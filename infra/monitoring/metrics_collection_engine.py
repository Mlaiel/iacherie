"""
Metrics Collection Engine module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import logging
import asyncio
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import aiofiles
import aiohttp
import boto3
from azure.monitor.query import MetricsQueryClient
from google.cloud import monitoring_v3
from dataclasses import dataclass, asdict
from kubernetes import client, config
import prometheus_client
from prometheus_client.parser import text_string_to_metric_families

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/ainflue/metrics_collection.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Data class for metric information"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: str  # counter, gauge, histogram, summary
    help_text: Optional[str] = None
    unit: Optional[str] = None

@dataclass
class MetricsCollectionConfig:
    """Configuration for metrics collection"""
    collection_interval: int = 30  # seconds
    retention_period: int = 86400  # seconds (24 hours)
    max_metrics_per_batch: int = 1000
    prometheus_endpoint: str = "http://localhost:9090"
    push_gateway_endpoint: Optional[str] = None
    enable_cloud_metrics: bool = True
    enable_kubernetes_metrics: bool = True
    enable_application_metrics: bool = True
    custom_collectors: List[str] = None

class CloudMetricsCollector:
    """Multi-cloud metrics collection"""
    
    def __init__(self) -> None:
        self.aws_cloudwatch = None
        self.azure_monitor = None
        self.gcp_monitoring = None
        self._initialize_cloud_clients()
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud monitoring clients"""
        try:
            # AWS CloudWatch
            self.aws_cloudwatch = boto3.client('cloudwatch')
            logger.info("AWS CloudWatch client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize AWS CloudWatch: {e}")
        
        try:
            # Azure Monitor
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            self.azure_monitor = MetricsQueryClient(credential)
            logger.info("Azure Monitor client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Monitor: {e}")
        
        try:
            # Google Cloud Monitoring
            self.gcp_monitoring = monitoring_v3.MetricServiceClient()
            logger.info("Google Cloud Monitoring client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud Monitoring: {e}")
    
    async def collect_aws_metrics(self, namespace: str, metric_names: List[str]) -> List[MetricData]:
        """Collect metrics from AWS CloudWatch"""
        metrics = []
        if not self.aws_cloudwatch:
            return metrics
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            for metric_name in metric_names:
                response = self.aws_cloudwatch.get_metric_statistics(
                    Namespace=namespace,
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5 minutes
                    Statistics=['Average', 'Maximum', 'Minimum']
                )
                
                for datapoint in response.get('Datapoints', []):
                    metrics.append(MetricData(
                        name=f"aws_{namespace.lower()}_{metric_name.lower()}",
                        value=datapoint['Average'],
                        timestamp=datapoint['Timestamp'],
                        labels={
                            'cloud_provider': 'aws',
                            'namespace': namespace,
                            'statistic': 'average'
                        },
                        metric_type='gauge',
                        help_text=f"AWS {namespace} {metric_name} metric",
                        unit=datapoint.get('Unit', '')
                    ))
        
        except Exception as e:
            logger.error(f"Error collecting AWS metrics: {e}")
        
        return metrics
    
    async def collect_azure_metrics(self, resource_id: str, metric_names: List[str]) -> List[MetricData]:
        """Collect metrics from Azure Monitor"""
        metrics = []
        if not self.azure_monitor:
            return metrics
        
        try:
            from azure.monitor.query import MetricsQueryRequest
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            request = MetricsQueryRequest(
                resource_uri=resource_id,
                metric_names=metric_names,
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1)
            )
            
            response = self.azure_monitor.query_metrics(request)
            
            for metric in response.metrics:
                for time_series in metric.timeseries:
                    for value in time_series.data:
                        if value.average is not None:
                            metrics.append(MetricData(
                                name=f"azure_{metric.name.value.lower()}",
                                value=value.average,
                                timestamp=value.timestamp,
                                labels={
                                    'cloud_provider': 'azure',
                                    'resource_id': resource_id,
                                    'metric_name': metric.name.value
                                },
                                metric_type='gauge',
                                help_text=f"Azure {metric.name.value} metric",
                                unit=str(metric.unit)
                            ))
        
        except Exception as e:
            logger.error(f"Error collecting Azure metrics: {e}")
        
        return metrics
    
    async def collect_gcp_metrics(self, project_id: str, metric_type: str) -> List[MetricData]:
        """Collect metrics from Google Cloud Monitoring"""
        metrics = []
        if not self.gcp_monitoring:
            return metrics
        
        try:
            project_name = f"projects/{project_id}"
            
            # Query time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())},
            })
            
            # Create filter
            filter_str = f'metric.type="{metric_type}"'
            
            request = monitoring_v3.ListTimeSeriesRequest(
                name=project_name,
                filter=filter_str,
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            )
            
            results = self.gcp_monitoring.list_time_series(request=request)
            
            for result in results:
                for point in result.points:
                    value = point.value.double_value or point.value.int64_value
                    
                    metrics.append(MetricData(
                        name=f"gcp_{metric_type.split('/')[-1].lower()}",
                        value=value,
                        timestamp=datetime.fromtimestamp(point.interval.end_time.seconds),
                        labels={
                            'cloud_provider': 'gcp',
                            'project_id': project_id,
                            'metric_type': metric_type,
                            **{k: v for k, v in result.metric.labels.items()}
                        },
                        metric_type='gauge',
                        help_text=f"GCP {metric_type} metric"
                    ))
        
        except Exception as e:
            logger.error(f"Error collecting GCP metrics: {e}")
        
        return metrics

class KubernetesMetricsCollector:
    """Kubernetes cluster metrics collection"""
    
    def __init__(self) -> None:
        self.v1 = None
        self.apps_v1 = None
        self.metrics_v1beta1 = None
        self._initialize_k8s_client()
    
    def _initialize_k8s_client(self) -> None:
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except Exception as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                return
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        
        # Try to get metrics API
        try:
            from kubernetes import client as k8s_client
            self.metrics_v1beta1 = k8s_client.CustomObjectsApi()
        except Exception as e:
            logger.warning(f"Metrics API not available: {e}")
    
    async def collect_cluster_metrics(self) -> List[MetricData]:
        """Collect cluster-level metrics"""
        metrics = []
        if not self.v1:
            return metrics
        
        try:
            # Node metrics
            nodes = self.v1.list_node()
            total_nodes = len(nodes.items)
            ready_nodes = sum(1 for node in nodes.items 
                            if any(condition.status == "True" and condition.type == "Ready" 
                                  for condition in node.status.conditions))
            
            metrics.extend([
                MetricData(
                    name="kubernetes_nodes_total",
                    value=total_nodes,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Total number of nodes in cluster"
                ),
                MetricData(
                    name="kubernetes_nodes_ready",
                    value=ready_nodes,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Number of ready nodes in cluster"
                )
            ])
            
            # Pod metrics
            pods = self.v1.list_pod_for_all_namespaces()
            total_pods = len(pods.items)
            running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
            pending_pods = sum(1 for pod in pods.items if pod.status.phase == "Pending")
            failed_pods = sum(1 for pod in pods.items if pod.status.phase == "Failed")
            
            metrics.extend([
                MetricData(
                    name="kubernetes_pods_total",
                    value=total_pods,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Total number of pods in cluster"
                ),
                MetricData(
                    name="kubernetes_pods_running",
                    value=running_pods,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Number of running pods"
                ),
                MetricData(
                    name="kubernetes_pods_pending",
                    value=pending_pods,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Number of pending pods"
                ),
                MetricData(
                    name="kubernetes_pods_failed",
                    value=failed_pods,
                    timestamp=datetime.utcnow(),
                    labels={'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Number of failed pods"
                )
            ])
            
            # Namespace metrics
            namespaces = self.v1.list_namespace()
            total_namespaces = len(namespaces.items)
            
            metrics.append(MetricData(
                name="kubernetes_namespaces_total",
                value=total_namespaces,
                timestamp=datetime.utcnow(),
                labels={'cluster': 'ainflue-production'},
                metric_type='gauge',
                help_text="Total number of namespaces"
            ))
            
        except Exception as e:
            logger.error(f"Error collecting Kubernetes metrics: {e}")
        
        return metrics
    
    async def collect_resource_metrics(self) -> List[MetricData]:
        """Collect resource usage metrics from metrics server"""
        metrics = []
        if not self.metrics_v1beta1:
            return metrics
        
        try:
            # Node metrics
            node_metrics = self.metrics_v1beta1.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )
            
            for node in node_metrics.get('items', []):
                node_name = node['metadata']['name']
                usage = node['usage']
                
                # CPU usage
                cpu_usage = self._parse_k8s_resource(usage.get('cpu', '0'))
                metrics.append(MetricData(
                    name="kubernetes_node_cpu_usage_cores",
                    value=cpu_usage,
                    timestamp=datetime.utcnow(),
                    labels={'node': node_name, 'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Node CPU usage in cores",
                    unit="cores"
                ))
                
                # Memory usage
                memory_usage = self._parse_k8s_resource(usage.get('memory', '0Ki'))
                metrics.append(MetricData(
                    name="kubernetes_node_memory_usage_bytes",
                    value=memory_usage,
                    timestamp=datetime.utcnow(),
                    labels={'node': node_name, 'cluster': 'ainflue-production'},
                    metric_type='gauge',
                    help_text="Node memory usage in bytes",
                    unit="bytes"
                ))
            
            # Pod metrics
            pod_metrics = self.metrics_v1beta1.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="pods"
            )
            
            for pod in pod_metrics.get('items', []):
                pod_name = pod['metadata']['name']
                namespace = pod['metadata']['namespace']
                
                for container in pod.get('containers', []):
                    container_name = container['name']
                    usage = container['usage']
                    
                    # CPU usage
                    cpu_usage = self._parse_k8s_resource(usage.get('cpu', '0'))
                    metrics.append(MetricData(
                        name="kubernetes_container_cpu_usage_cores",
                        value=cpu_usage,
                        timestamp=datetime.utcnow(),
                        labels={
                            'pod': pod_name,
                            'container': container_name,
                            'namespace': namespace,
                            'cluster': 'ainflue-production'
                        },
                        metric_type='gauge',
                        help_text="Container CPU usage in cores",
                        unit="cores"
                    ))
                    
                    # Memory usage
                    memory_usage = self._parse_k8s_resource(usage.get('memory', '0Ki'))
                    metrics.append(MetricData(
                        name="kubernetes_container_memory_usage_bytes",
                        value=memory_usage,
                        timestamp=datetime.utcnow(),
                        labels={
                            'pod': pod_name,
                            'container': container_name,
                            'namespace': namespace,
                            'cluster': 'ainflue-production'
                        },
                        metric_type='gauge',
                        help_text="Container memory usage in bytes",
                        unit="bytes"
                    ))
        
        except Exception as e:
            logger.error(f"Error collecting resource metrics: {e}")
        
        return metrics
    
    def _parse_k8s_resource(self, resource_str: str) -> float:
        """Parse Kubernetes resource string to numeric value"""
        if not resource_str:
            return 0.0
        
        # Handle CPU resources (cores, milicores)
        if resource_str.endswith('m'):
            return float(resource_str[:-1]) / 1000
        elif resource_str.endswith('n'):
            return float(resource_str[:-1]) / 1_000_000_000
        
        # Handle memory resources
        units = {
            'Ki': 1024,
            'Mi': 1024**2,
            'Gi': 1024**3,
            'Ti': 1024**4,
            'K': 1000,
            'M': 1000**2,
            'G': 1000**3,
            'T': 1000**4,
        }
        
        for unit, multiplier in units.items():
            if resource_str.endswith(unit):
                return float(resource_str[:-len(unit)]) * multiplier
        
        return float(resource_str)

class ApplicationMetricsCollector:
    """Application-specific metrics collection"""
    
    def __init__(self) -> None:
        self.registry = prometheus_client.CollectorRegistry()
        self.custom_metrics = {}
        self._initialize_custom_metrics()
    
    def _initialize_custom_metrics(self) -> None:
        """Initialize custom application metrics"""
        # API metrics
        self.api_request_counter = prometheus_client.Counter(
            'ainflue_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.api_request_duration = prometheus_client.Histogram(
            'ainflue_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Content processing metrics
        self.content_uploads = prometheus_client.Counter(
            'ainflue_content_uploads_total',
            'Total content uploads',
            ['content_type', 'user_type'],
            registry=self.registry
        )
        
        self.ai_processing_duration = prometheus_client.Histogram(
            'ainflue_ai_processing_duration_seconds',
            'AI processing duration',
            ['model_type', 'content_type'],
            registry=self.registry
        )
        
        # User metrics
        self.active_users = prometheus_client.Gauge(
            'ainflue_active_users',
            'Currently active users',
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections = prometheus_client.Gauge(
            'ainflue_database_connections',
            'Database connections',
            ['database'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits = prometheus_client.Counter(
            'ainflue_cache_hits_total',
            'Cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses = prometheus_client.Counter(
            'ainflue_cache_misses_total',
            'Cache misses',
            ['cache_type'],
            registry=self.registry
        )
    
    async def collect_application_metrics(self) -> List[MetricData]:
        """Collect application-specific metrics"""
        metrics = []
        
        try:
            # Convert Prometheus metrics to MetricData
            for metric_family in self.registry.collect():
                for sample in metric_family.samples:
                    metrics.append(MetricData(
                        name=sample.name,
                        value=sample.value,
                        timestamp=datetime.utcnow(),
                        labels=dict(sample.labels),
                        metric_type=metric_family.type,
                        help_text=metric_family.documentation
                    ))
        
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
        
        return metrics

class MetricsCollectionEngine:
    """Main metrics collection engine coordinating all collectors"""
    
    def __init__(self, config -> None: MetricsCollectionConfig) -> None:
        self.config = config
        self.cloud_collector = CloudMetricsCollector()
        self.k8s_collector = KubernetesMetricsCollector()
        self.app_collector = ApplicationMetricsCollector()
        self.metrics_storage = []
        self.is_running = False
    
    async def start_collection(self) -> None:
        """Start the metrics collection process"""
        self.is_running = True
        logger.info("Starting metrics collection engine")
        
        while self.is_running:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.config.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection cycle: {e}")
                await asyncio.sleep(self.config.collection_interval)
    
    def stop_collection(self) -> None:
        """Stop the metrics collection process"""
        self.is_running = False
        logger.info("Stopping metrics collection engine")
    
    async def _collect_all_metrics(self) -> None:
        """Collect metrics from all sources"""
        all_metrics = []
        
        # Collect cloud metrics
        if self.config.enable_cloud_metrics:
            try:
                # AWS metrics
                aws_metrics = await self.cloud_collector.collect_aws_metrics(
                    'AWS/ECS', ['CPUUtilization', 'MemoryUtilization']
                )
                all_metrics.extend(aws_metrics)
                
                # Add other cloud providers as needed
            except Exception as e:
                logger.error(f"Error collecting cloud metrics: {e}")
        
        # Collect Kubernetes metrics
        if self.config.enable_kubernetes_metrics:
            try:
                k8s_cluster_metrics = await self.k8s_collector.collect_cluster_metrics()
                k8s_resource_metrics = await self.k8s_collector.collect_resource_metrics()
                all_metrics.extend(k8s_cluster_metrics)
                all_metrics.extend(k8s_resource_metrics)
            except Exception as e:
                logger.error(f"Error collecting Kubernetes metrics: {e}")
        
        # Collect application metrics
        if self.config.enable_application_metrics:
            try:
                app_metrics = await self.app_collector.collect_application_metrics()
                all_metrics.extend(app_metrics)
            except Exception as e:
                logger.error(f"Error collecting application metrics: {e}")
        
        # Store metrics
        await self._store_metrics(all_metrics)
        
        # Push to external systems
        await self._push_metrics(all_metrics)
        
        logger.info(f"Collected {len(all_metrics)} metrics")
    
    async def _store_metrics(self, metrics -> None: List[MetricData]) -> None:
        """Store metrics locally"""
        # Clean old metrics
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.config.retention_period)
        self.metrics_storage = [m for m in self.metrics_storage if m.timestamp > cutoff_time]
        
        # Add new metrics
        self.metrics_storage.extend(metrics)
        
        # Limit storage size
        if len(self.metrics_storage) > self.config.max_metrics_per_batch * 10:
            self.metrics_storage = self.metrics_storage[-self.config.max_metrics_per_batch * 10:]
    
    async def _push_metrics(self, metrics -> None: List[MetricData]) -> None:
        """Push metrics to external systems"""
        # Push to Prometheus Push Gateway if configured
        if self.config.push_gateway_endpoint:
            await self._push_to_prometheus(metrics)
        
        # Save metrics to file for debugging
        await self._save_metrics_to_file(metrics)
    
    async def _push_to_prometheus(self, metrics -> None: List[MetricData]) -> None:
        """Push metrics to Prometheus Push Gateway"""
        try:
            from prometheus_client import push_to_gateway, CollectorRegistry
            
            registry = CollectorRegistry()
            
            # Group metrics by type
            counters = {}
            gauges = {}
            histograms = {}
            
            for metric in metrics:
                if metric.metric_type == 'counter':
                    if metric.name not in counters:
                        counters[metric.name] = prometheus_client.Counter(
                            metric.name, metric.help_text or '', 
                            list(metric.labels.keys()), registry=registry
                        )
                    counters[metric.name].labels(**metric.labels)._value._value = metric.value
                
                elif metric.metric_type == 'gauge':
                    if metric.name not in gauges:
                        gauges[metric.name] = prometheus_client.Gauge(
                            metric.name, metric.help_text or '',
                            list(metric.labels.keys()), registry=registry
                        )
                    gauges[metric.name].labels(**metric.labels).set(metric.value)
            
            # Push to gateway
            push_to_gateway(
                self.config.push_gateway_endpoint,
                job='ainflue-metrics-collection',
                registry=registry
            )
            
            logger.info(f"Pushed {len(metrics)} metrics to Prometheus Push Gateway")
        
        except Exception as e:
            logger.error(f"Error pushing metrics to Prometheus: {e}")
    
    async def _save_metrics_to_file(self, metrics -> None: List[MetricData]) -> None:
        """Save metrics to file for debugging and backup"""
        try:
            metrics_data = [asdict(metric) for metric in metrics]
            
            # Convert datetime to string for JSON serialization
            for metric_data in metrics_data:
                metric_data['timestamp'] = metric_data['timestamp'].isoformat()
            
            filename = f"/var/log/ainflue/metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(metrics_data, indent=2))
            
            logger.debug(f"Saved {len(metrics)} metrics to {filename}")
        
        except Exception as e:
            logger.error(f"Error saving metrics to file: {e}")
    
    def get_metrics(self, metric_name: Optional[str] = None, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[MetricData]:
        """Get stored metrics with optional filtering"""
        filtered_metrics = self.metrics_storage
        
        if metric_name:
            filtered_metrics = [m for m in filtered_metrics if m.name == metric_name]
        
        if start_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
        
        if end_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
        
        return filtered_metrics

async def main() -> None:
    """Main function for testing"""
    config = MetricsCollectionConfig(
        collection_interval=30,
        prometheus_endpoint="http://localhost:9090",
        enable_cloud_metrics=True,
        enable_kubernetes_metrics=True,
        enable_application_metrics=True
    )
    
    engine = MetricsCollectionEngine(config)
    
    try:
        await engine.start_collection()
    except KeyboardInterrupt:
        engine.stop_collection()
        logger.info("Metrics collection stopped")

if __name__ == "__main__":
    asyncio.run(main())