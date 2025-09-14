"""
Alert Manager Configuration module
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

"""
Alert Manager Configuration for Ainflue Platform
===============================================

Enterprise-grade alerting system for infrastructure and application monitoring.
Supports multi-channel notifications, alert routing, and escalation policies.

Features:
- Multi-channel alert delivery (Email, Slack, PagerDuty, SMS)
- Alert routing and grouping
- Escalation policies and oncall management
- Alert correlation and suppression
- SLA monitoring and breach notifications
- Custom alert rules and thresholds
"""

import yaml
import json
import logging
import smtplib
import requests
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """Alert status states"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"

class NotificationChannel(Enum):
    """Notification channel types"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"

@dataclass
class Alert:
    """Alert definition"""
    name: str
    severity: AlertSeverity
    message: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    timestamp: datetime
    status: AlertStatus = AlertStatus.FIRING
    fingerprint: Optional[str] = None

@dataclass
class NotificationTarget:
    """Notification target configuration"""
    name: str
    channel: NotificationChannel
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    expression: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]

class AlertManagerConfiguration:
    """
    Enterprise Alert Manager Configuration
    
    Manages alerting rules, notification channels, and escalation policies
    for comprehensive infrastructure and application monitoring.
    """
    
    def __init__(self, config_path -> None: str = "/etc/alertmanager") -> None:
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logging()
        
        self.notification_targets: Dict[str, NotificationTarget] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        
        self._load_configuration()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup enterprise logging"""
        logger = logging.getLogger("alertmanager.configuration")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("/var/log/ainflue/alertmanager")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "configuration.log")
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _load_configuration(self) -> None:
        """Load existing configuration files"""
        try:
            # Load notification targets
            targets_file = self.config_path / "notification_targets.yaml"
            if targets_file.exists():
                with open(targets_file, 'r') as f:
                    targets_data = yaml.safe_load(f)
                    for target_data in targets_data.get('targets', []):
                        target = NotificationTarget(**target_data)
                        self.notification_targets[target.name] = target
            
            # Load alert rules
            rules_file = self.config_path / "alert_rules.yaml"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = yaml.safe_load(f)
                    for rule_data in rules_data.get('rules', []):
                        rule_data['severity'] = AlertSeverity(rule_data['severity'])
                        rule = AlertRule(**rule_data)
                        self.alert_rules[rule.name] = rule
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
    
    def add_notification_target(self, target: NotificationTarget) -> bool:
        """Add notification target"""
        try:
            self.notification_targets[target.name] = target
            self._save_notification_targets()
            self.logger.info(f"Added notification target: {target.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add notification target {target.name}: {str(e)}")
            return False
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add alert rule"""
        try:
            self.alert_rules[rule.name] = rule
            self._save_alert_rules()
            self.logger.info(f"Added alert rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add alert rule {rule.name}: {str(e)}")
            return False
    
    def _save_notification_targets(self) -> None:
        """Save notification targets to file"""
        targets_file = self.config_path / "notification_targets.yaml"
        
        targets_data = {
            "targets": [
                {
                    "name": target.name,
                    "channel": target.channel.value,
                    "config": target.config,
                    "enabled": target.enabled
                }
                for target in self.notification_targets.values()
            ]
        }
        
        with open(targets_file, 'w') as f:
            yaml.dump(targets_data, f, default_flow_style=False)
    
    def _save_alert_rules(self) -> None:
        """Save alert rules to file"""
        rules_file = self.config_path / "alert_rules.yaml"
        
        rules_data = {
            "rules": [
                {
                    "name": rule.name,
                    "expression": rule.expression,
                    "duration": rule.duration,
                    "severity": rule.severity.value,
                    "summary": rule.summary,
                    "description": rule.description,
                    "labels": rule.labels,
                    "annotations": rule.annotations
                }
                for rule in self.alert_rules.values()
            ]
        }
        
        with open(rules_file, 'w') as f:
            yaml.dump(rules_data, f, default_flow_style=False)
    
    def generate_alertmanager_config(self) -> str:
        """Generate Alertmanager configuration YAML"""
        config = {
            "global": {
                "smtp_smarthost": "localhost:587",
                "smtp_from": "alerts@ainflue.com",
                "slack_api_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            },
            "templates": [
                "/etc/alertmanager/templates/*.tmpl"
            ],
            "route": {
                "group_by": ["alertname", "cluster", "service"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default",
                "routes": [
                    {
                        "match": {"severity": "critical"},
                        "receiver": "critical-alerts",
                        "group_wait": "5s",
                        "repeat_interval": "15m"
                    },
                    {
                        "match": {"severity": "high"},
                        "receiver": "high-alerts",
                        "group_wait": "10s",
                        "repeat_interval": "30m"
                    },
                    {
                        "match_re": {"service": "api|database"},
                        "receiver": "platform-team",
                        "group_wait": "5s"
                    }
                ]
            },
            "receivers": self._generate_receivers(),
            "inhibit_rules": [
                {
                    "source_match": {"severity": "critical"},
                    "target_match": {"severity": "high"},
                    "equal": ["alertname", "cluster", "service"]
                }
            ]
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    def _generate_receivers(self) -> List[Dict[str, Any]]:
        """Generate receiver configurations"""
        receivers = [
            {
                "name": "default",
                "email_configs": [
                    {
                        "to": "ops@ainflue.com",
                        "subject": "Ainflue Alert: {{ .GroupLabels.alertname }}",
                        "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                    }
                ]
            }
        ]
        
        # Critical alerts receiver
        critical_configs = []
        high_configs = []
        platform_configs = []
        
        for target in self.notification_targets.values():
            if not target.enabled:
                continue
                
            if target.channel == NotificationChannel.EMAIL:
                email_config = {
                    "to": target.config["email"],
                    "subject": "🚨 CRITICAL: {{ .GroupLabels.alertname }}",
                    "body": self._get_email_template(),
                    "html": self._get_html_email_template()
                }
                critical_configs.append({"email_configs": [email_config]})
                high_configs.append({"email_configs": [email_config]})
                platform_configs.append({"email_configs": [email_config]})
            
            elif target.channel == NotificationChannel.SLACK:
                slack_config = {
                    "api_url": target.config["webhook_url"],
                    "channel": target.config["channel"],
                    "title": "Ainflue Alert: {{ .GroupLabels.alertname }}",
                    "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                    "color": "{{ if eq .Status \"firing\" }}danger{{ else }}good{{ end }}"
                }
                critical_configs.append({"slack_configs": [slack_config]})
                high_configs.append({"slack_configs": [slack_config]})
                platform_configs.append({"slack_configs": [slack_config]})
            
            elif target.channel == NotificationChannel.WEBHOOK:
                webhook_config = {
                    "url": target.config["url"],
                    "send_resolved": True
                }
                critical_configs.append({"webhook_configs": [webhook_config]})
        
        if critical_configs:
            receivers.append({
                "name": "critical-alerts",
                **{k: v for config in critical_configs for k, v in config.items()}
            })
        
        if high_configs:
            receivers.append({
                "name": "high-alerts",
                **{k: v for config in high_configs for k, v in config.items()}
            })
        
        if platform_configs:
            receivers.append({
                "name": "platform-team",
                **{k: v for config in platform_configs for k, v in config.items()}
            })
        
        return receivers
    
    def _get_email_template(self) -> str:
        """Get email alert template"""
        return """
{{ range .Alerts }}
Alert: {{ .Annotations.summary }}
Description: {{ .Annotations.description }}
Severity: {{ .Labels.severity }}
Service: {{ .Labels.service }}
Instance: {{ .Labels.instance }}
Started: {{ .StartsAt }}
{{ if .EndsAt }}Ended: {{ .EndsAt }}{{ end }}

{{ end }}
        """.strip()
    
    def _get_html_email_template(self) -> str:
        """Get HTML email alert template"""
        return """
<html>
<body>
<h2>Ainflue Platform Alert</h2>
{{ range .Alerts }}
<div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
    <h3 style="color: {{ if eq .Labels.severity "critical" }}red{{ else if eq .Labels.severity "high" }}orange{{ else }}blue{{ end }};">
        {{ .Annotations.summary }}
    </h3>
    <p><strong>Description:</strong> {{ .Annotations.description }}</p>
    <p><strong>Severity:</strong> {{ .Labels.severity }}</p>
    <p><strong>Service:</strong> {{ .Labels.service }}</p>
    <p><strong>Instance:</strong> {{ .Labels.instance }}</p>
    <p><strong>Started:</strong> {{ .StartsAt }}</p>
    {{ if .EndsAt }}<p><strong>Ended:</strong> {{ .EndsAt }}</p>{{ end }}
</div>
{{ end }}
</body>
</html>
        """.strip()
    
    def generate_prometheus_rules(self) -> str:
        """Generate Prometheus alerting rules"""
        rules_config = {
            "groups": [
                {
                    "name": "ainflue-infrastructure",
                    "rules": []
                },
                {
                    "name": "ainflue-application",
                    "rules": []
                }
            ]
        }
        
        # Add alert rules
        for rule in self.alert_rules.values():
            prometheus_rule = {
                "alert": rule.name,
                "expr": rule.expression,
                "for": rule.duration,
                "labels": {
                    **rule.labels,
                    "severity": rule.severity.value
                },
                "annotations": {
                    **rule.annotations,
                    "summary": rule.summary,
                    "description": rule.description
                }
            }
            
            # Categorize rules
            if any(keyword in rule.name.lower() for keyword in ["cpu", "memory", "disk", "network"]):
                rules_config["groups"][0]["rules"].append(prometheus_rule)
            else:
                rules_config["groups"][1]["rules"].append(prometheus_rule)
        
        return yaml.dump(rules_config, default_flow_style=False)
    
    def send_test_alert(self, target_name: str) -> bool:
        """Send test alert to specific target"""
        try:
            if target_name not in self.notification_targets:
                self.logger.error(f"Notification target {target_name} not found")
                return False
            
            target = self.notification_targets[target_name]
            
            test_alert = Alert(
                name="test-alert",
                severity=AlertSeverity.INFO,
                message="This is a test alert from Ainflue Alert Manager",
                labels={"service": "alertmanager", "environment": "test"},
                annotations={
                    "summary": "Test Alert",
                    "description": "This is a test alert to verify notification configuration"
                },
                timestamp=datetime.now()
            )
            
            return self._send_notification(target, test_alert)
            
        except Exception as e:
            self.logger.error(f"Failed to send test alert: {str(e)}")
            return False
    
    def _send_notification(self, target: NotificationTarget, alert: Alert) -> bool:
        """Send notification to specific target"""
        try:
            if target.channel == NotificationChannel.EMAIL:
                return self._send_email_notification(target, alert)
            elif target.channel == NotificationChannel.SLACK:
                return self._send_slack_notification(target, alert)
            elif target.channel == NotificationChannel.WEBHOOK:
                return self._send_webhook_notification(target, alert)
            else:
                self.logger.warning(f"Unsupported notification channel: {target.channel}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send notification via {target.channel}: {str(e)}")
            return False
    
    def _send_email_notification(self, target: NotificationTarget, alert: Alert) -> bool:
        """Send email notification"""
        try:
            smtp_server = target.config.get("smtp_server", "localhost")
            smtp_port = target.config.get("smtp_port", 587)
            username = target.config.get("username")
            password = target.config.get("password")
            
            msg = MimeMultipart()
            msg['From'] = target.config.get("from_email", "alerts@ainflue.com")
            msg['To'] = target.config["email"]
            msg['Subject'] = f"Ainflue Alert: {alert.name} [{alert.severity.value.upper()}]"
            
            body = f"""
Alert: {alert.name}
Severity: {alert.severity.value}
Status: {alert.status.value}
Message: {alert.message}
Timestamp: {alert.timestamp}

Labels: {json.dumps(alert.labels, indent=2)}
Annotations: {json.dumps(alert.annotations, indent=2)}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            if username and password:
                server.starttls()
                server.login(username, password)
            
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def _send_slack_notification(self, target: NotificationTarget, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            webhook_url = target.config["webhook_url"]
            
            color = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.HIGH: "warning",
                AlertSeverity.MEDIUM: "good",
                AlertSeverity.LOW: "good",
                AlertSeverity.INFO: "#36a64f"
            }.get(alert.severity, "good")
            
            payload = {
                "channel": target.config.get("channel", "#alerts"),
                "username": "Ainflue AlertManager",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": color,
                        "title": f"Alert: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Status",
                                "value": alert.status.value,
                                "short": True
                            },
                            {
                                "title": "Service",
                                "value": alert.labels.get("service", "Unknown"),
                                "short": True
                            },
                            {
                                "title": "Environment",
                                "value": alert.labels.get("environment", "Unknown"),
                                "short": True
                            }
                        ],
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            return False
    
    def _send_webhook_notification(self, target: NotificationTarget, alert: Alert) -> bool:
        """Send webhook notification"""
        try:
            webhook_url = target.config["url"]
            
            payload = {
                "alert": {
                    "name": alert.name,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "labels": alert.labels,
                    "annotations": alert.annotations
                }
            }
            
            headers = {"Content-Type": "application/json"}
            if "headers" in target.config:
                headers.update(target.config["headers"])
            
            response = requests.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {str(e)}")
            return False
    
    def create_default_rules(self) -> bool:
        """Create default alert rules for Ainflue platform"""
        try:
            default_rules = [
                AlertRule(
                    name="HighCPUUsage",
                    expression="(100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)) > 80",
                    duration="5m",
                    severity=AlertSeverity.HIGH,
                    summary="High CPU usage detected",
                    description="CPU usage is above 80% for more than 5 minutes",
                    labels={"category": "infrastructure"},
                    annotations={"runbook": "https://docs.ainflue.com/runbooks/high-cpu"}
                ),
                AlertRule(
                    name="HighMemoryUsage",
                    expression="(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85",
                    duration="5m",
                    severity=AlertSeverity.HIGH,
                    summary="High memory usage detected",
                    description="Memory usage is above 85% for more than 5 minutes",
                    labels={"category": "infrastructure"},
                    annotations={"runbook": "https://docs.ainflue.com/runbooks/high-memory"}
                ),
                AlertRule(
                    name="DiskSpaceLow",
                    expression="(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 90",
                    duration="1m",
                    severity=AlertSeverity.CRITICAL,
                    summary="Disk space critically low",
                    description="Disk space usage is above 90%",
                    labels={"category": "infrastructure"},
                    annotations={"runbook": "https://docs.ainflue.com/runbooks/disk-space"}
                ),
                AlertRule(
                    name="APIHighLatency",
                    expression="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5",
                    duration="5m",
                    severity=AlertSeverity.HIGH,
                    summary="API high latency detected",
                    description="95th percentile latency is above 500ms for more than 5 minutes",
                    labels={"category": "application"},
                    annotations={"runbook": "https://docs.ainflue.com/runbooks/api-latency"}
                ),
                AlertRule(
                    name="ServiceDown",
                    expression="up == 0",
                    duration="1m",
                    severity=AlertSeverity.CRITICAL,
                    summary="Service is down",
                    description="Service has been down for more than 1 minute",
                    labels={"category": "availability"},
                    annotations={"runbook": "https://docs.ainflue.com/runbooks/service-down"}
                )
            ]
            
            for rule in default_rules:
                self.add_alert_rule(rule)
            
            self.logger.info("Default alert rules created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create default rules: {str(e)}")
            return False
    
    def save_configuration(self) -> bool:
        """Save complete configuration to files"""
        try:
            # Save AlertManager configuration
            alertmanager_config = self.generate_alertmanager_config()
            with open(self.config_path / "alertmanager.yml", 'w') as f:
                f.write(alertmanager_config)
            
            # Save Prometheus rules
            prometheus_rules = self.generate_prometheus_rules()
            with open(self.config_path / "alert_rules.yml", 'w') as f:
                f.write(prometheus_rules)
            
            # Save notification targets and alert rules
            self._save_notification_targets()
            self._save_alert_rules()
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    manager = AlertManagerConfiguration()
    
    # Add notification targets
    email_target = NotificationTarget(
        name="ops-team-email",
        channel=NotificationChannel.EMAIL,
        config={
            "email": "ops@ainflue.com",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "alerts@ainflue.com",
            "password": "app_password"
        }
    )
    
    slack_target = NotificationTarget(
        name="ops-team-slack",
        channel=NotificationChannel.SLACK,
        config={
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "channel": "#alerts"
        }
    )
    
    manager.add_notification_target(email_target)
    manager.add_notification_target(slack_target)
    
    # Create default alert rules
    if manager.create_default_rules():
        print("✅ Default alert rules created")
    
    # Save configuration
    if manager.save_configuration():
        print("✅ Configuration saved successfully")
    
    # Test notification
    print("Testing Slack notification...")
    if manager.send_test_alert("ops-team-slack"):
        print("✅ Test alert sent successfully")
    else:
        print("❌ Failed to send test alert")