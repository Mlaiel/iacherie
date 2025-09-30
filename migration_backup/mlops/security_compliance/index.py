"""
Security & Compliance Module - Index
Enterprise security and compliance orchestration for MLOps

This module provides comprehensive security and compliance management for ML systems
including threat detection, vulnerability management, privacy protection, and
regulatory compliance across multiple frameworks (GDPR, HIPAA, SOX, etc.).

Components:
- Model Security Management
- Adversarial Defense Systems  
- Data Encryption & Privacy Protection
- Compliance Framework Management
- Audit Trail & Logging
- Security Scanning & Vulnerability Assessment
- Privacy-Preserving ML Techniques
- Secure Communication
- Security Analytics & Threat Intelligence
- Threat Modeling & Risk Assessment
- Identity & Access Management
- Compliance Reporting & Documentation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import all security and compliance components
from .model_security_manager import ModelSecurityManager, SecurityLevel, SecurityPolicy
from .adversarial_defense import AdversarialDefenseEngine, AttackType, DefenseStrategy
from .data_encryption_manager import DataEncryptionManager, EncryptionType, KeyType
from .compliance_framework import ComplianceFramework, ComplianceStandard, ComplianceStatus
from .audit_trail_manager import AuditTrailManager, AuditEventType, AuditSeverity
from .security_scanning_suite import SecurityScanningSuite, ScanType, VulnerabilitySeverity
from .privacy_preserving_ml import PrivacyPreservingML, PrivacyTechnique, PrivacyLevel
from .secure_communication import SecureCommunication, SecurityProtocol, AuthenticationMethod
from .security_analytics import SecurityAnalytics, ThreatLevel, SecurityEventType
from .threat_modeling_engine import ThreatModelingEngine, ThreatCategory, RiskLevel
from .identity_access_manager import IdentityAccessManager, AccessLevel, User, Role
from .security_compliance_reporter import SecurityComplianceReporter, ReportType, ComplianceFramework as ReportFramework


@dataclass
class SecurityComplianceConfig:
    """Configuration for security and compliance module"""
    enable_model_security: bool = True
    enable_adversarial_defense: bool = True
    enable_data_encryption: bool = True
    enable_compliance_tracking: bool = True
    enable_audit_logging: bool = True
    enable_security_scanning: bool = True
    enable_privacy_preservation: bool = True
    enable_secure_communication: bool = True
    enable_security_analytics: bool = True
    enable_threat_modeling: bool = True
    enable_identity_management: bool = True
    enable_compliance_reporting: bool = True
    
    # Default security levels
    default_security_level: SecurityLevel = SecurityLevel.MEDIUM
    default_privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM
    default_encryption_type: EncryptionType = EncryptionType.HYBRID
    
    # Compliance frameworks to monitor
    compliance_frameworks: List[ComplianceStandard] = None
    
    # Audit and monitoring settings
    audit_retention_days: int = 365
    security_scan_frequency: str = "weekly"
    threat_assessment_frequency: str = "monthly"


class SecurityComplianceOrchestrator:
    """
    Security & Compliance Module Orchestrator
    Central coordination for all security and compliance operations
    """
    
    def __init__(self, config: Optional[SecurityComplianceConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or SecurityComplianceConfig()
        
        # Initialize all security components
        self.model_security = ModelSecurityManager() if self.config.enable_model_security else None
        self.adversarial_defense = AdversarialDefenseEngine() if self.config.enable_adversarial_defense else None
        self.data_encryption = DataEncryptionManager() if self.config.enable_data_encryption else None
        self.compliance_framework = ComplianceFramework() if self.config.enable_compliance_tracking else None
        self.audit_manager = AuditTrailManager() if self.config.enable_audit_logging else None
        self.security_scanner = SecurityScanningSuite() if self.config.enable_security_scanning else None
        self.privacy_ml = PrivacyPreservingML() if self.config.enable_privacy_preservation else None
        self.secure_comm = SecureCommunication() if self.config.enable_secure_communication else None
        self.security_analytics = SecurityAnalytics() if self.config.enable_security_analytics else None
        self.threat_modeling = ThreatModelingEngine() if self.config.enable_threat_modeling else None
        self.identity_manager = IdentityAccessManager() if self.config.enable_identity_management else None
        self.compliance_reporter = SecurityComplianceReporter() if self.config.enable_compliance_reporting else None
        
        # Set default compliance frameworks if not specified
        if self.config.compliance_frameworks is None:
            self.config.compliance_frameworks = [
                ComplianceStandard.GDPR,
                ComplianceStandard.ISO_27001
            ]
    
    async def initialize_security_for_model(
        self,
        model_id: str,
        security_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize comprehensive security for a new ML model"""
        try:
            security_setup = {
                "model_id": model_id,
                "security_components": {},
                "initialization_status": "in_progress",
                "security_level": self.config.default_security_level.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Model Security Setup
            if self.model_security:
                security_policy = SecurityPolicy(
                    encryption_required=security_requirements.get("encryption_required", True),
                    access_control_enabled=security_requirements.get("access_control", True),
                    audit_logging=True,
                    vulnerability_scanning=True,
                    threat_monitoring=True
                )
                
                security_config = await self.model_security.register_model(
                    model_id, self.config.default_security_level, security_policy
                )
                security_setup["security_components"]["model_security"] = security_config
            
            # Adversarial Defense Setup
            if self.adversarial_defense:
                defense_config = DefenseStrategy.ENSEMBLE_DEFENSE
                await self.adversarial_defense.configure_defense(model_id, defense_config)
                security_setup["security_components"]["adversarial_defense"] = defense_config.value
            
            # Data Encryption Setup
            if self.data_encryption:
                encryption_config = {
                    "encryption_type": self.config.default_encryption_type,
                    "key_rotation_days": 90
                }
                await self.data_encryption.configure_encryption(model_id, encryption_config)
                security_setup["security_components"]["data_encryption"] = encryption_config
            
            # Compliance Setup
            if self.compliance_framework:
                for framework in self.config.compliance_frameworks:
                    await self.compliance_framework.configure_compliance(
                        model_id, [framework], ["personal", "sensitive"], 
                        "machine_learning", "legitimate_interest"
                    )
                security_setup["security_components"]["compliance"] = [f.value for f in self.config.compliance_frameworks]
            
            # Privacy-Preserving ML Setup
            if self.privacy_ml:
                privacy_config = {
                    "technique": PrivacyTechnique.DIFFERENTIAL_PRIVACY,
                    "privacy_level": self.config.default_privacy_level,
                    "epsilon": 1.0
                }
                await self.privacy_ml.configure_privacy(model_id, privacy_config)
                security_setup["security_components"]["privacy_ml"] = privacy_config
            
            # Threat Modeling
            if self.threat_modeling:
                threat_model_id = await self.threat_modeling.create_threat_model(
                    f"ML_Model_{model_id}",
                    f"Security threat model for ML model {model_id}",
                    self._create_model_assets(model_id, security_requirements)
                )
                security_setup["security_components"]["threat_model_id"] = threat_model_id
            
            # Audit Logging Setup
            if self.audit_manager:
                await self.audit_manager.configure_audit_trail(model_id, {
                    "enabled": True,
                    "real_time_alerts": True,
                    "retention_days": self.config.audit_retention_days
                })
                
                # Log security initialization
                await self.audit_manager.log_event(
                    AuditEventType.CONFIGURATION_CHANGE,
                    AuditSeverity.INFORMATIONAL,
                    model_id, "model", "security_initialization", "success",
                    details={"security_setup": security_setup}
                )
            
            security_setup["initialization_status"] = "completed"
            
            self.logger.info(f"Security initialized for model {model_id}")
            return security_setup
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security for model {model_id}: {str(e)}")
            raise
    
    async def perform_security_assessment(
        self,
        target_id: str,
        assessment_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Perform comprehensive security assessment"""
        try:
            assessment_result = {
                "assessment_id": f"SEC_ASSESS_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "target_id": target_id,
                "assessment_type": assessment_type,
                "timestamp": datetime.now().isoformat(),
                "components_assessed": {},
                "overall_score": 0.0,
                "critical_findings": [],
                "recommendations": []
            }
            
            total_score = 0.0
            components_count = 0
            
            # Security Scanning
            if self.security_scanner:
                scan_id = await self.security_scanner.start_security_scan(
                    target_id, [ScanType.VULNERABILITY, ScanType.CONFIGURATION, ScanType.DATA_EXPOSURE]
                )
                # Wait for scan completion (simplified)
                await asyncio.sleep(2)
                scan_results = await self.security_scanner.get_scan_results(scan_id)
                
                if scan_results:
                    vuln_score = max(0, 100 - len(scan_results.vulnerabilities) * 5)
                    assessment_result["components_assessed"]["vulnerability_scan"] = {
                        "score": vuln_score,
                        "vulnerabilities_found": len(scan_results.vulnerabilities),
                        "scan_id": scan_id
                    }
                    total_score += vuln_score
                    components_count += 1
            
            # Compliance Assessment
            if self.compliance_framework:
                compliance_assessments = {}
                for framework in self.config.compliance_frameworks:
                    assessment = await self.compliance_framework.assess_compliance(target_id, [framework])
                    compliance_assessments[framework.value] = {
                        "score": assessment.score,
                        "status": assessment.overall_status.value,
                        "findings_count": len(assessment.findings)
                    }
                    total_score += assessment.score
                    components_count += 1
                
                assessment_result["components_assessed"]["compliance"] = compliance_assessments
            
            # Threat Assessment
            if self.threat_modeling:
                attack_surface = await self.threat_modeling.analyze_attack_surface(target_id)
                if attack_surface:
                    threat_score = max(0, 100 - attack_surface.get("exposure_score", 0) * 100)
                    assessment_result["components_assessed"]["threat_analysis"] = {
                        "score": threat_score,
                        "exposure_score": attack_surface.get("exposure_score", 0),
                        "critical_assets": len(attack_surface.get("critical_assets", []))
                    }
                    total_score += threat_score
                    components_count += 1
            
            # Security Analytics
            if self.security_analytics:
                analytics_report = await self.security_analytics.analyze_threat_patterns()
                threat_score = max(0, 100 - len(analytics_report.get("anomalies", [])) * 10)
                assessment_result["components_assessed"]["security_analytics"] = {
                    "score": threat_score,
                    "anomalies_detected": len(analytics_report.get("anomalies", [])),
                    "total_events": analytics_report.get("total_events", 0)
                }
                total_score += threat_score
                components_count += 1
            
            # Calculate overall score
            assessment_result["overall_score"] = total_score / max(components_count, 1)
            
            # Identify critical findings
            if assessment_result["overall_score"] < 70:
                assessment_result["critical_findings"].append("Overall security score below threshold")
            
            # Generate recommendations
            assessment_result["recommendations"] = self._generate_assessment_recommendations(
                assessment_result["components_assessed"], assessment_result["overall_score"]
            )
            
            # Log assessment
            if self.audit_manager:
                await self.audit_manager.log_event(
                    AuditEventType.SECURITY_VIOLATION if assessment_result["overall_score"] < 70 else AuditEventType.SYSTEM_ACTION,
                    AuditSeverity.HIGH if assessment_result["overall_score"] < 70 else AuditSeverity.INFORMATIONAL,
                    target_id, "security_assessment", "security_assessment", "completed",
                    details={"assessment_summary": assessment_result}
                )
            
            return assessment_result
            
        except Exception as e:
            self.logger.error(f"Security assessment failed for {target_id}: {str(e)}")
            raise
    
    async def handle_security_incident(
        self,
        incident_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle security incident with automated response"""
        try:
            incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            incident_response = {
                "incident_id": incident_id,
                "timestamp": datetime.now().isoformat(),
                "incident_type": incident_data.get("type", "unknown"),
                "severity": incident_data.get("severity", "medium"),
                "affected_resources": incident_data.get("resources", []),
                "response_actions": [],
                "status": "investigating"
            }
            
            severity = incident_data.get("severity", "medium")
            incident_type = incident_data.get("type", "unknown")
            
            # Log incident
            if self.audit_manager:
                await self.audit_manager.log_event(
                    AuditEventType.SECURITY_VIOLATION,
                    AuditSeverity.CRITICAL if severity == "critical" else AuditSeverity.HIGH,
                    incident_data.get("target_id", "unknown"),
                    "security_incident", "incident_detected", "investigating",
                    details=incident_data
                )
                incident_response["response_actions"].append("Incident logged to audit trail")
            
            # Security Analytics Response
            if self.security_analytics:
                await self.security_analytics.ingest_security_event(
                    SecurityEventType.SECURITY_VIOLATION,
                    incident_data.get("source_ip"),
                    incident_data.get("user_id"),
                    incident_data.get("target_id", "unknown"),
                    f"Security incident: {incident_type}",
                    incident_data
                )
                incident_response["response_actions"].append("Event ingested to security analytics")
            
            # Automated Response Actions
            if severity in ["critical", "high"]:
                # Generate security alert
                alerts = await self.security_analytics.get_real_time_alerts(ThreatLevel.HIGH)
                incident_response["response_actions"].append("High-priority security alert generated")
                
                # If model is compromised, recommend suspension
                if incident_type in ["model_compromise", "data_poisoning"]:
                    incident_response["response_actions"].append("RECOMMENDATION: Suspend affected model")
                    incident_response["automated_actions"] = ["model_quarantine_recommended"]
            
            # Generate incident report
            if self.compliance_reporter:
                report_id = await self.compliance_reporter.generate_security_overview_report(
                    time_period=timedelta(hours=1)  # Recent context
                )
                incident_response["incident_report_id"] = report_id
                incident_response["response_actions"].append("Incident report generated")
            
            incident_response["status"] = "response_initiated"
            
            self.logger.warning(f"Security incident handled: {incident_id}")
            return incident_response
            
        except Exception as e:
            self.logger.error(f"Failed to handle security incident: {str(e)}")
            raise
    
    async def generate_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate real-time compliance and security dashboard"""
        try:
            dashboard = {
                "dashboard_id": f"DASH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "security_overview": {},
                "compliance_status": {},
                "recent_alerts": [],
                "metrics": {},
                "health_indicators": {}
            }
            
            # Security Overview
            if self.security_analytics:
                alerts = await self.security_analytics.get_real_time_alerts()
                dashboard["recent_alerts"] = alerts[:10]  # Last 10 alerts
                
                stats = await self.security_analytics.get_audit_statistics()
                dashboard["security_overview"] = stats
            
            # Compliance Status
            if self.compliance_reporter:
                compliance_summary = await self.compliance_reporter.get_compliance_summary()
                dashboard["compliance_status"] = compliance_summary
            
            # System Metrics
            metrics = {}
            if self.model_security:
                security_metrics = await self.model_security.get_security_metrics()
                metrics["model_security"] = security_metrics
            
            if self.data_encryption:
                encryption_metrics = await self.data_encryption.get_encryption_metrics()
                metrics["encryption"] = encryption_metrics
            
            if self.identity_manager:
                iam_metrics = await self.identity_manager.get_iam_metrics()
                metrics["identity_access"] = iam_metrics
            
            dashboard["metrics"] = metrics
            
            # Health Indicators
            dashboard["health_indicators"] = self._calculate_health_indicators(dashboard)
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance dashboard: {str(e)}")
            return {}
    
    async def validate_user_access(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        requested_access: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate user access with comprehensive security checks"""
        try:
            if not self.identity_manager:
                return {"access_granted": False, "reason": "iam_not_enabled"}
            
            # Convert string access level to enum
            access_level_map = {
                "read": AccessLevel.READ,
                "write": AccessLevel.WRITE,
                "execute": AccessLevel.EXECUTE,
                "admin": AccessLevel.ADMIN
            }
            access_level = access_level_map.get(requested_access.lower(), AccessLevel.READ)
            
            # Check access with IAM
            access_result = await self.identity_manager.check_access(
                user_id, resource_id, resource_type, access_level, context
            )
            
            # Additional security checks
            if access_result["access_granted"]:
                # Check for security alerts related to user
                if self.security_analytics:
                    user_alerts = await self.security_analytics.get_real_time_alerts()
                    user_related_alerts = [
                        alert for alert in user_alerts 
                        if alert.get("user_id") == user_id and alert.get("threat_level") in ["high", "critical"]
                    ]
                    
                    if user_related_alerts:
                        access_result["access_granted"] = False
                        access_result["reason"] = "security_alert_active"
                        access_result["security_alerts"] = len(user_related_alerts)
                
                # Check compliance requirements
                if self.compliance_framework and access_result["access_granted"]:
                    # For sensitive resources, ensure compliance
                    if resource_type in ["sensitive_data", "personal_data"]:
                        compliance_check = await self.compliance_framework.validate_data_processing_consent(
                            resource_id, [{"user_id": user_id, "consent_granted": True}]
                        )
                        if not compliance_check.get("processing_allowed", False):
                            access_result["access_granted"] = False
                            access_result["reason"] = "compliance_violation"
            
            # Log access attempt
            if self.audit_manager:
                await self.audit_manager.log_event(
                    AuditEventType.ACCESS_VIOLATION if not access_result["access_granted"] else AuditEventType.USER_ACTION,
                    AuditSeverity.MEDIUM if not access_result["access_granted"] else AuditSeverity.INFORMATIONAL,
                    resource_id, resource_type, f"access_request_{requested_access}",
                    "denied" if not access_result["access_granted"] else "granted",
                    user_id=user_id,
                    source_ip=context.get("source_ip") if context else None,
                    details=access_result
                )
            
            return access_result
            
        except Exception as e:
            self.logger.error(f"Access validation failed: {str(e)}")
            return {"access_granted": False, "reason": "system_error"}
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get overall security and compliance status"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "security_score": 0.0,
                "compliance_score": 0.0,
                "components_status": {},
                "active_threats": 0,
                "recommendations": []
            }
            
            scores = []
            
            # Check each component status
            if self.model_security:
                metrics = await self.model_security.get_security_metrics()
                security_score = metrics.get("health", {}).get("encryption_success_rate", 100)
                status["components_status"]["model_security"] = {"status": "operational", "score": security_score}
                scores.append(security_score)
            
            if self.compliance_framework:
                # Get compliance score for all frameworks
                compliance_scores = []
                for framework in self.config.compliance_frameworks:
                    try:
                        assessment = await self.compliance_framework.assess_compliance("system", [framework])
                        compliance_scores.append(assessment.score)
                    except:
                        pass
                
                if compliance_scores:
                    avg_compliance = sum(compliance_scores) / len(compliance_scores)
                    status["components_status"]["compliance"] = {"status": "operational", "score": avg_compliance}
                    status["compliance_score"] = avg_compliance
                    scores.append(avg_compliance)
            
            if self.security_analytics:
                alerts = await self.security_analytics.get_real_time_alerts(ThreatLevel.MEDIUM)
                status["active_threats"] = len(alerts)
                threat_score = max(0, 100 - len(alerts) * 5)
                status["components_status"]["threat_detection"] = {"status": "operational", "score": threat_score}
                scores.append(threat_score)
            
            # Calculate overall scores
            if scores:
                status["security_score"] = sum(scores) / len(scores)
                
                if status["security_score"] >= 90:
                    status["overall_status"] = "excellent"
                elif status["security_score"] >= 80:
                    status["overall_status"] = "good"
                elif status["security_score"] >= 70:
                    status["overall_status"] = "acceptable"
                else:
                    status["overall_status"] = "needs_attention"
            
            # Generate recommendations
            if status["security_score"] < 80:
                status["recommendations"].append("Security improvements needed")
            if status["active_threats"] > 5:
                status["recommendations"].append("High number of active threats - investigate")
            if status["compliance_score"] < 85:
                status["recommendations"].append("Compliance score below recommended threshold")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get security status: {str(e)}")
            return {"overall_status": "error", "error": str(e)}
    
    # Private helper methods
    
    def _create_model_assets(self, model_id: str, security_requirements: Dict[str, Any]) -> List[Any]:
        """Create asset inventory for threat modeling"""
        # This would create actual AssetInventory objects in production
        return [
            {
                "asset_id": f"{model_id}_model",
                "asset_type": "model",
                "name": f"ML Model {model_id}",
                "description": "Machine learning model for inference",
                "criticality": security_requirements.get("criticality", "medium"),
                "data_sensitivity": security_requirements.get("data_sensitivity", "medium"),
                "access_points": security_requirements.get("access_points", ["api", "batch"]),
                "dependencies": security_requirements.get("dependencies", []),
                "security_controls": security_requirements.get("security_controls", [])
            }
        ]
    
    def _generate_assessment_recommendations(
        self,
        components_assessed: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """Generate recommendations based on security assessment"""
        recommendations = []
        
        if overall_score < 70:
            recommendations.append("URGENT: Overall security score below acceptable threshold")
        
        # Component-specific recommendations
        if "vulnerability_scan" in components_assessed:
            vuln_data = components_assessed["vulnerability_scan"]
            if vuln_data.get("vulnerabilities_found", 0) > 5:
                recommendations.append("High number of vulnerabilities detected - prioritize patching")
        
        if "compliance" in components_assessed:
            for framework, data in components_assessed["compliance"].items():
                if data.get("score", 100) < 80:
                    recommendations.append(f"Improve {framework} compliance score")
        
        if "threat_analysis" in components_assessed:
            threat_data = components_assessed["threat_analysis"]
            if threat_data.get("exposure_score", 0) > 0.7:
                recommendations.append("High attack surface exposure - implement additional controls")
        
        return recommendations
    
    def _calculate_health_indicators(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate system health indicators"""
        health = {
            "overall_health": "unknown",
            "security_health": "unknown",
            "compliance_health": "unknown",
            "threat_level": "unknown"
        }
        
        try:
            # Security health
            alerts = dashboard.get("recent_alerts", [])
            critical_alerts = len([a for a in alerts if a.get("threat_level") == "critical"])
            
            if critical_alerts == 0:
                health["security_health"] = "excellent"
            elif critical_alerts <= 2:
                health["security_health"] = "good"
            else:
                health["security_health"] = "poor"
            
            # Compliance health
            compliance_data = dashboard.get("compliance_status", {})
            overall_compliance = compliance_data.get("overall_score", 0)
            
            if overall_compliance >= 90:
                health["compliance_health"] = "excellent"
            elif overall_compliance >= 80:
                health["compliance_health"] = "good"
            else:
                health["compliance_health"] = "needs_improvement"
            
            # Threat level
            if len(alerts) == 0:
                health["threat_level"] = "low"
            elif len(alerts) <= 5:
                health["threat_level"] = "medium"
            else:
                health["threat_level"] = "high"
            
            # Overall health
            if (health["security_health"] == "excellent" and 
                health["compliance_health"] == "excellent" and
                health["threat_level"] == "low"):
                health["overall_health"] = "excellent"
            elif critical_alerts > 0 or overall_compliance < 70:
                health["overall_health"] = "poor"
            else:
                health["overall_health"] = "good"
                
        except Exception as e:
            self.logger.error(f"Failed to calculate health indicators: {str(e)}")
        
        return health


# Global instances for easy access
security_compliance_config = SecurityComplianceConfig()
security_compliance_orchestrator = SecurityComplianceOrchestrator(security_compliance_config)

# Export main components
__all__ = [
    # Main orchestrator
    "SecurityComplianceOrchestrator",
    "SecurityComplianceConfig",
    "security_compliance_orchestrator",
    
    # Core security components
    "ModelSecurityManager",
    "AdversarialDefenseEngine", 
    "DataEncryptionManager",
    "ComplianceFramework",
    "AuditTrailManager",
    "SecurityScanningSuite",
    "PrivacyPreservingML",
    "SecureCommunication",
    "SecurityAnalytics",
    "ThreatModelingEngine",
    "IdentityAccessManager",
    "SecurityComplianceReporter",
    
    # Enums and data classes
    "SecurityLevel",
    "AttackType",
    "DefenseStrategy",
    "EncryptionType",
    "ComplianceStandard",
    "AuditEventType",
    "ScanType",
    "PrivacyTechnique",
    "SecurityProtocol",
    "ThreatLevel",
    "ThreatCategory",
    "AccessLevel",
    "ReportType"
]