#!/usr/bin/env python3
"""
Compliance Orchestrator - Enterprise Core Component
Regulatory compliance coordination system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive compliance orchestration capabilities including:
- Regulatory compliance coordination
- Audit trail management
- Policy enforcement automation
- Compliance reporting generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import hashlib
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Compliance framework types"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    CCPA = "ccpa"
    NIST = "nist"
    CUSTOM = "custom"


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    UNKNOWN = "unknown"


class AuditEventType(Enum):
    """Audit event types"""
    ACCESS = "access"
    MODIFICATION = "modification"
    DELETION = "deletion"
    CREATION = "creation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_EXPORT = "data_export"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"


class PolicyType(Enum):
    """Policy types"""
    DATA_RETENTION = "data_retention"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    BACKUP = "backup"
    INCIDENT_RESPONSE = "incident_response"
    PRIVACY = "privacy"
    SECURITY = "security"
    OPERATIONAL = "operational"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    name: str
    description: str
    requirement: str
    policy_type: PolicyType
    severity: str  # low, medium, high, critical
    automated_check: bool = True
    check_frequency: timedelta = field(default_factory=lambda: timedelta(hours=24))
    remediation_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    service_id: str
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    framework: ComplianceFramework
    severity: str
    detected_at: datetime
    description: str
    affected_resources: List[str]
    evidence: Dict[str, Any]
    remediation_required: bool = True
    remediated: bool = False
    remediated_at: Optional[datetime] = None
    remediation_notes: Optional[str] = None


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    framework: ComplianceFramework
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    overall_status: ComplianceStatus
    total_rules: int
    compliant_rules: int
    violations: List[ComplianceViolation]
    recommendations: List[str]
    executive_summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataRetentionPolicy:
    """Data retention policy"""
    policy_id: str
    name: str
    data_type: str
    retention_period: timedelta
    deletion_method: str  # secure_delete, archive, anonymize
    applicable_frameworks: List[ComplianceFramework]
    exceptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ComplianceOrchestrator:
    """
    Enterprise Compliance Orchestrator
    
    Manages comprehensive regulatory compliance including audit trails,
    policy enforcement, violation detection, and automated reporting.
    """
    
    def __init__(self):
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.audit_events: List[AuditEvent] = []
        self.violations: Dict[str, ComplianceViolation] = {}
        self.retention_policies: Dict[str, DataRetentionPolicy] = {}
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.retention_tasks: Dict[str, asyncio.Task] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[callable]] = {
            "violation_detected": [],
            "violation_remediated": [],
            "audit_event_recorded": [],
            "compliance_check_completed": [],
            "report_generated": [],
            "retention_policy_applied": []
        }
        
        # Configuration
        self.audit_retention_days = 2555  # 7 years default
        self.max_audit_events = 1000000
        self.auto_remediation_enabled = True
        self.real_time_monitoring = True
        self.encryption_required = True
        
        # Initialize default rules and policies
        self._initialize_default_rules()
        self._initialize_default_policies()
        
        logger.info("Compliance Orchestrator initialized")
    
    async def register_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Register a compliance rule"""
        try:
            self.compliance_rules[rule.rule_id] = rule
            
            # Start automated monitoring if enabled
            if rule.automated_check and self.real_time_monitoring:
                await self._start_rule_monitoring(rule)
            
            logger.info(f"Compliance rule registered: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register compliance rule {rule.rule_id}: {e}")
            return False
    
    async def record_audit_event(self, event: AuditEvent) -> bool:
        """Record an audit event"""
        try:
            # Add compliance framework tags based on event type
            event.compliance_frameworks = self._determine_applicable_frameworks(event)
            
            # Store event
            self.audit_events.append(event)
            
            # Maintain retention limit
            if len(self.audit_events) > self.max_audit_events:
                self.audit_events = self.audit_events[-self.max_audit_events:]
            
            # Check for compliance violations
            await self._check_event_compliance(event)
            
            await self._trigger_event("audit_event_recorded", event.event_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record audit event {event.event_id}: {e}")
            return False
    
    async def perform_compliance_check(
        self,
        framework: Optional[ComplianceFramework] = None,
        rule_ids: Optional[List[str]] = None
    ) -> Dict[str, ComplianceStatus]:
        """Perform compliance checks"""
        results = {}
        
        try:
            rules_to_check = []
            
            if rule_ids:
                rules_to_check = [self.compliance_rules[rid] for rid in rule_ids if rid in self.compliance_rules]
            elif framework:
                rules_to_check = [rule for rule in self.compliance_rules.values() if rule.framework == framework]
            else:
                rules_to_check = list(self.compliance_rules.values())
            
            for rule in rules_to_check:
                try:
                    status = await self._check_rule_compliance(rule)
                    results[rule.rule_id] = status
                    
                    if status == ComplianceStatus.NON_COMPLIANT:
                        await self._handle_compliance_violation(rule)
                        
                except Exception as e:
                    logger.error(f"Failed to check rule {rule.rule_id}: {e}")
                    results[rule.rule_id] = ComplianceStatus.UNKNOWN
            
            await self._trigger_event("compliance_check_completed", f"checked_{len(results)}_rules")
            return results
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {}
    
    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Optional[ComplianceReport]:
        """Generate compliance report"""
        try:
            if not period_end:
                period_end = datetime.utcnow()
            if not period_start:
                period_start = period_end - timedelta(days=30)
            
            report_id = str(uuid.uuid4())
            
            # Get framework-specific rules
            framework_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework
            ]
            
            # Perform compliance checks
            compliance_results = await self.perform_compliance_check(framework)
            
            # Count compliant rules
            compliant_count = sum(
                1 for status in compliance_results.values()
                if status == ComplianceStatus.COMPLIANT
            )
            
            # Get violations in the period
            period_violations = [
                violation for violation in self.violations.values()
                if (violation.framework == framework and
                    period_start <= violation.detected_at <= period_end)
            ]
            
            # Determine overall status
            overall_status = self._calculate_overall_compliance_status(compliance_results)
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(framework, period_violations)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                framework, overall_status, len(framework_rules), compliant_count, len(period_violations)
            )
            
            report = ComplianceReport(
                report_id=report_id,
                framework=framework,
                generated_at=datetime.utcnow(),
                period_start=period_start,
                period_end=period_end,
                overall_status=overall_status,
                total_rules=len(framework_rules),
                compliant_rules=compliant_count,
                violations=period_violations,
                recommendations=recommendations,
                executive_summary=executive_summary
            )
            
            self.compliance_reports[report_id] = report
            await self._trigger_event("report_generated", report_id)
            
            logger.info(f"Compliance report generated: {report_id} for {framework.value}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report for {framework}: {e}")
            return None
    
    async def create_retention_policy(self, policy: DataRetentionPolicy) -> bool:
        """Create data retention policy"""
        try:
            self.retention_policies[policy.policy_id] = policy
            
            # Start retention monitoring
            await self._start_retention_monitoring(policy)
            
            logger.info(f"Data retention policy created: {policy.policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create retention policy {policy.policy_id}: {e}")
            return False
    
    async def remediate_violation(self, violation_id: str, remediation_notes: str) -> bool:
        """Mark violation as remediated"""
        try:
            violation = self.violations.get(violation_id)
            if not violation:
                logger.error(f"Violation not found: {violation_id}")
                return False
            
            violation.remediated = True
            violation.remediated_at = datetime.utcnow()
            violation.remediation_notes = remediation_notes
            
            await self._trigger_event("violation_remediated", violation_id)
            logger.info(f"Violation remediated: {violation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remediate violation {violation_id}: {e}")
            return False
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            # Overall statistics
            total_rules = len(self.compliance_rules)
            active_violations = len([v for v in self.violations.values() if not v.remediated])
            
            # Framework breakdown
            framework_stats = {}
            for framework in ComplianceFramework:
                framework_rules = [r for r in self.compliance_rules.values() if r.framework == framework]
                framework_violations = [v for v in self.violations.values() if v.framework == framework and not v.remediated]
                
                if framework_rules:
                    framework_stats[framework.value] = {
                        "total_rules": len(framework_rules),
                        "active_violations": len(framework_violations),
                        "compliance_rate": max(0, (len(framework_rules) - len(framework_violations)) / len(framework_rules) * 100)
                    }
            
            # Recent activity
            recent_events = len([
                e for e in self.audit_events
                if e.timestamp > datetime.utcnow() - timedelta(hours=24)
            ])
            
            recent_violations = len([
                v for v in self.violations.values()
                if v.detected_at > datetime.utcnow() - timedelta(hours=24)
            ])
            
            return {
                "overview": {
                    "total_rules": total_rules,
                    "active_violations": active_violations,
                    "recent_audit_events": recent_events,
                    "recent_violations": recent_violations,
                    "overall_compliance_rate": max(0, (total_rules - active_violations) / max(total_rules, 1) * 100)
                },
                "frameworks": framework_stats,
                "recent_activity": {
                    "audit_events_24h": recent_events,
                    "violations_24h": recent_violations
                },
                "data_retention": {
                    "active_policies": len(self.retention_policies),
                    "audit_retention_days": self.audit_retention_days
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance dashboard: {e}")
            return {}
    
    async def export_audit_trail(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[AuditEventType]] = None,
        format_type: str = "json"
    ) -> Optional[str]:
        """Export audit trail"""
        try:
            # Filter events
            filtered_events = [
                event for event in self.audit_events
                if start_date <= event.timestamp <= end_date
            ]
            
            if event_types:
                filtered_events = [
                    event for event in filtered_events
                    if event.event_type in event_types
                ]
            
            # Format export data
            export_data = {
                "export_info": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "period_start": start_date.isoformat(),
                    "period_end": end_date.isoformat(),
                    "total_events": len(filtered_events)
                },
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "user_id": event.user_id,
                        "service_id": event.service_id,
                        "resource_id": event.resource_id,
                        "action": event.action,
                        "details": event.details,
                        "ip_address": event.ip_address,
                        "compliance_frameworks": [f.value for f in event.compliance_frameworks]
                    }
                    for event in filtered_events
                ]
            }
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                # Could add CSV, XML formats here
                return json.dumps(export_data, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to export audit trail: {e}")
            return None
    
    # Private methods
    
    def _initialize_default_rules(self):
        """Initialize default compliance rules"""
        # GDPR rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="gdpr_data_retention",
                framework=ComplianceFramework.GDPR,
                name="Data Retention Limits",
                description="Personal data must not be kept longer than necessary",
                requirement="Article 5(1)(e) - Storage limitation",
                policy_type=PolicyType.DATA_RETENTION,
                severity="high"
            ),
            ComplianceRule(
                rule_id="gdpr_access_control",
                framework=ComplianceFramework.GDPR,
                name="Access Control",
                description="Implement appropriate technical measures for data protection",
                requirement="Article 32 - Security of processing",
                policy_type=PolicyType.ACCESS_CONTROL,
                severity="high"
            ),
            ComplianceRule(
                rule_id="gdpr_encryption",
                framework=ComplianceFramework.GDPR,
                name="Data Encryption",
                description="Encrypt personal data in transit and at rest",
                requirement="Article 32 - Security of processing",
                policy_type=PolicyType.ENCRYPTION,
                severity="critical"
            )
        ]
        
        # SOX rules
        sox_rules = [
            ComplianceRule(
                rule_id="sox_audit_trail",
                framework=ComplianceFramework.SOX,
                name="Audit Trail Integrity",
                description="Maintain comprehensive audit trails for financial data",
                requirement="Section 404 - Internal Controls",
                policy_type=PolicyType.SECURITY,
                severity="critical"
            ),
            ComplianceRule(
                rule_id="sox_access_control",
                framework=ComplianceFramework.SOX,
                name="Financial Data Access Control",
                description="Restrict access to financial systems and data",
                requirement="Section 302 - Corporate Responsibility",
                policy_type=PolicyType.ACCESS_CONTROL,
                severity="high"
            )
        ]
        
        all_rules = gdpr_rules + sox_rules
        self.compliance_rules = {rule.rule_id: rule for rule in all_rules}
    
    def _initialize_default_policies(self):
        """Initialize default retention policies"""
        default_policies = [
            DataRetentionPolicy(
                policy_id="audit_logs_retention",
                name="Audit Logs Retention",
                data_type="audit_logs",
                retention_period=timedelta(days=2555),  # 7 years
                deletion_method="secure_delete",
                applicable_frameworks=[ComplianceFramework.SOX, ComplianceFramework.GDPR]
            ),
            DataRetentionPolicy(
                policy_id="user_data_retention",
                name="User Data Retention",
                data_type="user_personal_data",
                retention_period=timedelta(days=1095),  # 3 years
                deletion_method="secure_delete",
                applicable_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA]
            )
        ]
        
        self.retention_policies = {policy.policy_id: policy for policy in default_policies}
    
    def _determine_applicable_frameworks(self, event: AuditEvent) -> List[ComplianceFramework]:
        """Determine which compliance frameworks apply to an event"""
        frameworks = []
        
        # Access events are relevant to most frameworks
        if event.event_type in [AuditEventType.ACCESS, AuditEventType.AUTHENTICATION, AuditEventType.AUTHORIZATION]:
            frameworks.extend([ComplianceFramework.GDPR, ComplianceFramework.SOX, ComplianceFramework.HIPAA])
        
        # Data modification events
        if event.event_type in [AuditEventType.MODIFICATION, AuditEventType.DELETION, AuditEventType.CREATION]:
            frameworks.extend([ComplianceFramework.GDPR, ComplianceFramework.CCPA])
        
        # Financial or system events
        if "financial" in event.service_id.lower() or event.event_type == AuditEventType.CONFIGURATION_CHANGE:
            frameworks.append(ComplianceFramework.SOX)
        
        # Remove duplicates
        return list(set(frameworks))
    
    async def _check_event_compliance(self, event: AuditEvent):
        """Check if an event violates any compliance rules"""
        for rule in self.compliance_rules.values():
            if await self._event_violates_rule(event, rule):
                await self._create_violation(rule, event)
    
    async def _event_violates_rule(self, event: AuditEvent, rule: ComplianceRule) -> bool:
        """Check if an event violates a specific rule"""
        # Simplified violation detection logic
        # In production, this would be more sophisticated
        
        if rule.policy_type == PolicyType.ACCESS_CONTROL:
            # Check for unauthorized access
            if event.event_type == AuditEventType.ACCESS and not event.user_id:
                return True
        
        elif rule.policy_type == PolicyType.ENCRYPTION:
            # Check for unencrypted data operations
            if event.event_type in [AuditEventType.DATA_EXPORT, AuditEventType.CREATION]:
                if not event.details.get("encrypted", False):
                    return True
        
        return False
    
    async def _create_violation(self, rule: ComplianceRule, event: AuditEvent):
        """Create a compliance violation"""
        violation_id = str(uuid.uuid4())
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            rule_id=rule.rule_id,
            framework=rule.framework,
            severity=rule.severity,
            detected_at=datetime.utcnow(),
            description=f"Rule '{rule.name}' violated by event {event.event_id}",
            affected_resources=[event.resource_id] if event.resource_id else [],
            evidence={
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "details": event.details
            }
        )
        
        self.violations[violation_id] = violation
        await self._trigger_event("violation_detected", violation_id)
        
        logger.warning(f"Compliance violation detected: {violation_id} for rule {rule.rule_id}")
    
    async def _check_rule_compliance(self, rule: ComplianceRule) -> ComplianceStatus:
        """Check compliance status for a specific rule"""
        # Simplified compliance checking
        # In production, this would involve actual system checks
        
        # Check for recent violations
        recent_violations = [
            v for v in self.violations.values()
            if (v.rule_id == rule.rule_id and 
                not v.remediated and
                v.detected_at > datetime.utcnow() - timedelta(days=30))
        ]
        
        if recent_violations:
            if len(recent_violations) > 5:
                return ComplianceStatus.NON_COMPLIANT
            else:
                return ComplianceStatus.PARTIALLY_COMPLIANT
        
        return ComplianceStatus.COMPLIANT
    
    async def _handle_compliance_violation(self, rule: ComplianceRule):
        """Handle compliance violation detection"""
        if self.auto_remediation_enabled and rule.remediation_steps:
            # Attempt auto-remediation
            logger.info(f"Attempting auto-remediation for rule: {rule.rule_id}")
            # Implementation would go here
    
    def _calculate_overall_compliance_status(self, compliance_results: Dict[str, ComplianceStatus]) -> ComplianceStatus:
        """Calculate overall compliance status"""
        if not compliance_results:
            return ComplianceStatus.UNKNOWN
        
        status_counts = {}
        for status in compliance_results.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_rules = len(compliance_results)
        compliant_rules = status_counts.get(ComplianceStatus.COMPLIANT, 0)
        
        compliance_rate = compliant_rules / total_rules
        
        if compliance_rate >= 0.95:
            return ComplianceStatus.COMPLIANT
        elif compliance_rate >= 0.80:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    async def _generate_compliance_recommendations(
        self,
        framework: ComplianceFramework,
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if violations:
            # Group violations by rule
            rule_violations = {}
            for violation in violations:
                if violation.rule_id not in rule_violations:
                    rule_violations[violation.rule_id] = 0
                rule_violations[violation.rule_id] += 1
            
            # Generate recommendations based on most common violations
            for rule_id, count in sorted(rule_violations.items(), key=lambda x: x[1], reverse=True):
                rule = self.compliance_rules.get(rule_id)
                if rule:
                    recommendations.append(f"Address {count} violations of '{rule.name}' - {rule.description}")
                    recommendations.extend(rule.remediation_steps[:2])  # Add first 2 remediation steps
        
        # Generic recommendations
        if framework == ComplianceFramework.GDPR:
            recommendations.append("Review and update data retention policies")
            recommendations.append("Ensure all data processing has legal basis")
        elif framework == ComplianceFramework.SOX:
            recommendations.append("Strengthen financial data access controls")
            recommendations.append("Review audit trail completeness")
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def _generate_executive_summary(
        self,
        framework: ComplianceFramework,
        overall_status: ComplianceStatus,
        total_rules: int,
        compliant_rules: int,
        violation_count: int
    ) -> str:
        """Generate executive summary"""
        compliance_rate = (compliant_rules / max(total_rules, 1)) * 100
        
        summary = f"""
Executive Summary - {framework.value.upper()} Compliance Assessment

Overall Status: {overall_status.value.replace('_', ' ').title()}
Compliance Rate: {compliance_rate:.1f}% ({compliant_rules}/{total_rules} rules)

During this assessment period, {violation_count} compliance violations were identified.
"""
        
        if overall_status == ComplianceStatus.COMPLIANT:
            summary += "The organization demonstrates strong compliance posture with all critical requirements met."
        elif overall_status == ComplianceStatus.PARTIALLY_COMPLIANT:
            summary += "The organization shows good compliance but requires attention to identified gaps."
        else:
            summary += "Immediate action is required to address significant compliance deficiencies."
        
        return summary.strip()
    
    async def _start_rule_monitoring(self, rule: ComplianceRule):
        """Start monitoring for a compliance rule"""
        async def monitoring_loop():
            while True:
                try:
                    await asyncio.sleep(rule.check_frequency.total_seconds())
                    
                    # Perform rule check
                    status = await self._check_rule_compliance(rule)
                    
                    if status == ComplianceStatus.NON_COMPLIANT:
                        await self._handle_compliance_violation(rule)
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Rule monitoring error for {rule.rule_id}: {e}")
        
        task = asyncio.create_task(monitoring_loop())
        self.monitoring_tasks[rule.rule_id] = task
    
    async def _start_retention_monitoring(self, policy: DataRetentionPolicy):
        """Start monitoring for retention policy"""
        async def retention_loop():
            while True:
                try:
                    # Check daily
                    await asyncio.sleep(86400)  # 24 hours
                    
                    # Apply retention policy
                    await self._apply_retention_policy(policy)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Retention monitoring error for {policy.policy_id}: {e}")
        
        task = asyncio.create_task(retention_loop())
        self.retention_tasks[policy.policy_id] = task
    
    async def _apply_retention_policy(self, policy: DataRetentionPolicy):
        """Apply data retention policy"""
        try:
            cutoff_date = datetime.utcnow() - policy.retention_period
            
            if policy.data_type == "audit_logs":
                # Remove old audit events
                initial_count = len(self.audit_events)
                self.audit_events = [
                    event for event in self.audit_events
                    if event.timestamp > cutoff_date
                ]
                removed_count = initial_count - len(self.audit_events)
                
                if removed_count > 0:
                    logger.info(f"Retention policy applied: removed {removed_count} old audit events")
                    await self._trigger_event("retention_policy_applied", f"{policy.policy_id}:{removed_count}")
            
        except Exception as e:
            logger.error(f"Failed to apply retention policy {policy.policy_id}: {e}")
    
    async def _trigger_event(self, event_type: str, event_data: str):
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
compliance_orchestrator = ComplianceOrchestrator()


# Convenience functions
async def record_access_event(
    user_id: str,
    service_id: str,
    resource_id: str,
    action: str,
    ip_address: Optional[str] = None
) -> bool:
    """Record an access audit event"""
    event = AuditEvent(
        event_id=str(uuid.uuid4()),
        event_type=AuditEventType.ACCESS,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        service_id=service_id,
        resource_id=resource_id,
        action=action,
        details={"action_type": action},
        ip_address=ip_address
    )
    return await compliance_orchestrator.record_audit_event(event)


async def generate_gdpr_report() -> Optional[ComplianceReport]:
    """Generate GDPR compliance report"""
    return await compliance_orchestrator.generate_compliance_report(ComplianceFramework.GDPR)


async def get_compliance_overview() -> Dict[str, Any]:
    """Get compliance dashboard overview"""
    return await compliance_orchestrator.get_compliance_dashboard()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Record some audit events
        await record_access_event("user123", "api-service", "user-data", "read", "192.168.1.100")
        await record_access_event("admin", "database", "financial-data", "modify", "10.0.0.5")
        
        # Perform compliance check
        results = await compliance_orchestrator.perform_compliance_check(ComplianceFramework.GDPR)
        print(f"GDPR compliance results: {results}")
        
        # Generate compliance report
        report = await generate_gdpr_report()
        if report:
            print(f"Generated compliance report: {report.report_id}")
            print(f"Overall status: {report.overall_status.value}")
            print(f"Violations: {len(report.violations)}")
        
        # Get dashboard overview
        dashboard = await get_compliance_overview()
        print(f"Compliance overview: {dashboard}")
    
    asyncio.run(main())