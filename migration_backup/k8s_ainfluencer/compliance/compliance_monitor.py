"""IA Influencer Agent - Compliance Monitor
Real-time compliance monitoring and alerting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.compliance import ComplianceMetric, ComplianceAlert, ComplianceReport
from backend.models.audit import AuditLog
from backend.core.cache import redis_client
from backend.utils.notifications import send_compliance_alert
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, ComplianceFramework
from .gdpr_compliance import GDPRComplianceManager

logger = get_logger(__name__)


class ComplianceStatus(str, Enum):
    """
Compliance status levels"""

    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MonitoringScope(str, Enum):
    """Monitoring scope levels"""

    SYSTEM = "system"
    ORGANIZATION = "organization"
    USER = "user"
    RESOURCE = "resource"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Compliance monitoring rule definition"""
    rule_id: str
    name: str
    description: str
    framework: ComplianceFramework
    regulation_section: str
    metric_type: str
    threshold_value: float
    comparison_operator: str  # gte, lte, eq, ne
    evaluation_period: int  # minutes
    alert_severity: AlertSeverity
    remediation_steps: List[str]
    automated_remediation: bool
    enabled: bool


@dataclass
class ComplianceMetricSnapshot:
    """
Point-in-time compliance metric snapshot"""
    metric_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    scope: MonitoringScope
    scope_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    metadata: Dict[str, Any]


@dataclass
class ComplianceAlert:
    """
Compliance alert details"""
    alert_id: str
    rule_id: str
    metric_id: str
    severity: AlertSeverity
    status: ComplianceStatus
    triggered_at: datetime
    resolved_at: Optional[datetime]
    message: str
    details: Dict[str, Any]
    remediation_taken: List[str]
    assignee: Optional[str]


class ComplianceMonitor:
    """
Real-time compliance monitoring and alerting system"""
    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.gdpr_manager = GDPRComplianceManager()
        self.monitoring_interval = settings.COMPLIANCE_MONITORING_INTERVAL
        self.alert_retention_days = settings.COMPLIANCE_ALERT_RETENTION_DAYS
        self.automated_remediation = settings.COMPLIANCE_AUTOMATED_REMEDIATION
        
        # Compliance monitoring rules
        self.monitoring_rules = self._load_compliance_rules()
        
        # Metric collection registry
        self.metric_collectors = {
            "gdpr_consent_rate": self._collect_gdpr_consent_metrics,
            "data_retention_compliance": self._collect_data_retention_metrics,
            "audit_log_integrity": self._collect_audit_integrity_metrics,
            "security_incident_rate": self._collect_security_metrics,
            "content_protection_rate": self._collect_content_protection_metrics,
            "financial_compliance_rate": self._collect_financial_metrics,
            "api_access_compliance": self._collect_api_compliance_metrics,
            "user_privacy_compliance": self._collect_privacy_metrics
        }
        
        # Active monitoring tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._is_monitoring = False
    
    async def start_monitoring(self) -> None:
        """Start real-time compliance monitoring"""
        try:
            if self._is_monitoring:
                self.logger.warning("Compliance monitoring already running")
                return
            
            self._is_monitoring = True
            
            # Start monitoring tasks for each framework
            for framework in ComplianceFramework:
                task = asyncio.create_task(
                    self._monitor_compliance_framework(framework)
                )
                self._monitoring_tasks.add(task)
            
            # Start metric collection task
            collection_task = asyncio.create_task(self._collect_all_metrics())
            self._monitoring_tasks.add(collection_task)
            
            # Start alert processing task
            alert_task = asyncio.create_task(self._process_alerts())
            self._monitoring_tasks.add(alert_task)
            
            self.logger.info("Compliance monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start compliance monitoring: {str(e)}")
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop compliance monitoring"""
        try:
            self._is_monitoring = False
            
            # Cancel all monitoring tasks
            for task in self._monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
            self._monitoring_tasks.clear()
            
            self.logger.info("Compliance monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping compliance monitoring: {str(e)}")
    
    async def evaluate_compliance_status(
        self,
        framework: ComplianceFramework,
        scope: MonitoringScope,
        scope_id: str = None
    ) -> Dict[str, Any]:
        """Evaluate current compliance status for framework and scope"""
        try:
            # Collect current metrics
            metrics = await self._collect_framework_metrics(framework, scope, scope_id)
            
            # Evaluate against rules
            compliance_results = []
            overall_status = ComplianceStatus.COMPLIANT
            critical_violations = 0
            
            applicable_rules = [
                rule for rule in self.monitoring_rules
                if rule.framework == framework and rule.enabled
            ]
            
            for rule in applicable_rules:
                result = await self._evaluate_compliance_rule(rule, metrics)
                compliance_results.append(result)
                
                # Update overall status
                if result["status"] == ComplianceStatus.CRITICAL:
                    overall_status = ComplianceStatus.CRITICAL
                    critical_violations += 1
                elif result["status"] == ComplianceStatus.NON_COMPLIANT and overall_status != ComplianceStatus.CRITICAL:
                    overall_status = ComplianceStatus.NON_COMPLIANT
                elif result["status"] == ComplianceStatus.WARNING and overall_status == ComplianceStatus.COMPLIANT:
                    overall_status = ComplianceStatus.WARNING
            
            # Calculate compliance score
            compliant_rules = sum(1 for r in compliance_results if r["status"] == ComplianceStatus.COMPLIANT)
            compliance_score = (compliant_rules / len(applicable_rules)) * 100 if applicable_rules else 100
            
            return {
                "framework": framework.value,
                "scope": scope.value,
                "scope_id": scope_id,
                "overall_status": overall_status.value,
                "compliance_score": compliance_score,
                "critical_violations": critical_violations,
                "rules_evaluated": len(applicable_rules),
                "compliant_rules": compliant_rules,
                "evaluation_timestamp": datetime.utcnow().isoformat(),
                "detailed_results": compliance_results,
                "metrics": [asdict(m) for m in metrics]
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating compliance status: {str(e)}")
            return {
                "framework": framework.value,
                "scope": scope.value,
                "overall_status": ComplianceStatus.UNKNOWN.value,
                "error": str(e)
            }
    
    async def generate_compliance_report(
        self,
        framework: Optional[ComplianceFramework] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        scope: Optional[MonitoringScope] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get frameworks to evaluate
            frameworks = [framework] if framework else list(ComplianceFramework)
            
            report = {
                "report_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "period_start": start_date.isoformat(),
                    "period_end": end_date.isoformat(),
                    "frameworks_included": [f.value for f in frameworks],
                    "scope": scope.value if scope else "all"
                },
                "executive_summary": {
                    "overall_compliance_score": 0.0,
                    "frameworks_compliant": 0,
                    "critical_violations": 0,
                    "open_alerts": 0,
                    "remediation_actions": 0
                },
                "framework_details": {},
                "trend_analysis": {},
                "alerts_summary": {},
                "recommendations": []
            }
            
            total_score = 0
            compliant_frameworks = 0
            total_critical = 0
            
            # Evaluate each framework
            for fw in frameworks:
                framework_status = await self.evaluate_compliance_status(
                    fw, scope or MonitoringScope.SYSTEM
                )
                
                report["framework_details"][fw.value] = framework_status
                total_score += framework_status["compliance_score"]
                
                if framework_status["overall_status"] == ComplianceStatus.COMPLIANT.value:
                    compliant_frameworks += 1
                
                total_critical += framework_status["critical_violations"]
            
            # Calculate overall metrics
            report["executive_summary"]["overall_compliance_score"] = total_score / len(frameworks) if frameworks else 0
            report["executive_summary"]["frameworks_compliant"] = compliant_frameworks
            report["executive_summary"]["critical_violations"] = total_critical
            
            # Get alerts summary
            alerts_summary = await self._get_alerts_summary(start_date, end_date, frameworks)
            report["alerts_summary"] = alerts_summary
            report["executive_summary"]["open_alerts"] = alerts_summary["total_open"]
            
            # Generate trend analysis
            trend_analysis = await self._generate_trend_analysis(frameworks, start_date, end_date)
            report["trend_analysis"] = trend_analysis
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(report)
            report["recommendations"] = recommendations
            report["executive_summary"]["remediation_actions"] = len(recommendations)
            
            # Log report generation
            await self.audit_logger.log_audit_event(
                event_type="compliance_report_generated",
                category=AuditCategory.COMPLIANCE,
                level=AuditLogger.AuditLevel.INFO,
                message="Compliance report generated",
                details={
                    "frameworks": [f.value for f in frameworks],
                    "period_days": (end_date - start_date).days,
                    "overall_score": report["executive_summary"]["overall_compliance_score"]
                }
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate compliance report")
    
    async def trigger_compliance_alert(
        self,
        rule_id: str,
        metric_value: float,
        expected_value: float,
        scope: MonitoringScope,
        scope_id: str,
        details: Dict[str, Any] = None
    ) -> str:
        """Trigger compliance alert for rule violation"""
        try:
            # Get rule details
            rule = next((r for r in self.monitoring_rules if r.rule_id == rule_id), None)
            if not rule:
                raise ValueError(f"Compliance rule not found: {rule_id}")
            
            # Generate alert ID
            alert_id = f"CA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{rule_id[-8:]}"
            
            # Create alert
            alert = ComplianceAlert(
                alert_id=alert_id,
                rule_id=rule_id,
                metric_id=f"{rule.metric_type}_{scope.value}_{scope_id}",
                severity=rule.alert_severity,
                status=ComplianceStatus.NON_COMPLIANT,
                triggered_at=datetime.utcnow(),
                resolved_at=None,
                message=f"Compliance violation: {rule.name}",
                details={
                    "rule_name": rule.name,
                    "framework": rule.framework.value,
                    "regulation_section": rule.regulation_section,
                    "metric_value": metric_value,
                    "expected_value": expected_value,
                    "threshold_exceeded": abs(metric_value - expected_value),
                    "scope": scope.value,
                    "scope_id": scope_id,
                    **(details or {})
                },
                remediation_taken=[],
                assignee=None
            )
            
            # Store alert in database
            async with get_db_session() as session:
                db_alert = ComplianceAlert(
                    alert_id=alert_id,
                    rule_id=rule_id,
                    severity=rule.alert_severity.value,
                    status=ComplianceStatus.NON_COMPLIANT.value,
                    triggered_at=alert.triggered_at,
                    message=alert.message,
                    details=json.dumps(alert.details),
                    framework=rule.framework.value,
                    scope=scope.value,
                    scope_id=scope_id
                )
                
                session.add(db_alert)
                await session.commit()
            
            # Log alert
            await self.audit_logger.log_audit_event(
                event_type="compliance_alert_triggered",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.WARNING if rule.alert_severity in [AlertSeverity.LOW, AlertSeverity.MEDIUM] else AuditLevel.ERROR,
                message=f"Compliance alert triggered: {rule.name}",
                details={
                    "alert_id": alert_id,
                    "rule_id": rule_id,
                    "severity": rule.alert_severity.value,
                    "framework": rule.framework.value,
                    "scope": scope.value,
                    "metric_violation": {
                        "actual": metric_value,
                        "expected": expected_value
                    }
                }
            )
            
            # Send notification
            await self._send_compliance_notification(alert)
            
            # Trigger automated remediation if enabled
            if rule.automated_remediation and self.automated_remediation:
                await self._trigger_automated_remediation(alert, rule)
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error triggering compliance alert: {str(e)}")
            raise
    
    async def resolve_compliance_alert(
        self,
        alert_id: str,
        resolution_notes: str,
        resolved_by: str
    ) -> bool:
        """Resolve compliance alert"""
        try:
            async with get_db_session() as session:
                # Update alert status
                result = await session.execute(
                    update(ComplianceAlert)
                    .where(ComplianceAlert.alert_id == alert_id)
                    .values(
                        status=ComplianceStatus.COMPLIANT.value,
                        resolved_at=datetime.utcnow(),
                        resolution_notes=resolution_notes,
                        resolved_by=resolved_by
                    )
                )
                
                if result.rowcount == 0:
                    return False
                
                await session.commit()
            
            # Log resolution
            await self.audit_logger.log_audit_event(
                event_type="compliance_alert_resolved",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Compliance alert resolved: {alert_id}",
                details={
                    "alert_id": alert_id,
                    "resolved_by": resolved_by,
                    "resolution_notes": resolution_notes
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving compliance alert: {str(e)}")
            return False
    
    async def _monitor_compliance_framework(self, framework: ComplianceFramework) -> None:
        """Monitor specific compliance framework continuously"""
        try:
            while self._is_monitoring:
                try:
                    # Evaluate framework compliance
                    status = await self.evaluate_compliance_status(
                        framework, MonitoringScope.SYSTEM
                    )
                    
                    # Check for violations and trigger alerts
                    if status["overall_status"] in [ComplianceStatus.NON_COMPLIANT.value, ComplianceStatus.CRITICAL.value]:
                        for result in status["detailed_results"]:
                            if result["violated"]:
                                await self.trigger_compliance_alert(
                                    rule_id=result["rule_id"],
                                    metric_value=result["metric_value"],
                                    expected_value=result["threshold_value"],
                                    scope=MonitoringScope.SYSTEM,
                                    scope_id="global",
                                    details=result
                                )
                    
                    # Wait for next monitoring cycle
                    await asyncio.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in framework monitoring {framework.value}: {str(e)}")
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except asyncio.CancelledError:
            self.logger.info(f"Framework monitoring cancelled: {framework.value}")
        except Exception as e:
            self.logger.error(f"Fatal error in framework monitoring {framework.value}: {str(e)}")
    
    async def _collect_gdpr_consent_metrics(self) -> List[ComplianceMetricSnapshot]:
        """Collect GDPR consent compliance metrics"""
        try:
            metrics = []
            
            async with get_db_session() as session:
                # Calculate consent rate
                total_users_result = await session.execute(
                    select(func.count(User.id)).where(User.is_active == True)
                )
                total_users = total_users_result.scalar() or 0
                
                if total_users > 0:
                    consented_users_result = await session.execute(
                        select(func.count(func.distinct(ConsentRecord.user_id)))
                        .where(
                            ConsentRecord.granted == True,
                            ConsentRecord.withdrawal_date.is_(None)
                        )
                    )
                    consented_users = consented_users_result.scalar() or 0
                    consent_rate = (consented_users / total_users) * 100
                else:
                    consent_rate = 100  # No users = 100% compliance
                
                metrics.append(ComplianceMetricSnapshot(
                    metric_id="gdpr_consent_rate_system",
                    metric_name="GDPR Consent Rate",
                    value=consent_rate,
                    unit="percentage",
                    timestamp=datetime.utcnow(),
                    scope=MonitoringScope.SYSTEM,
                    scope_id="global",
                    framework=ComplianceFramework.GDPR,
                    status=ComplianceStatus.COMPLIANT if consent_rate >= 95 else ComplianceStatus.WARNING,
                    metadata={
                        "total_users": total_users,
                        "consented_users": consented_users
                    }
                ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting GDPR consent metrics: {str(e)}")
            return []
    
    def _load_compliance_rules(self) -> List[ComplianceRule]:
        """Load compliance monitoring rules"""
        return [
            # GDPR Rules
            ComplianceRule(
                rule_id="GDPR-001",
                name="GDPR Consent Rate",
                description="Monitor user consent rate for GDPR compliance",
                framework=ComplianceFramework.GDPR,
                regulation_section="Article 6",
                metric_type="gdpr_consent_rate",
                threshold_value=95.0,
                comparison_operator="gte",
                evaluation_period=60,
                alert_severity=AlertSeverity.HIGH,
                remediation_steps=[
                    "Review consent collection processes",
                    "Update privacy notices",
                    "Implement consent renewal campaigns"
                ],
                automated_remediation=False,
                enabled=True
            ),
            
            ComplianceRule(
                rule_id="GDPR-002",
                name="Data Retention Compliance",
                description="Monitor data retention policy compliance",
                framework=ComplianceFramework.GDPR,
                regulation_section="Article 5(1)(e)",
                metric_type="data_retention_compliance",
                threshold_value=98.0,
                comparison_operator="gte",
                evaluation_period=1440,  # Daily
                alert_severity=AlertSeverity.CRITICAL,
                remediation_steps=[
                    "Review data retention policies",
                    "Implement automated data cleanup",
                    "Update data retention schedules"
                ],
                automated_remediation=True,
                enabled=True
            ),
            
            # Security Rules
            ComplianceRule(
                rule_id="SEC-001",
                name="Security Incident Rate",
                description="Monitor security incident frequency",
                framework=ComplianceFramework.ISO27001,
                regulation_section="A.16.1.1",
                metric_type="security_incident_rate",
                threshold_value=5.0,
                comparison_operator="lte",
                evaluation_period=1440,
                alert_severity=AlertSeverity.HIGH,
                remediation_steps=[
                    "Review security controls",
                    "Enhance monitoring systems",
                    "Update incident response procedures"
                ],
                automated_remediation=False,
                enabled=True
            ),
            
            # Content Protection Rules
            ComplianceRule(
                rule_id="DMCA-001",
                name="Content Protection Rate",
                description="Monitor content protection effectiveness",
                framework=ComplianceFramework.DMCA,
                regulation_section="Section 512",
                metric_type="content_protection_rate",
                threshold_value=95.0,
                comparison_operator="gte",
                evaluation_period=60,
                alert_severity=AlertSeverity.MEDIUM,
                remediation_steps=[
                    "Review content scanning algorithms",
                    "Update fingerprinting systems",
                    "Enhance takedown procedures"
                ],
                automated_remediation=True,
                enabled=True
            )
        ]


# Export for use in other modules
__all__ = ["ComplianceMonitor", "ComplianceStatus", "MonitoringScope", "AlertSeverity"]
