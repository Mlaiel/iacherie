"""IA Influencer Agent - Regulatory Reporting System
Automated compliance reporting for multiple regulatory frameworks

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.compliance import ComplianceReport, RegulatorySubmission
from backend.models.audit import AuditLog
from backend.utils.document_generation import generate_pdf_report, generate_xml_report
from backend.utils.encryption import encrypt_report_data, sign_report
from backend.core.storage import upload_to_secure_storage
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel, ComplianceFramework
from .compliance_monitor import ComplianceMonitor

logger = get_logger(__name__)


class ReportType(str, Enum):
    """Regulatory report types"""
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    INCIDENT = "incident"
    BREACH_NOTIFICATION = "breach_notification"
    AUDIT_RESPONSE = "audit_response"
    TRANSPARENCY = "transparency"
    COMPLIANCE_ASSESSMENT = "compliance_assessment"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    XML = "xml"
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class SubmissionMethod(str, Enum):
    """Report submission methods"""
    AUTOMATED_API = "automated_api"
    SECURE_PORTAL = "secure_portal"
    EMAIL_ENCRYPTED = "email_encrypted"
    MANUAL_UPLOAD = "manual_upload"
    POSTAL_MAIL = "postal_mail"


class ReportStatus(str, Enum):
    """Report generation and submission status"""
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    RESUBMISSION_REQUIRED = "resubmission_required"


@dataclass
class RegulatoryRequirement:
    """Regulatory reporting requirement definition"""
    requirement_id: str
    framework: ComplianceFramework
    jurisdiction: str
    report_type: ReportType
    frequency: str  # monthly, quarterly, annual, event-driven
    due_date_offset_days: int
    required_sections: List[str]
    data_sources: List[str]
    submission_method: SubmissionMethod
    format_requirements: List[ReportFormat]
    contact_authority: Dict[str, str]
    penalties_for_non_compliance: str
    automated_submission: bool


@dataclass
class ComplianceMetrics:
    """Compliance metrics for reporting"""
    metric_name: str
    metric_value: float
    unit: str
    period_start: datetime
    period_end: datetime
    data_source: str
    calculation_method: str
    confidence_level: float
    supporting_evidence: List[str]


@dataclass
class RegulatoryReport:
    """Complete regulatory report structure"""
    report_id: str
    framework: ComplianceFramework
    report_type: ReportType
    jurisdiction: str
    reporting_period: Dict[str, datetime]
    organization_details: Dict[str, Any]
    executive_summary: Dict[str, Any]
    compliance_metrics: List[ComplianceMetrics]
    incidents_summary: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    controls_effectiveness: Dict[str, Any]
    remediation_actions: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    appendices: Dict[str, Any]
    generated_at: datetime
    generated_by: str
    digital_signature: Optional[str]


class RegulatoryReportingSystem:
    """Automated regulatory reporting and submission system"""
    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.compliance_monitor = ComplianceMonitor()
        self.automated_reporting = settings.AUTOMATED_REGULATORY_REPORTING
        self.report_encryption = settings.REGULATORY_REPORT_ENCRYPTION
        self.digital_signatures = settings.REGULATORY_REPORT_SIGNATURES
        
        # Regulatory requirements by framework
        self.regulatory_requirements = self._load_regulatory_requirements()
        
        # Report templates and sections
        self.report_templates = self._load_report_templates()
        
        # Scheduled reporting tasks
        self._reporting_tasks: Set[asyncio.Task] = set()
        self._scheduler_running = False
    
    async def start_reporting_scheduler(self) -> None:
        """Start automated regulatory reporting scheduler"""
        try:
            if self._scheduler_running:
                self.logger.warning("Regulatory reporting scheduler already running")
                return
            
            self._scheduler_running = True
            
            # Start periodic report generation task
            scheduler_task = asyncio.create_task(self._periodic_report_scheduler())
            self._reporting_tasks.add(scheduler_task)
            
            # Start submission status monitoring
            monitoring_task = asyncio.create_task(self._monitor_submission_status())
            self._reporting_tasks.add(monitoring_task)
            
            self.logger.info("Regulatory reporting scheduler started")
            
        except Exception as e:
            self.logger.error(f"Failed to start reporting scheduler: {str(e)}")
            raise
    
    async def stop_reporting_scheduler(self) -> None:
        """Stop regulatory reporting scheduler"""
        try:
            self._scheduler_running = False
            
            # Cancel all reporting tasks
            for task in self._reporting_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._reporting_tasks, return_exceptions=True)
            self._reporting_tasks.clear()
            
            self.logger.info("Regulatory reporting scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping reporting scheduler: {str(e)}")
    
    async def generate_regulatory_report(
        self,
        framework: ComplianceFramework,
        report_type: ReportType,
        jurisdiction: str,
        period_start: datetime,
        period_end: datetime,
        generated_by: str
    ) -> str:
        """Generate comprehensive regulatory report"""
        try:
            # Get regulatory requirement
            requirement = self._get_regulatory_requirement(framework, report_type, jurisdiction)
            if not requirement:
                raise ValueError(f"No regulatory requirement found for {framework.value} {report_type.value} in {jurisdiction}")
            
            # Generate report ID
            report_id = f"REG-{framework.value.upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Collect compliance data
            compliance_data = await self._collect_compliance_data(
                framework, period_start, period_end, requirement.data_sources
            )
            
            # Generate report sections
            report_sections = await self._generate_report_sections(
                framework, report_type, compliance_data, requirement.required_sections
            )
            
            # Create regulatory report
            regulatory_report = RegulatoryReport(
                report_id=report_id,
                framework=framework,
                report_type=report_type,
                jurisdiction=jurisdiction,
                reporting_period={
                    "start": period_start,
                    "end": period_end
                },
                organization_details=await self._get_organization_details(),
                executive_summary=report_sections["executive_summary"],
                compliance_metrics=report_sections["compliance_metrics"],
                incidents_summary=report_sections["incidents_summary"],
                risk_assessment=report_sections["risk_assessment"],
                controls_effectiveness=report_sections["controls_effectiveness"],
                remediation_actions=report_sections["remediation_actions"],
                certifications=report_sections["certifications"],
                appendices=report_sections["appendices"],
                generated_at=datetime.utcnow(),
                generated_by=generated_by,
                digital_signature=None
            )
            
            # Generate digital signature if enabled
            if self.digital_signatures:
                regulatory_report.digital_signature = await self._generate_digital_signature(
                    regulatory_report
                )
            
            # Store report
            await self._store_regulatory_report(regulatory_report, requirement)
            
            # Generate output formats
            output_files = await self._generate_report_formats(
                regulatory_report, requirement.format_requirements
            )
            
            # Log report generation
            await self.audit_logger.log_audit_event(
                event_type="regulatory_report_generated",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Regulatory report generated: {framework.value} {report_type.value}",
                details={
                    "report_id": report_id,
                    "framework": framework.value,
                    "report_type": report_type.value,
                    "jurisdiction": jurisdiction,
                    "period_days": (period_end - period_start).days,
                    "generated_by": generated_by,
                    "output_formats": [fmt.value for fmt in requirement.format_requirements]
                }
            )
            
            return report_id
            
        except Exception as e:
            self.logger.error(f"Error generating regulatory report: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate regulatory report")
    
    async def submit_regulatory_report(
        self,
        report_id: str,
        submission_method: Optional[SubmissionMethod] = None,
        reviewer_approval: bool = False
    ) -> Dict[str, Any]:
        """Submit regulatory report to authorities"""
        try:
            # Get report details
            async with get_db_session() as session:
                report_result = await session.execute(
                    select(ComplianceReport).where(ComplianceReport.report_id == report_id)
                )
                report_record = report_result.scalar_one_or_none()
                
                if not report_record:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                if report_record.status not in [ReportStatus.GENERATED.value, ReportStatus.REVIEWED.value, ReportStatus.APPROVED.value]:
                    raise HTTPException(status_code=400, detail="Report not ready for submission")
            
            # Get requirement details
            requirement = self._get_regulatory_requirement(
                ComplianceFramework(report_record.framework),
                ReportType(report_record.report_type),
                report_record.jurisdiction
            )
            
            # Use specified submission method or default from requirement
            method = submission_method or requirement.submission_method
            
            # Check if approval is required but not obtained
            if requirement.automated_submission == False and not reviewer_approval:
                raise HTTPException(status_code=400, detail="Manual approval required before submission")
            
            # Submit based on method
            submission_result = {}
            if method == SubmissionMethod.AUTOMATED_API:
                submission_result = await self._submit_via_api(report_id, requirement)
            elif method == SubmissionMethod.SECURE_PORTAL:
                submission_result = await self._submit_via_portal(report_id, requirement)
            elif method == SubmissionMethod.EMAIL_ENCRYPTED:
                submission_result = await self._submit_via_email(report_id, requirement)
            else:
                # Manual submission methods
                submission_result = await self._prepare_manual_submission(report_id, requirement, method)
            
            # Update submission status
            submission_id = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{report_id[-8:]}"
            
            async with get_db_session() as session:
                submission_record = RegulatorySubmission(
                    submission_id=submission_id,
                    report_id=report_id,
                    submission_method=method.value,
                    submitted_at=datetime.utcnow(),
                    status="submitted",
                    authority_response=json.dumps(submission_result),
                    tracking_reference=submission_result.get("tracking_reference"),
                    acknowledgment_deadline=datetime.utcnow() + timedelta(days=requirement.due_date_offset_days)
                )
                
                session.add(submission_record)
                
                # Update report status
                await session.execute(
                    update(ComplianceReport)
                    .where(ComplianceReport.report_id == report_id)
                    .values(
                        status=ReportStatus.SUBMITTED.value,
                        submitted_at=datetime.utcnow(),
                        submission_id=submission_id
                    )
                )
                
                await session.commit()
            
            # Log submission
            await self.audit_logger.log_audit_event(
                event_type="regulatory_report_submitted",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Regulatory report submitted: {report_id}",
                details={
                    "report_id": report_id,
                    "submission_id": submission_id,
                    "submission_method": method.value,
                    "authority": requirement.contact_authority.get("name", "Unknown"),
                    "tracking_reference": submission_result.get("tracking_reference")
                }
            )
            
            return {
                "submission_id": submission_id,
                "report_id": report_id,
                "status": "submitted",
                "submission_method": method.value,
                "submitted_at": datetime.utcnow().isoformat(),
                "tracking_reference": submission_result.get("tracking_reference"),
                "acknowledgment_deadline": (datetime.utcnow() + timedelta(days=requirement.due_date_offset_days)).isoformat(),
                "authority_contact": requirement.contact_authority
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting regulatory report: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to submit regulatory report")
    
    async def track_regulatory_compliance(
        self,
        framework: ComplianceFramework,
        jurisdiction: str = None
    ) -> Dict[str, Any]:
        """Track regulatory compliance status and upcoming deadlines"""
        try:
            # Get applicable requirements
            requirements = [
                req for req in self.regulatory_requirements.values()
                if req.framework == framework and (not jurisdiction or req.jurisdiction == jurisdiction)
            ]
            
            compliance_status = {
                "framework": framework.value,
                "jurisdiction": jurisdiction or "all",
                "overall_status": "compliant",
                "requirements_tracked": len(requirements),
                "upcoming_deadlines": [],
                "overdue_reports": [],
                "recent_submissions": [],
                "compliance_score": 100.0,
                "next_actions": []
            }
            
            now = datetime.utcnow()
            
            # Check each requirement
            for req in requirements:
                try:
                    # Calculate next due date
                    next_due_date = await self._calculate_next_due_date(req)
                    days_until_due = (next_due_date - now).days
                    
                    # Check for upcoming deadlines (within 30 days)
                    if 0 <= days_until_due <= 30:
                        compliance_status["upcoming_deadlines"].append({
                            "requirement_id": req.requirement_id,
                            "report_type": req.report_type.value,
                            "due_date": next_due_date.isoformat(),
                            "days_remaining": days_until_due,
                            "urgency": "high" if days_until_due <= 7 else "medium"
                        })
                    
                    # Check for overdue reports
                    if days_until_due < 0:
                        compliance_status["overdue_reports"].append({
                            "requirement_id": req.requirement_id,
                            "report_type": req.report_type.value,
                            "due_date": next_due_date.isoformat(),
                            "days_overdue": abs(days_until_due),
                            "penalties": req.penalties_for_non_compliance
                        })
                        compliance_status["overall_status"] = "non_compliant"
                        compliance_status["compliance_score"] -= 20  # -20 points per overdue report
                
                except Exception as e:
                    self.logger.error(f"Error checking requirement {req.requirement_id}: {str(e)}")
                    continue
            
            # Get recent submissions
            compliance_status["recent_submissions"] = await self._get_recent_submissions(
                framework, jurisdiction, days=90
            )
            
            # Generate next actions
            if compliance_status["overdue_reports"]:
                compliance_status["next_actions"].append("Address overdue reports immediately")
            
            if compliance_status["upcoming_deadlines"]:
                urgent_deadlines = [d for d in compliance_status["upcoming_deadlines"] if d["urgency"] == "high"]
                if urgent_deadlines:
                    compliance_status["next_actions"].append(f"Prepare {len(urgent_deadlines)} urgent reports")
            
            # Ensure compliance score is within bounds
            compliance_status["compliance_score"] = max(0.0, min(100.0, compliance_status["compliance_score"]))
            
            return compliance_status
            
        except Exception as e:
            self.logger.error(f"Error tracking regulatory compliance: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to track regulatory compliance")
    
    async def _collect_compliance_data(
        self,
        framework: ComplianceFramework,
        period_start: datetime,
        period_end: datetime,
        data_sources: List[str]
    ) -> Dict[str, Any]:
        """Collect compliance data from various sources"""
        try:
            compliance_data = {
                "audit_logs": [],
                "compliance_metrics": [],
                "incidents": [],
                "user_data": {},
                "system_metrics": {}
            }
            
            async with get_db_session() as session:
                # Collect audit logs
                if "audit_logs" in data_sources:
                    audit_result = await session.execute(
                        select(AuditLog).where(
                            and_(
                                AuditLog.timestamp >= period_start,
                                AuditLog.timestamp <= period_end
                            )
                        )
                    )
                    compliance_data["audit_logs"] = [
                        {
                            "event_id": log.event_id,
                            "event_type": log.event_type,
                            "category": log.category,
                            "level": log.level,
                            "timestamp": log.timestamp.isoformat(),
                            "user_id": log.user_id
                        }
                        for log in audit_result.scalars().all()
                    ]
                
                # Collect compliance metrics
                if "compliance_metrics" in data_sources:
                    compliance_data["compliance_metrics"] = await self.compliance_monitor.evaluate_compliance_status(
                        framework, self.compliance_monitor.MonitoringScope.SYSTEM
                    )
                
                # Collect user statistics
                if "user_data" in data_sources:
                    user_count_result = await session.execute(
                        select(func.count(User.id)).where(User.is_active == True)
                    )
                    compliance_data["user_data"]["total_active_users"] = user_count_result.scalar() or 0
            
            return compliance_data
            
        except Exception as e:
            self.logger.error(f"Error collecting compliance data: {str(e)}")
            return {}
    
    def _load_regulatory_requirements(self) -> Dict[str, RegulatoryRequirement]:
        """Load regulatory reporting requirements"""
        return {
            "GDPR_ANNUAL_EU": RegulatoryRequirement(
                requirement_id="GDPR_ANNUAL_EU",
                framework=ComplianceFramework.GDPR,
                jurisdiction="EU",
                report_type=ReportType.ANNUAL,
                frequency="annual",
                due_date_offset_days=90,  # 90 days after year end
                required_sections=[
                    "data_processing_activities",
                    "data_subject_requests",
                    "data_breaches",
                    "privacy_impact_assessments",
                    "data_protection_measures"
                ],
                data_sources=["audit_logs", "compliance_metrics", "user_data"],
                submission_method=SubmissionMethod.SECURE_PORTAL,
                format_requirements=[ReportFormat.PDF, ReportFormat.XML],
                contact_authority={
                    "name": "Data Protection Authority",
                    "email": "contact@dataprotection.eu",
                    "portal": "https://compliance.dataprotection.eu"
                },
                penalties_for_non_compliance="Up to 4% of annual turnover or €20 million",
                automated_submission=False
            ),
            "CCPA_ANNUAL_CA": RegulatoryRequirement(
                requirement_id="CCPA_ANNUAL_CA",
                framework=ComplianceFramework.CCPA,
                jurisdiction="CA",
                report_type=ReportType.ANNUAL,
                frequency="annual",
                due_date_offset_days=120,
                required_sections=[
                    "consumer_requests",
                    "personal_information_categories",
                    "third_party_disclosures",
                    "privacy_policy_updates"
                ],
                data_sources=["audit_logs", "compliance_metrics"],
                submission_method=SubmissionMethod.EMAIL_ENCRYPTED,
                format_requirements=[ReportFormat.PDF],
                contact_authority={
                    "name": "California Attorney General",
                    "email": "privacy@oag.ca.gov"
                },
                penalties_for_non_compliance="Up to $7,500 per violation",
                automated_submission=False
            )
        }


# Export for use in other modules
__all__ = ["RegulatoryReportingSystem", "ReportType", "ReportFormat", "SubmissionMethod", "ReportStatus"]
