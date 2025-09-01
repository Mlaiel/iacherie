"""Compliance Monitoring and Security Auditing for Deployment Security

Provides comprehensive compliance monitoring, security audit logging, and policy
enforcement for the IA Influencer Agent platform deployment infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib
import psutil
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """
Supported compliance frameworks"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOX = "sox"


class AuditEventType(Enum):
    """Types of audit events"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_INCIDENT = "security_incident"
    COMPLIANCE_VIOLATION = "compliance_violation"
    POLICY_ENFORCEMENT = "policy_enforcement"


class SeverityLevel(Enum):
    """Severity levels for audit events"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event container"""
    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: SeverityLevel
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any]
    compliance_frameworks: List[ComplianceFramework]
    success: bool
    error_message: Optional[str] = None


@dataclass
class ComplianceRule:
    """
Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    category: str
    description: str
    requirement: str
    validation_function: Callable[[Dict[str, Any]], bool]
    remediation_steps: List[str]
    severity: SeverityLevel
    enabled: bool = True


@dataclass
class ComplianceReport:
    """
Compliance assessment report"""
    framework: ComplianceFramework
    assessment_date: datetime
    total_rules: int
    passed_rules: int
    failed_rules: int
    skipped_rules: int
    compliance_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]


class SecurityAuditLogger:
    """
    Advanced security audit logging system with compliance support
    """
    
    def __init__(
        self,
        log_directory: str = "/var/log/ia-influencer/audit",
        retention_days: int = 2555,  # 7 years for compliance
        encryption_enabled: bool = True,
        max_log_size_mb: int = 100
    ):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self.retention_days = retention_days
        self.encryption_enabled = encryption_enabled
        self.max_log_size_mb = max_log_size_mb
        
        # Initialize log file handlers
        self._setup_log_handlers()
        
        # Event buffer for batch processing
        self._event_buffer: List[AuditEvent] = []
        self._buffer_size = 100
        
        logger.info("Security audit logger initialized")
    
    def _setup_log_handlers(self):
        """Setup specialized log handlers for different event types"""
        self.handlers = {}
        
        for event_type in AuditEventType:
            log_file = self.log_directory / f"audit_{event_type.value}.log"
            
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            
            # Create formatter for structured logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            self.handlers[event_type] = handler
    
    async def log_event(self, event: AuditEvent):
        """
        Log audit event with compliance tracking
        
        Args:
            event: Audit event to log
        """
        try:
            # Add to buffer
            self._event_buffer.append(event)
            
            # Process buffer if full
            if len(self._event_buffer) >= self._buffer_size:
                await self._flush_buffer()
            
            # Immediate logging for critical events
            if event.severity == SeverityLevel.CRITICAL:
                await self._write_event_immediate(event)
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def _flush_buffer(self):
        """Flush event buffer to persistent storage"""
        try:
            if not self._event_buffer:
                return
            
            # Group events by type for efficient writing
            events_by_type = {}
            for event in self._event_buffer:
                if event.event_type not in events_by_type:
                    events_by_type[event.event_type] = []
                events_by_type[event.event_type].append(event)
            
            # Write events to respective log files
            for event_type, events in events_by_type.items():
                await self._write_events_batch(event_type, events)
            
            # Clear buffer
            self._event_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush audit buffer: {e}")
    
    async def _write_events_batch(self, event_type: AuditEventType, events: List[AuditEvent]):
        """Write batch of events to log file"""
        try:
            log_file = self.log_directory / f"audit_{event_type.value}.log"
            
            async with aiofiles.open(log_file, 'a') as file:
                for event in events:
                    log_entry = self._format_log_entry(event)
                    await file.write(log_entry + '\n')
            
            logger.debug(f"Wrote {len(events)} events to {log_file}")
            
        except Exception as e:
            logger.error(f"Failed to write events batch: {e}")
    
    async def _write_event_immediate(self, event: AuditEvent):
        """Write critical event immediately"""
        try:
            log_file = self.log_directory / f"audit_{event.event_type.value}.log"
            
            async with aiofiles.open(log_file, 'a') as file:
                log_entry = self._format_log_entry(event)
                await file.write(log_entry + '\n')
            
            # Also write to critical events log
            critical_log = self.log_directory / "audit_critical.log"
            async with aiofiles.open(critical_log, 'a') as file:
                await file.write(log_entry + '\n')
            
        except Exception as e:
            logger.error(f"Failed to write critical event: {e}")
    
    def _format_log_entry(self, event: AuditEvent) -> str:
        """Format audit event for logging"""
        log_data = {
            'id': event.id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type.value,
            'severity': event.severity.value,
            'user_id': event.user_id,
            'session_id': event.session_id,
            'ip_address': event.ip_address,
            'user_agent': event.user_agent,
            'resource': event.resource,
            'action': event.action,
            'details': event.details,
            'compliance_frameworks': [f.value for f in event.compliance_frameworks],
            'success': event.success,
            'error_message': event.error_message
        }
        
        return json.dumps(log_data, separators=(',', ':'))
    
    async def search_events(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """
        Search audit events with filters
        
        Args:
            start_date: Start date for search
            end_date: End date for search
            event_types: Event types to filter
            user_id: User ID to filter
            severity: Severity level to filter
            limit: Maximum number of results
            
        Returns:
            List of matching audit events
        """
        try:
            events = []
            search_types = event_types or list(AuditEventType)
            
            for event_type in search_types:
                log_file = self.log_directory / f"audit_{event_type.value}.log"
                
                if not log_file.exists():
                    continue
                
                async with aiofiles.open(log_file, 'r') as file:
                    async for line in file:
                        try:
                            log_data = json.loads(line.strip())
                            event_time = datetime.fromisoformat(log_data['timestamp'])
                            
                            # Check date range
                            if not (start_date <= event_time <= end_date):
                                continue
                            
                            # Check user filter
                            if user_id and log_data.get('user_id') != user_id:
                                continue
                            
                            # Check severity filter
                            if severity and log_data.get('severity') != severity.value:
                                continue
                            
                            # Create event object
                            event = AuditEvent(
                                id=log_data['id'],
                                timestamp=event_time,
                                event_type=AuditEventType(log_data['event_type']),
                                severity=SeverityLevel(log_data['severity']),
                                user_id=log_data.get('user_id'),
                                session_id=log_data.get('session_id'),
                                ip_address=log_data.get('ip_address'),
                                user_agent=log_data.get('user_agent'),
                                resource=log_data['resource'],
                                action=log_data['action'],
                                details=log_data['details'],
                                compliance_frameworks=[
                                    ComplianceFramework(f) for f in log_data['compliance_frameworks']
                                ],
                                success=log_data['success'],
                                error_message=log_data.get('error_message')
                            )
                            
                            events.append(event)
                            
                            if len(events) >= limit:
                                break
                                
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            logger.warning(f"Failed to parse log entry: {e}")
                            continue
                
                if len(events) >= limit:
                    break
            
            return sorted(events, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to search audit events: {e}")
            return []
    
    async def cleanup_old_logs(self):
        """Remove old log files based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for log_file in self.log_directory.glob("audit_*.log"):
                # Check file modification time
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old log file: {log_file}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old log files")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")


class ComplianceChecker:
    """
    Comprehensive compliance monitoring and validation system
    """
    
    def __init__(self, audit_logger: SecurityAuditLogger):
        self.audit_logger = audit_logger
        self.compliance_rules: Dict[ComplianceFramework, List[ComplianceRule]] = {}
        self._setup_default_rules()
        logger.info("Compliance checker initialized")
    
    def _setup_default_rules(self):
        """Setup default compliance rules for supported frameworks"""
        
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="GDPR_001",
                framework=ComplianceFramework.GDPR,
                category="Data Protection",
                description="Personal data must be encrypted at rest",
                requirement="Article 32 - Security of processing",
                validation_function=self._check_data_encryption,
                remediation_steps=[
                    "Enable database encryption",
                    "Implement application-level encryption for sensitive fields",
                    "Use strong encryption algorithms (AES-256)"
                ],
                severity=SeverityLevel.HIGH
            ),
            ComplianceRule(
                rule_id="GDPR_002",
                framework=ComplianceFramework.GDPR,
                category="Access Control",
                description="Access to personal data must be logged",
                requirement="Article 30 - Records of processing activities",
                validation_function=self._check_access_logging,
                remediation_steps=[
                    "Implement comprehensive audit logging",
                    "Log all data access operations",
                    "Include user identity and timestamp"
                ],
                severity=SeverityLevel.MEDIUM
            ),
            ComplianceRule(
                rule_id="GDPR_003",
                framework=ComplianceFramework.GDPR,
                category="Data Retention",
                description="Personal data retention periods must be enforced",
                requirement="Article 5 - Principles relating to processing",
                validation_function=self._check_data_retention,
                remediation_steps=[
                    "Implement automatic data deletion",
                    "Define retention policies per data type",
                    "Regular data cleanup processes"
                ],
                severity=SeverityLevel.MEDIUM
            )
        ]
        
        # SOC 2 Rules
        soc2_rules = [
            ComplianceRule(
                rule_id="SOC2_001",
                framework=ComplianceFramework.SOC2,
                category="Security",
                description="System access must be properly controlled",
                requirement="CC6.1 - Logical and Physical Access Controls",
                validation_function=self._check_access_controls,
                remediation_steps=[
                    "Implement role-based access control",
                    "Regular access reviews",
                    "Multi-factor authentication"
                ],
                severity=SeverityLevel.HIGH
            ),
            ComplianceRule(
                rule_id="SOC2_002",
                framework=ComplianceFramework.SOC2,
                category="Availability",
                description="System monitoring must be in place",
                requirement="CC7.1 - System Monitoring",
                validation_function=self._check_system_monitoring,
                remediation_steps=[
                    "Implement comprehensive monitoring",
                    "Set up alerting for critical events",
                    "Regular health checks"
                ],
                severity=SeverityLevel.MEDIUM
            )
        ]
        
        # ISO 27001 Rules
        iso27001_rules = [
            ComplianceRule(
                rule_id="ISO27001_001",
                framework=ComplianceFramework.ISO27001,
                category="Information Security",
                description="Security incident management process must be defined",
                requirement="A.16.1 - Management of information security incidents",
                validation_function=self._check_incident_management,
                remediation_steps=[
                    "Define incident response procedures",
                    "Implement incident tracking system",
                    "Regular incident response training"
                ],
                severity=SeverityLevel.HIGH
            )
        ]
        
        self.compliance_rules = {
            ComplianceFramework.GDPR: gdpr_rules,
            ComplianceFramework.SOC2: soc2_rules,
            ComplianceFramework.ISO27001: iso27001_rules
        }
    
    def _check_data_encryption(self, context: Dict[str, Any]) -> bool:
        """Check if data encryption is properly implemented"""
        try:
            # Check database encryption settings
            db_encrypted = context.get('database_encryption_enabled', False)
            
            # Check application-level encryption
            app_encryption = context.get('application_encryption_enabled', False)
            
            return db_encrypted and app_encryption
            
        except Exception:
            return False
    
    def _check_access_logging(self, context: Dict[str, Any]) -> bool:
        """
Check if access logging is properly implemented"""
        try:
            # Check if audit logging is enabled
            audit_enabled = context.get('audit_logging_enabled', False)
            
            # Check if data access events are logged
            data_access_logged = context.get('data_access_logging_enabled', False)
            
            return audit_enabled and data_access_logged
            
        except Exception:
            return False
    
    def _check_data_retention(self, context: Dict[str, Any]) -> bool:
        """
Check if data retention policies are enforced"""
        try:
            # Check if retention policies are defined
            policies_defined = context.get('retention_policies_defined', False)
            
            # Check if automatic cleanup is enabled
            auto_cleanup = context.get('automatic_cleanup_enabled', False)
            
            return policies_defined and auto_cleanup
            
        except Exception:
            return False
    
    def _check_access_controls(self, context: Dict[str, Any]) -> bool:
        """
Check if access controls are properly implemented"""
        try:
            # Check role-based access control
            rbac_enabled = context.get('rbac_enabled', False)
            
            # Check multi-factor authentication
            mfa_enabled = context.get('mfa_enabled', False)
            
            return rbac_enabled and mfa_enabled
            
        except Exception:
            return False
    
    def _check_system_monitoring(self, context: Dict[str, Any]) -> bool:
        """
Check if system monitoring is properly implemented"""
        try:
            # Check monitoring system status
            monitoring_enabled = context.get('monitoring_enabled', False)
            
            # Check alerting configuration
            alerting_configured = context.get('alerting_configured', False)
            
            return monitoring_enabled and alerting_configured
            
        except Exception:
            return False
    
    def _check_incident_management(self, context: Dict[str, Any]) -> bool:
        """
Check if incident management process is defined"""
        try:
            # Check incident response procedures
            procedures_defined = context.get('incident_procedures_defined', False)
            
            # Check incident tracking system
            tracking_system = context.get('incident_tracking_system', False)
            
            return procedures_defined and tracking_system
            
        except Exception:
            return False
    
    async def assess_compliance(
        self,
        framework: ComplianceFramework,
        context: Dict[str, Any]
    ) -> ComplianceReport:
        """
        Assess compliance against specific framework
        
        Args:
            framework: Compliance framework to assess
            context: Assessment context with system information
            
        Returns:
            Compliance assessment report
        """
        try:
            if framework not in self.compliance_rules:
                raise ValueError(f"Unsupported compliance framework: {framework}")
            
            rules = self.compliance_rules[framework]
            passed_rules = 0
            failed_rules = 0
            skipped_rules = 0
            violations = []
            recommendations = []
            
            for rule in rules:
                if not rule.enabled:
                    skipped_rules += 1
                    continue
                
                try:
                    # Run validation function
                    is_compliant = rule.validation_function(context)
                    
                    if is_compliant:
                        passed_rules += 1
                    else:
                        failed_rules += 1
                        
                        # Record violation
                        violation = {
                            'rule_id': rule.rule_id,
                            'category': rule.category,
                            'description': rule.description,
                            'requirement': rule.requirement,
                            'severity': rule.severity.value,
                            'remediation_steps': rule.remediation_steps
                        }
                        violations.append(violation)
                        
                        # Add to recommendations
                        recommendations.extend(rule.remediation_steps)
                        
                        # Log compliance violation
                        await self._log_compliance_violation(rule, context)
                    
                except Exception as e:
                    logger.error(f"Failed to validate rule {rule.rule_id}: {e}")
                    skipped_rules += 1
            
            # Calculate compliance score
            total_assessed = passed_rules + failed_rules
            compliance_score = (passed_rules / total_assessed * 100) if total_assessed > 0 else 0
            
            report = ComplianceReport(
                framework=framework,
                assessment_date=datetime.utcnow(),
                total_rules=len(rules),
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                skipped_rules=skipped_rules,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=list(set(recommendations))  # Remove duplicates
            )
            
            logger.info(f"Compliance assessment completed for {framework.value}: {compliance_score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"Failed to assess compliance: {e}")
            raise
    
    async def _log_compliance_violation(self, rule: ComplianceRule, context: Dict[str, Any]):
        """Log compliance violation as audit event"""
        try:
            event = AuditEvent(
                id=hashlib.sha256(f"{rule.rule_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.COMPLIANCE_VIOLATION,
                severity=rule.severity,
                user_id=context.get('user_id'),
                session_id=context.get('session_id'),
                ip_address=context.get('ip_address'),
                user_agent=context.get('user_agent'),
                resource=f"compliance/{rule.framework.value}",
                action="assessment",
                details={
                    'rule_id': rule.rule_id,
                    'category': rule.category,
                    'description': rule.description,
                    'requirement': rule.requirement,
                    'remediation_steps': rule.remediation_steps
                },
                compliance_frameworks=[rule.framework],
                success=False,
                error_message=f"Compliance violation: {rule.description}"
            )
            
            await self.audit_logger.log_event(event)
            
        except Exception as e:
            logger.error(f"Failed to log compliance violation: {e}")
    
    def add_custom_rule(self, rule: ComplianceRule):
        """
        Add custom compliance rule
        
        Args:
            rule: Custom compliance rule
        """
        if rule.framework not in self.compliance_rules:
            self.compliance_rules[rule.framework] = []
        
        self.compliance_rules[rule.framework].append(rule)
        logger.info(f"Added custom compliance rule: {rule.rule_id}")
    
    async def generate_compliance_report(
        self,
        frameworks: List[ComplianceFramework],
        context: Dict[str, Any],
        output_file: Optional[str] = None
    ) -> Dict[str, ComplianceReport]:
        """
        Generate comprehensive compliance report for multiple frameworks
        
        Args:
            frameworks: List of compliance frameworks to assess
            context: Assessment context
            output_file: Optional output file path
            
        Returns:
            Dictionary of compliance reports by framework
        """
        try:
            reports = {}
            
            for framework in frameworks:
                report = await self.assess_compliance(framework, context)
                reports[framework.value] = report
            
            # Save to file if requested
            if output_file:
                report_data = {}
                for framework, report in reports.items():
                    report_data[framework] = {
                        'assessment_date': report.assessment_date.isoformat(),
                        'total_rules': report.total_rules,
                        'passed_rules': report.passed_rules,
                        'failed_rules': report.failed_rules,
                        'skipped_rules': report.skipped_rules,
                        'compliance_score': report.compliance_score,
                        'violations': report.violations,
                        'recommendations': report.recommendations
                    }
                
                async with aiofiles.open(output_file, 'w') as file:
                    await file.write(json.dumps(report_data, indent=2))
                
                logger.info(f"Compliance report saved to: {output_file}")
            
            return reports
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise


class PolicyEnforcer:
    """
    Security policy enforcement system
    """
    
    def __init__(self, audit_logger: SecurityAuditLogger):
        self.audit_logger = audit_logger
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.enforcement_handlers: Dict[str, Callable] = {}
        self._setup_default_policies()
        logger.info("Policy enforcer initialized")
    
    def _setup_default_policies(self):
        """Setup default security policies"""
        self.policies = {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'history_count': 5
            },
            'session_policy': {
                'max_duration_minutes': 480,  # 8 hours
                'idle_timeout_minutes': 30,
                'concurrent_sessions_limit': 3,
                'require_mfa': True
            },
            'access_policy': {
                'max_failed_attempts': 5,
                'lockout_duration_minutes': 30,
                'ip_whitelist_enabled': False,
                'rate_limit_enabled': True,
                'rate_limit_requests_per_minute': 100
            },
            'data_classification_policy': {
                'encryption_required_for_pii': True,
                'encryption_required_for_financial': True,
                'access_logging_required': True,
                'retention_enforcement': True
            }
        }
    
    async def enforce_password_policy(
        self,
        user_id: str,
        password: str,
        current_password_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enforce password policy compliance
        
        Args:
            user_id: User identifier
            password: New password to validate
            current_password_hash: Current password hash for history check
            
        Returns:
            Policy enforcement result
        """
        try:
            policy = self.policies['password_policy']
            violations = []
            
            # Check minimum length
            if len(password) < policy['min_length']:
                violations.append(f"Password must be at least {policy['min_length']} characters")
            
            # Check character requirements
            if policy['require_uppercase'] and not any(c.isupper() for c in password):
                violations.append("Password must contain uppercase letters")
            
            if policy['require_lowercase'] and not any(c.islower() for c in password):
                violations.append("Password must contain lowercase letters")
            
            if policy['require_numbers'] and not any(c.isdigit() for c in password):
                violations.append("Password must contain numbers")
            
            if policy['require_special_chars'] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                violations.append("Password must contain special characters")
            
            is_compliant = len(violations) == 0
            
            # Log policy enforcement
            await self._log_policy_enforcement(
                policy_name="password_policy",
                user_id=user_id,
                resource="user_password",
                action="password_change",
                success=is_compliant,
                violations=violations
            )
            
            return {
                'compliant': is_compliant,
                'violations': violations,
                'policy': policy
            }
            
        except Exception as e:
            logger.error(f"Failed to enforce password policy: {e}")
            return {
                'compliant': False,
                'violations': [str(e)],
                'policy': {}
            }
    
    async def enforce_session_policy(
        self,
        user_id: str,
        session_id: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforce session policy compliance
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            session_data: Session information
            
        Returns:
            Policy enforcement result
        """
        try:
            policy = self.policies['session_policy']
            violations = []
            actions_required = []
            
            # Check session duration
            session_start = datetime.fromisoformat(session_data.get('created_at', datetime.utcnow().isoformat()))
            session_age_minutes = (datetime.utcnow() - session_start).total_seconds() / 60
            
            if session_age_minutes > policy['max_duration_minutes']:
                violations.append(f"Session exceeded maximum duration of {policy['max_duration_minutes']} minutes")
                actions_required.append("terminate_session")
            
            # Check idle timeout
            last_activity = datetime.fromisoformat(session_data.get('last_activity', datetime.utcnow().isoformat()))
            idle_minutes = (datetime.utcnow() - last_activity).total_seconds() / 60
            
            if idle_minutes > policy['idle_timeout_minutes']:
                violations.append(f"Session idle for {idle_minutes:.1f} minutes, exceeds {policy['idle_timeout_minutes']} limit")
                actions_required.append("terminate_session")
            
            # Check MFA requirement
            if policy['require_mfa'] and not session_data.get('mfa_verified', False):
                violations.append("Multi-factor authentication required")
                actions_required.append("require_mfa")
            
            is_compliant = len(violations) == 0
            
            # Log policy enforcement
            await self._log_policy_enforcement(
                policy_name="session_policy",
                user_id=user_id,
                resource=f"session/{session_id}",
                action="session_validation",
                success=is_compliant,
                violations=violations
            )
            
            return {
                'compliant': is_compliant,
                'violations': violations,
                'actions_required': actions_required,
                'policy': policy
            }
            
        except Exception as e:
            logger.error(f"Failed to enforce session policy: {e}")
            return {
                'compliant': False,
                'violations': [str(e)],
                'actions_required': [],
                'policy': {}
            }
    
    async def enforce_access_policy(
        self,
        user_id: str,
        ip_address: str,
        resource: str,
        failed_attempts: int = 0
    ) -> Dict[str, Any]:
        """
        Enforce access policy compliance
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            resource: Resource being accessed
            failed_attempts: Number of recent failed attempts
            
        Returns:
            Policy enforcement result
        """
        try:
            policy = self.policies['access_policy']
            violations = []
            actions_required = []
            
            # Check failed attempts limit
            if failed_attempts >= policy['max_failed_attempts']:
                violations.append(f"Failed attempts limit exceeded: {failed_attempts}/{policy['max_failed_attempts']}")
                actions_required.append("account_lockout")
            
            # Check IP whitelist (if enabled)
            if policy.get('ip_whitelist_enabled', False):
                whitelist = policy.get('ip_whitelist', [])
                if ip_address not in whitelist:
                    violations.append(f"IP address not in whitelist: {ip_address}")
                    actions_required.append("deny_access")
            
            is_compliant = len(violations) == 0
            
            # Log policy enforcement
            await self._log_policy_enforcement(
                policy_name="access_policy",
                user_id=user_id,
                resource=resource,
                action="access_attempt",
                success=is_compliant,
                violations=violations,
                context={'ip_address': ip_address, 'failed_attempts': failed_attempts}
            )
            
            return {
                'compliant': is_compliant,
                'violations': violations,
                'actions_required': actions_required,
                'policy': policy
            }
            
        except Exception as e:
            logger.error(f"Failed to enforce access policy: {e}")
            return {
                'compliant': False,
                'violations': [str(e)],
                'actions_required': [],
                'policy': {}
            }
    
    async def _log_policy_enforcement(
        self,
        policy_name: str,
        user_id: str,
        resource: str,
        action: str,
        success: bool,
        violations: List[str],
        context: Optional[Dict[str, Any]] = None
    ):
        """Log policy enforcement event"""
        try:
            event = AuditEvent(
                id=hashlib.sha256(f"{policy_name}:{user_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.POLICY_ENFORCEMENT,
                severity=SeverityLevel.HIGH if not success else SeverityLevel.LOW,
                user_id=user_id,
                session_id=context.get('session_id') if context else None,
                ip_address=context.get('ip_address') if context else None,
                user_agent=context.get('user_agent') if context else None,
                resource=resource,
                action=action,
                details={
                    'policy_name': policy_name,
                    'violations': violations,
                    'context': context or {}
                },
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
                success=success,
                error_message='; '.join(violations) if violations else None
            )
            
            await self.audit_logger.log_event(event)
            
        except Exception as e:
            logger.error(f"Failed to log policy enforcement: {e}")
    
    def update_policy(self, policy_name: str, policy_config: Dict[str, Any]):
        """
        Update security policy configuration
        
        Args:
            policy_name: Name of the policy to update
            policy_config: New policy configuration
        """
        self.policies[policy_name] = policy_config
        logger.info(f"Updated policy: {policy_name}")
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Get summary of all configured policies
        
        Returns:
            Policy summary
        """
        summary = {
            'total_policies': len(self.policies),
            'policies': {}
        }
        
        for policy_name, policy_config in self.policies.items():
            summary['policies'][policy_name] = {
                'configured': True,
                'settings_count': len(policy_config),
                'last_updated': datetime.utcnow().isoformat()
            }
        
        return summary
