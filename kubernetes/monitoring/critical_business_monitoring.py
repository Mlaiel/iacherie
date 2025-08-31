"""
Critical Business Operations Monitoring Configuration
===================================================

Enhanced monitoring and alerting configuration for Ainflue platform's critical business operations.
Includes performance SLAs, business metrics monitoring, and comprehensive alerting strategies.

Author: Performance Optimization Team
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringCategory(Enum):
    """Monitoring categories"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    USER_EXPERIENCE = "user_experience"


@dataclass
class SLATarget:
    """Service Level Agreement target"""
    metric_name: str
    target_value: float
    comparison: str  # >, <, >=, <=, ==
    unit: str
    business_impact: str
    measurement_window: str = "5m"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    category: MonitoringCategory
    severity: AlertSeverity
    metric_query: str
    threshold: str
    duration: str = "5m"
    business_impact: str = ""
    runbook_url: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


class CriticalBusinessMonitoring:
    """Critical business operations monitoring configuration"""
    
    def __init__(self):
        self.sla_targets = self._define_sla_targets()
        self.alert_rules = self._define_alert_rules()
        self.monitoring_dashboards = self._define_monitoring_dashboards()
        self.notification_channels = self._define_notification_channels()
        
    def _define_sla_targets(self) -> Dict[str, List[SLATarget]]:
        """Define SLA targets for critical business operations"""



        return {
            "authentication": [
                SLATarget("api_response_time_seconds", 0.2, "<=", "seconds", "Users cannot login - direct revenue impact"),
                SLATarget("auth_success_rate", 0.99, ">=", "ratio", "Authentication failures block user access"),
                SLATarget("auth_availability", 0.999, ">=", "ratio", "Service unavailability blocks all user access")
            ],
            "content_upload": [
                SLATarget("upload_response_time_seconds", 2.0, "<=", "seconds", "Creators cannot upload content - direct revenue impact"),
                SLATarget("upload_success_rate", 0.95, ">=", "ratio", "Failed uploads frustrate creators"),
                SLATarget("upload_throughput_rps", 50, ">=", "requests/sec", "Low throughput limits platform growth")
            ],
            "fingerprint_processing": [
                SLATarget("fingerprint_processing_time_seconds", 30.0, "<=", "seconds", "Delayed protection affects creator confidence"),
                SLATarget("fingerprint_accuracy", 0.95, ">=", "ratio", "Poor accuracy allows content theft"),
                SLATarget("fingerprint_queue_size", 500, "<=", "count", "Large queue indicates processing bottleneck")
            ],
            "revenue_analytics": [
                SLATarget("analytics_response_time_seconds", 1.0, "<=", "seconds", "Slow analytics affect business decisions"),
                SLATarget("analytics_data_freshness_minutes", 15, "<=", "minutes", "Stale data leads to poor decisions"),
                SLATarget("analytics_accuracy", 0.99, ">=", "ratio", "Inaccurate data leads to wrong decisions")
            ],
            "protection_monitoring": [
                SLATarget("protection_check_time_seconds", 0.5, "<=", "seconds", "Slow protection checks delay response"),
                SLATarget("protection_alert_delivery_seconds", 60, "<=", "seconds", "Delayed alerts allow content theft"),
                SLATarget("protection_detection_accuracy", 0.95, ">=", "ratio", "Missed detections enable IP theft")
            ],
            "collaboration_matching": [
                SLATarget("matching_response_time_seconds", 2.0, "<=", "seconds", "Slow matching reduces user engagement"),
                SLATarget("matching_quality_score", 0.8, ">=", "ratio", "Poor matches reduce platform value"),
                SLATarget("matching_success_rate", 0.7, ">=", "ratio", "Low success rate frustrates users")
            ]
        }
    
    def _define_alert_rules(self) -> List[AlertRule]:
        """Define comprehensive alert rules for critical operations"""
        rules = []
        
        # Performance alerts
        performance_rules = [
            AlertRule(
                name="authentication_high_latency",
                description="Authentication API response time exceeds SLA",
                category=MonitoringCategory.PERFORMANCE,
                severity=AlertSeverity.CRITICAL,
                metric_query="avg_over_time(api_response_time_seconds{endpoint='/auth/login'}[5m])",
                threshold="> 0.2",
                duration="2m",
                business_impact="Users cannot log in - direct revenue impact",
                runbook_url="https://runbooks.ainflue.com/auth-performance",
                labels={"service": "authentication", "endpoint": "/auth/login"},
                annotations={
                    "summary": "Authentication API latency high",
                    "description": "Average response time for /auth/login is {{ $value }}s (SLA: 0.2s)"
                }
            ),
            AlertRule(
                name="content_upload_high_error_rate",
                description="Content upload error rate exceeds threshold",
                category=MonitoringCategory.PERFORMANCE,
                severity=AlertSeverity.CRITICAL,
                metric_query="rate(api_errors_total{endpoint='/content/upload'}[5m]) / rate(api_requests_total{endpoint='/content/upload'}[5m])",
                threshold="> 0.05",
                duration="3m",
                business_impact="Creators cannot upload content - direct revenue impact",
                runbook_url="https://runbooks.ainflue.com/content-upload-errors",
                labels={"service": "content", "endpoint": "/content/upload"},
                annotations={
                    "summary": "High error rate for content uploads",
                    "description": "Upload error rate is {{ $value | humanizePercentage }} (SLA: 5%)"
                }
            ),
            AlertRule(
                name="fingerprint_processing_queue_backup",
                description="AI fingerprinting queue backup exceeds capacity",
                category=MonitoringCategory.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                metric_query="fingerprint_queue_size",
                threshold="> 500",
                duration="5m",
                business_impact="Delayed content protection - indirect revenue impact",
                runbook_url="https://runbooks.ainflue.com/fingerprint-queue",
                labels={"service": "fingerprinting", "component": "queue"},
                annotations={
                    "summary": "Fingerprint processing queue backup",
                    "description": "Queue size is {{ $value }} items (SLA: 500 items)"
                }
            ),
            AlertRule(
                name="database_query_performance_degradation",
                description="Database query performance degraded",
                category=MonitoringCategory.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                metric_query="avg_over_time(db_query_duration_seconds{operation='SELECT'}[10m])",
                threshold="> 0.1",
                duration="5m",
                business_impact="Slow database queries affect all operations",
                runbook_url="https://runbooks.ainflue.com/database-performance",
                labels={"service": "database", "operation": "SELECT"},
                annotations={
                    "summary": "Database query performance degradation",
                    "description": "Average SELECT query time is {{ $value }}s (threshold: 0.1s)"
                }
            )
        ]
        
        # Business operation alerts
        business_rules = [
            AlertRule(
                name="revenue_significant_drop",
                description="Significant drop in hourly revenue detected",
                category=MonitoringCategory.BUSINESS,
                severity=AlertSeverity.CRITICAL,
                metric_query="(rate(revenue_total[1h]) - rate(revenue_total[1h] offset 24h)) / rate(revenue_total[1h] offset 24h) * 100",
                threshold="< -20",
                duration="15m",
                business_impact="Major revenue loss - immediate investigation required",
                runbook_url="https://runbooks.ainflue.com/revenue-drop",
                labels={"metric": "revenue", "timeframe": "hourly"},
                annotations={
                    "summary": "Significant revenue drop detected",
                    "description": "Hourly revenue dropped by {{ $value }}% compared to same time yesterday"
                }
            ),
            AlertRule(
                name="user_registration_drop",
                description="Significant drop in new user registrations",
                category=MonitoringCategory.BUSINESS,
                severity=AlertSeverity.WARNING,
                metric_query="increase(new_user_registrations_total[1h])",
                threshold="< 10",
                duration="30m",
                business_impact="Growth metric impact - marketing investigation needed",
                runbook_url="https://runbooks.ainflue.com/user-registration",
                labels={"metric": "user_growth", "timeframe": "hourly"},
                annotations={
                    "summary": "Low new user registration rate",
                    "description": "Only {{ $value }} new users registered in the last hour"
                }
            ),
            AlertRule(
                name="content_upload_volume_drop",
                description="Significant drop in content upload volume",
                category=MonitoringCategory.BUSINESS,
                severity=AlertSeverity.WARNING,
                metric_query="increase(content_uploads_total[1h])",
                threshold="< 50",
                duration="20m",
                business_impact="Reduced creator activity - platform engagement impact",
                runbook_url="https://runbooks.ainflue.com/content-volume",
                labels={"metric": "content_activity", "timeframe": "hourly"},
                annotations={
                    "summary": "Low content upload volume",
                    "description": "Only {{ $value }} content uploads in the last hour"
                }
            )
        ]
        
        # Security alerts
        security_rules = [
            AlertRule(
                name="suspicious_login_activity",
                description="High number of failed login attempts detected",
                category=MonitoringCategory.SECURITY,
                severity=AlertSeverity.CRITICAL,
                metric_query="rate(failed_login_attempts_total[5m]) * 60",
                threshold="> 100",
                duration="2m",
                business_impact="Potential security attack - user account safety at risk",
                runbook_url="https://runbooks.ainflue.com/security-login",
                labels={"security_event": "login_failures", "severity": "high"},
                annotations={
                    "summary": "High failed login attempt rate",
                    "description": "{{ $value }} failed login attempts per minute (threshold: 100/min)"
                }
            ),
            AlertRule(
                name="content_protection_breach_detected",
                description="Potential content protection breach detected",
                category=MonitoringCategory.SECURITY,
                severity=AlertSeverity.EMERGENCY,
                metric_query="protection_breach_confidence_score",
                threshold="> 0.8",
                duration="1m",
                business_impact="IP theft detected - immediate legal and technical response required",
                runbook_url="https://runbooks.ainflue.com/security-breach",
                labels={"security_event": "content_breach", "severity": "emergency"},
                annotations={
                    "summary": "Content protection breach detected",
                    "description": "Breach confidence score: {{ $value }} (threshold: 0.8)"
                }
            ),
            AlertRule(
                name="api_rate_limit_abuse",
                description="API rate limit abuse pattern detected",
                category=MonitoringCategory.SECURITY,
                severity=AlertSeverity.WARNING,
                metric_query="rate(rate_limit_violations_total[5m]) * 60",
                threshold="> 50",
                duration="3m",
                business_impact="Potential API abuse - service stability risk",
                runbook_url="https://runbooks.ainflue.com/api-abuse",
                labels={"security_event": "rate_limit_abuse", "component": "api"},
                annotations={
                    "summary": "API rate limit abuse detected",
                    "description": "{{ $value }} rate limit violations per minute (threshold: 50/min)"
                }
            )
        ]
        
        # Infrastructure alerts
        infrastructure_rules = [
            AlertRule(
                name="database_connection_pool_exhaustion",
                description="Database connection pool near exhaustion",
                category=MonitoringCategory.INFRASTRUCTURE,
                severity=AlertSeverity.CRITICAL,
                metric_query="(db_connections_active / db_connections_max) * 100",
                threshold="> 90",
                duration="3m",
                business_impact="Service degradation imminent - all operations affected",
                runbook_url="https://runbooks.ainflue.com/db-connections",
                labels={"component": "database", "resource": "connections"},
                annotations={
                    "summary": "Database connection pool near exhaustion",
                    "description": "Connection pool usage: {{ $value }}% (threshold: 90%)"
                }
            ),
            AlertRule(
                name="redis_cache_memory_critical",
                description="Redis cache memory usage critical",
                category=MonitoringCategory.INFRASTRUCTURE,
                severity=AlertSeverity.CRITICAL,
                metric_query="(redis_memory_used_bytes / redis_memory_max_bytes) * 100",
                threshold="> 90",
                duration="2m",
                business_impact="Cache performance degradation - slower response times",
                runbook_url="https://runbooks.ainflue.com/redis-memory",
                labels={"component": "redis", "resource": "memory"},
                annotations={
                    "summary": "Redis memory usage critical",
                    "description": "Redis memory usage: {{ $value }}% (threshold: 90%)"
                }
            ),
            AlertRule(
                name="application_cpu_high",
                description="High CPU usage across application instances",
                category=MonitoringCategory.INFRASTRUCTURE,
                severity=AlertSeverity.WARNING,
                metric_query="avg(cpu_usage_percent{job='ainflue-app'})",
                threshold="> 80",
                duration="10m",
                business_impact="Performance degradation - user experience impact",
                runbook_url="https://runbooks.ainflue.com/cpu-usage",
                labels={"component": "application", "resource": "cpu"},
                annotations={
                    "summary": "High CPU usage on application servers",
                    "description": "Average CPU usage: {{ $value }}% (threshold: 80%)"
                }
            ),
            AlertRule(
                name="disk_space_critical",
                description="Critical disk space on application servers",
                category=MonitoringCategory.INFRASTRUCTURE,
                severity=AlertSeverity.CRITICAL,
                metric_query="(1 - (disk_free_bytes / disk_total_bytes)) * 100",
                threshold="> 85",
                duration="5m",
                business_impact="Service failure imminent - immediate action required",
                runbook_url="https://runbooks.ainflue.com/disk-space",
                labels={"component": "storage", "resource": "disk"},
                annotations={
                    "summary": "Critical disk space usage",
                    "description": "Disk usage: {{ $value }}% (threshold: 85%)"
                }
            )
        ]
        
        # User experience alerts
        user_experience_rules = [
            AlertRule(
                name="page_load_time_degradation",
                description="Page load time degradation detected",
                category=MonitoringCategory.USER_EXPERIENCE,
                severity=AlertSeverity.WARNING,
                metric_query="avg_over_time(page_load_time_seconds[10m])",
                threshold="> 3.0",
                duration="5m",
                business_impact="Poor user experience - potential user churn",
                runbook_url="https://runbooks.ainflue.com/page-performance",
                labels={"component": "frontend", "metric": "page_load_time"},
                annotations={
                    "summary": "Page load time degradation",
                    "description": "Average page load time: {{ $value }}s (threshold: 3.0s)"
                }
            ),
            AlertRule(
                name="user_session_error_rate_high",
                description="High user session error rate",
                category=MonitoringCategory.USER_EXPERIENCE,
                severity=AlertSeverity.WARNING,
                metric_query="rate(user_session_errors_total[5m]) / rate(user_sessions_total[5m])",
                threshold="> 0.02",
                duration="5m",
                business_impact="User experience degradation - potential user frustration",
                runbook_url="https://runbooks.ainflue.com/session-errors",
                labels={"component": "frontend", "metric": "session_errors"},
                annotations={
                    "summary": "High user session error rate",
                    "description": "Session error rate: {{ $value | humanizePercentage }} (threshold: 2%)"
                }
            )
        ]
        
        # Combine all rules
        rules.extend(performance_rules)
        rules.extend(business_rules)
        rules.extend(security_rules)
        rules.extend(infrastructure_rules)
        rules.extend(user_experience_rules)
        
        return rules
    
    def _define_notification_channels(self) -> Dict[str, Dict[str, Any]]:
        """Define notification channels for different alert types"""



        return {
            "slack_critical": {
                "type": "slack",
                "webhook_url": "${SLACK_CRITICAL_WEBHOOK}",
                "channel": "#critical-alerts",
                "username": "Ainflue Critical Alert Bot",
                "severity_filter": [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY],
                "template": {
                    "title": " CRITICAL: {{ .GroupLabels.alertname }}",
                    "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                    "color": "danger"
                }
            },
            "slack_warnings": {
                "type": "slack",
                "webhook_url": "${SLACK_WARNINGS_WEBHOOK}",
                "channel": "#warnings",
                "username": "Ainflue Warning Bot",
                "severity_filter": [AlertSeverity.WARNING],
                "template": {
                    "title": " WARNING: {{ .GroupLabels.alertname }}",
                    "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                    "color": "warning"
                }
            },
            "email_critical": {
                "type": "email",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "${SMTP_USERNAME}",
                "password": "${SMTP_PASSWORD}",
                "from": "alerts@ainflue.com",
                "to": ["ops@ainflue.com", "cto@ainflue.com"],
                "severity_filter": [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY],
                "template": {
                    "subject": "[AINFLUE CRITICAL] {{ .GroupLabels.alertname }}",
                    "body": "Critical alert detected:\\n\\n{{ range .Alerts }}{{ .Annotations.description }}\\n{{ end }}"
                }
            },
            "pagerduty_emergency": {
                "type": "pagerduty",
                "integration_key": "${PAGERDUTY_INTEGRATION_KEY}",
                "severity_filter": [AlertSeverity.EMERGENCY],
                "escalation_policy": "critical-business-operations"
            },
            "webhook_monitoring": {
                "type": "webhook",
                "url": "https://monitoring.ainflue.com/api/alerts",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer ${MONITORING_API_TOKEN}"
                },
                "severity_filter": [AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            }
        }
    
    def _define_monitoring_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """Define Grafana dashboard configurations"""



        return {
            "critical_business_operations": {
                "title": "Critical Business Operations - Ainflue Platform",
                "tags": ["business", "critical", "sla"],
                "refresh": "30s",
                "time_range": "1h",
                "panels": [
                    {
                        "title": "SLA Compliance Overview",
                        "type": "stat",
                        "grid_pos": {"h": 8, "w": 24, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "avg(sla_compliance_ratio{service='authentication'})",
                                "legend": "Auth SLA"
                            },
                            {
                                "expr": "avg(sla_compliance_ratio{service='content'})",
                                "legend": "Content SLA"
                            },
                            {
                                "expr": "avg(sla_compliance_ratio{service='fingerprinting'})",
                                "legend": "Fingerprint SLA"
                            }
                        ],
                        "thresholds": [
                            {"color": "red", "value": 0.95},
                            {"color": "yellow", "value": 0.98},
                            {"color": "green", "value": 0.99}
                        ]
                    },
                    {
                        "title": "API Response Times",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(api_response_time_seconds_bucket{endpoint='/auth/login'}[5m]))",
                                "legend": "Auth P95"
                            },
                            {
                                "expr": "histogram_quantile(0.95, rate(api_response_time_seconds_bucket{endpoint='/content/upload'}[5m]))",
                                "legend": "Upload P95"
                            },
                            {
                                "expr": "histogram_quantile(0.95, rate(api_response_time_seconds_bucket{endpoint='/fingerprint/generate'}[5m]))",
                                "legend": "Fingerprint P95"
                            }
                        ],
                        "y_axis": {"unit": "seconds", "max": 2.0}
                    },
                    {
                        "title": "Business Metrics",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "rate(revenue_total[1h])",
                                "legend": "Hourly Revenue Rate"
                            },
                            {
                                "expr": "rate(new_user_registrations_total[1h])",
                                "legend": "New Users/Hour"
                            },
                            {
                                "expr": "rate(content_uploads_total[1h])",
                                "legend": "Content Uploads/Hour"
                            }
                        ]
                    },
                    {
                        "title": "Error Rates",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 0, "y": 16},
                        "targets": [
                            {
                                "expr": "rate(api_errors_total{endpoint='/auth/login'}[5m]) / rate(api_requests_total{endpoint='/auth/login'}[5m])",
                                "legend": "Auth Error Rate"
                            },
                            {
                                "expr": "rate(api_errors_total{endpoint='/content/upload'}[5m]) / rate(api_requests_total{endpoint='/content/upload'}[5m])",
                                "legend": "Upload Error Rate"
                            }
                        ],
                        "y_axis": {"unit": "percentunit", "max": 0.1}
                    },
                    {
                        "title": "System Resource Usage",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 12, "y": 16},
                        "targets": [
                            {
                                "expr": "avg(cpu_usage_percent{job='ainflue-app'})",
                                "legend": "CPU Usage %"
                            },
                            {
                                "expr": "avg(memory_usage_percent{job='ainflue-app'})",
                                "legend": "Memory Usage %"
                            },
                            {
                                "expr": "(redis_memory_used_bytes / redis_memory_max_bytes) * 100",
                                "legend": "Redis Memory %"
                            }
                        ],
                        "y_axis": {"unit": "percent", "max": 100}
                    }
                ]
            },
            "performance_load_testing": {
                "title": "Performance & Load Testing Results",
                "tags": ["performance", "load-testing", "optimization"],
                "refresh": "1m",
                "time_range": "6h",
                "panels": [
                    {
                        "title": "Load Test Summary",
                        "type": "table",
                        "grid_pos": {"h": 8, "w": 24, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "load_test_response_time_p95",
                                "format": "table",
                                "instant": True
                            },
                            {
                                "expr": "load_test_success_rate",
                                "format": "table",
                                "instant": True
                            },
                            {
                                "expr": "load_test_throughput_rps",
                                "format": "table",
                                "instant": True
                            }
                        ]
                    },
                    {
                        "title": "Database Query Performance",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))",
                                "legend": "P95 Query Time"
                            },
                            {
                                "expr": "rate(db_slow_queries_total[5m])",
                                "legend": "Slow Queries/sec"
                            },
                            {
                                "expr": "db_connections_active",
                                "legend": "Active Connections"
                            }
                        ]
                    },
                    {
                        "title": "Cache Performance",
                        "type": "timeseries",
                        "grid_pos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "cache_hit_ratio",
                                "legend": "Hit Ratio"
                            },
                            {
                                "expr": "cache_latency_ms",
                                "legend": "Cache Latency (ms)"
                            },
                            {
                                "expr": "cache_memory_usage_percent",
                                "legend": "Memory Usage %"
                            }
                        ]
                    }
                ]
            }
        }
    
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration with alerting rules"""
        rules_groups = {}
        
        # Group rules by category
        for rule in self.alert_rules:
            category = rule.category.value
            if category not in rules_groups:
                rules_groups[category] = {
                    "name": f"ainflue_{category}",
                    "rules": []
                }
            
            prometheus_rule = {
                "alert": rule.name,
                "expr": f"{rule.metric_query} {rule.threshold}",
                "for": rule.duration,
                "labels": {
                    "severity": rule.severity.value,
                    "category": rule.category.value,
                    **rule.labels
                },
                "annotations": {
                    "summary": rule.description,
                    "business_impact": rule.business_impact,
                    "runbook_url": rule.runbook_url,
                    **rule.annotations
                }
            }
            
            rules_groups[category]["rules"].append(prometheus_rule)
        
        return {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {"targets": ["alertmanager:9093"]}
                        ]
                    }
                ]
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
            "scrape_configs": [
                {
                    "job_name": "ainflue-app",
                    "static_configs": [
                        {"targets": ["ainflue-app:8000"]}
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "15s"
                },
                {
                    "job_name": "redis",
                    "static_configs": [
                        {"targets": ["redis-exporter:9121"]}
                    ]
                },
                {
                    "job_name": "postgres",
                    "static_configs": [
                        {"targets": ["postgres-exporter:9187"]}
                    ]
                }
            ],
            "groups": list(rules_groups.values())
        }
    
    def generate_alertmanager_config(self) -> Dict[str, Any]:
        """Generate Alertmanager configuration"""



        return {
            "global": {
                "smtp_smarthost": "smtp.gmail.com:587",
                "smtp_from": "alerts@ainflue.com"
            },
            "route": {
                "group_by": ["alertname", "cluster", "service"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default",
                "routes": [
                    {
                        "match": {"severity": "emergency"},
                        "receiver": "emergency-alerts",
                        "group_wait": "1s",
                        "repeat_interval": "5m"
                    },
                    {
                        "match": {"severity": "critical"},
                        "receiver": "critical-alerts",
                        "group_wait": "5s",
                        "repeat_interval": "15m"
                    },
                    {
                        "match": {"severity": "warning"},
                        "receiver": "warning-alerts",
                        "group_wait": "30s",
                        "repeat_interval": "1h"
                    }
                ]
            },
            "receivers": [
                {
                    "name": "default",
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_DEFAULT_WEBHOOK}",
                            "channel": "#general-alerts",
                            "title": "Ainflue Alert",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ]
                },
                {
                    "name": "emergency-alerts",
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_CRITICAL_WEBHOOK}",
                            "channel": "#critical-alerts",
                            "title": " EMERGENCY: {{ .GroupLabels.alertname }}",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                            "color": "danger"
                        }
                    ],
                    "email_configs": [
                        {
                            "to": "ops@ainflue.com",
                            "subject": "[EMERGENCY] {{ .GroupLabels.alertname }}",
                            "body": "Emergency alert:\\n\\n{{ range .Alerts }}{{ .Annotations.description }}\\n{{ end }}"
                        }
                    ],
                    "pagerduty_configs": [
                        {
                            "routing_key": "${PAGERDUTY_INTEGRATION_KEY}",
                            "description": "{{ .GroupLabels.alertname }}"
                        }
                    ]
                },
                {
                    "name": "critical-alerts",
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_CRITICAL_WEBHOOK}",
                            "channel": "#critical-alerts",
                            "title": " CRITICAL: {{ .GroupLabels.alertname }}",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                            "color": "danger"
                        }
                    ],
                    "email_configs": [
                        {
                            "to": "ops@ainflue.com",
                            "subject": "[CRITICAL] {{ .GroupLabels.alertname }}",
                            "body": "Critical alert:\\n\\n{{ range .Alerts }}{{ .Annotations.description }}\\n{{ end }}"
                        }
                    ]
                },
                {
                    "name": "warning-alerts",
                    "slack_configs": [
                        {
                            "api_url": "${SLACK_WARNINGS_WEBHOOK}",
                            "channel": "#warnings",
                            "title": " WARNING: {{ .GroupLabels.alertname }}",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                            "color": "warning"
                        }
                    ]
                }
            ],
            "inhibit_rules": [
                {
                    "source_match": {"severity": "critical"},
                    "target_match": {"severity": "warning"},
                    "equal": ["alertname", "cluster", "service"]
                }
            ]
        }
    
    def generate_deployment_plan(self) -> Dict[str, Any]:
        """Generate deployment plan for monitoring infrastructure"""



        return {
            "overview": {
                "components": ["Prometheus", "Alertmanager", "Grafana", "Exporters"],
                "alert_rules_count": len(self.alert_rules),
                "sla_targets_count": sum(len(targets) for targets in self.sla_targets.values()),
                "notification_channels": len(self.notification_channels),
                "dashboards": len(self.monitoring_dashboards)
            },
            "deployment_phases": {
                "phase_1": {
                    "name": "Core Monitoring Setup",
                    "duration": "1-2 days",
                    "components": ["Prometheus", "Basic alerting"],
                    "objectives": [
                        "Deploy Prometheus with basic metrics collection",
                        "Set up critical performance alerts",
                        "Configure basic notification channels"
                    ]
                },
                "phase_2": {
                    "name": "Business Metrics & Dashboards",
                    "duration": "2-3 days",
                    "components": ["Grafana", "Business dashboards", "SLA monitoring"],
                    "objectives": [
                        "Deploy Grafana with custom dashboards",
                        "Implement business metrics collection",
                        "Set up SLA monitoring and alerting"
                    ]
                },
                "phase_3": {
                    "name": "Advanced Alerting & Integration",
                    "duration": "1-2 days",
                    "components": ["Alertmanager", "PagerDuty", "Advanced notifications"],
                    "objectives": [
                        "Configure comprehensive alerting rules",
                        "Integrate with external services (PagerDuty, Slack)",
                        "Set up escalation policies"
                    ]
                }
            },
            "success_criteria": {
                "monitoring_coverage": "95% of critical operations monitored",
                "alert_response_time": "< 2 minutes for critical alerts",
                "dashboard_availability": "99.9% uptime for monitoring dashboards",
                "false_positive_rate": "< 5% for critical alerts"
            },
            "maintenance": {
                "alert_rule_review": "Monthly review of alert thresholds",
                "dashboard_updates": "Quarterly dashboard optimization",
                "sla_target_review": "Quarterly SLA target assessment",
                "monitoring_capacity": "Monthly capacity planning review"
            }
        }


# Example usage
if __name__ == "__main__":
    monitoring = CriticalBusinessMonitoring()
    
    # Generate configurations
    prometheus_config = monitoring.generate_prometheus_config()
    alertmanager_config = monitoring.generate_alertmanager_config()
    deployment_plan = monitoring.generate_deployment_plan()
    
    print("CRITICAL BUSINESS MONITORING CONFIGURATION")
    print("=" * 60)
    
    print(f"\\nAlert Rules: {len(monitoring.alert_rules)}")
    print(f"SLA Targets: {sum(len(targets) for targets in monitoring.sla_targets.values())}")
    print(f"Notification Channels: {len(monitoring.notification_channels)}")
    print(f"Monitoring Dashboards: {len(monitoring.monitoring_dashboards)}")
    
    print("\\nDeployment Plan:")
    for phase_name, phase_config in deployment_plan["deployment_phases"].items():
        print(f"  {phase_config['name']} ({phase_config['duration']})")
        for objective in phase_config['objectives']:
            print(f"    - {objective}")
    
    print("\\nSample Alert Rules:")
    for rule in monitoring.alert_rules[:3]:  # Show first 3 rules
        print(f"  {rule.name}: {rule.description} ({rule.severity.value})")
    
    # Save configurations to files for deployment
    with open("/tmp/prometheus-config.json", "w") as f:
        json.dump(prometheus_config, f, indent=2)
    
    with open("/tmp/alertmanager-config.json", "w") as f:
        json.dump(alertmanager_config, f, indent=2)
    
    with open("/tmp/monitoring-deployment-plan.json", "w") as f:
        json.dump(deployment_plan, f, indent=2)
    
    print("\\nConfiguration files saved to /tmp/")