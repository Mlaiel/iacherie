"""🚨 Technical Alerts Module - Infrastructure & Security Monitoring
================================================================

Advanced technical alert management for infrastructure monitoring and security threat detection.
Monitors system health, performance, and security indicators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import json

from .intelligent_alert_manager import (
    IntelligentAlertManager, AlertCategory, AlertSeverity, 
    AlertType, AlertRule, IntelligentAlert
)

logger = logging.getLogger(__name__)


class TechnicalMetric(Enum):
    """
Technical metrics for monitoring"""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_LATENCY = "network_latency"
    SERVICE_AVAILABILITY = "service_availability"
    API_RESPONSE_TIME = "api_response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SECURITY_THREAT_SCORE = "security_threat_score"


class SecurityThreatLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class TechnicalMetrics:
    """Technical metrics data structure"""
    timestamp: datetime
    
    # System metrics
    cpu_usage: float  # Percentage
    memory_usage: float  # Percentage
    disk_usage: float  # Percentage
    network_latency: float  # Milliseconds
    
    # Service metrics
    service_availability: float  # Percentage (0-100)
    api_response_time: float  # Milliseconds
    error_rate: float  # Percentage (0-1)
    throughput: float  # Requests per second
    
    # Security metrics
    security_threat_score: float  # 0-1 scale
    failed_logins: int
    suspicious_activities: int
    blocked_ips: int
    security_events: List[Dict[str, Any]]
    
    # Additional context
    service_name: str = "unknown"
    environment: str = "production"
    region: str = "default"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: str
    threat_level: SecurityThreatLevel
    source_ip: str
    target_resource: str
    description: str
    metadata: Dict[str, Any]
    blocked: bool = False
    resolved: bool = False


class TechnicalAlertManager:
    """
    Advanced technical alert management for infrastructure and security monitoring
    
    Features:
    - Infrastructure health monitoring
    - Performance degradation detection
    - Security threat detection and response
    - Service availability monitoring
    - Resource exhaustion alerts
    - API performance monitoring
    """
    
    def __init__(self, alert_manager -> None: IntelligentAlertManager) -> None:
        """
Initialize technical alert manager"""
        self.alert_manager = alert_manager
        self.technical_metrics_history: List[TechnicalMetrics] = []
        self.security_events: List[SecurityEvent] = []
        self.service_baselines: Dict[str, Dict[str, float]] = {}
        
        # Technical alert thresholds
        self.thresholds = {
            # Infrastructure thresholds
            "cpu_critical": 90.0,
            "cpu_warning": 80.0,
            "memory_critical": 90.0,
            "memory_warning": 85.0,
            "disk_critical": 95.0,
            "disk_warning": 90.0,
            
            # Performance thresholds
            "response_time_critical": 10000,  # 10 seconds
            "response_time_warning": 5000,    # 5 seconds
            "error_rate_critical": 0.10,      # 10%
            "error_rate_warning": 0.05,       # 5%
            "availability_critical": 0.99,    # 99%
            "availability_warning": 0.995,    # 99.5%
            
            # Security thresholds
            "threat_score_emergency": 0.9,
            "threat_score_critical": 0.8,
            "threat_score_warning": 0.6,
            "failed_logins_critical": 100,
            "failed_logins_warning": 50,
            "suspicious_activities_critical": 20,
            "suspicious_activities_warning": 10,
        }
        
        self._initialize_technical_rules()
        logger.info("TechnicalAlertManager initialized")
    
    def _initialize_technical_rules(self) -> None:
        """Initialize technical alert rules"""
        
        # Infrastructure Alerts
        
        # Critical CPU Usage
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="technical_cpu_critical",
            name="Critical CPU Usage",
            category=AlertCategory.TECHNICAL,
            alert_type=AlertType.RESOURCE_EXHAUSTION,
            severity=AlertSeverity.CRITICAL,
            expression="cpu_usage > 90",
            threshold={
                "cpu_percent": 90,
                "duration": "5m",
                "service_impact": "high"
            },
            duration="5m",
            escalation_levels=[
                {"level": 1, "delay": "10m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "30m", "channels": ["email", "slack", "phone"]}
            ],
            correlation_rules=["technical_memory_critical", "technical_performance_degradation"]
        ))
        
        # Service Down Alert
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="technical_service_down_emergency",
            name="Service Down - Emergency",
            category=AlertCategory.TECHNICAL,
            alert_type=AlertType.SERVICE_DOWN,
            severity=AlertSeverity.EMERGENCY,
            expression="service_availability < 99",
            threshold={
                "availability_percent": 99,
                "grace_period": "1m"
            },
            duration="1m",
            auto_resolve=True,
            escalation_levels=[
                {"level": 1, "delay": "0m", "channels": ["email", "slack", "phone", "pagerduty"]},
                {"level": 2, "delay": "10m", "channels": ["email", "slack", "phone", "pagerduty", "sms"]}
            ]
        ))
        
        # API Performance Degradation
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="technical_api_performance_critical",
            name="Critical API Performance Degradation",
            category=AlertCategory.TECHNICAL,
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.CRITICAL,
            expression="api_response_time > 10000 or error_rate > 0.10",
            threshold={
                "response_time_ms": 10000,
                "error_rate": 0.10,
                "sample_size": 100
            },
            duration="10m",
            escalation_levels=[
                {"level": 1, "delay": "15m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "45m", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Security Alerts
        
        # Security Breach Emergency
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="security_breach_emergency",
            name="Security Breach - Emergency Response",
            category=AlertCategory.SECURITY,
            alert_type=AlertType.SECURITY_BREACH,
            severity=AlertSeverity.EMERGENCY,
            expression="security_threat_score > 0.9",
            threshold={
                "threat_score": 0.9,
                "confidence": 0.95,
                "immediate_response": True
            },
            duration="1m",
            auto_resolve=False,
            suppress_duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "0m", "channels": ["email", "slack", "phone", "pagerduty"]},
                {"level": 2, "delay": "5m", "channels": ["email", "slack", "phone", "pagerduty", "sms"]}
            ]
        ))
        
        # Suspicious Activity Detection
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="security_suspicious_activity_critical",
            name="Critical Suspicious Activity",
            category=AlertCategory.SECURITY,
            alert_type=AlertType.SUSPICIOUS_ACTIVITY,
            severity=AlertSeverity.CRITICAL,
            expression="suspicious_activities > 20 or failed_logins > 100",
            threshold={
                "suspicious_activities": 20,
                "failed_logins": 100,
                "time_window": "15m"
            },
            duration="5m",
            escalation_levels=[
                {"level": 1, "delay": "10m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "30m", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Authentication Failure Spike
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="security_auth_failure_spike",
            name="Authentication Failure Spike",
            category=AlertCategory.SECURITY,
            alert_type=AlertType.AUTHENTICATION_FAILURE,
            severity=AlertSeverity.WARNING,
            expression="failed_logins > 50",
            threshold={
                "failed_logins": 50,
                "time_window": "10m",
                "unique_ips": 5
            },
            duration="10m",
            escalation_levels=[
                {"level": 1, "delay": "20m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "1h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        logger.info("Technical alert rules initialized")
    
    async def evaluate_technical_metrics(self, metrics: TechnicalMetrics) -> List[IntelligentAlert]:
        """Evaluate technical metrics and trigger alerts"""
        triggered_alerts = []
        
        # Store metrics for trend analysis
        self.technical_metrics_history.append(metrics)
        
        # Keep only last 24 hours of history
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.technical_metrics_history = [
            m for m in self.technical_metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        try:
            # Evaluate infrastructure alerts
            infra_alerts = await self._evaluate_infrastructure_alerts(metrics)
            triggered_alerts.extend(infra_alerts)
            
            # Evaluate performance alerts
            perf_alerts = await self._evaluate_performance_alerts(metrics)
            triggered_alerts.extend(perf_alerts)
            
            # Evaluate security alerts
            security_alerts = await self._evaluate_security_alerts(metrics)
            triggered_alerts.extend(security_alerts)
            
            # Update service baselines
            await self._update_service_baselines(metrics)
            
            logger.debug(f"Evaluated technical metrics, triggered {len(triggered_alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error evaluating technical metrics: {e}")
        
        return triggered_alerts
    
    async def _evaluate_infrastructure_alerts(self, metrics: TechnicalMetrics) -> List[IntelligentAlert]:
        """Evaluate infrastructure-related alerts"""
        alerts = []
        
        try:
            # CPU Usage Alert
            if metrics.cpu_usage >= self.thresholds["cpu_critical"]:
                alert_metrics = {
                    "cpu_usage": metrics.cpu_usage,
                    "threshold": self.thresholds["cpu_critical"],
                    "service_name": metrics.service_name,
                    "environment": metrics.environment
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["technical_cpu_critical"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
            # Memory Usage Alert
            if metrics.memory_usage >= self.thresholds["memory_critical"]:
                alert_metrics = {
                    "memory_usage": metrics.memory_usage,
                    "threshold": self.thresholds["memory_critical"],
                    "service_name": metrics.service_name
                }
                
                # Create alert (rule would need to be defined)
                logger.warning(f"Memory usage critical: {metrics.memory_usage}%")
            
            # Disk Usage Alert
            if metrics.disk_usage >= self.thresholds["disk_critical"]:
                alert_metrics = {
                    "disk_usage": metrics.disk_usage,
                    "threshold": self.thresholds["disk_critical"],
                    "service_name": metrics.service_name
                }
                
                logger.warning(f"Disk usage critical: {metrics.disk_usage}%")
            
            # Service Availability Alert
            if metrics.service_availability < self.thresholds["availability_critical"] * 100:
                alert_metrics = {
                    "service_availability": metrics.service_availability,
                    "threshold": self.thresholds["availability_critical"] * 100,
                    "service_name": metrics.service_name,
                    "downtime_impact": "high"
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["technical_service_down_emergency"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating infrastructure alerts: {e}")
        
        return alerts
    
    async def _evaluate_performance_alerts(self, metrics: TechnicalMetrics) -> List[IntelligentAlert]:
        """Evaluate performance-related alerts"""
        alerts = []
        
        try:
            # API Performance Alert
            if (metrics.api_response_time >= self.thresholds["response_time_critical"] or
                metrics.error_rate >= self.thresholds["error_rate_critical"]):
                
                alert_metrics = {
                    "api_response_time": metrics.api_response_time,
                    "error_rate": metrics.error_rate,
                    "throughput": metrics.throughput,
                    "service_name": metrics.service_name,
                    "performance_degradation": await self._calculate_performance_degradation(metrics)
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["technical_api_performance_critical"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
            # Network Latency Alert
            if metrics.network_latency > 1000:  # 1 second
                logger.warning(f"High network latency: {metrics.network_latency}ms")
            
        except Exception as e:
            logger.error(f"Error evaluating performance alerts: {e}")
        
        return alerts
    
    async def _evaluate_security_alerts(self, metrics: TechnicalMetrics) -> List[IntelligentAlert]:
        """Evaluate security-related alerts"""
        alerts = []
        
        try:
            # Security Breach Alert
            if metrics.security_threat_score >= self.thresholds["threat_score_emergency"]:
                alert_metrics = {
                    "security_threat_score": metrics.security_threat_score,
                    "threshold": self.thresholds["threat_score_emergency"],
                    "security_events": metrics.security_events,
                    "immediate_action_required": True
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["security_breach_emergency"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
            # Suspicious Activity Alert
            elif (metrics.suspicious_activities >= self.thresholds["suspicious_activities_critical"] or
                  metrics.failed_logins >= self.thresholds["failed_logins_critical"]):
                
                alert_metrics = {
                    "suspicious_activities": metrics.suspicious_activities,
                    "failed_logins": metrics.failed_logins,
                    "blocked_ips": metrics.blocked_ips,
                    "security_events": metrics.security_events[-10:]  # Last 10 events
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["security_suspicious_activity_critical"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
            # Authentication Failure Spike
            elif metrics.failed_logins >= self.thresholds["failed_logins_warning"]:
                alert_metrics = {
                    "failed_logins": metrics.failed_logins,
                    "threshold": self.thresholds["failed_logins_warning"],
                    "time_window": "10m",
                    "security_recommendation": "Enable rate limiting"
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["security_auth_failure_spike"],
                    alert_metrics
                )
                await self.alert_manager._process_new_alert(alert)
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating security alerts: {e}")
        
        return alerts
    
    async def process_security_event(self, event: SecurityEvent) -> List[IntelligentAlert]:
        """Process a security event and trigger appropriate alerts"""
        alerts = []
        
        try:
            # Store the event
            self.security_events.append(event)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            # Analyze event severity and trigger alerts
            if event.threat_level == SecurityThreatLevel.EMERGENCY:
                alert_metrics = {
                    "security_event": {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "threat_level": event.threat_level.value,
                        "source_ip": event.source_ip,
                        "description": event.description
                    },
                    "immediate_response_required": True
                }
                
                # Would trigger emergency security alert
                logger.critical(f"Emergency security event: {event.event_id}")
            
            elif event.threat_level == SecurityThreatLevel.CRITICAL:
                # Would trigger critical security alert
                logger.error(f"Critical security event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing security event: {e}")
        
        return alerts
    
    async def _calculate_performance_degradation(self, metrics: TechnicalMetrics) -> float:
        """Calculate performance degradation percentage"""
        try:
            service_name = metrics.service_name
            
            # Get baseline performance if available
            if service_name in self.service_baselines:
                baseline = self.service_baselines[service_name]
                baseline_response_time = baseline.get("api_response_time", 1000)
                baseline_error_rate = baseline.get("error_rate", 0.01)
                
                # Calculate degradation
                response_time_degradation = max(0, (metrics.api_response_time - baseline_response_time) / baseline_response_time)
                error_rate_degradation = max(0, (metrics.error_rate - baseline_error_rate) / baseline_error_rate) if baseline_error_rate > 0 else 0
                
                # Weighted degradation score
                degradation = (response_time_degradation * 0.6 + error_rate_degradation * 0.4) * 100
                return min(100, degradation)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating performance degradation: {e}")
            return 0.0
    
    async def _update_service_baselines(self, metrics -> None: TechnicalMetrics) -> None:
        """Update service performance baselines"""
        try:
            service_name = metrics.service_name
            
            if service_name not in self.service_baselines:
                self.service_baselines[service_name] = {}
            
            baseline = self.service_baselines[service_name]
            
            # Update baselines with exponential smoothing
            alpha = 0.1  # Smoothing factor
            
            baseline["api_response_time"] = (
                alpha * metrics.api_response_time + 
                (1 - alpha) * baseline.get("api_response_time", metrics.api_response_time)
            )
            
            baseline["error_rate"] = (
                alpha * metrics.error_rate + 
                (1 - alpha) * baseline.get("error_rate", metrics.error_rate)
            )
            
            baseline["throughput"] = (
                alpha * metrics.throughput + 
                (1 - alpha) * baseline.get("throughput", metrics.throughput)
            )
            
            baseline["last_updated"] = metrics.timestamp.isoformat()
            
        except Exception as e:
            logger.error(f"Error updating service baselines: {e}")
    
    async def get_technical_alert_summary(self) -> Dict[str, Any]:
        """Get technical alert summary and system health"""
        try:
            if not self.technical_metrics_history:
                return {"error": "No technical metrics available"}
            
            latest_metrics = self.technical_metrics_history[-1]
            
            # Calculate system health score
            health_score = await self._calculate_system_health_score(latest_metrics)
            
            # Get security status
            security_status = await self._get_security_status()
            
            # Get performance trends
            performance_trend = await self._calculate_performance_trend()
            
            return {
                "timestamp": latest_metrics.timestamp.isoformat(),
                "system_health": {
                    "score": health_score,
                    "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.6 else "critical"
                },
                "infrastructure": {
                    "cpu_usage": latest_metrics.cpu_usage,
                    "memory_usage": latest_metrics.memory_usage,
                    "disk_usage": latest_metrics.disk_usage,
                    "service_availability": latest_metrics.service_availability
                },
                "performance": {
                    "api_response_time": latest_metrics.api_response_time,
                    "error_rate": latest_metrics.error_rate,
                    "throughput": latest_metrics.throughput,
                    "trend": performance_trend
                },
                "security": security_status,
                "alert_thresholds": self.thresholds,
                "metrics_history_hours": len(self.technical_metrics_history)
            }
            
        except Exception as e:
            logger.error(f"Error generating technical alert summary: {e}")
            return {"error": str(e)}
    
    async def _calculate_system_health_score(self, metrics: TechnicalMetrics) -> float:
        """Calculate overall system health score (0-1)"""
        try:
            # Component health scores
            cpu_health = max(0, (100 - metrics.cpu_usage) / 100)
            memory_health = max(0, (100 - metrics.memory_usage) / 100)
            disk_health = max(0, (100 - metrics.disk_usage) / 100)
            availability_health = metrics.service_availability / 100
            performance_health = max(0, 1 - (metrics.error_rate * 2))  # Error rate impact
            
            # Weighted health score
            health_score = (
                cpu_health * 0.2 +
                memory_health * 0.2 +
                disk_health * 0.15 +
                availability_health * 0.25 +
                performance_health * 0.2
            )
            
            return min(1.0, max(0.0, health_score))
            
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 0.5
    
    async def _get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            if not self.technical_metrics_history:
                return {"status": "unknown"}
            
            latest_metrics = self.technical_metrics_history[-1]
            
            # Recent security events
            recent_events = [
                event for event in self.security_events 
                if event.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ]
            
            threat_level = "low"
            if latest_metrics.security_threat_score >= 0.8:
                threat_level = "critical"
            elif latest_metrics.security_threat_score >= 0.6:
                threat_level = "high"
            elif latest_metrics.security_threat_score >= 0.3:
                threat_level = "medium"
            
            return {
                "threat_level": threat_level,
                "threat_score": latest_metrics.security_threat_score,
                "failed_logins": latest_metrics.failed_logins,
                "suspicious_activities": latest_metrics.suspicious_activities,
                "blocked_ips": latest_metrics.blocked_ips,
                "recent_events": len(recent_events),
                "status": "secure" if threat_level == "low" else "monitoring"
            }
            
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    async def _calculate_performance_trend(self) -> str:
        """Calculate performance trend direction"""
        try:
            if len(self.technical_metrics_history) < 3:
                return "insufficient_data"
            
            recent_response_times = [m.api_response_time for m in self.technical_metrics_history[-3:]]
            
            if recent_response_times[2] < recent_response_times[1] < recent_response_times[0]:
                return "improving"
            elif recent_response_times[2] > recent_response_times[1] > recent_response_times[0]:
                return "degrading"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating performance trend: {e}")
            return "unknown"


# Export the main classes
__all__ = [
    "TechnicalAlertManager", 
    "TechnicalMetrics", 
    "SecurityEvent", 
    "TechnicalMetric", 
    "SecurityThreatLevel"
]