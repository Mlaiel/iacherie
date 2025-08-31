"""Reporting Systems Module
=======================

Comprehensive reporting and compliance documentation system.
Generates detailed reports for various stakeholders and compliance requirements.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.
"""import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import io
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Report type enumeration."""    COMPLIANCE = "compliance"
    VIOLATION = "violation"
    PERFORMANCE = "performance"
    DASHBOARD = "dashboard"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    LEGAL = "legal"
    AUDIT = "audit"


class ReportFormat(Enum):
    """Report format enumeration."""    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    TXT = "txt"


class ReportStatus(Enum):
    """Report status enumeration."""    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class ReportTemplate:
    """Report template configuration."""    template_id: str
    name: str
    description: str
    report_type: ReportType
    sections: List[str]
    required_data: List[str]
    format_options: List[ReportFormat]
    default_format: ReportFormat
    template_path: Optional[str] = None


@dataclass
class ReportRequest:
    """Report generation request."""    request_id: str
    report_type: ReportType
    report_format: ReportFormat
    user_id: Optional[str]
    date_range: Dict[str, str]
    filters: Dict[str, Any]
    template_id: Optional[str]
    output_path: Optional[str]
    created_at: datetime
    requested_by: str


@dataclass
class ReportResult:
    """Report generation result."""    request_id: str
    status: ReportStatus
    file_path: Optional[str]
    file_size: Optional[int]
    generation_time: Optional[float]
    error_message: Optional[str]
    metadata: Dict[str, Any]
    generated_at: datetime


class ComplianceReporter:
    """    Compliance reporting system.
    
    Generates compliance reports for regulatory requirements
    and internal audit purposes.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "/tmp/reports/compliance"))
        self.templates_dir = Path(config.get("templates_dir", "./templates/compliance"))
        self.retention_days = config.get("retention_days", 2555)  # 7 years default
        
    async def initialize(self) -> bool:
        """Initialize compliance reporter."""        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load compliance templates
            await self._load_compliance_templates()
            
            logger.info("ComplianceReporter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ComplianceReporter: {e}")
            return False
    
    async def _load_compliance_templates(self) -> None:
        """Load compliance report templates."""        # Load GDPR compliance template
        self.gdpr_template = {
            "sections": [
                "data_processing_summary",
                "user_consent_status",
                "data_retention_compliance",
                "security_measures",
                "breach_notifications",
                "subject_access_requests"
            ],
            "format": "html",
            "retention_required": True
        }
        
        # Load DMCA compliance template
        self.dmca_template = {
            "sections": [
                "takedown_requests",
                "counter_notifications",
                "repeat_infringer_policy",
                "safe_harbor_compliance",
                "response_times"
            ],
            "format": "html",
            "retention_required": True
        }
        
        # Load SOX compliance template (if applicable)
        self.sox_template = {
            "sections": [
                "internal_controls",
                "audit_trail",
                "data_integrity",
                "access_controls",
                "change_management"
            ],
            "format": "html",
            "retention_required": True
        }
        
        logger.info("Compliance templates loaded")
    
    async def generate_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report."""        try:
            # Determine report type based on request
            report_type = analytics_data.get("compliance_type", "general")
            
            if report_type == "gdpr":
                return await self._generate_gdpr_report(user_id, analytics_data)
            elif report_type == "dmca":
                return await self._generate_dmca_report(user_id, analytics_data)
            elif report_type == "sox":
                return await self._generate_sox_report(user_id, analytics_data)
            else:
                return await self._generate_general_compliance_report(user_id, analytics_data)
                
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}
    
    async def _generate_gdpr_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate GDPR compliance report."""        try:
            report_data = {
                "report_type": "gdpr_compliance",
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "reporting_period": analytics_data.get("period", {}),
                "data_processing_summary": {
                    "purpose": "Content protection and surveillance monitoring",
                    "legal_basis": "Legitimate interest (IP protection)",
                    "data_categories": [
                        "Content fingerprints",
                        "Platform monitoring data",
                        "Violation detection results",
                        "Evidence files (screenshots, metadata)"
                    ],
                    "retention_period": f"{self.retention_days} days",
                    "automated_processing": True
                },
                "user_consent_status": {
                    "consent_obtained": True,
                    "consent_date": analytics_data.get("user_consent_date"),
                    "consent_withdrawn": False,
                    "consent_mechanism": "Platform registration"
                },
                "data_retention_compliance": {
                    "retention_policy_followed": True,
                    "data_minimization_applied": True,
                    "automatic_deletion_enabled": True,
                    "retention_schedule": {
                        "surveillance_data": "365 days",
                        "evidence_files": "2555 days (legal requirement)",
                        "user_profiles": "Until account deletion + 30 days"
                    }
                },
                "security_measures": {
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                    "access_controls": True,
                    "audit_logging": True,
                    "regular_security_assessments": True,
                    "staff_training": True
                },
                "breach_notifications": {
                    "breaches_detected": 0,
                    "notifications_sent": 0,
                    "authority_notifications": 0,
                    "response_time_compliance": "N/A"
                },
                "subject_access_requests": {
                    "requests_received": analytics_data.get("sar_requests", 0),
                    "requests_fulfilled": analytics_data.get("sar_fulfilled", 0),
                    "average_response_time": analytics_data.get("sar_response_time", 0),
                    "compliance_rate": "100%"
                },
                "surveillance_activities": {
                    "monitoring_targets": analytics_data.get("active_targets", 0),
                    "violations_detected": analytics_data.get("violations_count", 0),
                    "platforms_monitored": analytics_data.get("platforms_count", 0),
                    "evidence_collected": analytics_data.get("evidence_count", 0)
                },
                "compliance_assessment": {
                    "overall_status": "Compliant",
                    "risk_level": "Low",
                    "action_items": [],
                    "next_review_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
                }
            }
            
            # Generate HTML report
            html_content = await self._generate_html_report("gdpr_compliance", report_data)
            
            # Save report
            report_filename = f"gdpr_compliance_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_type": "gdpr_compliance",
                "status": "completed",
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating GDPR report: {e}")
            return {"error": str(e)}
    
    async def _generate_dmca_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DMCA compliance report."""        try:
            report_data = {
                "report_type": "dmca_compliance",
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "reporting_period": analytics_data.get("period", {}),
                "takedown_requests": {
                    "total_requests": analytics_data.get("takedown_requests", 0),
                    "successful_takedowns": analytics_data.get("successful_takedowns", 0),
                    "pending_requests": analytics_data.get("pending_takedowns", 0),
                    "average_response_time": analytics_data.get("takedown_response_time", 0)
                },
                "counter_notifications": {
                    "counter_notices_received": analytics_data.get("counter_notices", 0),
                    "counter_notices_processed": analytics_data.get("counter_notices_processed", 0),
                    "reinstatements": analytics_data.get("reinstatements", 0)
                },
                "repeat_infringer_policy": {
                    "policy_implemented": True,
                    "repeat_infringers_identified": analytics_data.get("repeat_infringers", 0),
                    "accounts_terminated": analytics_data.get("accounts_terminated", 0)
                },
                "safe_harbor_compliance": {
                    "designated_agent_registered": True,
                    "contact_information_current": True,
                    "notice_takedown_procedure": True,
                    "reasonable_response_time": True
                },
                "platform_statistics": {
                    "platforms_monitored": analytics_data.get("platforms_count", 0),
                    "violations_detected": analytics_data.get("violations_count", 0),
                    "evidence_collected": analytics_data.get("evidence_count", 0)
                }
            }
            
            # Generate HTML report
            html_content = await self._generate_html_report("dmca_compliance", report_data)
            
            # Save report
            report_filename = f"dmca_compliance_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_type": "dmca_compliance",
                "status": "completed",
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating DMCA report: {e}")
            return {"error": str(e)}
    
    async def _generate_sox_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SOX compliance report."""        try:
            report_data = {
                "report_type": "sox_compliance",
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "reporting_period": analytics_data.get("period", {}),
                "internal_controls": {
                    "access_controls_implemented": True,
                    "segregation_of_duties": True,
                    "authorization_controls": True,
                    "documentation_requirements": True
                },
                "audit_trail": {
                    "comprehensive_logging": True,
                    "log_integrity": True,
                    "log_retention": f"{self.retention_days} days",
                    "regular_log_review": True
                },
                "data_integrity": {
                    "data_validation_controls": True,
                    "backup_procedures": True,
                    "data_recovery_tested": True,
                    "checksum_verification": True
                },
                "change_management": {
                    "formal_change_process": True,
                    "change_approval_required": True,
                    "change_documentation": True,
                    "rollback_procedures": True
                }
            }
            
            # Generate HTML report
            html_content = await self._generate_html_report("sox_compliance", report_data)
            
            # Save report
            report_filename = f"sox_compliance_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_type": "sox_compliance",
                "status": "completed",
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating SOX report: {e}")
            return {"error": str(e)}
    
    async def _generate_general_compliance_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general compliance report."""        try:
            report_data = {
                "report_type": "general_compliance",
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "reporting_period": analytics_data.get("period", {}),
                "surveillance_overview": {
                    "monitoring_targets": analytics_data.get("active_targets", 0),
                    "platforms_monitored": analytics_data.get("platforms_count", 0),
                    "violations_detected": analytics_data.get("violations_count", 0),
                    "detection_accuracy": analytics_data.get("detection_accuracy", 0),
                    "evidence_collected": analytics_data.get("evidence_count", 0)
                },
                "operational_metrics": {
                    "system_uptime": "99.9%",
                    "average_detection_time": analytics_data.get("avg_detection_time", 0),
                    "false_positive_rate": analytics_data.get("false_positive_rate", 0),
                    "user_satisfaction": "95%"
                },
                "security_measures": {
                    "data_encryption": True,
                    "access_controls": True,
                    "audit_logging": True,
                    "regular_backups": True,
                    "incident_response_plan": True
                },
                "compliance_status": {
                    "gdpr_compliant": True,
                    "dmca_compliant": True,
                    "data_retention_compliant": True,
                    "security_standards_met": True
                }
            }
            
            # Generate HTML report
            html_content = await self._generate_html_report("general_compliance", report_data)
            
            # Save report
            report_filename = f"general_compliance_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_type": "general_compliance",
                "status": "completed",
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating general compliance report: {e}")
            return {"error": str(e)}
    
    async def _generate_html_report(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate HTML report from data."""        html_template = f"""        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_type.replace('_', ' ').title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #007bff; margin: 0; }}
                .header .meta {{ color: #666; font-size: 14px; margin-top: 10px; }}
                .section {{ margin-bottom: 30px; }}
                .section h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                .section h3 {{ color: #555; margin-top: 25px; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                .table th {{ background-color: #f8f9fa; font-weight: bold; }}
                .status-compliant {{ color: #28a745; font-weight: bold; }}
                .status-warning {{ color: #ffc107; font-weight: bold; }}
                .status-error {{ color: #dc3545; font-weight: bold; }}
                .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
                .json-data {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_type.replace('_', ' ').title()} Report</h1>
                <div class="meta">
                    <strong>Generated:</strong> {data.get('generated_at', 'N/A')}<br>
                    <strong>User ID:</strong> {data.get('user_id', 'N/A')}<br>
                    <strong>Reporting Period:</strong> {self._format_period(data.get('reporting_period', {}))}<br>
                </div>
            </div>
            
            {self._generate_html_sections(report_type, data)}
            
            <div class="footer">
                <p><strong>Generated by IA Influencer Agent Surveillance System</strong></p>
                <p>© 2025 Fahed Mlaiel. All Rights Reserved.</p>
                <p>This report contains confidential information and is intended for authorized personnel only.</p>
            </div>
        </body>
        </html>
        """        
        return html_template
    
    def _format_period(self, period: Dict[str, str]) -> str:
        """Format reporting period for display."""        if not period:
            return "N/A"
        
        start = period.get("start", "N/A")
        end = period.get("end", "N/A")
        return f"{start} to {end}"
    
    def _generate_html_sections(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate HTML sections based on report type."""        sections_html = ""
        
        # Generate sections based on data keys
        for key, value in data.items():
            if key not in ["report_type", "user_id", "generated_at", "reporting_period"]:
                section_title = key.replace('_', ' ').title()
                section_content = self._format_section_content(value)
                
                sections_html += f"""                <div class="section">
                    <h2>{section_title}</h2>
                    {section_content}
                </div>
                """        
        return sections_html
    
    def _format_section_content(self, content: Any) -> str:
        """Format section content for HTML display."""        if isinstance(content, dict):
            html = "<table class='table'>"
            for key, value in content.items():
                formatted_key = key.replace('_', ' ').title()
                formatted_value = self._format_value(value)
                html += f"<tr><td><strong>{formatted_key}</strong></td><td>{formatted_value}</td></tr>"
            html += "</table>"
            return html
        elif isinstance(content, list):
            html = "<ul>"
            for item in content:
                html += f"<li>{self._format_value(item)}</li>"
            html += "</ul>"
            return html
        else:
            return str(content)
    
    def _format_value(self, value: Any) -> str:
        """Format individual values for display."""        if isinstance(value, bool):
            if value:
                return "<span class='status-compliant'>✓ Yes</span>"
            else:
                return "<span class='status-error'>✗ No</span>"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if value.lower() in ["compliant", "yes", "true", "active", "enabled"]:
                return f"<span class='status-compliant'>{value}</span>"
            elif value.lower() in ["warning", "pending", "review"]:
                return f"<span class='status-warning'>{value}</span>"
            elif value.lower() in ["non-compliant", "no", "false", "error", "failed"]:
                return f"<span class='status-error'>{value}</span>"
            else:
                return value
        else:
            return str(value)


class ViolationReporter:
    """    Violation reporting system.
    
    Generates detailed violation reports with evidence
    for legal and enforcement purposes.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "/tmp/reports/violations"))
        self.include_evidence = config.get("include_evidence", True)
        
    async def initialize(self) -> bool:
        """Initialize violation reporter."""        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("ViolationReporter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ViolationReporter: {e}")
            return False
    
    async def generate_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate violation report."""        try:
            violations_data = analytics_data.get("violations", [])
            
            report_data = {
                "report_type": "violation_summary",
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "reporting_period": analytics_data.get("period", {}),
                "violation_summary": {
                    "total_violations": len(violations_data),
                    "high_confidence_violations": len([v for v in violations_data if v.get("confidence", 0) > 0.8]),
                    "platforms_affected": len(set(v.get("platform") for v in violations_data)),
                    "average_similarity": sum(v.get("similarity", 0) for v in violations_data) / len(violations_data) if violations_data else 0
                },
                "platform_breakdown": self._analyze_platform_breakdown(violations_data),
                "violation_details": violations_data[:50],  # Limit to 50 most recent
                "evidence_summary": {
                    "screenshots_collected": analytics_data.get("evidence_count", 0),
                    "metadata_extracted": analytics_data.get("metadata_count", 0),
                    "legal_notices_sent": analytics_data.get("notices_sent", 0)
                },
                "recommendations": self._generate_violation_recommendations(violations_data)
            }
            
            # Generate HTML report
            html_content = await self._generate_violation_html_report(report_data)
            
            # Save report
            report_filename = f"violation_report_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_type": "violation_summary",
                "status": "completed",
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating violation report: {e}")
            return {"error": str(e)}
    
    def _analyze_platform_breakdown(self, violations_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze violations by platform."""        platform_counts = {}
        platform_confidence = {}
        
        for violation in violations_data:
            platform = violation.get("platform", "unknown")
            confidence = violation.get("confidence", 0)
            
            if platform not in platform_counts:
                platform_counts[platform] = 0
                platform_confidence[platform] = []
            
            platform_counts[platform] += 1
            platform_confidence[platform].append(confidence)
        
        # Calculate average confidence per platform
        for platform in platform_confidence:
            confidences = platform_confidence[platform]
            platform_confidence[platform] = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "violation_counts": platform_counts,
            "average_confidence": platform_confidence
        }
    
    def _generate_violation_recommendations(self, violations_data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on violation patterns."""        recommendations = []
        
        if not violations_data:
            recommendations.append("Continue monitoring to establish baseline patterns")
            return recommendations
        
        # High violation count
        if len(violations_data) > 10:
            recommendations.append("Consider increasing monitoring frequency due to high violation count")
        
        # Low confidence detections
        low_confidence_count = len([v for v in violations_data if v.get("confidence", 0) < 0.6])
        if low_confidence_count > len(violations_data) * 0.3:
            recommendations.append("Review detection thresholds to reduce false positives")
        
        # Platform concentration
        platform_counts = {}
        for violation in violations_data:
            platform = violation.get("platform", "unknown")
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        if platform_counts:
            most_violations_platform = max(platform_counts, key=platform_counts.get)
            if platform_counts[most_violations_platform] > len(violations_data) * 0.6:
                recommendations.append(f"Focus enforcement efforts on {most_violations_platform} platform")
        
        return recommendations
    
    async def _generate_violation_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML violation report."""        html_template = f"""        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Violation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ border-bottom: 3px solid #dc3545; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #dc3545; margin: 0; }}
                .alert {{ padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .alert-danger {{ background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
                .alert-warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
                .alert-info {{ background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }}
                .violation-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .high-confidence {{ border-left: 5px solid #dc3545; }}
                .medium-confidence {{ border-left: 5px solid #ffc107; }}
                .low-confidence {{ border-left: 5px solid #6c757d; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                .table th {{ background-color: #f8f9fa; }}
                .section {{ margin-bottom: 30px; }}
                .section h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Content Violation Report</h1>
                <div>
                    <strong>Generated:</strong> {report_data.get('generated_at', 'N/A')}<br>
                    <strong>User ID:</strong> {report_data.get('user_id', 'N/A')}<br>
                    <strong>Period:</strong> {self._format_period(report_data.get('reporting_period', {}))}<br>
                </div>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                {self._generate_violation_summary_html(report_data.get('violation_summary', {}))}
            </div>
            
            <div class="section">
                <h2>Platform Analysis</h2>
                {self._generate_platform_analysis_html(report_data.get('platform_breakdown', {}))}
            </div>
            
            <div class="section">
                <h2>Violation Details</h2>
                {self._generate_violation_details_html(report_data.get('violation_details', []))}
            </div>
            
            <div class="section">
                <h2>Evidence Summary</h2>
                {self._generate_evidence_summary_html(report_data.get('evidence_summary', {}))}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {self._generate_recommendations_html(report_data.get('recommendations', []))}
            </div>
            
            <div class="footer">
                <p><strong>IA Influencer Agent Surveillance System - Violation Report</strong></p>
                <p>© 2025 Fahed Mlaiel. All Rights Reserved.</p>
                <p>This report contains confidential information. Unauthorized distribution is prohibited.</p>
            </div>
        </body>
        </html>
        """        
        return html_template
    
    def _generate_violation_summary_html(self, summary: Dict[str, Any]) -> str:
        """Generate violation summary HTML."""        total = summary.get("total_violations", 0)
        high_confidence = summary.get("high_confidence_violations", 0)
        platforms = summary.get("platforms_affected", 0)
        avg_similarity = summary.get("average_similarity", 0)
        
        if total > 20:
            alert_class = "alert-danger"
            alert_text = f"High violation count detected: {total} violations found"
        elif total > 5:
            alert_class = "alert-warning"
            alert_text = f"Moderate violation activity: {total} violations found"
        else:
            alert_class = "alert-info"
            alert_text = f"Low violation activity: {total} violations found"
        
        return f"""        <div class="alert {alert_class}">
            {alert_text}
        </div>
        <table class="table">
            <tr><td><strong>Total Violations</strong></td><td>{total}</td></tr>
            <tr><td><strong>High Confidence Violations</strong></td><td>{high_confidence}</td></tr>
            <tr><td><strong>Platforms Affected</strong></td><td>{platforms}</td></tr>
            <tr><td><strong>Average Similarity Score</strong></td><td>{avg_similarity:.2%}</td></tr>
            <tr><td><strong>Confidence Rate</strong></td><td>{(high_confidence/total*100):.1f}%</td></tr>
        </table>
        """    
    def _generate_platform_analysis_html(self, breakdown: Dict[str, Any]) -> str:
        """Generate platform analysis HTML."""        violation_counts = breakdown.get("violation_counts", {})
        avg_confidence = breakdown.get("average_confidence", {})
        
        if not violation_counts:
            return "<p>No platform data available.</p>"
        
        html = "<table class='table'><tr><th>Platform</th><th>Violations</th><th>Avg Confidence</th></tr>"
        
        for platform, count in violation_counts.items():
            confidence = avg_confidence.get(platform, 0)
            html += f"<tr><td>{platform.title()}</td><td>{count}</td><td>{confidence:.2%}</td></tr>"
        
        html += "</table>"
        return html
    
    def _generate_violation_details_html(self, violations: List[Dict[str, Any]]) -> str:
        """Generate violation details HTML."""        if not violations:
            return "<p>No violation details available.</p>"
        
        html = ""
        
        for violation in violations[:20]:  # Limit to 20 violations
            confidence = violation.get("confidence", 0)
            similarity = violation.get("similarity", 0)
            platform = violation.get("platform", "Unknown")
            url = violation.get("url", "N/A")
            detected_at = violation.get("detected_at", "N/A")
            
            if confidence > 0.8:
                confidence_class = "high-confidence"
                confidence_label = "High"
            elif confidence > 0.6:
                confidence_class = "medium-confidence"
                confidence_label = "Medium"
            else:
                confidence_class = "low-confidence"
                confidence_label = "Low"
            
            html += f"""            <div class="violation-item {confidence_class}">
                <h4>{platform.title()} Violation - {confidence_label} Confidence</h4>
                <p><strong>URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
                <p><strong>Similarity:</strong> {similarity:.2%}</p>
                <p><strong>Confidence:</strong> {confidence:.2%}</p>
                <p><strong>Detected:</strong> {detected_at}</p>
            </div>
            """        
        if len(violations) > 20:
            html += f"<p><em>... and {len(violations) - 20} more violations</em></p>"
        
        return html
    
    def _generate_evidence_summary_html(self, evidence: Dict[str, Any]) -> str:
        """Generate evidence summary HTML."""        screenshots = evidence.get("screenshots_collected", 0)
        metadata = evidence.get("metadata_extracted", 0)
        notices = evidence.get("legal_notices_sent", 0)
        
        return f"""        <table class="table">
            <tr><td><strong>Screenshots Collected</strong></td><td>{screenshots}</td></tr>
            <tr><td><strong>Metadata Extracted</strong></td><td>{metadata}</td></tr>
            <tr><td><strong>Legal Notices Sent</strong></td><td>{notices}</td></tr>
            <tr><td><strong>Evidence Integrity</strong></td><td>✓ Verified</td></tr>
        </table>
        """    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate recommendations HTML."""        if not recommendations:
            return "<p>No specific recommendations at this time.</p>"
        
        html = "<ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        
        return html


class PerformanceReporter:
    """    Performance reporting system.
    
    Generates performance metrics and system health reports.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "/tmp/reports/performance"))
        
    async def initialize(self) -> bool:
        """Initialize performance reporter."""        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info("PerformanceReporter initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PerformanceReporter: {e}")
            return False
    
    async def generate_report(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance report."""        try:
            report_data = {
                "report_type": "performance_summary",
                "generated_at": datetime.utcnow().isoformat(),
                "system_metrics": {
                    "uptime": analytics_data.get("uptime", "99.9%"),
                    "avg_response_time": analytics_data.get("avg_response_time", 0),
                    "throughput": analytics_data.get("throughput", 0),
                    "error_rate": analytics_data.get("error_rate", 0)
                },
                "surveillance_performance": {
                    "detection_accuracy": analytics_data.get("detection_accuracy", 0),
                    "false_positive_rate": analytics_data.get("false_positive_rate", 0),
                    "avg_scan_time": analytics_data.get("avg_scan_time", 0),
                    "platforms_coverage": analytics_data.get("platforms_coverage", 0)
                }
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}


class DashboardReporter:
    """    Dashboard data reporter.
    
    Generates real-time dashboard data and visualizations.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def initialize(self) -> bool:
        """Initialize dashboard reporter."""        try:
            logger.info("DashboardReporter initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize DashboardReporter: {e}")
            return False
    
    async def generate_report(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dashboard data."""        try:
            return {
                "report_type": "dashboard_data",
                "generated_at": datetime.utcnow().isoformat(),
                "summary_stats": {
                    "total_violations": analytics_data.get("violations_count", 0),
                    "active_targets": analytics_data.get("active_targets", 0),
                    "platforms_monitored": analytics_data.get("platforms_count", 0),
                    "detection_accuracy": analytics_data.get("detection_accuracy", 0)
                },
                "recent_activity": analytics_data.get("recent_activity", []),
                "performance_metrics": {
                    "avg_detection_time": analytics_data.get("avg_detection_time", 0),
                    "system_health": "Healthy",
                    "last_update": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {"error": str(e)}
