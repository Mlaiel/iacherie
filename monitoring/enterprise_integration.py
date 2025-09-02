"""Enterprise Integration and Analytics Service
===========================================

Advanced enterprise monitoring and integration for production environments.
Integrates with major enterprise tools and cloud platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiohttp
import boto3
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential
import socket
import ssl


class IntegrationType(Enum):
    """
Types of enterprise integrations"""

    SLACK = "slack"
    TEAMS = "teams"
    JIRA = "jira"
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"
    SPLUNK = "splunk"
    AWS_CLOUDWATCH = "aws_cloudwatch"
    AZURE_MONITOR = "azure_monitor"
    GOOGLE_CLOUD_MONITORING = "google_cloud_monitoring"
    PAGERDUTY = "pagerduty"
    OPSGENIE = "opsgenie"


class AlertSeverity(Enum):
    """Alert severity levels for enterprise systems"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class EnterpriseAlert:
    """Enterprise alert structure"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class IntegrationConfig:
    """
Configuration for enterprise integrations"""
    integration_type: IntegrationType
    enabled: bool
    credentials: Dict[str, str]
    endpoints: Dict[str, str]
    settings: Dict[str, Any] = field(default_factory=dict)


class BaseEnterpriseIntegration:
    """
Base class for enterprise integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            logger.info(f"Executing __aexit__")
            
            # Implementation for __aexit__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__aexit__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__aexit__ failed: {e}")
            raise
            logger.info(f"Executing __aexit__")
            
            # Implementation for __aexit__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__aexit__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__aexit__ failed: {e}")
            raise
            await self.session.close()
    
    async def send_alert(self, alert: EnterpriseAlert) -> bool:
        """
Send alert to enterprise system"""
        self.logger.warning(f"Base implementation called for {self.__class__.__name__}")
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from enterprise system"""
        return {
            "integration_type": "base",
            "connection_status": False,
            "last_alert_sent": None,
            "total_alerts_sent": 0,
            "implementation_status": "base_class"
        }
    
    async def test_connection(self) -> bool:
        """Test connection to enterprise system"""
        self.logger.info(f"Testing connection for {self.__class__.__name__}")
        return False


class SlackIntegration(BaseEnterpriseIntegration):
    """Slack integration for alerts and notifications"""
    
    async def send_alert(self, alert: EnterpriseAlert) -> bool:
        """
Send alert to Slack"""
        try:
            webhook_url = self.config.endpoints.get("webhook_url")
            if not webhook_url:
                self.logger.error("Slack webhook URL not configured")
                return False
            
            # Format alert for Slack
            color_map = {
                AlertSeverity.CRITICAL: "#FF0000",
                AlertSeverity.HIGH: "#FF8C00",
                AlertSeverity.MEDIUM: "#FFD700",
                AlertSeverity.LOW: "#90EE90",
                AlertSeverity.INFO: "#87CEEB"
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#808080"),
                        "title": f"🚨 {alert.title}",
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.isoformat(),
                                "short": True
                            }
                        ],
                        "footer": "AI Influencer Platform",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            async with self.session.post(webhook_url, json=payload) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            webhook_url = self.config.endpoints.get("webhook_url")
            if not webhook_url:
                return False
            
            test_payload = {
                "text": "🟢 AI Influencer Platform - Connection Test Successful"
            }
            
            async with self.session.post(webhook_url, json=test_payload) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Slack connection test failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Slack integration metrics"""
        return {
            "integration_type": "slack",
            "last_alert_sent": getattr(self, "_last_alert_sent", None),
            "total_alerts_sent": getattr(self, "_total_alerts_sent", 0),
            "connection_status": await self.test_connection()
        }


class DatadogIntegration(BaseEnterpriseIntegration):
    """Datadog integration for metrics and alerts"""
    
    async def send_alert(self, alert: EnterpriseAlert) -> bool:
        """
Send alert to Datadog as event"""
        try:
            api_key = self.config.credentials.get("api_key")
            if not api_key:
                self.logger.error("Datadog API key not configured")
                return False
            
            # Datadog Events API
            events_url = "https://api.datadoghq.com/api/v1/events"
            
            # Map severity to Datadog alert type
            alert_type_map = {
                AlertSeverity.CRITICAL: "error",
                AlertSeverity.HIGH: "warning",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.LOW: "info",
                AlertSeverity.INFO: "info"
            }
            
            payload = {
                "title": alert.title,
                "text": alert.description,
                "date_happened": int(alert.timestamp.timestamp()),
                "priority": "high" if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH] else "normal",
                "alert_type": alert_type_map.get(alert.severity, "info"),
                "source_type_name": "ai_influencer_platform",
                "tags": alert.tags + [f"severity:{alert.severity.value}", f"source:{alert.source}"]
            }
            
            headers = {
                "DD-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(events_url, json=payload, headers=headers) as response:
                return response.status == 202
                
        except Exception as e:
            self.logger.error(f"Error sending Datadog alert: {e}")
            return False
    
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send custom metrics to Datadog"""
        try:
            api_key = self.config.credentials.get("api_key")
            if not api_key:
                return False
            
            metrics_url = "https://api.datadoghq.com/api/v1/series"
            
            # Format metrics for Datadog
            series = []
            current_time = int(datetime.utcnow().timestamp())
            
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    series.append({
                        "metric": f"ai_influencer.{metric_name}",
                        "points": [[current_time, value]],
                        "type": "gauge",
                        "tags": ["platform:ai_influencer"]
                    })
            
            payload = {"series": series}
            
            headers = {
                "DD-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(metrics_url, json=payload, headers=headers) as response:
                return response.status == 202
                
        except Exception as e:
            self.logger.error(f"Error sending Datadog metrics: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Datadog connection"""
        try:
            api_key = self.config.credentials.get("api_key")
            if not api_key:
                return False
            
            # Validate API key
            validate_url = "https://api.datadoghq.com/api/v1/validate"
            headers = {"DD-API-KEY": api_key}
            
            async with self.session.get(validate_url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Datadog connection test failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Datadog integration metrics"""
        return {
            "integration_type": "datadog",
            "connection_status": await self.test_connection(),
            "last_metric_sent": getattr(self, "_last_metric_sent", None),
            "total_metrics_sent": getattr(self, "_total_metrics_sent", 0)
        }


class PagerDutyIntegration(BaseEnterpriseIntegration):
    """PagerDuty integration for incident management"""
    
    async def send_alert(self, alert: EnterpriseAlert) -> bool:
        """
Send alert to PagerDuty as incident"""
        try:
            integration_key = self.config.credentials.get("integration_key")
            if not integration_key:
                self.logger.error("PagerDuty integration key not configured")
                return False
            
            events_url = "https://events.pagerduty.com/v2/enqueue"
            
            # Only send critical and high alerts to PagerDuty
            if alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                return True  # Skip but return success
            
            payload = {
                "routing_key": integration_key,
                "event_action": "trigger",
                "dedup_key": f"ai_influencer_{alert.alert_id}",
                "payload": {
                    "summary": alert.title,
                    "source": alert.source,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "component": "ai_influencer_platform",
                    "group": "monitoring",
                    "class": "application_alert",
                    "custom_details": alert.metadata
                }
            }
            
            async with self.session.post(events_url, json=payload) as response:
                return response.status == 202
                
        except Exception as e:
            self.logger.error(f"Error sending PagerDuty alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert in PagerDuty"""
        try:
            integration_key = self.config.credentials.get("integration_key")
            if not integration_key:
                return False
            
            events_url = "https://events.pagerduty.com/v2/enqueue"
            
            payload = {
                "routing_key": integration_key,
                "event_action": "resolve",
                "dedup_key": f"ai_influencer_{alert_id}"
            }
            
            async with self.session.post(events_url, json=payload) as response:
                return response.status == 202
                
        except Exception as e:
            self.logger.error(f"Error resolving PagerDuty alert: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test PagerDuty connection"""
        try:
            integration_key = self.config.credentials.get("integration_key")
            if not integration_key:
                return False
            
            # Send a test event
            events_url = "https://events.pagerduty.com/v2/enqueue"
            
            payload = {
                "routing_key": integration_key,
                "event_action": "trigger",
                "dedup_key": "ai_influencer_connection_test",
                "payload": {
                    "summary": "AI Influencer Platform - Connection Test",
                    "source": "connection_test",
                    "severity": "info"
                }
            }
            
            async with self.session.post(events_url, json=payload) as response:
                success = response.status == 202
                
                # Immediately resolve the test incident
                if success:
                    resolve_payload = {
                        "routing_key": integration_key,
                        "event_action": "resolve",
                        "dedup_key": "ai_influencer_connection_test"
                    }
                    await self.session.post(events_url, json=resolve_payload)
                
                return success
                
        except Exception as e:
            self.logger.error(f"PagerDuty connection test failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get PagerDuty integration metrics"""
        return {
            "integration_type": "pagerduty",
            "connection_status": await self.test_connection(),
            "last_incident_created": getattr(self, "_last_incident_created", None),
            "total_incidents_created": getattr(self, "_total_incidents_created", 0)
        }


class AWSCloudWatchIntegration(BaseEnterpriseIntegration):
    """AWS CloudWatch integration for metrics and alarms"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.cloudwatch_client = None
        self._initialize_aws_client()
    
    def _initialize_aws_client(self):
        """
Initialize AWS CloudWatch client"""
        try:
            aws_access_key = self.config.credentials.get("aws_access_key_id")
            aws_secret_key = self.config.credentials.get("aws_secret_access_key")
            region = self.config.settings.get("region", "us-east-1")
            
            if aws_access_key and aws_secret_key:
                self.cloudwatch_client = boto3.client(
                    'cloudwatch',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region
                )
            else:
                # Use default credential chain
                self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
                
        except Exception as e:
            self.logger.error(f"Error initializing AWS CloudWatch client: {e}")
    
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send custom metrics to CloudWatch"""
        try:
            if not self.cloudwatch_client:
                return False
            
            # Prepare metric data for CloudWatch
            metric_data = []
            namespace = self.config.settings.get("namespace", "AIInfluencer/Platform")
            
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_data.append({
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'Platform',
                                'Value': 'AIInfluencer'
                            }
                        ]
                    })
            
            if metric_data:
                # CloudWatch accepts maximum 20 metrics per call
                for i in range(0, len(metric_data), 20):
                    batch = metric_data[i:i+20]
                    self.cloudwatch_client.put_metric_data(
                        Namespace=namespace,
                        MetricData=batch
                    )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending CloudWatch metrics: {e}")
            return False
    
    async def create_alarm(self, alarm_config: Dict[str, Any]) -> bool:
        """Create CloudWatch alarm"""
        try:
            if not self.cloudwatch_client:
                return False
            
            self.cloudwatch_client.put_metric_alarm(**alarm_config)
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating CloudWatch alarm: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test AWS CloudWatch connection"""
        try:
            if not self.cloudwatch_client:
                return False
            
            # List metric namespaces to test connection
            self.cloudwatch_client.list_metrics(MaxRecords=1)
            return True
            
        except Exception as e:
            self.logger.error(f"CloudWatch connection test failed: {e}")
            return False
    
    async def send_alert(self, alert: EnterpriseAlert) -> bool:
        """Send alert as CloudWatch custom metric"""
        metrics = {
            f"Alert_{alert.severity.value}": 1,
            "TotalAlerts": 1
        }
        return await self.send_metrics(metrics)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get CloudWatch integration metrics"""
        return {
            "integration_type": "aws_cloudwatch",
            "connection_status": await self.test_connection(),
            "namespace": self.config.settings.get("namespace", "AIInfluencer/Platform"),
            "region": self.config.settings.get("region", "us-east-1")
        }


class EnterpriseIntegrationManager:
    """
    Central manager for enterprise integrations
    
    Coordinates multiple enterprise integrations and provides
    unified interface for alerts, metrics, and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.integrations: Dict[IntegrationType, BaseEnterpriseIntegration] = {}
        self.active_alerts: Dict[str, EnterpriseAlert] = {}
        
        # Metrics
        self.metrics = {
            "total_alerts_sent": 0,
            "total_metrics_sent": 0,
            "integration_errors": 0,
            "successful_integrations": 0
        }
    
    async def add_integration(self, integration_config: IntegrationConfig) -> bool:
        """Add enterprise integration"""
        try:
            integration_class_map = {
                IntegrationType.SLACK: SlackIntegration,
                IntegrationType.DATADOG: DatadogIntegration,
                IntegrationType.PAGERDUTY: PagerDutyIntegration,
                IntegrationType.AWS_CLOUDWATCH: AWSCloudWatchIntegration
            }
            
            integration_class = integration_class_map.get(integration_config.integration_type)
            if not integration_class:
                self.logger.error(f"Unsupported integration type: {integration_config.integration_type}")
                return False
            
            integration = integration_class(integration_config)
            
            # Test connection
            async with integration:
                if await integration.test_connection():
                    self.integrations[integration_config.integration_type] = integration
                    self.metrics["successful_integrations"] += 1
                    self.logger.info(f"Added {integration_config.integration_type.value} integration")
                    return True
                else:
                    self.logger.error(f"Failed to connect to {integration_config.integration_type.value}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error adding integration: {e}")
            self.metrics["integration_errors"] += 1
            return False
    
    async def send_alert_to_all(self, alert: EnterpriseAlert) -> Dict[IntegrationType, bool]:
        """Send alert to all configured integrations"""
        results = {}
        
        for integration_type, integration in self.integrations.items():
            try:
                async with integration:
                    success = await integration.send_alert(alert)
                    results[integration_type] = success
                    
                    if success:
                        self.metrics["total_alerts_sent"] += 1
                    else:
                        self.metrics["integration_errors"] += 1
                        
            except Exception as e:
                self.logger.error(f"Error sending alert to {integration_type.value}: {e}")
                results[integration_type] = False
                self.metrics["integration_errors"] += 1
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        
        return results
    
    async def send_metrics_to_all(self, metrics: Dict[str, Any]) -> Dict[IntegrationType, bool]:
        """Send metrics to all configured integrations that support metrics"""
        results = {}
        
        for integration_type, integration in self.integrations.items():
            # Only send to integrations that support metrics
            if hasattr(integration, 'send_metrics'):
                try:
                    async with integration:
                        success = await integration.send_metrics(metrics)
                        results[integration_type] = success
                        
                        if success:
                            self.metrics["total_metrics_sent"] += 1
                        else:
                            self.metrics["integration_errors"] += 1
                            
                except Exception as e:
                    self.logger.error(f"Error sending metrics to {integration_type.value}: {e}")
                    results[integration_type] = False
                    self.metrics["integration_errors"] += 1
        
        return results
    
    async def resolve_alert(self, alert_id: str) -> Dict[IntegrationType, bool]:
        """Resolve alert in all integrations"""
        results = {}
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            for integration_type, integration in self.integrations.items():
                if hasattr(integration, 'resolve_alert'):
                    try:
                        async with integration:
                            success = await integration.resolve_alert(alert_id)
                            results[integration_type] = success
                            
                    except Exception as e:
                        self.logger.error(f"Error resolving alert in {integration_type.value}: {e}")
                        results[integration_type] = False
        
        return results
    
    async def test_all_connections(self) -> Dict[IntegrationType, bool]:
        """Test all integration connections"""
        results = {}
        
        for integration_type, integration in self.integrations.items():
            try:
                async with integration:
                    success = await integration.test_connection()
                    results[integration_type] = success
                    
            except Exception as e:
                self.logger.error(f"Connection test failed for {integration_type.value}: {e}")
                results[integration_type] = False
        
        return results
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        status = {
            "total_integrations": len(self.integrations),
            "active_integrations": [],
            "connection_status": {},
            "metrics": self.metrics,
            "active_alerts_count": len([a for a in self.active_alerts.values() if not a.resolved])
        }
        
        # Test connections
        connection_results = await self.test_all_connections()
        
        for integration_type, integration in self.integrations.items():
            status["active_integrations"].append(integration_type.value)
            status["connection_status"][integration_type.value] = connection_results.get(integration_type, False)
        
        return status
    
    async def create_governance_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create and send governance alert to all integrations"""
        alert = EnterpriseAlert(
            alert_id=f"gov_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            severity=severity,
            source=source,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            tags=["governance", "compliance", "ai_influencer"]
        )
        
        # Send to all integrations
        results = await self.send_alert_to_all(alert)
        
        self.logger.info(f"Sent governance alert {alert.alert_id} to {len(results)} integrations")
        return alert.alert_id


# Factory function for easy integration setup
async def create_enterprise_integrations(integrations_config: List[Dict[str, Any]]) -> EnterpriseIntegrationManager:
    """
    Factory function to create enterprise integration manager with multiple integrations
    
    Args:
        integrations_config: List of integration configurations
        
    Returns:
        EnterpriseIntegrationManager: Configured integration manager
    """
    manager = EnterpriseIntegrationManager()
    
    for config_dict in integrations_config:
        try:
            integration_config = IntegrationConfig(
                integration_type=IntegrationType(config_dict["type"]),
                enabled=config_dict.get("enabled", True),
                credentials=config_dict.get("credentials", {}),
                endpoints=config_dict.get("endpoints", {}),
                settings=config_dict.get("settings", {})
            )
            
            if integration_config.enabled:
                await manager.add_integration(integration_config)
                
        except Exception as e:
            logging.getLogger(__name__).error(f"Error configuring integration: {e}")
    
    return manager