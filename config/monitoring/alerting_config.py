"""
Alerting Configuration Module for IA-Influencer Agent Platform
==============================================================

Professional alerting and notification system configuration for
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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class NotificationChannel(Enum):
    """Notification channels"""
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    TELEGRAM = "telegram"
    SMS = "sms"


@dataclass
class AlertRule:
    """Prometheus alert rule configuration"""
    alert_name: str
    expression: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    runbook_url: Optional[str] = None


@dataclass
class NotificationReceiver:
    """Alertmanager notification receiver configuration"""
    name: str
    channel: NotificationChannel
    config: Dict[str, Any]
    send_resolved: bool = True


@dataclass
class AlertRoute:
    """Alertmanager routing configuration"""
    receiver: str
    group_by: List[str] = field(default_factory=list)
    group_wait: str = "10s"
    group_interval: str = "10s"
    repeat_interval: str = "1h"
    match: Dict[str, str] = field(default_factory=dict)
    match_re: Dict[str, str] = field(default_factory=dict)


class AlertingConfig:
    """Professional alerting configuration for IA-Influencer platform"""
    
    def __init__(self):
        self.alertmanager_port = int(os.getenv("ALERTMANAGER_PORT", "9093"))
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    def get_system_alert_rules(self) -> List[AlertRule]:
        """Get system-level alert rules"""



        return [
            AlertRule(
                alert_name="ServiceDown",
                expression="up == 0",
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Service {{ $labels.job }} is down",
                description="Service {{ $labels.job }} on instance {{ $labels.instance }} has been down for more than 1 minute.",
                labels={"team": "infrastructure"},
                runbook_url="https://docs.ia-influencer.com/runbooks/service-down"
            ),
            AlertRule(
                alert_name="HighMemoryUsage",
                expression="(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85",
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="High memory usage on {{ $labels.instance }}",
                description="Memory usage is above 85% on {{ $labels.instance }} for more than 5 minutes."
            ),
            AlertRule(
                alert_name="HighCPUUsage",
                expression="100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100) > 80",
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High CPU usage on {{ $labels.instance }}",
                description="CPU usage is above 80% on {{ $labels.instance }} for more than 10 minutes."
            ),
            AlertRule(
                alert_name="DiskSpaceLow",
                expression="(node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1",
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="Disk space low on {{ $labels.instance }}",
                description="Disk space is below 10% on {{ $labels.instance }} {{ $labels.mountpoint }}."
            )
        ]
    
    def get_application_alert_rules(self) -> List[AlertRule]:
        """Get application-level alert rules"""



        return [
            AlertRule(
                alert_name="HighErrorRate",
                expression="rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) > 0.1",
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                summary="High error rate in {{ $labels.service }}",
                description="Error rate is above 10% in {{ $labels.service }} for more than 5 minutes.",
                labels={"team": "backend"}
            ),
            AlertRule(
                alert_name="HighResponseTime",
                expression="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2",
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High response time in {{ $labels.service }}",
                description="95th percentile response time is above 2 seconds in {{ $labels.service }}."
            ),
            AlertRule(
                alert_name="DatabaseConnectionPoolExhausted",
                expression="db_connection_pool_active / db_connection_pool_max > 0.9",
                duration="2m",
                severity=AlertSeverity.CRITICAL,
                summary="Database connection pool nearly exhausted",
                description="Database connection pool usage is above 90% for {{ $labels.database }}."
            ),
            AlertRule(
                alert_name="CeleryQueueBacklog",
                expression="celery_queue_length > 1000",
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="Large Celery queue backlog",
                description="Celery queue {{ $labels.queue_name }} has more than 1000 pending tasks."
            )
        ]
    
    def get_ai_services_alert_rules(self) -> List[AlertRule]:
        """Get AI services alert rules"""



        return [
            AlertRule(
                alert_name="AIModelInferenceLatency",
                expression="histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket[5m])) > 10",
                duration="3m",
                severity=AlertSeverity.WARNING,
                summary="AI model inference latency high",
                description="95th percentile inference latency for {{ $labels.model_type }} is above 10 seconds.",
                labels={"team": "ai"}
            ),
            AlertRule(
                alert_name="AIModelAccuracyDrop",
                expression="ai_model_accuracy < 0.85",
                duration="10m",
                severity=AlertSeverity.CRITICAL,
                summary="AI model accuracy dropped",
                description="Model {{ $labels.model_name }} accuracy dropped below 85%.",
                labels={"team": "ai"}
            ),
            AlertRule(
                alert_name="GPUMemoryHigh",
                expression="ai_gpu_memory_used_percent > 90",
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="GPU memory usage high",
                description="GPU {{ $labels.device_id }} memory usage is above 90%."
            ),
            AlertRule(
                alert_name="AIProcessingQueueHigh",
                expression="ai_processing_queue_size > 500",
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="AI processing queue backlog",
                description="AI processing queue {{ $labels.queue_type }} has more than 500 pending items."
            )
        ]
    
    def get_content_protection_alert_rules(self) -> List[AlertRule]:
        """Get content protection alert rules"""



        return [
            AlertRule(
                alert_name="ContentProtectionDown",
                expression="up{job=\"content-protection\"} == 0",
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Content protection service down",
                description="Content protection service is unavailable.",
                labels={"team": "protection"}
            ),
            AlertRule(
                alert_name="FingerprintGenerationFailed",
                expression="rate(fingerprint_generation_failed_total[5m]) > 0.1",
                duration="5m",
                severity=AlertSeverity.WARNING,
                summary="High fingerprint generation failure rate",
                description="Fingerprint generation failure rate is above 10% for {{ $labels.content_type }}."
            ),
            AlertRule(
                alert_name="CrawlerFailureRate",
                expression="rate(crawler_requests_failed_total[5m]) / rate(crawler_requests_total[5m]) > 0.2",
                duration="10m",
                severity=AlertSeverity.WARNING,
                summary="High crawler failure rate",
                description="Crawler failure rate for {{ $labels.platform }} is above 20%."
            ),
            AlertRule(
                alert_name="SuspiciousContentMatch",
                expression="rate(content_matches_total{confidence=\"high\"}[1m]) > 10",
                duration="1m",
                severity=AlertSeverity.INFO,
                summary="High volume of content matches",
                description="Detected high volume of content matches for {{ $labels.content_type }}."
            )
        ]
    
    def get_security_alert_rules(self) -> List[AlertRule]:
        """Get security alert rules"""



        return [
            AlertRule(
                alert_name="AuthenticationFailureSpike",
                expression="rate(auth_attempts_total{status=\"failure\"}[5m]) > 10",
                duration="2m",
                severity=AlertSeverity.WARNING,
                summary="High authentication failure rate",
                description="Authentication failure rate is above 10 failures per second.",
                labels={"team": "security"}
            ),
            AlertRule(
                alert_name="SuspiciousActivity",
                expression="suspicious_activity_score > 0.8",
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Suspicious activity detected",
                description="Suspicious activity detected from {{ $labels.source_ip }} with score {{ $value }}.",
                labels={"team": "security"}
            ),
            AlertRule(
                alert_name="RateLimitExceeded",
                expression="rate(api_rate_limit_exceeded_total[5m]) > 5",
                duration="2m",
                severity=AlertSeverity.WARNING,
                summary="High rate limit violations",
                description="Rate limit exceeded more than 5 times per second on {{ $labels.endpoint }}."
            ),
            AlertRule(
                alert_name="SecurityScannerAlert",
                expression="security_vulnerability_score > 7.0",
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="High severity security vulnerability detected",
                description="Security vulnerability with score {{ $value }} detected in {{ $labels.component }}."
            )
        ]
    
    def get_business_alert_rules(self) -> List[AlertRule]:
        """Get business-level alert rules"""



        return [
            AlertRule(
                alert_name="RevenueDropSignificant",
                expression="(rate(revenue_generated_total[1h]) / rate(revenue_generated_total[1h] offset 24h)) < 0.7",
                duration="30m",
                severity=AlertSeverity.CRITICAL,
                summary="Significant revenue drop detected",
                description="Revenue has dropped by more than 30% compared to same time yesterday.",
                labels={"team": "business"}
            ),
            AlertRule(
                alert_name="UserActivityLow",
                expression="active_users_count < 100",
                duration="15m",
                severity=AlertSeverity.WARNING,
                summary="Low user activity",
                description="Active user count has dropped below 100."
            ),
            AlertRule(
                alert_name="ContentUploadsDrop",
                expression="rate(content_uploads_total[1h]) < 10",
                duration="30m",
                severity=AlertSeverity.WARNING,
                summary="Content uploads below threshold",
                description="Content upload rate has dropped below 10 per hour."
            ),
            AlertRule(
                alert_name="PaymentProcessingFailed",
                expression="rate(payment_processing_failed_total[5m]) > 0",
                duration="1m",
                severity=AlertSeverity.CRITICAL,
                summary="Payment processing failures",
                description="Payment processing failures detected for {{ $labels.platform }}."
            )
        ]
    
    def get_notification_receivers(self) -> List[NotificationReceiver]:
        """Get notification receiver configurations"""
        receivers = []
        
        # Email receiver
        if self.smtp_username and self.smtp_password:
            receivers.append(NotificationReceiver(
                name="email-critical",
                channel=NotificationChannel.EMAIL,
                config={
                    "to": ["admin@ia-influencer.com", "alerts@ia-influencer.com"],
                    "from": self.smtp_username,
                    "smarthost": f"{self.smtp_host}:{self.smtp_port}",
                    "auth_username": self.smtp_username,
                    "auth_password": self.smtp_password,
                    "subject": " {{ .GroupLabels.alertname }} - {{ .GroupLabels.severity }}",
                    "body": """
Alert: {{ .GroupLabels.alertname }}
Severity: {{ .GroupLabels.severity }}
Description: {{ .CommonAnnotations.description }}
Runbook: {{ .CommonAnnotations.runbook_url }}

Details:
{{ range .Alerts }}
- Instance: {{ .Labels.instance }}
- Value: {{ .Annotations.value }}
{{ end }}
"""
                }
            ))
        
        # Slack receiver
        if self.slack_webhook:
            receivers.append(NotificationReceiver(
                name="slack-alerts",
                channel=NotificationChannel.SLACK,
                config={
                    "api_url": self.slack_webhook,
                    "channel": "#alerts",
                    "username": "AlertManager",
                    "title": "{{ .GroupLabels.alertname }}",
                    "text": "{{ .CommonAnnotations.description }}",
                    "color": "{{ if eq .Status \"firing\" }}danger{{ else }}good{{ end }}"
                }
            ))
        
        # PagerDuty receiver
        if self.pagerduty_key:
            receivers.append(NotificationReceiver(
                name="pagerduty-critical",
                channel=NotificationChannel.PAGERDUTY,
                config={
                    "routing_key": self.pagerduty_key,
                    "description": "{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}"
                }
            ))
        
        # Telegram receiver
        if self.telegram_token and self.telegram_chat_id:
            receivers.append(NotificationReceiver(
                name="telegram-alerts",
                channel=NotificationChannel.TELEGRAM,
                config={
                    "bot_token": self.telegram_token,
                    "chat_id": self.telegram_chat_id,
                    "message": " *{{ .GroupLabels.alertname }}*\n{{ .CommonAnnotations.description }}",
                    "parse_mode": "Markdown"
                }
            ))
        
        return receivers
    
    def get_alert_routes(self) -> List[AlertRoute]:
        """Get alert routing configuration"""
        routes = [
            # Critical alerts to PagerDuty and email
            AlertRoute(
                receiver="pagerduty-critical",
                match={"severity": "critical"},
                group_by=["alertname", "cluster", "service"],
                group_wait="10s",
                group_interval="10s",
                repeat_interval="12h"
            ),
            # Security alerts to dedicated channel
            AlertRoute(
                receiver="slack-alerts",
                match={"team": "security"},
                group_by=["alertname"],
                group_wait="5s",
                repeat_interval="30m"
            ),
            # AI/ML alerts to AI team
            AlertRoute(
                receiver="email-critical",
                match={"team": "ai"},
                group_by=["alertname", "model_type"],
                repeat_interval="2h"
            ),
            # Business alerts to business team
            AlertRoute(
                receiver="slack-alerts",
                match={"team": "business"},
                group_by=["alertname"],
                repeat_interval="4h"
            ),
            # Default route for all other alerts
            AlertRoute(
                receiver="slack-alerts",
                group_by=["alertname", "cluster"],
                group_wait="10s",
                group_interval="5m",
                repeat_interval="1h"
            )
        ]
        
        return routes
    
    def get_alertmanager_config(self) -> Dict[str, Any]:
        """Get complete Alertmanager configuration"""
        receivers = self.get_notification_receivers()
        routes = self.get_alert_routes()
        
        # Convert receivers to Alertmanager format
        alertmanager_receivers = []
        for receiver in receivers:
            config = {"name": receiver.name}
            
            if receiver.channel == NotificationChannel.EMAIL:
                config["email_configs"] = [receiver.config]
            elif receiver.channel == NotificationChannel.SLACK:
                config["slack_configs"] = [receiver.config]
            elif receiver.channel == NotificationChannel.PAGERDUTY:
                config["pagerduty_configs"] = [receiver.config]
            elif receiver.channel == NotificationChannel.TELEGRAM:
                config["telegram_configs"] = [receiver.config]
            
            alertmanager_receivers.append(config)
        
        # Convert routes to Alertmanager format
        alertmanager_routes = []
        for route in routes:
            route_config = {
                "receiver": route.receiver,
                "group_by": route.group_by,
                "group_wait": route.group_wait,
                "group_interval": route.group_interval,
                "repeat_interval": route.repeat_interval
            }
            
            if route.match:
                route_config["match"] = route.match
            if route.match_re:
                route_config["match_re"] = route.match_re
            
            alertmanager_routes.append(route_config)
        
        return {
            "global": {
                "smtp_smarthost": f"{self.smtp_host}:{self.smtp_port}",
                "smtp_from": self.smtp_username,
                "smtp_auth_username": self.smtp_username,
                "smtp_auth_password": self.smtp_password
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default",
                "routes": alertmanager_routes
            },
            "receivers": alertmanager_receivers,
            "inhibit_rules": [
                {
                    "source_match": {"severity": "critical"},
                    "target_match": {"severity": "warning"},
                    "equal": ["alertname", "cluster", "service"]
                }
            ]
        }
    
    def get_all_alert_rules(self) -> Dict[str, List[AlertRule]]:
        """Get all alert rules organized by category"""



        return {
            "system": self.get_system_alert_rules(),
            "application": self.get_application_alert_rules(),
            "ai_services": self.get_ai_services_alert_rules(),
            "content_protection": self.get_content_protection_alert_rules(),
            "security": self.get_security_alert_rules(),
            "business": self.get_business_alert_rules()
        }
    
    def export_prometheus_rules(self) -> str:
        """Export all alert rules in Prometheus format"""
        all_rules = self.get_all_alert_rules()
        
        groups = []
        for category, rules in all_rules.items():
            group = {
                "name": f"ia-influencer-{category}",
                "rules": []
            }
            
            for rule in rules:
                prometheus_rule = {
                    "alert": rule.alert_name,
                    "expr": rule.expression,
                    "for": rule.duration,
                    "labels": {
                        "severity": rule.severity.value,
                        **rule.labels
                    },
                    "annotations": {
                        "summary": rule.summary,
                        "description": rule.description
                    }
                }
                
                if rule.runbook_url:
                    prometheus_rule["annotations"]["runbook_url"] = rule.runbook_url
                
                group["rules"].append(prometheus_rule)
            
            groups.append(group)
        
        return yaml.dump({"groups": groups}, default_flow_style=False, indent=2)
