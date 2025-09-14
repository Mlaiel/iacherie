"""
Security Compliance Reporter
Enterprise security compliance reporting and documentation

Features:
- Automated compliance reports
- Regulatory compliance tracking
- Security metrics dashboards
- Audit documentation generation
- Risk assessment reports
- Compliance gap analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import uuid


class ReportType(Enum):
    """Types of compliance reports"""
    SECURITY_OVERVIEW = "security_overview"
    AUDIT_TRAIL = "audit_trail"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_STATUS = "compliance_status"
    VULNERABILITY_REPORT = "vulnerability_report"
    INCIDENT_REPORT = "incident_report"
    METRICS_DASHBOARD = "metrics_dashboard"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO_27001 = "iso_27001"
    NIST = "nist"


@dataclass
class ComplianceReport:
    """Compliance report structure"""
    report_id: str
    report_type: ReportType
    title: str
    generated_at: datetime
    time_period: Dict[str, str]
    scope: List[str]
    executive_summary: str
    findings: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    recommendations: List[str]
    compliance_score: float
    metadata: Dict[str, Any]


class SecurityComplianceReporter:
    """
    Enterprise Security Compliance Reporter
    Comprehensive compliance reporting and documentation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reports: Dict[str, ComplianceReport] = {}
        self.report_templates: Dict[ReportType, Dict[str, Any]] = {}
        self.compliance_frameworks: Dict[str, Dict[str, Any]] = {}
        
        # Initialize report templates and framework mappings
        self._initialize_report_templates()
        self._initialize_compliance_frameworks()
    
    def _initialize_report_templates(self):
        """Initialize standard report templates"""
        self.report_templates = {
            ReportType.SECURITY_OVERVIEW: {
                "sections": [
                    "Executive Summary",
                    "Security Posture Overview", 
                    "Key Security Metrics",
                    "Recent Security Events",
                    "Risk Assessment Summary",
                    "Recommendations"
                ],
                "metrics_required": [
                    "total_security_events",
                    "high_risk_events",
                    "compliance_score",
                    "vulnerability_count"
                ]
            },
            ReportType.AUDIT_TRAIL: {
                "sections": [
                    "Audit Overview",
                    "Access Logs Summary",
                    "Security Events",
                    "User Activity Analysis",
                    "System Changes",
                    "Compliance Notes"
                ],
                "metrics_required": [
                    "total_access_requests",
                    "denied_access_count",
                    "unique_users",
                    "failed_authentications"
                ]
            },
            ReportType.RISK_ASSESSMENT: {
                "sections": [
                    "Risk Overview",
                    "Threat Analysis",
                    "Vulnerability Assessment",
                    "Risk Matrix",
                    "Mitigation Status",
                    "Action Plan"
                ],
                "metrics_required": [
                    "total_risks",
                    "high_risk_count",
                    "mitigated_risks",
                    "residual_risk_score"
                ]
            }
        }
    
    def _initialize_compliance_frameworks(self):
        """Initialize compliance framework requirements"""
        self.compliance_frameworks = {
            ComplianceFramework.GDPR.value: {
                "name": "General Data Protection Regulation",
                "key_requirements": [
                    "Data Protection by Design",
                    "Consent Management",
                    "Data Subject Rights",
                    "Data Breach Notification",
                    "Privacy Impact Assessments"
                ],
                "required_controls": [
                    "encryption_at_rest",
                    "encryption_in_transit",
                    "access_controls",
                    "audit_logging",
                    "data_minimization"
                ]
            },
            ComplianceFramework.HIPAA.value: {
                "name": "Health Insurance Portability and Accountability Act",
                "key_requirements": [
                    "Administrative Safeguards",
                    "Physical Safeguards", 
                    "Technical Safeguards",
                    "Business Associate Agreements",
                    "Breach Notification"
                ],
                "required_controls": [
                    "phi_encryption",
                    "access_controls",
                    "audit_trails",
                    "employee_training",
                    "incident_response"
                ]
            },
            ComplianceFramework.SOX.value: {
                "name": "Sarbanes-Oxley Act",
                "key_requirements": [
                    "Internal Controls",
                    "Financial Reporting",
                    "Audit Trail",
                    "Change Management",
                    "Risk Assessment"
                ],
                "required_controls": [
                    "change_management",
                    "segregation_of_duties",
                    "audit_logging",
                    "data_integrity",
                    "backup_recovery"
                ]
            }
        }
    
    async def generate_security_overview_report(
        self,
        time_period: timedelta = timedelta(days=30),
        scope: Optional[List[str]] = None
    ) -> str:
        """Generate comprehensive security overview report"""
        try:
            report_id = str(uuid.uuid4())
            end_time = datetime.now()
            start_time = end_time - time_period
            
            # Gather security metrics from various sources
            # (In a real implementation, these would come from actual security components)
            security_metrics = await self._gather_security_metrics(start_time, end_time)
            
            # Generate findings
            findings = await self._analyze_security_findings(security_metrics)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(security_metrics)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                security_metrics, findings, compliance_score
            )
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(findings)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=ReportType.SECURITY_OVERVIEW,
                title="Security Overview Report",
                generated_at=datetime.now(),
                time_period={
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                scope=scope or ["all_systems"],
                executive_summary=executive_summary,
                findings=findings,
                metrics=security_metrics,
                recommendations=recommendations,
                compliance_score=compliance_score,
                metadata={"template_version": "1.0"}
            )
            
            self.reports[report_id] = report
            
            self.logger.info(f"Security overview report generated: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate security overview report: {str(e)}")
            raise
    
    async def generate_compliance_assessment(
        self,
        framework: ComplianceFramework,
        time_period: timedelta = timedelta(days=90)
    ) -> str:
        """Generate compliance assessment report for specific framework"""
        try:
            report_id = str(uuid.uuid4())
            end_time = datetime.now()
            start_time = end_time - time_period
            
            framework_info = self.compliance_frameworks.get(framework.value)
            if not framework_info:
                raise ValueError(f"Unsupported compliance framework: {framework.value}")
            
            # Assess compliance for each requirement
            compliance_assessment = await self._assess_framework_compliance(
                framework, start_time, end_time
            )
            
            # Generate gap analysis
            gap_analysis = self._perform_gap_analysis(framework, compliance_assessment)
            
            # Calculate overall compliance score
            compliance_score = self._calculate_framework_compliance_score(compliance_assessment)
            
            findings = [
                {
                    "type": "compliance_assessment",
                    "framework": framework.value,
                    "overall_score": compliance_score,
                    "requirements_assessed": len(compliance_assessment),
                    "gaps_identified": len(gap_analysis)
                }
            ]
            
            executive_summary = f"""
            Compliance assessment for {framework_info['name']} completed.
            Overall compliance score: {compliance_score:.1f}%
            {len(gap_analysis)} gaps identified requiring attention.
            """
            
            recommendations = self._generate_compliance_recommendations(gap_analysis)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=ReportType.COMPLIANCE_STATUS,
                title=f"{framework_info['name']} Compliance Assessment",
                generated_at=datetime.now(),
                time_period={
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                scope=[framework.value],
                executive_summary=executive_summary,
                findings=findings,
                metrics={
                    "compliance_assessment": compliance_assessment,
                    "gap_analysis": gap_analysis
                },
                recommendations=recommendations,
                compliance_score=compliance_score,
                metadata={
                    "framework": framework.value,
                    "framework_name": framework_info['name']
                }
            )
            
            self.reports[report_id] = report
            
            self.logger.info(f"Compliance assessment report generated: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance assessment: {str(e)}")
            raise
    
    async def generate_risk_assessment_report(
        self,
        risk_categories: Optional[List[str]] = None
    ) -> str:
        """Generate comprehensive risk assessment report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Gather risk data from threat modeling and security systems
            risk_data = await self._gather_risk_data(risk_categories)
            
            # Perform risk analysis
            risk_analysis = self._analyze_risks(risk_data)
            
            # Generate risk matrix
            risk_matrix = self._generate_risk_matrix(risk_data)
            
            # Calculate overall risk score
            overall_risk = self._calculate_overall_risk_score(risk_data)
            
            findings = [
                {
                    "type": "risk_assessment",
                    "total_risks": len(risk_data),
                    "high_risks": len([r for r in risk_data if r.get("risk_level") == "high"]),
                    "critical_risks": len([r for r in risk_data if r.get("risk_level") == "critical"]),
                    "overall_risk_score": overall_risk
                }
            ]
            
            executive_summary = f"""
            Risk assessment identified {len(risk_data)} risks across the ML systems.
            Overall risk score: {overall_risk:.2f}
            Immediate attention required for {findings[0]['critical_risks']} critical risks.
            """
            
            recommendations = self._generate_risk_recommendations(risk_analysis)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=ReportType.RISK_ASSESSMENT,
                title="ML Systems Risk Assessment",
                generated_at=datetime.now(),
                time_period={
                    "start": (datetime.now() - timedelta(days=1)).isoformat(),
                    "end": datetime.now().isoformat()
                },
                scope=risk_categories or ["all_systems"],
                executive_summary=executive_summary,
                findings=findings,
                metrics={
                    "risk_data": risk_data,
                    "risk_analysis": risk_analysis,
                    "risk_matrix": risk_matrix
                },
                recommendations=recommendations,
                compliance_score=100 - overall_risk * 10,  # Inverse relationship
                metadata={"assessment_type": "comprehensive"}
            )
            
            self.reports[report_id] = report
            
            self.logger.info(f"Risk assessment report generated: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate risk assessment report: {str(e)}")
            raise
    
    async def generate_vulnerability_report(
        self,
        severity_threshold: str = "medium"
    ) -> str:
        """Generate vulnerability assessment report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Gather vulnerability data from security scanning
            vulnerability_data = await self._gather_vulnerability_data(severity_threshold)
            
            # Analyze vulnerabilities
            vuln_analysis = self._analyze_vulnerabilities(vulnerability_data)
            
            # Calculate vulnerability metrics
            vuln_metrics = self._calculate_vulnerability_metrics(vulnerability_data)
            
            findings = [
                {
                    "type": "vulnerability_assessment",
                    "total_vulnerabilities": len(vulnerability_data),
                    "critical_vulns": vuln_metrics.get("critical", 0),
                    "high_vulns": vuln_metrics.get("high", 0),
                    "medium_vulns": vuln_metrics.get("medium", 0),
                    "remediation_rate": vuln_metrics.get("remediation_rate", 0)
                }
            ]
            
            executive_summary = f"""
            Vulnerability assessment identified {len(vulnerability_data)} vulnerabilities.
            Critical: {vuln_metrics.get('critical', 0)}, High: {vuln_metrics.get('high', 0)}
            Remediation rate: {vuln_metrics.get('remediation_rate', 0):.1f}%
            """
            
            recommendations = self._generate_vulnerability_recommendations(vuln_analysis)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=ReportType.VULNERABILITY_REPORT,
                title="Security Vulnerability Assessment",
                generated_at=datetime.now(),
                time_period={
                    "start": (datetime.now() - timedelta(days=7)).isoformat(),
                    "end": datetime.now().isoformat()
                },
                scope=["all_systems"],
                executive_summary=executive_summary,
                findings=findings,
                metrics=vuln_metrics,
                recommendations=recommendations,
                compliance_score=max(0, 100 - len(vulnerability_data) * 2),
                metadata={"severity_threshold": severity_threshold}
            )
            
            self.reports[report_id] = report
            
            self.logger.info(f"Vulnerability report generated: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate vulnerability report: {str(e)}")
            raise
    
    async def generate_metrics_dashboard(self) -> Dict[str, Any]:
        """Generate real-time security metrics dashboard"""
        try:
            dashboard_data = {
                "dashboard_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "metrics": {},
                "alerts": [],
                "trends": {},
                "health_status": {}
            }
            
            # Gather real-time metrics
            security_metrics = await self._gather_real_time_metrics()
            dashboard_data["metrics"] = security_metrics
            
            # Get active alerts
            alerts = await self._get_active_security_alerts()
            dashboard_data["alerts"] = alerts
            
            # Calculate trends
            trends = await self._calculate_security_trends()
            dashboard_data["trends"] = trends
            
            # Assess overall health
            health_status = self._assess_security_health(security_metrics, alerts)
            dashboard_data["health_status"] = health_status
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics dashboard: {str(e)}")
            return {}
    
    async def export_report(
        self,
        report_id: str,
        format: str = "json"
    ) -> str:
        """Export report in specified format"""
        try:
            report = self.reports.get(report_id)
            if not report:
                raise ValueError(f"Report {report_id} not found")
            
            if format.lower() == "json":
                return json.dumps(asdict(report), default=str, indent=2)
            elif format.lower() == "html":
                return self._generate_html_report(report)
            elif format.lower() == "pdf":
                return self._generate_pdf_report(report)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Failed to export report: {str(e)}")
            raise
    
    async def get_compliance_summary(
        self,
        frameworks: Optional[List[ComplianceFramework]] = None
    ) -> Dict[str, Any]:
        """Get summary of compliance status across frameworks"""
        try:
            if frameworks is None:
                frameworks = list(ComplianceFramework)
            
            summary = {
                "summary_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "frameworks": {},
                "overall_score": 0.0,
                "critical_gaps": 0,
                "recommendations": []
            }
            
            total_score = 0.0
            for framework in frameworks:
                framework_assessment = await self._quick_compliance_check(framework)
                summary["frameworks"][framework.value] = framework_assessment
                total_score += framework_assessment.get("score", 0)
                
                # Count critical gaps
                gaps = framework_assessment.get("gaps", [])
                critical_gaps = [g for g in gaps if g.get("severity") == "critical"]
                summary["critical_gaps"] += len(critical_gaps)
            
            summary["overall_score"] = total_score / len(frameworks) if frameworks else 0
            
            # Generate high-level recommendations
            if summary["overall_score"] < 70:
                summary["recommendations"].append("Overall compliance below threshold - immediate action required")
            if summary["critical_gaps"] > 0:
                summary["recommendations"].append(f"Address {summary['critical_gaps']} critical compliance gaps")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance summary: {str(e)}")
            return {}
    
    # Private methods for data gathering and analysis
    
    async def _gather_security_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Gather security metrics from various sources"""
        # Simulated metrics - in production would gather from actual security systems
        return {
            "total_security_events": 1250,
            "high_risk_events": 45,
            "failed_authentications": 23,
            "successful_authentications": 8932,
            "unique_users": 156,
            "vulnerability_count": 12,
            "compliance_violations": 3,
            "model_access_requests": 45620,
            "denied_access_requests": 234,
            "encryption_coverage": 95.5,
            "backup_success_rate": 99.2
        }
    
    async def _analyze_security_findings(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze security metrics to generate findings"""
        findings = []
        
        # Analyze authentication failures
        failed_auth = metrics.get("failed_authentications", 0)
        total_auth = metrics.get("successful_authentications", 0) + failed_auth
        failure_rate = (failed_auth / total_auth * 100) if total_auth > 0 else 0
        
        if failure_rate > 5:
            findings.append({
                "type": "authentication",
                "severity": "medium",
                "description": f"High authentication failure rate: {failure_rate:.1f}%",
                "impact": "Potential brute force attacks or account issues",
                "recommendation": "Review authentication logs and implement additional controls"
            })
        
        # Analyze access denials
        denied_requests = metrics.get("denied_access_requests", 0)
        total_requests = metrics.get("model_access_requests", 0)
        denial_rate = (denied_requests / total_requests * 100) if total_requests > 0 else 0
        
        if denial_rate > 2:
            findings.append({
                "type": "access_control", 
                "severity": "low",
                "description": f"Elevated access denial rate: {denial_rate:.1f}%",
                "impact": "Potential misconfigurations or policy issues",
                "recommendation": "Review access control policies and user permissions"
            })
        
        # Analyze vulnerabilities
        vuln_count = metrics.get("vulnerability_count", 0)
        if vuln_count > 10:
            findings.append({
                "type": "vulnerabilities",
                "severity": "high",
                "description": f"{vuln_count} vulnerabilities identified",
                "impact": "Potential security breaches and system compromise",
                "recommendation": "Prioritize vulnerability remediation efforts"
            })
        
        return findings
    
    def _calculate_compliance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall compliance score from metrics"""
        # Simplified scoring algorithm
        base_score = 100.0
        
        # Deduct for high-risk events
        high_risk_events = metrics.get("high_risk_events", 0)
        base_score -= min(high_risk_events * 2, 20)
        
        # Deduct for vulnerabilities
        vulnerabilities = metrics.get("vulnerability_count", 0)
        base_score -= min(vulnerabilities * 3, 30)
        
        # Deduct for compliance violations
        violations = metrics.get("compliance_violations", 0)
        base_score -= violations * 10
        
        # Adjust for encryption coverage
        encryption_coverage = metrics.get("encryption_coverage", 100)
        if encryption_coverage < 95:
            base_score -= (95 - encryption_coverage) * 2
        
        return max(0, base_score)
    
    def _generate_executive_summary(
        self,
        metrics: Dict[str, Any],
        findings: List[Dict[str, Any]],
        compliance_score: float
    ) -> str:
        """Generate executive summary for security report"""
        high_severity_findings = [f for f in findings if f.get("severity") == "high"]
        
        summary = f"""
        EXECUTIVE SUMMARY
        
        Overall Security Posture: {'Strong' if compliance_score >= 85 else 'Moderate' if compliance_score >= 70 else 'Needs Improvement'}
        Compliance Score: {compliance_score:.1f}%
        
        Key Metrics:
        - Total Security Events: {metrics.get('total_security_events', 0):,}
        - High-Risk Events: {metrics.get('high_risk_events', 0)}
        - Vulnerabilities: {metrics.get('vulnerability_count', 0)}
        - Authentication Success Rate: {((metrics.get('successful_authentications', 0) / (metrics.get('successful_authentications', 0) + metrics.get('failed_authentications', 1))) * 100):.1f}%
        
        Critical Findings: {len(high_severity_findings)} items require immediate attention.
        
        {"Overall security posture is strong with minor areas for improvement." if compliance_score >= 85 else "Security improvements needed to meet compliance standards." if compliance_score >= 70 else "Significant security enhancements required immediately."}
        """
        
        return summary.strip()
    
    def _generate_security_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Group findings by type
        finding_types = {}
        for finding in findings:
            finding_type = finding.get("type", "general")
            if finding_type not in finding_types:
                finding_types[finding_type] = []
            finding_types[finding_type].append(finding)
        
        # Generate type-specific recommendations
        if "authentication" in finding_types:
            recommendations.append("Implement stronger authentication controls and monitor for brute force attacks")
        
        if "vulnerabilities" in finding_types:
            recommendations.append("Establish regular vulnerability scanning and remediation processes")
        
        if "access_control" in finding_types:
            recommendations.append("Review and optimize access control policies and procedures")
        
        # General recommendations
        recommendations.extend([
            "Maintain regular security assessments and compliance reviews",
            "Ensure incident response procedures are tested and up-to-date",
            "Provide ongoing security awareness training for all personnel"
        ])
        
        return recommendations
    
    async def _assess_framework_compliance(
        self,
        framework: ComplianceFramework,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Assess compliance for specific framework requirements"""
        framework_info = self.compliance_frameworks.get(framework.value, {})
        requirements = framework_info.get("key_requirements", [])
        
        assessment = []
        for requirement in requirements:
            # Simulate compliance assessment for each requirement
            compliance_status = self._assess_requirement_compliance(requirement, framework)
            assessment.append({
                "requirement": requirement,
                "status": compliance_status["status"],
                "score": compliance_status["score"], 
                "gaps": compliance_status["gaps"],
                "evidence": compliance_status["evidence"]
            })
        
        return assessment
    
    def _assess_requirement_compliance(self, requirement: str, framework: ComplianceFramework) -> Dict[str, Any]:
        """Assess compliance for individual requirement"""
        # Simplified assessment - in production would check actual controls
        compliance_levels = {
            "Data Protection by Design": {"status": "compliant", "score": 85},
            "Consent Management": {"status": "partially_compliant", "score": 70},
            "Administrative Safeguards": {"status": "compliant", "score": 90},
            "Technical Safeguards": {"status": "compliant", "score": 88},
            "Internal Controls": {"status": "partially_compliant", "score": 75}
        }
        
        default_compliance = {"status": "compliant", "score": 80}
        compliance = compliance_levels.get(requirement, default_compliance)
        
        return {
            "status": compliance["status"],
            "score": compliance["score"],
            "gaps": [] if compliance["status"] == "compliant" else ["Implementation incomplete"],
            "evidence": ["Policy documentation", "Technical controls", "Training records"]
        }
    
    def _perform_gap_analysis(
        self,
        framework: ComplianceFramework,
        assessment: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform gap analysis for compliance framework"""
        gaps = []
        
        for item in assessment:
            if item["status"] != "compliant":
                gaps.append({
                    "requirement": item["requirement"],
                    "current_status": item["status"],
                    "score": item["score"],
                    "severity": "high" if item["score"] < 60 else "medium" if item["score"] < 80 else "low",
                    "remediation_effort": "high" if item["score"] < 60 else "medium",
                    "gaps": item["gaps"]
                })
        
        return gaps
    
    def _calculate_framework_compliance_score(self, assessment: List[Dict[str, Any]]) -> float:
        """Calculate overall compliance score for framework"""
        if not assessment:
            return 0.0
        
        total_score = sum(item["score"] for item in assessment)
        return total_score / len(assessment)
    
    def _generate_compliance_recommendations(self, gap_analysis: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on compliance gaps"""
        recommendations = []
        
        high_priority_gaps = [g for g in gap_analysis if g["severity"] == "high"]
        medium_priority_gaps = [g for g in gap_analysis if g["severity"] == "medium"]
        
        if high_priority_gaps:
            recommendations.append(f"Address {len(high_priority_gaps)} high-priority compliance gaps immediately")
        
        if medium_priority_gaps:
            recommendations.append(f"Plan remediation for {len(medium_priority_gaps)} medium-priority gaps")
        
        # Specific recommendations based on common gaps
        recommendations.extend([
            "Implement comprehensive compliance monitoring system",
            "Establish regular compliance assessment schedule",
            "Provide compliance training for relevant personnel",
            "Document all compliance-related processes and procedures"
        ])
        
        return recommendations
    
    async def _gather_risk_data(self, risk_categories: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Gather risk data from threat modeling systems"""
        # Simulated risk data
        return [
            {
                "risk_id": "RISK-001",
                "category": "data_poisoning",
                "risk_level": "high",
                "probability": 0.7,
                "impact": 0.8,
                "risk_score": 0.56,
                "description": "Training data manipulation risk",
                "mitigation_status": "in_progress"
            },
            {
                "risk_id": "RISK-002", 
                "category": "model_theft",
                "risk_level": "medium",
                "probability": 0.5,
                "impact": 0.6,
                "risk_score": 0.30,
                "description": "Model extraction attack risk",
                "mitigation_status": "planned"
            }
        ]
    
    def _analyze_risks(self, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risk data and generate insights"""
        total_risks = len(risk_data)
        high_risks = len([r for r in risk_data if r.get("risk_level") == "high"])
        avg_risk_score = sum(r.get("risk_score", 0) for r in risk_data) / max(total_risks, 1)
        
        return {
            "total_risks": total_risks,
            "high_risks": high_risks,
            "average_risk_score": avg_risk_score,
            "risk_categories": list(set(r.get("category") for r in risk_data)),
            "mitigation_coverage": len([r for r in risk_data if r.get("mitigation_status") != "none"]) / max(total_risks, 1)
        }
    
    def _generate_risk_matrix(self, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk matrix visualization data"""
        matrix = {"high_prob_high_impact": [], "high_prob_low_impact": [], "low_prob_high_impact": [], "low_prob_low_impact": []}
        
        for risk in risk_data:
            prob = risk.get("probability", 0)
            impact = risk.get("impact", 0)
            
            if prob >= 0.5 and impact >= 0.5:
                matrix["high_prob_high_impact"].append(risk["risk_id"])
            elif prob >= 0.5 and impact < 0.5:
                matrix["high_prob_low_impact"].append(risk["risk_id"])
            elif prob < 0.5 and impact >= 0.5:
                matrix["low_prob_high_impact"].append(risk["risk_id"])
            else:
                matrix["low_prob_low_impact"].append(risk["risk_id"])
        
        return matrix
    
    def _calculate_overall_risk_score(self, risk_data: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score"""
        if not risk_data:
            return 0.0
        
        total_risk = sum(r.get("risk_score", 0) for r in risk_data)
        return total_risk / len(risk_data)
    
    def _generate_risk_recommendations(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_analysis.get("high_risks", 0) > 0:
            recommendations.append(f"Prioritize mitigation of {risk_analysis['high_risks']} high-risk items")
        
        if risk_analysis.get("mitigation_coverage", 0) < 0.8:
            recommendations.append("Increase mitigation coverage - many risks lack proper controls")
        
        recommendations.extend([
            "Implement continuous risk monitoring and assessment",
            "Establish risk review board for high-impact decisions",
            "Regular risk assessment training for team members"
        ])
        
        return recommendations
    
    async def _gather_vulnerability_data(self, severity_threshold: str) -> List[Dict[str, Any]]:
        """Gather vulnerability data from security scanning systems"""
        # Simulated vulnerability data
        return [
            {
                "vuln_id": "CVE-2024-0001",
                "severity": "high",
                "component": "tensorflow",
                "description": "Security vulnerability in ML framework",
                "cvss_score": 8.2,
                "remediation_available": True
            },
            {
                "vuln_id": "CVE-2024-0002",
                "severity": "medium", 
                "component": "docker_image",
                "description": "Container vulnerability",
                "cvss_score": 6.5,
                "remediation_available": True
            }
        ]
    
    def _analyze_vulnerabilities(self, vulnerability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze vulnerability data"""
        return {
            "total_vulnerabilities": len(vulnerability_data),
            "by_severity": {
                "critical": len([v for v in vulnerability_data if v.get("severity") == "critical"]),
                "high": len([v for v in vulnerability_data if v.get("severity") == "high"]),
                "medium": len([v for v in vulnerability_data if v.get("severity") == "medium"]),
                "low": len([v for v in vulnerability_data if v.get("severity") == "low"])
            },
            "remediation_available": len([v for v in vulnerability_data if v.get("remediation_available")])
        }
    
    def _calculate_vulnerability_metrics(self, vulnerability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate vulnerability metrics"""
        total_vulns = len(vulnerability_data)
        remediation_available = len([v for v in vulnerability_data if v.get("remediation_available")])
        
        return {
            "total": total_vulns,
            "critical": len([v for v in vulnerability_data if v.get("severity") == "critical"]),
            "high": len([v for v in vulnerability_data if v.get("severity") == "high"]),
            "medium": len([v for v in vulnerability_data if v.get("severity") == "medium"]),
            "low": len([v for v in vulnerability_data if v.get("severity") == "low"]),
            "remediation_rate": (remediation_available / max(total_vulns, 1)) * 100
        }
    
    def _generate_vulnerability_recommendations(self, vuln_analysis: Dict[str, Any]) -> List[str]:
        """Generate vulnerability-based recommendations"""
        recommendations = []
        
        if vuln_analysis.get("by_severity", {}).get("critical", 0) > 0:
            recommendations.append("Immediate patching required for critical vulnerabilities")
        
        if vuln_analysis.get("remediation_available", 0) > 0:
            recommendations.append("Apply available security patches and updates")
        
        recommendations.extend([
            "Implement automated vulnerability scanning",
            "Establish vulnerability management process",
            "Regular security updates and patch management"
        ])
        
        return recommendations
    
    async def _gather_real_time_metrics(self) -> Dict[str, Any]:
        """Gather real-time security metrics"""
        return {
            "active_users": 45,
            "active_sessions": 23,
            "recent_alerts": 3,
            "system_health": 98.5,
            "compliance_score": 87.2
        }
    
    async def _get_active_security_alerts(self) -> List[Dict[str, Any]]:
        """Get active security alerts"""
        return [
            {
                "alert_id": "ALERT-001",
                "severity": "medium",
                "type": "unusual_access_pattern",
                "description": "Unusual access pattern detected",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _calculate_security_trends(self) -> Dict[str, Any]:
        """Calculate security trends"""
        return {
            "security_events_trend": "decreasing",
            "compliance_score_trend": "improving",
            "vulnerability_trend": "stable"
        }
    
    def _assess_security_health(self, metrics: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall security health"""
        health_score = 85.0  # Base score
        
        # Adjust based on alerts
        critical_alerts = len([a for a in alerts if a.get("severity") == "critical"])
        health_score -= critical_alerts * 10
        
        # Determine health status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 80:
            status = "good"
        elif health_score >= 70:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "overall_score": health_score,
            "status": status,
            "critical_issues": critical_alerts
        }
    
    async def _quick_compliance_check(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Perform quick compliance check for framework"""
        # Simplified quick check
        return {
            "framework": framework.value,
            "score": 82.5,
            "status": "compliant",
            "gaps": [
                {"requirement": "data_encryption", "severity": "medium"}
            ],
            "last_assessed": datetime.now().isoformat()
        }
    
    def _generate_html_report(self, report: ComplianceReport) -> str:
        """Generate HTML version of report"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>Generated: {report.generated_at.isoformat()}</p>
                <p>Compliance Score: {report.compliance_score:.1f}%</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <pre>{report.executive_summary}</pre>
            </div>
            
            <div class="section">
                <h2>Key Metrics</h2>
                {self._format_metrics_html(report.metrics)}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                </ul>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def _format_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for HTML display"""
        html_parts = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                html_parts.append(f'<div class="metric"><strong>{key}:</strong> {value}</div>')
        return ''.join(html_parts)
    
    def _generate_pdf_report(self, report: ComplianceReport) -> str:
        """Generate PDF version of report (placeholder)"""
        # In production, would use a PDF library like ReportLab
        return f"PDF report generation not implemented. Report ID: {report.report_id}"


# Global instance
security_compliance_reporter = SecurityComplianceReporter()