"""
Compliance Engine
================

Advanced legal compliance monitoring and validation system
for licensing agreements and regulatory requirements.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID
import logging
from enum import Enum

from .models import (
    LicenseAgreement, ComplianceReport, LicenseUsageTracking,
    TerritoryScope, UsageType
)
from .repository import LicensingRepository
from ...core.exceptions import ComplianceError, ValidationError
from ...utils.legal import LegalValidator
from ...utils.territory import TerritoryValidator
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ComplianceLevel(Enum):
    """Compliance severity levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceEngine:
    """
    Professional compliance monitoring engine with real-time validation,
    automated reporting, and risk assessment capabilities.
    """
    
    def __init__(
        self,
        repository: LicensingRepository = None,
        legal_validator: LegalValidator = None,
        territory_validator: TerritoryValidator = None
    ):
        """Initialize compliance engine with validators"""
        self.repository = repository or LicensingRepository()
        self.legal_validator = legal_validator or LegalValidator()
        self.territory_validator = territory_validator or TerritoryValidator()
        self._logger = logger
        
        # Compliance thresholds
        self.usage_violation_threshold = 1.1  # 10% over allowed usage
        self.revenue_reporting_threshold = 1000.0  # USD
        self.critical_violation_score = 75.0  # Out of 100
        
        # Monitoring frequencies
        self.monitoring_frequencies = {
            "critical": timedelta(hours=1),
            "high": timedelta(hours=6),
            "medium": timedelta(days=1),
            "low": timedelta(days=7)
        }
    
    async def validate_license_compliance(
        self,
        license_agreement_id: UUID,
        user_id: UUID = None
    ) -> Dict[str, Any]:
        """Comprehensive license compliance validation"""
        try:
            # Get license agreement with relations
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id, include_relations=True
            )
            
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            compliance_results = {
                "license_id": str(license_agreement_id),
                "license_number": license_agreement.license_number,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "overall_status": ComplianceLevel.COMPLIANT.value,
                "compliance_score": 100.0,
                "validations": {
                    "territorial": await self._validate_territorial_compliance(license_agreement),
                    "usage_rights": await self._validate_usage_rights_compliance(license_agreement),
                    "financial": await self._validate_financial_compliance(license_agreement),
                    "temporal": await self._validate_temporal_compliance(license_agreement),
                    "legal": await self._validate_legal_compliance(license_agreement),
                    "technical": await self._validate_technical_compliance(license_agreement)
                },
                "violations": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Calculate overall compliance score and status
            compliance_results = await self._calculate_overall_compliance(compliance_results)
            
            # Generate recommendations
            compliance_results["recommendations"] = await self._generate_compliance_recommendations(
                license_agreement, compliance_results
            )
            
            self._logger.info(
                f"Compliance validation completed for license {license_agreement.license_number}: "
                f"{compliance_results['overall_status']} ({compliance_results['compliance_score']:.1f}%)"
            )
            
            return compliance_results
            
        except (ValidationError, ComplianceError):
            raise
        except Exception as e:
            raise ComplianceError(f"Error validating license compliance: {str(e)}")
    
    async def monitor_real_time_compliance(
        self,
        license_agreement_id: UUID,
        usage_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Real-time compliance monitoring for usage events"""
        try:
            # Get license agreement
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, include_relations=True
            )
            
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            monitoring_results = {
                "event_timestamp": datetime.utcnow().isoformat(),
                "license_number": license_agreement.license_number,
                "usage_event": usage_event,
                "compliance_status": ComplianceLevel.COMPLIANT.value,
                "violations_detected": [],
                "immediate_actions": [],
                "risk_level": RiskLevel.LOW.value
            }
            
            # Check territorial compliance
            territory_check = await self._check_territorial_usage(
                license_agreement, usage_event
            )
            if not territory_check["compliant"]:
                monitoring_results["violations_detected"].append(territory_check)
                monitoring_results["compliance_status"] = ComplianceLevel.VIOLATION.value
            
            # Check usage rights compliance
            usage_check = await self._check_usage_rights(
                license_agreement, usage_event
            )
            if not usage_check["compliant"]:
                monitoring_results["violations_detected"].append(usage_check)
                monitoring_results["compliance_status"] = ComplianceLevel.VIOLATION.value
            
            # Check platform compliance
            platform_check = await self._check_platform_restrictions(
                license_agreement, usage_event
            )
            if not platform_check["compliant"]:
                monitoring_results["violations_detected"].append(platform_check)
                monitoring_results["compliance_status"] = ComplianceLevel.VIOLATION.value
            
            # Check content restrictions
            content_check = await self._check_content_restrictions(
                license_agreement, usage_event
            )
            if not content_check["compliant"]:
                monitoring_results["violations_detected"].append(content_check)
                monitoring_results["compliance_status"] = ComplianceLevel.VIOLATION.value
            
            # Assess risk level
            monitoring_results["risk_level"] = await self._assess_violation_risk(
                monitoring_results["violations_detected"]
            )
            
            # Generate immediate actions if violations detected
            if monitoring_results["violations_detected"]:
                monitoring_results["immediate_actions"] = await self._generate_immediate_actions(
                    license_agreement, monitoring_results["violations_detected"]
                )
            
            return monitoring_results
            
        except (ValidationError, ComplianceError):
            raise
        except Exception as e:
            raise ComplianceError(f"Error in real-time compliance monitoring: {str(e)}")
    
    async def generate_compliance_report(
        self,
        license_agreement_id: UUID,
        reporting_period: Tuple[date, date],
        user_id: UUID
    ) -> ComplianceReport:
        """Generate comprehensive compliance report"""
        try:
            period_start, period_end = reporting_period
            
            # Get license agreement
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id, include_relations=True
            )
            
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            # Get usage analytics for the period
            usage_analytics = await self.repository.get_license_usage_analytics(
                license_agreement_id, user_id, period_start, period_end
            )
            
            # Perform comprehensive compliance analysis
            compliance_analysis = await self._analyze_period_compliance(
                license_agreement, usage_analytics, (period_start, period_end)
            )
            
            # Create compliance report data
            report_data = {
                "report_id": await self._generate_report_id(),
                "license_agreement_id": license_agreement_id,
                "report_type": "comprehensive",
                "report_date": date.today(),
                "reporting_period_start": period_start,
                "reporting_period_end": period_end,
                "overall_compliance_status": compliance_analysis["overall_status"],
                "compliance_score": compliance_analysis["compliance_score"],
                "violations_found": len(compliance_analysis["violations"]),
                "critical_violations": len([
                    v for v in compliance_analysis["violations"] 
                    if v.get("severity") == "critical"
                ]),
                "warnings": len(compliance_analysis["warnings"]),
                "territorial_compliance": compliance_analysis["territorial_compliance"],
                "usage_compliance": compliance_analysis["usage_compliance"],
                "payment_compliance": compliance_analysis["payment_compliance"],
                "technical_compliance": compliance_analysis["technical_compliance"],
                "corrective_actions": compliance_analysis["corrective_actions"],
                "penalties_applied": compliance_analysis.get("penalties_applied", 0),
                "risk_level": compliance_analysis["risk_level"],
                "risk_factors": compliance_analysis["risk_factors"],
                "auditor_id": user_id,
                "audit_methodology": "automated_comprehensive",
                "evidence_collected": compliance_analysis["evidence_collected"],
                "next_review_date": await self._calculate_next_review_date(
                    compliance_analysis["risk_level"]
                )
            }
            
            # Save compliance report (would need to implement this method)
            # compliance_report = await self.repository.create_compliance_report(report_data)
            
            self._logger.info(
                f"Generated compliance report for license {license_agreement.license_number}: "
                f"{compliance_analysis['overall_status']} "
                f"({compliance_analysis['compliance_score']:.1f}%)"
            )
            
            return report_data
            
        except (ValidationError, ComplianceError):
            raise
        except Exception as e:
            raise ComplianceError(f"Error generating compliance report: {str(e)}")
    
    async def assess_compliance_risk(
        self,
        license_agreement_id: UUID,
        user_id: UUID = None
    ) -> Dict[str, Any]:
        """Assess compliance risk factors and probability"""
        try:
            # Get license agreement
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id, include_relations=True
            )
            
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            risk_assessment = {
                "license_id": str(license_agreement_id),
                "assessment_date": datetime.utcnow().isoformat(),
                "overall_risk_level": RiskLevel.LOW.value,
                "risk_score": 0.0,  # 0-100 scale
                "risk_factors": {},
                "mitigation_recommendations": [],
                "monitoring_frequency": "weekly"
            }
            
            # Assess various risk factors
            risk_factors = {
                "territorial_complexity": await self._assess_territorial_risk(license_agreement),
                "usage_complexity": await self._assess_usage_rights_risk(license_agreement),
                "financial_risk": await self._assess_financial_risk(license_agreement),
                "legal_jurisdiction_risk": await self._assess_legal_jurisdiction_risk(license_agreement),
                "compliance_history": await self._assess_compliance_history_risk(license_agreement),
                "technical_integration": await self._assess_technical_integration_risk(license_agreement)
            }
            
            # Calculate overall risk score
            total_risk_score = sum(factor["score"] for factor in risk_factors.values())
            risk_assessment["risk_score"] = min(total_risk_score, 100.0)
            risk_assessment["risk_factors"] = risk_factors
            
            # Determine overall risk level
            if risk_assessment["risk_score"] >= 75:
                risk_assessment["overall_risk_level"] = RiskLevel.CRITICAL.value
                risk_assessment["monitoring_frequency"] = "hourly"
            elif risk_assessment["risk_score"] >= 50:
                risk_assessment["overall_risk_level"] = RiskLevel.HIGH.value
                risk_assessment["monitoring_frequency"] = "daily"
            elif risk_assessment["risk_score"] >= 25:
                risk_assessment["overall_risk_level"] = RiskLevel.MEDIUM.value
                risk_assessment["monitoring_frequency"] = "weekly"
            else:
                risk_assessment["overall_risk_level"] = RiskLevel.LOW.value
                risk_assessment["monitoring_frequency"] = "monthly"
            
            # Generate mitigation recommendations
            risk_assessment["mitigation_recommendations"] = await self._generate_risk_mitigation_recommendations(
                risk_factors
            )
            
            return risk_assessment
            
        except (ValidationError, ComplianceError):
            raise
        except Exception as e:
            raise ComplianceError(f"Error assessing compliance risk: {str(e)}")
    
    # Private validation methods
    
    async def _validate_territorial_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate territorial compliance"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Check if territory scope is valid
            if license_agreement.territory not in [t.value for t in TerritoryScope]:
                validation_result["issues"].append({
                    "type": "invalid_territory",
                    "message": f"Invalid territory scope: {license_agreement.territory}",
                    "severity": "warning"
                })
                validation_result["score"] -= 10
            
            # Check geographical restrictions
            if license_agreement.geographical_restrictions:
                geo_validation = await self.territory_validator.validate_restrictions(
                    license_agreement.geographical_restrictions
                )
                if not geo_validation["valid"]:
                    validation_result["issues"].extend(geo_validation["errors"])
                    validation_result["score"] -= 20
            
            # Update status based on score
            if validation_result["score"] < 80:
                validation_result["status"] = ComplianceLevel.WARNING.value
            if validation_result["score"] < 60:
                validation_result["status"] = ComplianceLevel.VIOLATION.value
            
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating territorial compliance: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    async def _validate_usage_rights_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate usage rights compliance"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Check usage rights validity
            if not license_agreement.usage_rights:
                validation_result["issues"].append({
                    "type": "missing_usage_rights",
                    "message": "No usage rights specified",
                    "severity": "critical"
                })
                validation_result["score"] = 0
                validation_result["status"] = ComplianceLevel.CRITICAL.value
                return validation_result
            
            # Validate usage rights against known types
            valid_usage_types = [t.value for t in UsageType]
            invalid_rights = [
                right for right in license_agreement.usage_rights 
                if right not in valid_usage_types
            ]
            
            if invalid_rights:
                validation_result["issues"].append({
                    "type": "invalid_usage_rights",
                    "message": f"Invalid usage rights: {invalid_rights}",
                    "severity": "warning"
                })
                validation_result["score"] -= len(invalid_rights) * 5
            
            # Check for conflicting rights
            conflicting_pairs = [
                ("commercial", "non_commercial"),
                ("exclusive", "non_exclusive")
            ]
            
            for pair in conflicting_pairs:
                if all(right in license_agreement.usage_rights for right in pair):
                    validation_result["issues"].append({
                        "type": "conflicting_rights",
                        "message": f"Conflicting usage rights: {pair}",
                        "severity": "violation"
                    })
                    validation_result["score"] -= 25
                    validation_result["status"] = ComplianceLevel.VIOLATION.value
            
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating usage rights: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    async def _validate_financial_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate financial compliance"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Check royalty rate validity
            if license_agreement.royalty_rate < 0 or license_agreement.royalty_rate > 100:
                validation_result["issues"].append({
                    "type": "invalid_royalty_rate",
                    "message": f"Royalty rate {license_agreement.royalty_rate}% is outside valid range (0-100%)",
                    "severity": "critical"
                })
                validation_result["score"] = 0
                validation_result["status"] = ComplianceLevel.CRITICAL.value
            
            # Check minimum guarantee vs advance payment
            if (license_agreement.minimum_guarantee > 0 and 
                license_agreement.advance_payment > license_agreement.minimum_guarantee):
                validation_result["issues"].append({
                    "type": "advance_exceeds_guarantee",
                    "message": "Advance payment exceeds minimum guarantee",
                    "severity": "warning"
                })
                validation_result["score"] -= 10
            
            # Check currency validity
            valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]  # Add more as needed
            if license_agreement.currency not in valid_currencies:
                validation_result["issues"].append({
                    "type": "unsupported_currency",
                    "message": f"Currency {license_agreement.currency} may not be fully supported",
                    "severity": "warning"
                })
                validation_result["score"] -= 5
            
            # Check payment terms
            if license_agreement.payment_due_days > 90:
                validation_result["issues"].append({
                    "type": "excessive_payment_terms",
                    "message": f"Payment terms of {license_agreement.payment_due_days} days may be excessive",
                    "severity": "warning"
                })
                validation_result["score"] -= 5
            
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating financial compliance: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    async def _validate_temporal_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate temporal compliance (dates, durations)"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            current_date = date.today()
            
            # Check if license has started
            if license_agreement.start_date > current_date:
                validation_result["details"]["status"] = "future"
            elif license_agreement.end_date and license_agreement.end_date < current_date:
                validation_result["details"]["status"] = "expired"
                validation_result["issues"].append({
                    "type": "expired_license",
                    "message": "License has expired",
                    "severity": "critical"
                })
                validation_result["score"] = 0
                validation_result["status"] = ComplianceLevel.CRITICAL.value
            else:
                validation_result["details"]["status"] = "active"
            
            # Check date logic
            if license_agreement.end_date and license_agreement.start_date >= license_agreement.end_date:
                validation_result["issues"].append({
                    "type": "invalid_date_range",
                    "message": "Start date must be before end date",
                    "severity": "critical"
                })
                validation_result["score"] = 0
                validation_result["status"] = ComplianceLevel.CRITICAL.value
            
            # Check auto-renewal settings
            if license_agreement.auto_renewal and not license_agreement.end_date:
                validation_result["issues"].append({
                    "type": "perpetual_auto_renewal",
                    "message": "Auto-renewal set on perpetual license",
                    "severity": "warning"
                })
                validation_result["score"] -= 5
            
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating temporal compliance: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    async def _validate_legal_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate legal compliance"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Use legal validator if available
            if self.legal_validator:
                legal_validation = await self.legal_validator.validate_license_terms(
                    license_agreement
                )
                validation_result.update(legal_validation)
            else:
                # Basic legal compliance checks
                if not license_agreement.governing_law:
                    validation_result["issues"].append({
                        "type": "missing_governing_law",
                        "message": "No governing law specified",
                        "severity": "warning"
                    })
                    validation_result["score"] -= 10
                
                if not license_agreement.jurisdiction:
                    validation_result["issues"].append({
                        "type": "missing_jurisdiction",
                        "message": "No jurisdiction specified",
                        "severity": "warning"
                    })
                    validation_result["score"] -= 10
        
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating legal compliance: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    async def _validate_technical_compliance(
        self,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate technical compliance"""
        validation_result = {
            "status": ComplianceLevel.COMPLIANT.value,
            "score": 100.0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Check platform restrictions format
            if license_agreement.platform_restrictions:
                for platform in license_agreement.platform_restrictions:
                    if not isinstance(platform, str) or len(platform.strip()) == 0:
                        validation_result["issues"].append({
                            "type": "invalid_platform_restriction",
                            "message": f"Invalid platform restriction: {platform}",
                            "severity": "warning"
                        })
                        validation_result["score"] -= 5
            
            # Check content restrictions format
            if license_agreement.content_restrictions:
                if not isinstance(license_agreement.content_restrictions, dict):
                    validation_result["issues"].append({
                        "type": "invalid_content_restrictions_format",
                        "message": "Content restrictions must be in JSON object format",
                        "severity": "warning"
                    })
                    validation_result["score"] -= 10
            
            # Check custom terms format
            if license_agreement.custom_terms:
                if not isinstance(license_agreement.custom_terms, dict):
                    validation_result["issues"].append({
                        "type": "invalid_custom_terms_format",
                        "message": "Custom terms must be in JSON object format",
                        "severity": "warning"
                    })
                    validation_result["score"] -= 5
        
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": f"Error validating technical compliance: {str(e)}",
                "severity": "critical"
            })
            validation_result["status"] = ComplianceLevel.CRITICAL.value
            validation_result["score"] = 0
        
        return validation_result
    
    # Additional helper methods for risk assessment and monitoring
    
    async def _calculate_overall_compliance(self, compliance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall compliance score and status"""
        validations = compliance_results["validations"]
        total_score = sum(v["score"] for v in validations.values())
        average_score = total_score / len(validations)
        
        compliance_results["compliance_score"] = average_score
        
        # Collect all violations and warnings
        all_violations = []
        all_warnings = []
        
        for validation in validations.values():
            for issue in validation["issues"]:
                if issue["severity"] in ["critical", "violation"]:
                    all_violations.append(issue)
                elif issue["severity"] == "warning":
                    all_warnings.append(issue)
        
        compliance_results["violations"] = all_violations
        compliance_results["warnings"] = all_warnings
        
        # Determine overall status
        if any(issue["severity"] == "critical" for issue in all_violations):
            compliance_results["overall_status"] = ComplianceLevel.CRITICAL.value
        elif any(issue["severity"] == "violation" for issue in all_violations):
            compliance_results["overall_status"] = ComplianceLevel.VIOLATION.value
        elif all_warnings:
            compliance_results["overall_status"] = ComplianceLevel.WARNING.value
        else:
            compliance_results["overall_status"] = ComplianceLevel.COMPLIANT.value
        
        return compliance_results
    
    async def _generate_report_id(self) -> str:
        """Generate unique compliance report ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"COMP-{timestamp}-{hash(timestamp) % 10000:04d}"
    
    async def _calculate_next_review_date(self, risk_level: str) -> date:
        """Calculate next review date based on risk level"""
        current_date = date.today()
        
        if risk_level == RiskLevel.CRITICAL.value:
            return current_date + timedelta(days=7)  # Weekly
        elif risk_level == RiskLevel.HIGH.value:
            return current_date + timedelta(days=30)  # Monthly
        elif risk_level == RiskLevel.MEDIUM.value:
            return current_date + timedelta(days=90)  # Quarterly
        else:
            return current_date + timedelta(days=180)  # Semi-annually
