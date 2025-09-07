"""License Compliance Monitor - Legal Compliance Engine

Advanced license compliance monitoring system ensuring legal adherence 
across all content usage, distribution, and monetization activities.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LicenseType(str, Enum):
    """Supported license types"""
    COPYRIGHT = "copyright"
    CREATIVE_COMMONS_BY = "cc_by"
    CREATIVE_COMMONS_BY_SA = "cc_by_sa"
    CREATIVE_COMMONS_BY_NC = "cc_by_nc"
    CREATIVE_COMMONS_BY_ND = "cc_by_nd"
    CREATIVE_COMMONS_BY_NC_SA = "cc_by_nc_sa"
    CREATIVE_COMMONS_BY_NC_ND = "cc_by_nc_nd"
    CREATIVE_COMMONS_ZERO = "cc0"
    PUBLIC_DOMAIN = "public_domain"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EDITORIAL_USE = "editorial_use"
    COMMERCIAL_USE = "commercial_use"
    EXTENDED_LICENSE = "extended_license"
    EXCLUSIVE_LICENSE = "exclusive_license"
    CUSTOM_LICENSE = "custom_license"
    UNKNOWN = "unknown"


class ComplianceStatus(str, Enum):
    """License compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_ATTRIBUTION = "requires_attribution"
    REQUIRES_PAYMENT = "requires_payment"
    REQUIRES_PERMISSION = "requires_permission"
    EXPIRED = "expired"
    PENDING_REVIEW = "pending_review"
    VIOLATION = "violation"
    UNKNOWN = "unknown"


class UsageType(str, Enum):
    """Content usage types"""
    DISPLAY = "display"
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    COMMERCIAL_USE = "commercial_use"
    SUBLICENSING = "sublicensing"
    DERIVATIVE_WORKS = "derivative_works"
    PUBLIC_PERFORMANCE = "public_performance"
    BROADCASTING = "broadcasting"
    STREAMING = "streaming"
    PRINT_MEDIA = "print_media"
    DIGITAL_MEDIA = "digital_media"
    MERCHANDISE = "merchandise"
    ADVERTISING = "advertising"
    EDITORIAL = "editorial"


class ComplianceRisk(str, Enum):
    """Compliance risk levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LicenseInfo(BaseModel):
    """License information model"""
    license_id: str = Field(default_factory=lambda: str(uuid4()))
    license_type: LicenseType
    license_text: str = ""
    license_url: Optional[str] = None
    licensor: str = ""
    licensee: str = ""
    granted_rights: List[UsageType] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    attribution_required: bool = False
    attribution_text: str = ""
    commercial_use_allowed: bool = False
    derivative_works_allowed: bool = False
    share_alike_required: bool = False
    exclusive: bool = False
    territory: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    payment_required: bool = False
    payment_amount: Optional[float] = None
    payment_currency: str = "EUR"
    renewal_terms: Dict[str, Any] = Field(default_factory=dict)
    compliance_notes: List[str] = Field(default_factory=list)


class ContentUsage(BaseModel):
    """Content usage tracking model"""
    usage_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str
    usage_type: UsageType
    platform: str = ""
    distribution_channel: str = ""
    audience_reach: Optional[int] = None
    commercial_value: Optional[float] = None
    geographic_regions: List[str] = Field(default_factory=list)
    usage_start_date: datetime = Field(default_factory=datetime.utcnow)
    usage_end_date: Optional[datetime] = None
    user_id: str = ""
    organization: str = ""
    purpose: str = ""
    modification_applied: bool = False
    modification_details: str = ""
    attribution_provided: bool = False
    attribution_text: str = ""
    payment_made: bool = False
    payment_details: Dict[str, Any] = Field(default_factory=dict)


class ComplianceCheck(BaseModel):
    """License compliance check model"""
    check_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str
    license_info: LicenseInfo
    intended_usage: ContentUsage
    compliance_status: ComplianceStatus
    risk_level: ComplianceRisk
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    violations: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    legal_notes: List[str] = Field(default_factory=list)
    check_timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    manual_review_required: bool = False
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None


class ComplianceAlert(BaseModel):
    """Compliance alert model"""
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str
    alert_type: str = Field(..., regex="^(violation|expiration|renewal|payment_due|attribution_missing)$")
    severity: ComplianceRisk
    title: str
    description: str
    action_required: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    responsible_party: str = ""
    alert_timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: str = ""


class LicenseComplianceAnalyzer:
    """License compliance analysis engine"""
    
    def __init__(self):
        # License compliance rules
        self.compliance_rules = {
            LicenseType.COPYRIGHT: {
                "requires_permission": True,
                "attribution_required": True,
                "commercial_use_default": False,
                "derivative_works_default": False,
                "payment_required": True
            },
            LicenseType.CREATIVE_COMMONS_BY: {
                "requires_permission": False,
                "attribution_required": True,
                "commercial_use_default": True,
                "derivative_works_default": True,
                "payment_required": False
            },
            LicenseType.CREATIVE_COMMONS_BY_NC: {
                "requires_permission": False,
                "attribution_required": True,
                "commercial_use_default": False,
                "derivative_works_default": True,
                "payment_required": False
            },
            LicenseType.CREATIVE_COMMONS_BY_SA: {
                "requires_permission": False,
                "attribution_required": True,
                "commercial_use_default": True,
                "derivative_works_default": True,
                "share_alike_required": True,
                "payment_required": False
            },
            LicenseType.CREATIVE_COMMONS_BY_ND: {
                "requires_permission": False,
                "attribution_required": True,
                "commercial_use_default": True,
                "derivative_works_default": False,
                "payment_required": False
            },
            LicenseType.CREATIVE_COMMONS_ZERO: {
                "requires_permission": False,
                "attribution_required": False,
                "commercial_use_default": True,
                "derivative_works_default": True,
                "payment_required": False
            },
            LicenseType.PUBLIC_DOMAIN: {
                "requires_permission": False,
                "attribution_required": False,
                "commercial_use_default": True,
                "derivative_works_default": True,
                "payment_required": False
            },
            LicenseType.ROYALTY_FREE: {
                "requires_permission": False,
                "attribution_required": False,
                "commercial_use_default": True,
                "derivative_works_default": True,
                "payment_required": True  # Usually one-time payment
            }
        }
        
        # Risk assessment weights
        self.risk_weights = {
            "license_violation": 0.4,
            "attribution_missing": 0.2,
            "commercial_use_violation": 0.3,
            "territory_violation": 0.25,
            "expiration_risk": 0.15,
            "payment_overdue": 0.35
        }
    
    async def analyze_compliance(
        self, 
        license_info: LicenseInfo, 
        intended_usage: ContentUsage
    ) -> ComplianceCheck:
        """Analyze license compliance for intended usage"""
        
        try:
            logger.info(f"Analyzing license compliance for content: {intended_usage.content_id}")
            
            violations = []
            requirements = []
            recommendations = []
            legal_notes = []
            
            # Get license rules
            rules = self.compliance_rules.get(license_info.license_type, {})
            
            # Check permission requirements
            if rules.get("requires_permission", False):
                if not license_info.licensee or license_info.licensee != intended_usage.user_id:
                    violations.append("Explicit permission required but not obtained")
                    requirements.append("Obtain written permission from copyright holder")
            
            # Check attribution requirements
            if license_info.attribution_required:
                if not intended_usage.attribution_provided:
                    violations.append("Attribution required but not provided")
                    requirements.append("Provide proper attribution as specified in license")
                elif license_info.attribution_text and intended_usage.attribution_text != license_info.attribution_text:
                    violations.append("Attribution text does not match required format")
                    requirements.append(f"Use exact attribution: {license_info.attribution_text}")
            
            # Check commercial use compliance
            if intended_usage.usage_type == UsageType.COMMERCIAL_USE or intended_usage.commercial_value:
                if not license_info.commercial_use_allowed and not rules.get("commercial_use_default", False):
                    violations.append("Commercial use not permitted under this license")
                    legal_notes.append("Consider obtaining commercial license or using different content")
            
            # Check derivative works compliance
            if intended_usage.modification_applied:
                if not license_info.derivative_works_allowed and not rules.get("derivative_works_default", False):
                    violations.append("Derivative works not permitted under this license")
                    requirements.append("Use original content without modifications")
                elif license_info.share_alike_required or rules.get("share_alike_required", False):
                    requirements.append("Derivative work must be licensed under same terms (Share-Alike)")
            
            # Check territory restrictions
            if license_info.territory and intended_usage.geographic_regions:
                for region in intended_usage.geographic_regions:
                    if region not in license_info.territory:
                        violations.append(f"Usage in {region} not permitted under license")
                        requirements.append(f"Restrict distribution to licensed territories: {license_info.territory}")
            
            # Check payment requirements
            if license_info.payment_required and not intended_usage.payment_made:
                violations.append("Payment required but not completed")
                requirements.append(f"Complete payment: {license_info.payment_amount} {license_info.payment_currency}")
            
            # Check license expiration
            if license_info.expiration_date and license_info.expiration_date < datetime.utcnow():
                violations.append("License has expired")
                legal_notes.append("Renew license or cease usage immediately")
            
            # Determine compliance status
            status = self._determine_compliance_status(violations, license_info, intended_usage)
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(violations, license_info, intended_usage)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations, requirements)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                status, violations, license_info, intended_usage
            )
            
            # Determine if manual review is needed
            manual_review_required = (
                len(violations) > 0 or
                risk_level in [ComplianceRisk.HIGH, ComplianceRisk.CRITICAL] or
                license_info.license_type == LicenseType.CUSTOM_LICENSE
            )
            
            # Create compliance check result
            check = ComplianceCheck(
                content_id=intended_usage.content_id,
                license_info=license_info,
                intended_usage=intended_usage,
                compliance_status=status,
                risk_level=risk_level,
                compliance_score=compliance_score,
                violations=violations,
                requirements=requirements,
                recommendations=recommendations,
                legal_notes=legal_notes,
                manual_review_required=manual_review_required,
                expires_at=datetime.utcnow() + timedelta(days=90)
            )
            
            logger.info(f"Compliance analysis completed: {status.value} (Risk: {risk_level.value})")
            
            return check
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {str(e)}")
            
            return ComplianceCheck(
                content_id=intended_usage.content_id,
                license_info=license_info,
                intended_usage=intended_usage,
                compliance_status=ComplianceStatus.UNKNOWN,
                risk_level=ComplianceRisk.HIGH,
                compliance_score=0.0,
                violations=[f"Analysis error: {str(e)}"],
                requirements=["Manual legal review required"],
                recommendations=["Consult legal counsel before proceeding"],
                manual_review_required=True
            )
    
    def _determine_compliance_status(
        self, 
        violations: List[str], 
        license_info: LicenseInfo, 
        intended_usage: ContentUsage
    ) -> ComplianceStatus:
        """Determine overall compliance status"""
        
        if violations:
            # Check for critical violations
            critical_keywords = ["not permitted", "expired", "violation"]
            if any(keyword in violation.lower() for violation in violations for keyword in critical_keywords):
                return ComplianceStatus.VIOLATION
            
            # Check for attribution issues
            if any("attribution" in violation.lower() for violation in violations):
                return ComplianceStatus.REQUIRES_ATTRIBUTION
            
            # Check for payment issues
            if any("payment" in violation.lower() for violation in violations):
                return ComplianceStatus.REQUIRES_PAYMENT
            
            # Check for permission issues
            if any("permission" in violation.lower() for violation in violations):
                return ComplianceStatus.REQUIRES_PERMISSION
            
            return ComplianceStatus.NON_COMPLIANT
        
        # Check if license is expired
        if license_info.expiration_date and license_info.expiration_date < datetime.utcnow():
            return ComplianceStatus.EXPIRED
        
        # Check if approaching expiration (within 30 days)
        if license_info.expiration_date and license_info.expiration_date < datetime.utcnow() + timedelta(days=30):
            return ComplianceStatus.PENDING_REVIEW
        
        return ComplianceStatus.COMPLIANT
    
    def _calculate_risk_level(
        self, 
        violations: List[str], 
        license_info: LicenseInfo, 
        intended_usage: ContentUsage
    ) -> ComplianceRisk:
        """Calculate compliance risk level"""
        
        risk_score = 0.0
        
        # Violation-based risk
        if violations:
            violation_severity = {
                "not permitted": 0.8,
                "expired": 0.9,
                "commercial use": 0.7,
                "derivative works": 0.6,
                "attribution": 0.4,
                "payment": 0.6,
                "territory": 0.5
            }
            
            for violation in violations:
                for keyword, severity in violation_severity.items():
                    if keyword in violation.lower():
                        risk_score += severity
                        break
                else:
                    risk_score += 0.3  # Default violation weight
        
        # License type risk
        license_risk = {
            LicenseType.COPYRIGHT: 0.8,
            LicenseType.CUSTOM_LICENSE: 0.7,
            LicenseType.RIGHTS_MANAGED: 0.6,
            LicenseType.EXCLUSIVE_LICENSE: 0.6,
            LicenseType.EDITORIAL_USE: 0.5,
            LicenseType.ROYALTY_FREE: 0.3,
            LicenseType.CREATIVE_COMMONS_BY: 0.1,
            LicenseType.CREATIVE_COMMONS_ZERO: 0.0,
            LicenseType.PUBLIC_DOMAIN: 0.0
        }
        
        risk_score += license_risk.get(license_info.license_type, 0.5)
        
        # Commercial use risk
        if intended_usage.commercial_value and intended_usage.commercial_value > 1000:
            risk_score += 0.3
        
        # Territory risk
        if license_info.territory and len(intended_usage.geographic_regions) > len(license_info.territory):
            risk_score += 0.2
        
        # Normalize risk score
        risk_score = min(risk_score, 3.0)
        
        # Convert to risk level
        if risk_score >= 2.5:
            return ComplianceRisk.CRITICAL
        elif risk_score >= 2.0:
            return ComplianceRisk.HIGH
        elif risk_score >= 1.0:
            return ComplianceRisk.MEDIUM
        elif risk_score >= 0.5:
            return ComplianceRisk.LOW
        else:
            return ComplianceRisk.MINIMAL
    
    def _calculate_compliance_score(
        self, 
        violations: List[str], 
        requirements: List[str]
    ) -> float:
        """Calculate compliance score (0-1)"""
        
        if not violations and not requirements:
            return 1.0
        
        # Base score
        score = 1.0
        
        # Deduct for violations
        violation_penalty = len(violations) * 0.15
        score -= violation_penalty
        
        # Deduct for unfulfilled requirements
        requirement_penalty = len(requirements) * 0.10
        score -= requirement_penalty
        
        return max(score, 0.0)
    
    async def _generate_recommendations(
        self,
        status: ComplianceStatus,
        violations: List[str],
        license_info: LicenseInfo,
        intended_usage: ContentUsage
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        if status == ComplianceStatus.COMPLIANT:
            recommendations.extend([
                "Content usage is compliant with license terms",
                "Maintain proper documentation for audit purposes",
                "Monitor license expiration dates"
            ])
        
        elif status == ComplianceStatus.REQUIRES_ATTRIBUTION:
            recommendations.extend([
                "Add proper attribution as required by license",
                "Use exact attribution text specified in license",
                "Ensure attribution is clearly visible"
            ])
        
        elif status == ComplianceStatus.REQUIRES_PAYMENT:
            recommendations.extend([
                "Complete required license payment",
                "Obtain payment receipt for records",
                "Verify payment terms and renewal requirements"
            ])
        
        elif status == ComplianceStatus.REQUIRES_PERMISSION:
            recommendations.extend([
                "Obtain explicit written permission from rights holder",
                "Negotiate appropriate license terms",
                "Document permission terms clearly"
            ])
        
        elif status == ComplianceStatus.VIOLATION:
            recommendations.extend([
                "STOP current usage immediately",
                "Seek legal counsel",
                "Consider alternative content or licensing options"
            ])
        
        elif status == ComplianceStatus.EXPIRED:
            recommendations.extend([
                "Renew license immediately or cease usage",
                "Contact rights holder for renewal terms",
                "Remove content from all distribution channels if renewal not possible"
            ])
        
        # License-specific recommendations
        if license_info.license_type in [LicenseType.CREATIVE_COMMONS_BY_SA, LicenseType.CREATIVE_COMMONS_BY_NC_SA]:
            if intended_usage.modification_applied:
                recommendations.append("Ensure derivative work uses same license (Share-Alike requirement)")
        
        if license_info.commercial_use_allowed and intended_usage.commercial_value:
            recommendations.append("Maintain records of commercial use for potential royalty calculations")
        
        return recommendations


class ComplianceMonitor:
    """Continuous compliance monitoring system"""
    
    def __init__(self):
        self.analyzer = LicenseComplianceAnalyzer()
        self.monitored_content = {}
        self.compliance_alerts = []
        
        # Monitoring configuration
        self.monitoring_intervals = {
            "high_risk": timedelta(days=1),
            "medium_risk": timedelta(days=7),
            "low_risk": timedelta(days=30)
        }
        
        self.alert_thresholds = {
            "expiration_warning": timedelta(days=30),
            "renewal_reminder": timedelta(days=7),
            "payment_overdue": timedelta(days=1)
        }
    
    async def add_content_monitoring(
        self, 
        content_id: str, 
        license_info: LicenseInfo,
        usage_info: ContentUsage
    ) -> Dict[str, Any]:
        """Add content to compliance monitoring"""
        
        try:
            logger.info(f"Adding compliance monitoring for content: {content_id}")
            
            # Perform initial compliance check
            compliance_check = await self.analyzer.analyze_compliance(license_info, usage_info)
            
            # Set monitoring frequency based on risk level
            if compliance_check.risk_level in [ComplianceRisk.CRITICAL, ComplianceRisk.HIGH]:
                monitoring_interval = self.monitoring_intervals["high_risk"]
            elif compliance_check.risk_level == ComplianceRisk.MEDIUM:
                monitoring_interval = self.monitoring_intervals["medium_risk"]
            else:
                monitoring_interval = self.monitoring_intervals["low_risk"]
            
            # Store monitoring configuration
            monitoring_config = {
                "content_id": content_id,
                "license_info": license_info,
                "usage_info": usage_info,
                "last_check": compliance_check,
                "monitoring_interval": monitoring_interval,
                "next_check": datetime.utcnow() + monitoring_interval,
                "total_checks": 1,
                "compliance_history": [compliance_check],
                "active_alerts": [],
                "monitoring_active": True
            }
            
            self.monitored_content[content_id] = monitoring_config
            
            # Generate alerts if needed
            await self._check_for_alerts(content_id, compliance_check)
            
            logger.info(f"Compliance monitoring activated for: {content_id}")
            
            return {
                "success": True,
                "content_id": content_id,
                "initial_status": compliance_check.compliance_status.value,
                "risk_level": compliance_check.risk_level.value,
                "monitoring_interval": str(monitoring_interval),
                "next_check": monitoring_config["next_check"]
            }
            
        except Exception as e:
            logger.error(f"Failed to add compliance monitoring: {str(e)}")
            return {
                "success": False,
                "content_id": content_id,
                "error": str(e)
            }
    
    async def check_compliance_status(self, content_id: str) -> Optional[ComplianceCheck]:
        """Check current compliance status for content"""
        
        if content_id not in self.monitored_content:
            logger.warning(f"Content not found in monitoring: {content_id}")
            return None
        
        try:
            config = self.monitored_content[content_id]
            
            # Check if it's time for a new compliance check
            if datetime.utcnow() >= config["next_check"]:
                logger.info(f"Performing scheduled compliance check for: {content_id}")
                
                # Perform new compliance check
                new_check = await self.analyzer.analyze_compliance(
                    config["license_info"], 
                    config["usage_info"]
                )
                
                # Update monitoring configuration
                config["last_check"] = new_check
                config["total_checks"] += 1
                config["compliance_history"].append(new_check)
                config["next_check"] = datetime.utcnow() + config["monitoring_interval"]
                
                # Adjust monitoring interval based on new risk level
                if new_check.risk_level != config["last_check"].risk_level:
                    if new_check.risk_level in [ComplianceRisk.CRITICAL, ComplianceRisk.HIGH]:
                        config["monitoring_interval"] = self.monitoring_intervals["high_risk"]
                    elif new_check.risk_level == ComplianceRisk.MEDIUM:
                        config["monitoring_interval"] = self.monitoring_intervals["medium_risk"]
                    else:
                        config["monitoring_interval"] = self.monitoring_intervals["low_risk"]
                
                # Check for new alerts
                await self._check_for_alerts(content_id, new_check)
                
                return new_check
            else:
                # Return last check result
                return config["last_check"]
                
        except Exception as e:
            logger.error(f"Compliance status check failed for {content_id}: {str(e)}")
            return None
    
    async def get_compliance_alerts(
        self, 
        content_id: Optional[str] = None,
        severity: Optional[ComplianceRisk] = None,
        unresolved_only: bool = True
    ) -> List[ComplianceAlert]:
        """Get compliance alerts"""
        
        alerts = self.compliance_alerts.copy()
        
        # Filter by content ID
        if content_id:
            alerts = [alert for alert in alerts if alert.content_id == content_id]
        
        # Filter by severity
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Filter by resolution status
        if unresolved_only:
            alerts = [alert for alert in alerts if not alert.resolved]
        
        return alerts
    
    async def resolve_alert(
        self, 
        alert_id: str, 
        resolution_notes: str,
        resolved_by: str
    ) -> bool:
        """Mark alert as resolved"""
        
        try:
            for alert in self.compliance_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    alert.resolution_notes = resolution_notes
                    
                    logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
                    return True
            
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {str(e)}")
            return False
    
    async def _check_for_alerts(
        self, 
        content_id: str, 
        compliance_check: ComplianceCheck
    ) -> None:
        """Check for compliance alerts"""
        
        try:
            license_info = compliance_check.license_info
            
            # License expiration alert
            if license_info.expiration_date:
                days_until_expiration = (license_info.expiration_date - datetime.utcnow()).days
                
                if days_until_expiration <= 7 and days_until_expiration > 0:
                    alert = ComplianceAlert(
                        content_id=content_id,
                        alert_type="expiration",
                        severity=ComplianceRisk.HIGH,
                        title="License Expiring Soon",
                        description=f"License expires in {days_until_expiration} days",
                        action_required=["Renew license", "Plan content removal"],
                        deadline=license_info.expiration_date,
                        responsible_party=license_info.licensee
                    )
                    self.compliance_alerts.append(alert)
                
                elif days_until_expiration <= 0:
                    alert = ComplianceAlert(
                        content_id=content_id,
                        alert_type="expiration",
                        severity=ComplianceRisk.CRITICAL,
                        title="License Expired",
                        description="License has expired - immediate action required",
                        action_required=["Cease usage immediately", "Remove content", "Renew license"],
                        deadline=datetime.utcnow(),
                        responsible_party=license_info.licensee
                    )
                    self.compliance_alerts.append(alert)
            
            # Compliance violation alert
            if compliance_check.violations:
                alert = ComplianceAlert(
                    content_id=content_id,
                    alert_type="violation",
                    severity=compliance_check.risk_level,
                    title="License Compliance Violation",
                    description=f"{len(compliance_check.violations)} violations detected",
                    action_required=compliance_check.requirements,
                    deadline=datetime.utcnow() + timedelta(days=3),
                    responsible_party=compliance_check.intended_usage.user_id
                )
                self.compliance_alerts.append(alert)
            
            # Attribution missing alert
            if compliance_check.license_info.attribution_required and not compliance_check.intended_usage.attribution_provided:
                alert = ComplianceAlert(
                    content_id=content_id,
                    alert_type="attribution_missing",
                    severity=ComplianceRisk.MEDIUM,
                    title="Attribution Required",
                    description="Content requires attribution but none provided",
                    action_required=["Add proper attribution", "Update content display"],
                    deadline=datetime.utcnow() + timedelta(days=7),
                    responsible_party=compliance_check.intended_usage.user_id
                )
                self.compliance_alerts.append(alert)
            
            # Payment due alert
            if license_info.payment_required and not compliance_check.intended_usage.payment_made:
                alert = ComplianceAlert(
                    content_id=content_id,
                    alert_type="payment_due",
                    severity=ComplianceRisk.HIGH,
                    title="License Payment Required",
                    description=f"Payment of {license_info.payment_amount} {license_info.payment_currency} is due",
                    action_required=["Complete license payment", "Obtain payment receipt"],
                    deadline=datetime.utcnow() + timedelta(days=1),
                    responsible_party=license_info.licensee
                )
                self.compliance_alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Alert generation failed for {content_id}: {str(e)}")
    
    async def generate_compliance_report(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_content_monitored": len(self.monitored_content),
                    "compliant_content": 0,
                    "non_compliant_content": 0,
                    "high_risk_content": 0,
                    "total_alerts": len(self.compliance_alerts),
                    "unresolved_alerts": len([a for a in self.compliance_alerts if not a.resolved])
                },
                "compliance_status_breakdown": {},
                "risk_level_breakdown": {},
                "license_type_breakdown": {},
                "violation_analysis": {},
                "recommendations": []
            }
            
            # Analyze monitored content
            for content_id, config in self.monitored_content.items():
                last_check = config["last_check"]
                
                # Status breakdown
                status = last_check.compliance_status.value
                report["compliance_status_breakdown"][status] = report["compliance_status_breakdown"].get(status, 0) + 1
                
                if last_check.compliance_status == ComplianceStatus.COMPLIANT:
                    report["summary"]["compliant_content"] += 1
                else:
                    report["summary"]["non_compliant_content"] += 1
                
                # Risk breakdown
                risk = last_check.risk_level.value
                report["risk_level_breakdown"][risk] = report["risk_level_breakdown"].get(risk, 0) + 1
                
                if last_check.risk_level in [ComplianceRisk.HIGH, ComplianceRisk.CRITICAL]:
                    report["summary"]["high_risk_content"] += 1
                
                # License type breakdown
                license_type = last_check.license_info.license_type.value
                report["license_type_breakdown"][license_type] = report["license_type_breakdown"].get(license_type, 0) + 1
                
                # Violation analysis
                for violation in last_check.violations:
                    for keyword in ["attribution", "commercial", "permission", "payment", "expired"]:
                        if keyword in violation.lower():
                            report["violation_analysis"][keyword] = report["violation_analysis"].get(keyword, 0) + 1
                            break
            
            # Generate recommendations
            if report["summary"]["high_risk_content"] > 0:
                report["recommendations"].append("Immediate review required for high-risk content")
            
            if report["summary"]["unresolved_alerts"] > 0:
                report["recommendations"].append(f"Address {report['summary']['unresolved_alerts']} unresolved alerts")
            
            if report["violation_analysis"].get("attribution", 0) > 0:
                report["recommendations"].append("Implement automated attribution checking")
            
            if report["violation_analysis"].get("expired", 0) > 0:
                report["recommendations"].append("Set up proactive license renewal reminders")
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {str(e)}")
            return {"error": str(e)}


class LicenseComplianceMonitor:
    """Main license compliance monitoring system"""
    
    def __init__(self):
        self.analyzer = LicenseComplianceAnalyzer()
        self.monitor = ComplianceMonitor()
        
    async def check_usage_compliance(
        self,
        content_id: str,
        license_info: LicenseInfo,
        intended_usage: ContentUsage
    ) -> ComplianceCheck:
        """Check compliance for specific usage"""
        return await self.analyzer.analyze_compliance(license_info, intended_usage)
    
    async def setup_monitoring(
        self,
        content_id: str,
        license_info: LicenseInfo,
        usage_info: ContentUsage
    ) -> Dict[str, Any]:
        """Setup continuous compliance monitoring"""
        return await self.monitor.add_content_monitoring(content_id, license_info, usage_info)
    
    async def get_compliance_status(self, content_id: str) -> Optional[ComplianceCheck]:
        """Get current compliance status"""
        return await self.monitor.check_compliance_status(content_id)
    
    async def get_alerts(
        self,
        content_id: Optional[str] = None,
        severity: Optional[ComplianceRisk] = None
    ) -> List[ComplianceAlert]:
        """Get compliance alerts"""
        return await self.monitor.get_compliance_alerts(content_id, severity)
    
    async def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        return await self.monitor.generate_compliance_report(start_date, end_date)


# Factory function for easy usage
async def check_license_compliance(
    content_id: str,
    license_type: LicenseType,
    usage_type: UsageType,
    commercial_use: bool = False,
    attribution_provided: bool = False,
    payment_made: bool = False,
    user_id: str = "",
    **kwargs
) -> ComplianceCheck:
    """Convenience function for license compliance checking"""
    
    monitor = LicenseComplianceMonitor()
    
    # Create license info
    license_info = LicenseInfo(
        license_type=license_type,
        commercial_use_allowed=commercial_use,
        attribution_required=license_type.value.startswith("cc_") and license_type != LicenseType.CREATIVE_COMMONS_ZERO,
        payment_required=kwargs.get("payment_required", False),
        **{k: v for k, v in kwargs.items() if k in LicenseInfo.__fields__}
    )
    
    # Create usage info
    usage_info = ContentUsage(
        content_id=content_id,
        usage_type=usage_type,
        user_id=user_id,
        attribution_provided=attribution_provided,
        payment_made=payment_made,
        commercial_value=kwargs.get("commercial_value"),
        **{k: v for k, v in kwargs.items() if k in ContentUsage.__fields__}
    )
    
    return await monitor.check_usage_compliance(content_id, license_info, usage_info)


# Example usage
if __name__ == "__main__":
    async def demo():
        # Demo license compliance check
        result = await check_license_compliance(
            content_id="demo_content_123",
            license_type=LicenseType.CREATIVE_COMMONS_BY,
            usage_type=UsageType.COMMERCIAL_USE,
            commercial_use=True,
            attribution_provided=True,
            user_id="user_456",
            platform="instagram",
            commercial_value=500.0
        )
        
        print(f"Compliance Status: {result.compliance_status}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Compliance Score: {result.compliance_score:.2f}")
        print(f"Violations: {result.violations}")
        print(f"Recommendations: {result.recommendations}")
    
    asyncio.run(demo())