"""Multi-Cloud Monitoring System
================================

Enterprise-grade multi-cloud monitoring and observability platform
supporting AWS CloudWatch, Azure Monitor, GCP Operations, and more.

This module provides unified monitoring, alerting, log aggregation,
metrics collection, and performance analysis across multiple cloud
providers for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import statistics

import boto3
import httpx
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from google.cloud import monitoring_v3, logging as gcp_logging
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import pandas as pd
from botocore.exceptions import ClientError


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CloudProvider(Enum):
    """Supported cloud providers for monitoring."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    CLOUDFLARE = "cloudflare"
    HEROKU = "heroku"
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"
    GRAFANA = "grafana"


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Unified metric representation."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    provider: CloudProvider
    source: str  # Service/resource name
    region: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = "count"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert configuration and state."""
    id: str
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "value > 80"
    severity: AlertSeverity
    provider: CloudProvider
    enabled: bool = True
    threshold: float = 0.0
    duration_minutes: int = 5  # Alert after X minutes
    notification_channels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogEntry:
    """Unified log entry representation."""
    id: str
    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    provider: CloudProvider
    region: Optional[str] = None
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Monitoring dashboard configuration."""
    id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval: int = 60  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check configuration."""
    id: str
    name: str
    url: str
    method: str = "GET"
    expected_status: int = 200
    timeout_seconds: int = 30
    interval_seconds: int = 60
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    enabled: bool = True
    last_check: Optional[datetime] = None
    status: str = "unknown"  # healthy, unhealthy, unknown


class MultiCloudMonitoringSystem:
    """Enterprise multi-cloud monitoring and observability platform."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize multi-cloud monitoring system.
        
        Args:
            config: Configuration dict with provider credentials and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Provider clients
        self.aws_cloudwatch = None
        self.aws_logs = None
        self.azure_monitor = None
        self.gcp_monitoring = None
        self.gcp_logging = None
        
        # Prometheus registry for custom metrics
        self.prometheus_registry = CollectorRegistry()
        
        # Internal state
        self.metrics_buffer: List[Metric] = []
        self.alerts: Dict[str, Alert] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Log streaming
        self.log_buffer: List[LogEntry] = []
        self.log_filters: Dict[str, Any] = {}
        
        # Performance tracking
        self.monitoring_stats = {
            'metrics_collected': 0,
            'alerts_triggered': 0,
            'logs_processed': 0,
            'health_checks_performed': 0,
            'uptime_start': datetime.utcnow()
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider monitoring clients."""
        try:
            # AWS CloudWatch
            if 'aws' in self.config:
                aws_config = self.config['aws']
                self.aws_cloudwatch = boto3.client(
                    'cloudwatch',
                    aws_access_key_id=aws_config.get('access_key_id'),
                    aws_secret_access_key=aws_config.get('secret_access_key'),
                    region_name=aws_config.get('region', 'us-east-1')
                )
                
                self.aws_logs = boto3.client(
                    'logs',
                    aws_access_key_id=aws_config.get('access_key_id'),
                    aws_secret_access_key=aws_config.get('secret_access_key'),
                    region_name=aws_config.get('region', 'us-east-1')
                )
                self.logger.info("AWS CloudWatch and Logs clients initialized")
            
            # Azure Monitor
            if 'azure' in self.config:
                azure_config = self.config['azure']
                credential = DefaultAzureCredential()
                self.azure_monitor = MonitorManagementClient(
                    credential,
                    azure_config.get('subscription_id')
                )
                self.logger.info("Azure Monitor client initialized")
            
            # GCP Operations
            if 'gcp' in self.config:
                gcp_config = self.config['gcp']
                if 'credentials_path' in gcp_config:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_config['credentials_path']
                
                self.gcp_monitoring = monitoring_v3.MetricServiceClient()
                self.gcp_logging = gcp_logging.Client()
                self.logger.info("GCP Operations clients initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing monitoring providers: {e}")
            raise
    
    async def collect_metrics(self, provider: Optional[CloudProvider] = None) -> List[Metric]:
        """Collect metrics from cloud providers.
        
        Args:
            provider: Optional specific provider to query
            
        Returns:
            List of collected metrics
        """
        metrics = []
        
        try:
            if provider is None or provider == CloudProvider.AWS:
                metrics.extend(await self._collect_aws_metrics())
            
            if provider is None or provider == CloudProvider.AZURE:
                metrics.extend(await self._collect_azure_metrics())
            
            if provider is None or provider == CloudProvider.GCP:
                metrics.extend(await self._collect_gcp_metrics())
            
            # Store metrics in buffer
            self.metrics_buffer.extend(metrics)
            self.monitoring_stats['metrics_collected'] += len(metrics)
            
            # Check for alerts
            await self._check_alerts(metrics)
            
            self.logger.info(f"Collected {len(metrics)} metrics from cloud providers")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            raise
    
    async def _collect_aws_metrics(self) -> List[Metric]:
        """Collect metrics from AWS CloudWatch."""
        if not self.aws_cloudwatch:
            return []
        
        metrics = []
        try:
            # Get EC2 metrics
            ec2_metrics = await self._get_aws_ec2_metrics()
            metrics.extend(ec2_metrics)
            
            # Get RDS metrics
            rds_metrics = await self._get_aws_rds_metrics()
            metrics.extend(rds_metrics)
            
            # Get Lambda metrics
            lambda_metrics = await self._get_aws_lambda_metrics()
            metrics.extend(lambda_metrics)
            
            # Get Application Load Balancer metrics
            alb_metrics = await self._get_aws_alb_metrics()
            metrics.extend(alb_metrics)
            
        except ClientError as e:
            self.logger.error(f"AWS CloudWatch API error: {e}")
        except Exception as e:
            self.logger.error(f"Error collecting AWS metrics: {e}")
        
        return metrics
    
    async def _get_aws_ec2_metrics(self) -> List[Metric]:
        """Get AWS EC2 metrics."""
        metrics = []
        
        try:
            # Get list of EC2 instances
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=self.config['aws']['access_key_id'],
                aws_secret_access_key=self.config['aws']['secret_access_key'],
                region_name=self.config['aws']['region']
            )
            
            instances_response = ec2_client.describe_instances()
            
            for reservation in instances_response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    
                    # CPU Utilization
                    cpu_response = self.aws_cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.utcnow() - timedelta(minutes=10),
                        EndTime=datetime.utcnow(),
                        Period=300,
                        Statistics=['Average']
                    )
                    
                    if cpu_response['Datapoints']:
                        latest_cpu = cpu_response['Datapoints'][-1]
                        metrics.append(Metric(
                            name='ec2_cpu_utilization',
                            value=latest_cpu['Average'],
                            metric_type=MetricType.GAUGE,
                            timestamp=latest_cpu['Timestamp'],
                            provider=CloudProvider.AWS,
                            source=instance_id,
                            region=instance.get('Placement', {}).get('AvailabilityZone', '')[:-1],
                            unit='percent',
                            tags={
                                'instance_type': instance.get('InstanceType', ''),
                                'state': instance.get('State', {}).get('Name', '')
                            }
                        ))
                    
                    # Network In/Out
                    network_in_response = self.aws_cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='NetworkIn',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.utcnow() - timedelta(minutes=10),
                        EndTime=datetime.utcnow(),
                        Period=300,
                        Statistics=['Sum']
                    )
                    
                    if network_in_response['Datapoints']:
                        latest_network = network_in_response['Datapoints'][-1]
                        metrics.append(Metric(
                            name='ec2_network_in',
                            value=latest_network['Sum'],
                            metric_type=MetricType.COUNTER,
                            timestamp=latest_network['Timestamp'],
                            provider=CloudProvider.AWS,
                            source=instance_id,
                            unit='bytes',
                            tags={'instance_type': instance.get('InstanceType', '')}
                        ))
                        
        except Exception as e:
            self.logger.error(f"Error getting AWS EC2 metrics: {e}")
        
        return metrics
    
    async def _get_aws_rds_metrics(self) -> List[Metric]:
        """Get AWS RDS metrics."""
        metrics = []
        
        try:
            # Get RDS instances
            rds_client = boto3.client(
                'rds',
                aws_access_key_id=self.config['aws']['access_key_id'],
                aws_secret_access_key=self.config['aws']['secret_access_key'],
                region_name=self.config['aws']['region']
            )
            
            instances_response = rds_client.describe_db_instances()
            
            for db_instance in instances_response['DBInstances']:
                db_id = db_instance['DBInstanceIdentifier']
                
                # CPU Utilization
                cpu_response = self.aws_cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
                    StartTime=datetime.utcnow() - timedelta(minutes=10),
                    EndTime=datetime.utcnow(),
                    Period=300,
                    Statistics=['Average']
                )
                
                if cpu_response['Datapoints']:
                    latest_cpu = cpu_response['Datapoints'][-1]
                    metrics.append(Metric(
                        name='rds_cpu_utilization',
                        value=latest_cpu['Average'],
                        metric_type=MetricType.GAUGE,
                        timestamp=latest_cpu['Timestamp'],
                        provider=CloudProvider.AWS,
                        source=db_id,
                        unit='percent',
                        tags={
                            'engine': db_instance.get('Engine', ''),
                            'instance_class': db_instance.get('DBInstanceClass', '')
                        }
                    ))
                
                # Database connections
                connections_response = self.aws_cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='DatabaseConnections',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
                    StartTime=datetime.utcnow() - timedelta(minutes=10),
                    EndTime=datetime.utcnow(),
                    Period=300,
                    Statistics=['Average']
                )
                
                if connections_response['Datapoints']:
                    latest_connections = connections_response['Datapoints'][-1]
                    metrics.append(Metric(
                        name='rds_database_connections',
                        value=latest_connections['Average'],
                        metric_type=MetricType.GAUGE,
                        timestamp=latest_connections['Timestamp'],
                        provider=CloudProvider.AWS,
                        source=db_id,
                        unit='count',
                        tags={'engine': db_instance.get('Engine', '')}
                    ))
                    
        except Exception as e:
            self.logger.error(f"Error getting AWS RDS metrics: {e}")
        
        return metrics
    
    async def _collect_azure_metrics(self) -> List[Metric]:
        """Collect metrics from Azure Monitor."""
        if not self.azure_monitor:
            return []
        
        metrics = []
        try:
            # Azure metrics collection would be implemented here
            # This is a simplified placeholder
            
            # Get Virtual Machine metrics
            vm_metrics = await self._get_azure_vm_metrics()
            metrics.extend(vm_metrics)
            
            # Get SQL Database metrics
            sql_metrics = await self._get_azure_sql_metrics()
            metrics.extend(sql_metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting Azure metrics: {e}")
        
        return metrics
    
    async def _collect_gcp_metrics(self) -> List[Metric]:
        """Collect metrics from GCP Operations."""
        if not self.gcp_monitoring:
            return []
        
        metrics = []
        try:
            project_id = self.config['gcp']['project_id']
            
            # Create time interval for last 10 minutes
            now = datetime.utcnow()
            interval = monitoring_v3.TimeInterval({
                'end_time': {'seconds': int(now.timestamp())},
                'start_time': {'seconds': int((now - timedelta(minutes=10)).timestamp())}
            })
            
            # Get Compute Engine metrics
            gce_metrics = await self._get_gcp_compute_metrics(project_id, interval)
            metrics.extend(gce_metrics)
            
            # Get Cloud SQL metrics
            sql_metrics = await self._get_gcp_sql_metrics(project_id, interval)
            metrics.extend(sql_metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting GCP metrics: {e}")
        
        return metrics
    
    async def create_alert(
        self,
        name: str,
        description: str,
        metric_name: str,
        condition: str,
        severity: AlertSeverity,
        provider: CloudProvider,
        **kwargs
    ) -> Alert:
        """Create a new alert rule.
        
        Args:
            name: Alert name
            description: Alert description
            metric_name: Metric to monitor
            condition: Alert condition (e.g., "value > 80")
            severity: Alert severity
            provider: Cloud provider
            **kwargs: Additional alert configuration
            
        Returns:
            Created alert
        """
        try:
            alert_id = f"alert-{uuid.uuid4().hex[:8]}"
            
            alert = Alert(
                id=alert_id,
                name=name,
                description=description,
                metric_name=metric_name,
                condition=condition,
                severity=severity,
                provider=provider,
                threshold=kwargs.get('threshold', 0.0),
                duration_minutes=kwargs.get('duration_minutes', 5),
                notification_channels=kwargs.get('notification_channels', []),
                metadata=kwargs.get('metadata', {})
            )
            
            self.alerts[alert_id] = alert
            
            # Create provider-specific alert if supported
            if provider == CloudProvider.AWS:
                await self._create_aws_alarm(alert)
            elif provider == CloudProvider.AZURE:
                await self._create_azure_alert(alert)
            elif provider == CloudProvider.GCP:
                await self._create_gcp_alert(alert)
            
            self.logger.info(f"Created alert {alert_id}: {name}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            raise
    
    async def _create_aws_alarm(self, alert: Alert) -> None:
        """Create AWS CloudWatch alarm."""
        if not self.aws_cloudwatch:
            return
        
        try:
            # Parse condition to extract operator and threshold
            operator, threshold = self._parse_condition(alert.condition)
            
            alarm_name = f"ainflue-{alert.name}-{alert.id}"
            
            self.aws_cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator=operator,
                EvaluationPeriods=alert.duration_minutes,
                MetricName=alert.metric_name,
                Namespace='AWS/EC2',  # Would be dynamic based on metric
                Period=60,
                Statistic='Average',
                Threshold=threshold,
                ActionsEnabled=True,
                AlarmActions=alert.notification_channels,
                AlarmDescription=alert.description,
                Unit='Percent',
                Tags=[
                    {'Key': 'CreatedBy', 'Value': 'AinfluePlatform'},
                    {'Key': 'AlertId', 'Value': alert.id}
                ]
            )
            
            self.logger.info(f"Created AWS CloudWatch alarm: {alarm_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating AWS alarm: {e}")
    
    async def _check_alerts(self, metrics: List[Metric]) -> None:
        """Check metrics against alert conditions."""
        try:
            for metric in metrics:
                for alert in self.alerts.values():
                    if not alert.enabled:
                        continue
                    
                    if alert.metric_name != metric.name:
                        continue
                    
                    # Check condition
                    if self._evaluate_alert_condition(metric.value, alert.condition):
                        await self._trigger_alert(alert, metric)
                        
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def _evaluate_alert_condition(self, value: float, condition: str) -> bool:
        """Evaluate alert condition against metric value."""
        try:
            # Parse condition like "value > 80" or "value < 50"
            condition = condition.replace('value', str(value))
            return eval(condition)
        except:
            return False
    
    async def _trigger_alert(self, alert: Alert, metric: Metric) -> None:
        """Trigger an alert."""
        try:
            alert.last_triggered = datetime.utcnow()
            self.monitoring_stats['alerts_triggered'] += 1
            
            # Send notifications
            for channel in alert.notification_channels:
                await self._send_notification(alert, metric, channel)
            
            self.logger.warning(
                f"Alert triggered: {alert.name} - {metric.name}={metric.value} "
                f"(condition: {alert.condition})"
            )
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")
    
    async def _send_notification(self, alert: Alert, metric: Metric, channel: str) -> None:
        """Send alert notification to specified channel."""
        try:
            message = {
                'alert_id': alert.id,
                'alert_name': alert.name,
                'severity': alert.severity.value,
                'metric_name': metric.name,
                'metric_value': metric.value,
                'condition': alert.condition,
                'timestamp': metric.timestamp.isoformat(),
                'source': metric.source,
                'provider': metric.provider.value
            }
            
            # Send to different notification channels
            if channel.startswith('email:'):
                email = channel.split(':', 1)[1]
                await self._send_email_notification(email, alert, message)
            elif channel.startswith('webhook:'):
                webhook_url = channel.split(':', 1)[1]
                await self._send_webhook_notification(webhook_url, message)
            elif channel.startswith('slack:'):
                slack_webhook = channel.split(':', 1)[1]
                await self._send_slack_notification(slack_webhook, alert, message)
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    async def _send_webhook_notification(self, webhook_url: str, message: Dict[str, Any]) -> None:
        """Send webhook notification."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=message,
                    timeout=30
                )
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {e}")
    
    async def collect_logs(
        self,
        provider: Optional[CloudProvider] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEntry]:
        """Collect logs from cloud providers.
        
        Args:
            provider: Optional specific provider to query
            start_time: Start time for log collection
            end_time: End time for log collection
            
        Returns:
            List of log entries
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.utcnow()
        
        logs = []
        
        try:
            if provider is None or provider == CloudProvider.AWS:
                logs.extend(await self._collect_aws_logs(start_time, end_time))
            
            if provider is None or provider == CloudProvider.GCP:
                logs.extend(await self._collect_gcp_logs(start_time, end_time))
            
            # Store logs in buffer
            self.log_buffer.extend(logs)
            self.monitoring_stats['logs_processed'] += len(logs)
            
            self.logger.info(f"Collected {len(logs)} log entries")
            return logs
            
        except Exception as e:
            self.logger.error(f"Error collecting logs: {e}")
            raise
    
    async def _collect_aws_logs(self, start_time: datetime, end_time: datetime) -> List[LogEntry]:
        """Collect logs from AWS CloudWatch Logs."""
        if not self.aws_logs:
            return []
        
        logs = []
        try:
            # Get log groups
            log_groups_response = self.aws_logs.describe_log_groups(limit=50)
            
            for log_group in log_groups_response.get('logGroups', []):
                log_group_name = log_group['logGroupName']
                
                # Get log events
                events_response = self.aws_logs.filter_log_events(
                    logGroupName=log_group_name,
                    startTime=int(start_time.timestamp() * 1000),
                    endTime=int(end_time.timestamp() * 1000),
                    limit=100
                )
                
                for event in events_response.get('events', []):
                    log_entry = LogEntry(
                        id=f"aws-{event['eventId']}",
                        timestamp=datetime.fromtimestamp(event['timestamp'] / 1000),
                        level=self._parse_log_level(event['message']),
                        message=event['message'],
                        service=log_group_name,
                        provider=CloudProvider.AWS,
                        metadata={
                            'log_group': log_group_name,
                            'log_stream': event.get('logStreamName', '')
                        }
                    )
                    logs.append(log_entry)
                    
        except Exception as e:
            self.logger.error(f"Error collecting AWS logs: {e}")
        
        return logs
    
    async def create_dashboard(
        self,
        name: str,
        description: str,
        widgets: List[Dict[str, Any]]
    ) -> Dashboard:
        """Create a monitoring dashboard.
        
        Args:
            name: Dashboard name
            description: Dashboard description
            widgets: List of widget configurations
            
        Returns:
            Created dashboard
        """
        try:
            dashboard_id = f"dashboard-{uuid.uuid4().hex[:8]}"
            
            dashboard = Dashboard(
                id=dashboard_id,
                name=name,
                description=description,
                widgets=widgets
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            self.logger.info(f"Created dashboard {dashboard_id}: {name}")
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def create_health_check(
        self,
        name: str,
        url: str,
        **kwargs
    ) -> HealthCheck:
        """Create a health check.
        
        Args:
            name: Health check name
            url: URL to check
            **kwargs: Additional health check configuration
            
        Returns:
            Created health check
        """
        try:
            health_check_id = f"healthcheck-{uuid.uuid4().hex[:8]}"
            
            health_check = HealthCheck(
                id=health_check_id,
                name=name,
                url=url,
                method=kwargs.get('method', 'GET'),
                expected_status=kwargs.get('expected_status', 200),
                timeout_seconds=kwargs.get('timeout_seconds', 30),
                interval_seconds=kwargs.get('interval_seconds', 60),
                headers=kwargs.get('headers', {}),
                body=kwargs.get('body')
            )
            
            self.health_checks[health_check_id] = health_check
            
            self.logger.info(f"Created health check {health_check_id}: {name}")
            return health_check
            
        except Exception as e:
            self.logger.error(f"Error creating health check: {e}")
            raise
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks.
        
        Returns:
            Health check results
        """
        results = {
            'timestamp': datetime.utcnow(),
            'total_checks': len(self.health_checks),
            'healthy': 0,
            'unhealthy': 0,
            'checks': []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                for health_check in self.health_checks.values():
                    if not health_check.enabled:
                        continue
                    
                    try:
                        response = await client.request(
                            method=health_check.method,
                            url=health_check.url,
                            headers=health_check.headers,
                            content=health_check.body,
                            timeout=health_check.timeout_seconds
                        )
                        
                        is_healthy = response.status_code == health_check.expected_status
                        health_check.status = "healthy" if is_healthy else "unhealthy"
                        health_check.last_check = datetime.utcnow()
                        
                        if is_healthy:
                            results['healthy'] += 1
                        else:
                            results['unhealthy'] += 1
                        
                        results['checks'].append({
                            'id': health_check.id,
                            'name': health_check.name,
                            'url': health_check.url,
                            'status': health_check.status,
                            'response_time_ms': response.elapsed.total_seconds() * 1000,
                            'status_code': response.status_code,
                            'last_check': health_check.last_check
                        })
                        
                    except Exception as e:
                        health_check.status = "unhealthy"
                        health_check.last_check = datetime.utcnow()
                        results['unhealthy'] += 1
                        
                        results['checks'].append({
                            'id': health_check.id,
                            'name': health_check.name,
                            'url': health_check.url,
                            'status': 'unhealthy',
                            'error': str(e),
                            'last_check': health_check.last_check
                        })
                        
                        self.logger.error(f"Health check failed for {health_check.name}: {e}")
                
                self.monitoring_stats['health_checks_performed'] += len(self.health_checks)
                
        except Exception as e:
            self.logger.error(f"Error running health checks: {e}")
        
        return results
    
    async def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive monitoring report.
        
        Args:
            start_time: Report start time
            end_time: Report end time
            
        Returns:
            Monitoring report
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if end_time is None:
            end_time = datetime.utcnow()
        
        try:
            # Collect recent data
            metrics = await self.collect_metrics()
            logs = await self.collect_logs(start_time=start_time, end_time=end_time)
            health_results = await self.run_health_checks()
            
            # Analyze metrics
            metric_analysis = self._analyze_metrics(metrics, start_time, end_time)
            
            # Analyze logs
            log_analysis = self._analyze_logs(logs)
            
            # Generate report
            report = {
                'report_id': f"report-{uuid.uuid4().hex[:8]}",
                'generated_at': datetime.utcnow(),
                'period': {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_hours': (end_time - start_time).total_seconds() / 3600
                },
                'summary': {
                    'total_metrics': len(metrics),
                    'total_logs': len(logs),
                    'total_alerts': len(self.alerts),
                    'alerts_triggered': self.monitoring_stats['alerts_triggered'],
                    'health_checks': health_results,
                    'uptime_hours': (datetime.utcnow() - self.monitoring_stats['uptime_start']).total_seconds() / 3600
                },
                'metrics_analysis': metric_analysis,
                'log_analysis': log_analysis,
                'recommendations': await self._generate_recommendations(metrics, logs),
                'monitoring_stats': self.monitoring_stats.copy()
            }
            
            self.logger.info(f"Generated monitoring report {report['report_id']}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise
    
    def _analyze_metrics(
        self,
        metrics: List[Metric],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze collected metrics."""
        analysis = {
            'by_provider': {},
            'by_metric_type': {},
            'trending': {},
            'anomalies': []
        }
        
        try:
            # Group metrics by provider
            for metric in metrics:
                provider = metric.provider.value
                if provider not in analysis['by_provider']:
                    analysis['by_provider'][provider] = {
                        'count': 0,
                        'avg_value': 0,
                        'max_value': float('-inf'),
                        'min_value': float('inf')
                    }
                
                analysis['by_provider'][provider]['count'] += 1
                analysis['by_provider'][provider]['max_value'] = max(
                    analysis['by_provider'][provider]['max_value'],
                    metric.value
                )
                analysis['by_provider'][provider]['min_value'] = min(
                    analysis['by_provider'][provider]['min_value'],
                    metric.value
                )
            
            # Calculate averages
            for provider_data in analysis['by_provider'].values():
                if provider_data['count'] > 0:
                    provider_metrics = [m for m in metrics if m.provider.value == provider]
                    provider_data['avg_value'] = statistics.mean([m.value for m in provider_metrics])
            
            # Group by metric type
            for metric in metrics:
                metric_type = metric.metric_type.value
                if metric_type not in analysis['by_metric_type']:
                    analysis['by_metric_type'][metric_type] = 0
                analysis['by_metric_type'][metric_type] += 1
            
            # Simple anomaly detection (values > 2 standard deviations)
            if len(metrics) > 3:
                values = [m.value for m in metrics]
                mean_val = statistics.mean(values)
                std_dev = statistics.stdev(values)
                
                for metric in metrics:
                    if abs(metric.value - mean_val) > 2 * std_dev:
                        analysis['anomalies'].append({
                            'metric_name': metric.name,
                            'value': metric.value,
                            'timestamp': metric.timestamp,
                            'source': metric.source,
                            'deviation': abs(metric.value - mean_val) / std_dev
                        })
                        
        except Exception as e:
            self.logger.error(f"Error analyzing metrics: {e}")
        
        return analysis
    
    def _analyze_logs(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Analyze collected logs."""
        analysis = {
            'by_level': {},
            'by_service': {},
            'error_patterns': [],
            'top_errors': []
        }
        
        try:
            # Group by log level
            for log in logs:
                level = log.level.value
                if level not in analysis['by_level']:
                    analysis['by_level'][level] = 0
                analysis['by_level'][level] += 1
            
            # Group by service
            for log in logs:
                service = log.service
                if service not in analysis['by_service']:
                    analysis['by_service'][service] = {
                        'total': 0,
                        'errors': 0,
                        'warnings': 0
                    }
                
                analysis['by_service'][service]['total'] += 1
                if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                    analysis['by_service'][service]['errors'] += 1
                elif log.level == LogLevel.WARNING:
                    analysis['by_service'][service]['warnings'] += 1
            
            # Find error patterns
            error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
            error_messages = {}
            
            for log in error_logs:
                # Simple error pattern matching
                message_pattern = log.message[:100]  # First 100 chars
                if message_pattern not in error_messages:
                    error_messages[message_pattern] = 0
                error_messages[message_pattern] += 1
            
            # Top errors
            analysis['top_errors'] = sorted(
                [{'pattern': k, 'count': v} for k, v in error_messages.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]
            
        except Exception as e:
            self.logger.error(f"Error analyzing logs: {e}")
        
        return analysis
    
    async def _generate_recommendations(
        self,
        metrics: List[Metric],
        logs: List[LogEntry]
    ) -> List[Dict[str, Any]]:
        """Generate monitoring recommendations based on analysis."""
        recommendations = []
        
        try:
            # High CPU utilization recommendation
            cpu_metrics = [m for m in metrics if 'cpu' in m.name.lower()]
            if cpu_metrics:
                avg_cpu = statistics.mean([m.value for m in cpu_metrics])
                if avg_cpu > 80:
                    recommendations.append({
                        'type': 'performance',
                        'priority': 'high',
                        'title': 'High CPU utilization detected',
                        'description': f'Average CPU utilization is {avg_cpu:.1f}%. Consider scaling up resources.',
                        'affected_resources': list(set([m.source for m in cpu_metrics if m.value > 80]))
                    })
            
            # High error rate recommendation
            error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
            if len(error_logs) > len(logs) * 0.05:  # More than 5% error rate
                recommendations.append({
                    'type': 'reliability',
                    'priority': 'high',
                    'title': 'High error rate detected',
                    'description': f'Error rate is {len(error_logs)/len(logs)*100:.1f}%. Investigate application issues.',
                    'affected_services': list(set([log.service for log in error_logs]))
                })
            
            # Missing alerts recommendation
            if len(self.alerts) < 5:
                recommendations.append({
                    'type': 'monitoring',
                    'priority': 'medium',
                    'title': 'Insufficient alert coverage',
                    'description': 'Consider creating more alerts for critical metrics like CPU, memory, and error rates.',
                    'suggested_alerts': [
                        'CPU utilization > 80%',
                        'Memory utilization > 85%',
                        'Error rate > 5%',
                        'Response time > 2s'
                    ]
                })
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _parse_log_level(self, message: str) -> LogLevel:
        """Parse log level from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['critical', 'fatal']):
            return LogLevel.CRITICAL
        elif any(word in message_lower for word in ['error', 'exception']):
            return LogLevel.ERROR
        elif any(word in message_lower for word in ['warning', 'warn']):
            return LogLevel.WARNING
        elif any(word in message_lower for word in ['debug']):
            return LogLevel.DEBUG
        else:
            return LogLevel.INFO
    
    def _parse_condition(self, condition: str) -> Tuple[str, float]:
        """Parse alert condition to extract operator and threshold."""
        # Simple parsing for conditions like "value > 80"
        if '>' in condition:
            parts = condition.split('>')
            return 'GreaterThanThreshold', float(parts[1].strip())
        elif '<' in condition:
            parts = condition.split('<')
            return 'LessThanThreshold', float(parts[1].strip())
        else:
            return 'GreaterThanThreshold', 0.0
    
    def get_metrics_buffer(self) -> List[Metric]:
        """Get current metrics buffer."""
        return self.metrics_buffer.copy()
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics."""
        return self.monitoring_stats.copy()
    
    async def close(self) -> None:
        """Close monitoring system and cleanup resources."""
        try:
            self.logger.info("Closing multi-cloud monitoring system")
            
        except Exception as e:
            self.logger.error(f"Error closing monitoring system: {e}")


# Example usage
async def example_usage():
    """Example usage of MultiCloudMonitoringSystem."""
    
    config = {
        'aws': {
            'access_key_id': 'your-aws-key',
            'secret_access_key': 'your-aws-secret',
            'region': 'us-east-1'
        },
        'gcp': {
            'project_id': 'your-gcp-project',
            'credentials_path': '/path/to/credentials.json'
        },
        'azure': {
            'subscription_id': 'your-azure-subscription'
        }
    }
    
    monitoring = MultiCloudMonitoringSystem(config)
    
    try:
        # Collect metrics from all providers
        metrics = await monitoring.collect_metrics()
        print(f"Collected {len(metrics)} metrics")
        
        # Create critical CPU alert
        alert = await monitoring.create_alert(
            name="High CPU Utilization",
            description="Alert when CPU utilization exceeds 80%",
            metric_name="ec2_cpu_utilization",
            condition="value > 80",
            severity=AlertSeverity.HIGH,
            provider=CloudProvider.AWS,
            notification_channels=["email:admin@ainflue.com", "webhook:https://hooks.slack.com/..."]
        )
        
        print(f"Created alert: {alert.id}")
        
        # Create health check
        health_check = await monitoring.create_health_check(
            name="API Health Check",
            url="https://api.ainflue.com/health",
            interval_seconds=60,
            timeout_seconds=30
        )
        
        print(f"Created health check: {health_check.id}")
        
        # Run health checks
        health_results = await monitoring.run_health_checks()
        print(f"Health check results: {health_results['healthy']}/{health_results['total_checks']} healthy")
        
        # Generate comprehensive report
        report = await monitoring.generate_report()
        print(f"Generated report {report['report_id']} with {len(report['recommendations'])} recommendations")
        
        # Display key metrics
        stats = monitoring.get_monitoring_stats()
        print(f"Monitoring stats: {stats}")
        
    finally:
        await monitoring.close()


if __name__ == "__main__":
    asyncio.run(example_usage())