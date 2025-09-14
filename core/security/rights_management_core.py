"""
Rights Management Core - Advanced Digital Rights Management System
================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for managing digital rights, licensing, legal compliance,
and automated rights enforcement across multiple jurisdictions.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import hashlib
import uuid

# Get logger
logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Supported license types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"

class UsageType(Enum):
    """Content usage types"""
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"
    NON_PROFIT = "non_profit"

class ComplianceRegion(Enum):
    """Legal compliance regions"""
    EU_GDPR = "eu_gdpr"
    US_CCPA = "us_ccpa"
    US_DMCA = "us_dmca"
    INTERNATIONAL = "international"
    CUSTOM_REGION = "custom_region"

class RightsStatus(Enum):
    """Rights management status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"

@dataclass
class DigitalRights:
    """Digital rights definition"""
    rights_id: str
    content_id: str
    owner_id: str
    license_type: LicenseType
    usage_types: List[UsageType]
    territory: List[str]
    duration: Optional[timedelta]
    price: float
    currency: str
    restrictions: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: RightsStatus = RightsStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LicenseAgreement:
    """License agreement contract"""
    agreement_id: str
    rights_id: str
    licensee_id: str
    licensor_id: str
    terms: Dict[str, Any]
    royalty_rate: float
    minimum_guarantee: float
    territory: List[str]
    usage_restrictions: Dict[str, Any]
    signed_at: datetime = field(default_factory=datetime.utcnow)
    effective_from: datetime = field(default_factory=datetime.utcnow)
    effective_until: Optional[datetime] = None
    status: str = "active"
    digital_signature: Optional[str] = None

@dataclass
class UsageRecord:
    """Content usage tracking record"""
    usage_id: str
    rights_id: str
    licensee_id: str
    content_id: str
    usage_type: UsageType
    platform: str
    territory: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)
    revenue_generated: float = 0.0
    currency: str = "USD"
    compliance_verified: bool = False

@dataclass
class ComplianceRule:
    """Legal compliance rule"""
    rule_id: str
    regulation_type: ComplianceRegion
    rule_name: str
    description: str
    requirements: List[str]
    enforcement_level: str
    penalty_type: str
    penalty_amount: float
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    automated_check: bool = True

class LicensingEngine:
    """Advanced licensing management engine"""
    
    def __init__(self) -> None:
        self.license_templates = {}
        self.active_licenses = {}
        self.royalty_rates = {}
        
        # Initialize default license templates
        self._initialize_license_templates()
        
        logger.info("Licensing Engine initialized")

    def _initialize_license_templates(self) -> None:
        """Initialize standard license templates"""
        self.license_templates = {
            LicenseType.EXCLUSIVE.value: {
                "name": "Exclusive License",
                "description": "Exclusive rights with full control",
                "default_terms": {
                    "exclusivity": True,
                    "sublicensing_allowed": True,
                    "modification_allowed": True,
                    "resale_allowed": True,
                    "territory": ["worldwide"],
                    "duration": "perpetual"
                },
                "default_royalty_rate": 0.15,
                "minimum_price": 1000
            },
            LicenseType.NON_EXCLUSIVE.value: {
                "name": "Non-Exclusive License",
                "description": "Standard usage rights",
                "default_terms": {
                    "exclusivity": False,
                    "sublicensing_allowed": False,
                    "modification_allowed": False,
                    "resale_allowed": False,
                    "territory": ["specific"],
                    "duration": "limited"
                },
                "default_royalty_rate": 0.05,
                "minimum_price": 10
            },
            LicenseType.ROYALTY_FREE.value: {
                "name": "Royalty-Free License",
                "description": "One-time payment, ongoing usage",
                "default_terms": {
                    "exclusivity": False,
                    "sublicensing_allowed": False,
                    "modification_allowed": True,
                    "resale_allowed": False,
                    "territory": ["worldwide"],
                    "duration": "perpetual"
                },
                "default_royalty_rate": 0.0,
                "minimum_price": 50
            },
            LicenseType.CREATIVE_COMMONS.value: {
                "name": "Creative Commons License",
                "description": "Open license with attribution",
                "default_terms": {
                    "exclusivity": False,
                    "sublicensing_allowed": True,
                    "modification_allowed": True,
                    "resale_allowed": False,
                    "territory": ["worldwide"],
                    "duration": "perpetual",
                    "attribution_required": True
                },
                "default_royalty_rate": 0.0,
                "minimum_price": 0
            }
        }

    async def create_license(self, license_data: Dict[str, Any]) -> str:
        """Create a new license agreement"""
        try:
            license_type = LicenseType(license_data["license_type"])
            template = self.license_templates[license_type.value]
            
            # Generate unique license ID
            license_id = self._generate_license_id()
            
            # Merge template with custom terms
            terms = template["default_terms"].copy()
            terms.update(license_data.get("custom_terms", {}))
            
            # Create license agreement
            agreement = LicenseAgreement(
                agreement_id=license_id,
                rights_id=license_data["rights_id"],
                licensee_id=license_data["licensee_id"],
                licensor_id=license_data["licensor_id"],
                terms=terms,
                royalty_rate=license_data.get("royalty_rate", template["default_royalty_rate"]),
                minimum_guarantee=license_data.get("minimum_guarantee", 0),
                territory=license_data.get("territory", terms["territory"]),
                usage_restrictions=license_data.get("usage_restrictions", {}),
                effective_until=license_data.get("effective_until")
            )
            
            # Generate digital signature
            agreement.digital_signature = self._generate_digital_signature(agreement)
            
            # Store license
            self.active_licenses[license_id] = agreement
            
            logger.info(f"License created: {license_id}")
            return license_id
            
        except Exception as e:
            logger.error(f"Error creating license: {str(e)}")
            raise

    async def validate_license(self, license_id: str) -> Dict[str, Any]:
        """Validate license agreement and terms"""
        try:
            if license_id not in self.active_licenses:
                return {"valid": False, "reason": "License not found"}
            
            agreement = self.active_licenses[license_id]
            
            validation_result = {
                "valid": True,
                "license_id": license_id,
                "status": agreement.status,
                "validation_checks": {}
            }
            
            # Check expiry
            if agreement.effective_until and datetime.utcnow() > agreement.effective_until:
                validation_result["valid"] = False
                validation_result["reason"] = "License expired"
                validation_result["validation_checks"]["expiry"] = False
            else:
                validation_result["validation_checks"]["expiry"] = True
            
            # Check digital signature
            expected_signature = self._generate_digital_signature(agreement)
            if agreement.digital_signature == expected_signature:
                validation_result["validation_checks"]["signature"] = True
            else:
                validation_result["valid"] = False
                validation_result["reason"] = "Invalid digital signature"
                validation_result["validation_checks"]["signature"] = False
            
            # Check status
            if agreement.status != "active":
                validation_result["valid"] = False
                validation_result["reason"] = f"License status: {agreement.status}"
                validation_result["validation_checks"]["status"] = False
            else:
                validation_result["validation_checks"]["status"] = True
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating license: {str(e)}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    async def calculate_royalties(self, usage_record: UsageRecord) -> Dict[str, Any]:
        """Calculate royalties based on usage"""
        try:
            if usage_record.rights_id not in self.active_licenses:
                raise ValueError(f"License not found: {usage_record.rights_id}")
            
            agreement = self.active_licenses[usage_record.rights_id]
            
            # Base royalty calculation
            base_revenue = usage_record.revenue_generated
            royalty_amount = base_revenue * agreement.royalty_rate
            
            # Apply territory multipliers
            territory_multiplier = self._get_territory_multiplier(usage_record.territory)
            adjusted_royalty = royalty_amount * territory_multiplier
            
            # Apply usage type multipliers
            usage_multiplier = self._get_usage_type_multiplier(usage_record.usage_type)
            final_royalty = adjusted_royalty * usage_multiplier
            
            # Ensure minimum guarantee
            if final_royalty < agreement.minimum_guarantee:
                final_royalty = agreement.minimum_guarantee
            
            royalty_calculation = {
                "usage_id": usage_record.usage_id,
                "base_revenue": base_revenue,
                "royalty_rate": agreement.royalty_rate,
                "base_royalty": royalty_amount,
                "territory_multiplier": territory_multiplier,
                "usage_multiplier": usage_multiplier,
                "final_royalty": final_royalty,
                "currency": usage_record.currency,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
            return royalty_calculation
            
        except Exception as e:
            logger.error(f"Error calculating royalties: {str(e)}")
            raise

    def _generate_license_id(self) -> str:
        """Generate unique license ID"""
        return f"license_{uuid.uuid4().hex[:12]}"

    def _generate_digital_signature(self, agreement: LicenseAgreement) -> str:
        """Generate digital signature for license agreement"""
        # Create signature from key agreement data
        signature_data = {
            "agreement_id": agreement.agreement_id,
            "rights_id": agreement.rights_id,
            "licensee_id": agreement.licensee_id,
            "licensor_id": agreement.licensor_id,
            "terms": agreement.terms,
            "signed_at": agreement.signed_at.isoformat()
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()

    def _get_territory_multiplier(self, territory: str) -> float:
        """Get territory-based royalty multiplier"""
        multipliers = {
            "US": 1.0,
            "EU": 0.9,
            "UK": 1.1,
            "CA": 0.95,
            "JP": 1.2,
            "worldwide": 1.0
        }
        return multipliers.get(territory, 1.0)

    def _get_usage_type_multiplier(self, usage_type: UsageType) -> float:
        """Get usage type-based royalty multiplier"""
        multipliers = {
            UsageType.COMMERCIAL: 1.0,
            UsageType.EDITORIAL: 0.8,
            UsageType.PERSONAL: 0.3,
            UsageType.EDUCATIONAL: 0.5,
            UsageType.NON_PROFIT: 0.4
        }
        return multipliers.get(usage_type, 1.0)

class UsageTracker:
    """Advanced usage tracking system"""
    
    def __init__(self) -> None:
        self.usage_records = {}
        self.tracking_rules = {}
        self.compliance_validators = {}
        
        logger.info("Usage Tracker initialized")

    async def track_usage(self, usage_data: Dict[str, Any]) -> str:
        """Track content usage event"""
        try:
            usage_id = f"usage_{uuid.uuid4().hex[:12]}"
            
            usage_record = UsageRecord(
                usage_id=usage_id,
                rights_id=usage_data["rights_id"],
                licensee_id=usage_data["licensee_id"],
                content_id=usage_data["content_id"],
                usage_type=UsageType(usage_data["usage_type"]),
                platform=usage_data["platform"],
                territory=usage_data["territory"],
                metrics=usage_data.get("metrics", {}),
                revenue_generated=usage_data.get("revenue_generated", 0.0),
                currency=usage_data.get("currency", "USD")
            )
            
            # Verify compliance
            usage_record.compliance_verified = await self._verify_usage_compliance(usage_record)
            
            # Store usage record
            self.usage_records[usage_id] = usage_record
            
            logger.info(f"Usage tracked: {usage_id}")
            return usage_id
            
        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}")
            raise

    async def get_usage_analytics(self, rights_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for specific rights"""
        try:
            # Filter usage records for the rights and period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            relevant_records = [
                record for record in self.usage_records.values()
                if record.rights_id == rights_id and start_date <= record.timestamp <= end_date
            ]
            
            if not relevant_records:
                return {
                    "rights_id": rights_id,
                    "period_days": period_days,
                    "total_usage_events": 0,
                    "total_revenue": 0.0,
                    "analytics": {}
                }
            
            # Calculate analytics
            total_revenue = sum(record.revenue_generated for record in relevant_records)
            usage_by_platform = {}
            usage_by_territory = {}
            usage_by_type = {}
            
            for record in relevant_records:
                # Platform analytics
                platform = record.platform
                if platform not in usage_by_platform:
                    usage_by_platform[platform] = {"count": 0, "revenue": 0.0}
                usage_by_platform[platform]["count"] += 1
                usage_by_platform[platform]["revenue"] += record.revenue_generated
                
                # Territory analytics
                territory = record.territory
                if territory not in usage_by_territory:
                    usage_by_territory[territory] = {"count": 0, "revenue": 0.0}
                usage_by_territory[territory]["count"] += 1
                usage_by_territory[territory]["revenue"] += record.revenue_generated
                
                # Usage type analytics
                usage_type = record.usage_type.value
                if usage_type not in usage_by_type:
                    usage_by_type[usage_type] = {"count": 0, "revenue": 0.0}
                usage_by_type[usage_type]["count"] += 1
                usage_by_type[usage_type]["revenue"] += record.revenue_generated
            
            analytics = {
                "rights_id": rights_id,
                "period_days": period_days,
                "total_usage_events": len(relevant_records),
                "total_revenue": total_revenue,
                "average_revenue_per_usage": total_revenue / len(relevant_records) if relevant_records else 0,
                "usage_by_platform": usage_by_platform,
                "usage_by_territory": usage_by_territory,
                "usage_by_type": usage_by_type,
                "compliance_rate": sum(1 for r in relevant_records if r.compliance_verified) / len(relevant_records),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {str(e)}")
            raise

    async def _verify_usage_compliance(self, usage_record: UsageRecord) -> bool:
        """Verify usage compliance with license terms"""
        try:
            # This would integrate with the licensing engine
            # For now, return True as mock implementation
            return True
            
        except Exception as e:
            logger.error(f"Error verifying usage compliance: {str(e)}")
            return False

class ComplianceManager:
    """Legal compliance management system"""
    
    def __init__(self) -> None:
        self.compliance_rules = {}
        self.audit_logs = {}
        self.violation_alerts = {}
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        
        logger.info("Compliance Manager initialized")

    def _initialize_compliance_rules(self) -> None:
        """Initialize standard compliance rules"""
        self.compliance_rules = {
            ComplianceRegion.EU_GDPR.value: {
                "data_protection": {
                    "rule_id": "gdpr_001",
                    "name": "GDPR Data Protection",
                    "requirements": [
                        "explicit_consent_required",
                        "data_portability_support",
                        "right_to_erasure",
                        "privacy_by_design"
                    ],
                    "penalty_amount": 20000000,  # €20M or 4% of annual turnover
                    "automated_check": True
                },
                "cookie_consent": {
                    "rule_id": "gdpr_002",
                    "name": "Cookie Consent",
                    "requirements": [
                        "explicit_consent_for_non_essential_cookies",
                        "granular_consent_options",
                        "easy_withdrawal_mechanism"
                    ],
                    "penalty_amount": 10000000,
                    "automated_check": True
                }
            },
            ComplianceRegion.US_CCPA.value: {
                "consumer_privacy": {
                    "rule_id": "ccpa_001",
                    "name": "CCPA Consumer Privacy",
                    "requirements": [
                        "right_to_know",
                        "right_to_delete",
                        "right_to_opt_out",
                        "non_discrimination"
                    ],
                    "penalty_amount": 7500,  # Up to $7,500 per violation
                    "automated_check": True
                }
            },
            ComplianceRegion.US_DMCA.value: {
                "copyright_protection": {
                    "rule_id": "dmca_001",
                    "name": "DMCA Copyright Protection",
                    "requirements": [
                        "takedown_notice_compliance",
                        "counter_notification_process",
                        "repeat_infringer_policy",
                        "safe_harbor_compliance"
                    ],
                    "penalty_amount": 150000,  # Up to $150k per work
                    "automated_check": True
                }
            }
        }

    async def check_compliance(self, content_data: Dict[str, Any], region: ComplianceRegion) -> Dict[str, Any]:
        """Check compliance for specific content and region"""
        try:
            region_rules = self.compliance_rules.get(region.value, {})
            compliance_results = {
                "content_id": content_data.get("content_id"),
                "region": region.value,
                "overall_compliant": True,
                "compliance_score": 1.0,
                "rule_results": {},
                "violations": [],
                "recommendations": [],
                "checked_at": datetime.utcnow().isoformat()
            }
            
            total_rules = len(region_rules)
            passed_rules = 0
            
            for rule_category, rule_data in region_rules.items():
                rule_result = await self._check_individual_rule(content_data, rule_data)
                compliance_results["rule_results"][rule_category] = rule_result
                
                if rule_result["compliant"]:
                    passed_rules += 1
                else:
                    compliance_results["overall_compliant"] = False
                    compliance_results["violations"].append({
                        "rule_category": rule_category,
                        "rule_id": rule_data["rule_id"],
                        "rule_name": rule_data["name"],
                        "violation_details": rule_result["violations"],
                        "penalty_amount": rule_data["penalty_amount"]
                    })
                    compliance_results["recommendations"].extend(rule_result["recommendations"])
            
            # Calculate compliance score
            if total_rules > 0:
                compliance_results["compliance_score"] = passed_rules / total_rules
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Error checking compliance: {str(e)}")
            raise

    async def _check_individual_rule(self, content_data: Dict[str, Any], rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with individual rule"""
        try:
            # Mock compliance checking - in real implementation, this would
            # integrate with actual compliance verification systems
            
            rule_result = {
                "rule_id": rule_data["rule_id"],
                "rule_name": rule_data["name"],
                "compliant": True,
                "violations": [],
                "recommendations": []
            }
            
            # Check each requirement
            for requirement in rule_data["requirements"]:
                if not self._check_requirement(content_data, requirement):
                    rule_result["compliant"] = False
                    rule_result["violations"].append(requirement)
                    rule_result["recommendations"].append(f"Implement {requirement}")
            
            return rule_result
            
        except Exception as e:
            logger.error(f"Error checking individual rule: {str(e)}")
            return {
                "rule_id": rule_data.get("rule_id", "unknown"),
                "compliant": False,
                "violations": ["check_error"],
                "recommendations": ["Manual compliance review required"]
            }

    def _check_requirement(self, content_data: Dict[str, Any], requirement: str) -> bool:
        """Check specific compliance requirement"""
        # Mock implementation - would integrate with actual compliance systems
        compliance_flags = content_data.get("compliance_flags", {})
        return compliance_flags.get(requirement, False)

    async def generate_compliance_report(self, rights_id: str) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            report = {
                "rights_id": rights_id,
                "report_type": "comprehensive_compliance",
                "generated_at": datetime.utcnow().isoformat(),
                "compliance_summary": {},
                "regional_compliance": {},
                "violations": [],
                "recommendations": [],
                "risk_assessment": {}
            }
            
            # Check compliance across all regions
            for region in ComplianceRegion:
                mock_content_data = {"content_id": rights_id, "compliance_flags": {}}
                region_compliance = await self.check_compliance(mock_content_data, region)
                report["regional_compliance"][region.value] = region_compliance
                
                if not region_compliance["overall_compliant"]:
                    report["violations"].extend(region_compliance["violations"])
                    report["recommendations"].extend(region_compliance["recommendations"])
            
            # Calculate overall compliance
            total_regions = len(ComplianceRegion)
            compliant_regions = sum(1 for rc in report["regional_compliance"].values() if rc["overall_compliant"])
            
            report["compliance_summary"] = {
                "overall_compliance_rate": compliant_regions / total_regions,
                "compliant_regions": compliant_regions,
                "total_regions": total_regions,
                "total_violations": len(report["violations"]),
                "risk_level": "low" if compliant_regions == total_regions else "medium" if compliant_regions > total_regions / 2 else "high"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise

class RightsManagementCore:
    """Main Rights Management Core System"""
    
    def __init__(self) -> None:
        self.version = "2.1.0"
        self.licensing_engine = LicensingEngine()
        self.usage_tracker = UsageTracker()
        self.compliance_manager = ComplianceManager()
        self.digital_rights = {}
        
        logger.info("Rights Management Core initialized")

    async def create_digital_rights(self, rights_data: Dict[str, Any]) -> str:
        """Create new digital rights record"""
        try:
            rights_id = f"rights_{uuid.uuid4().hex[:12]}"
            
            # Calculate expiry date if duration provided
            expires_at = None
            if rights_data.get("duration_days"):
                expires_at = datetime.utcnow() + timedelta(days=rights_data["duration_days"])
            
            digital_rights = DigitalRights(
                rights_id=rights_id,
                content_id=rights_data["content_id"],
                owner_id=rights_data["owner_id"],
                license_type=LicenseType(rights_data["license_type"]),
                usage_types=[UsageType(ut) for ut in rights_data.get("usage_types", [])],
                territory=rights_data.get("territory", ["worldwide"]),
                duration=timedelta(days=rights_data["duration_days"]) if rights_data.get("duration_days") else None,
                price=rights_data.get("price", 0.0),
                currency=rights_data.get("currency", "USD"),
                restrictions=rights_data.get("restrictions", {}),
                expires_at=expires_at,
                metadata=rights_data.get("metadata", {})
            )
            
            self.digital_rights[rights_id] = digital_rights
            
            logger.info(f"Digital rights created: {rights_id}")
            return rights_id
            
        except Exception as e:
            logger.error(f"Error creating digital rights: {str(e)}")
            raise

    async def license_content(self, license_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process content licensing request"""
        try:
            rights_id = license_request["rights_id"]
            
            if rights_id not in self.digital_rights:
                raise ValueError(f"Rights not found: {rights_id}")
            
            rights = self.digital_rights[rights_id]
            
            # Validate licensing request
            validation_result = await self._validate_licensing_request(rights, license_request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "reason": validation_result["reason"],
                    "validation_details": validation_result
                }
            
            # Create license agreement
            license_id = await self.licensing_engine.create_license({
                "rights_id": rights_id,
                "licensee_id": license_request["licensee_id"],
                "licensor_id": rights.owner_id,
                "license_type": rights.license_type.value,
                "royalty_rate": license_request.get("royalty_rate"),
                "territory": license_request.get("territory", rights.territory),
                "custom_terms": license_request.get("custom_terms", {}),
                "usage_restrictions": license_request.get("usage_restrictions", {}),
                "effective_until": license_request.get("effective_until")
            })
            
            return {
                "success": True,
                "license_id": license_id,
                "rights_id": rights_id,
                "terms": await self._get_license_terms(license_id),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error licensing content: {str(e)}")
            raise

    async def track_content_usage(self, usage_data: Dict[str, Any]) -> str:
        """Track content usage for rights management"""
        try:
            usage_id = await self.usage_tracker.track_usage(usage_data)
            
            # Calculate royalties if revenue provided
            if usage_data.get("revenue_generated", 0) > 0:
                usage_record = self.usage_tracker.usage_records[usage_id]
                royalty_calculation = await self.licensing_engine.calculate_royalties(usage_record)
                
                # Store royalty calculation
                usage_record.metadata["royalty_calculation"] = royalty_calculation
            
            return usage_id
            
        except Exception as e:
            logger.error(f"Error tracking content usage: {str(e)}")
            raise

    async def check_rights_compliance(self, content_id: str, region: str = "international") -> Dict[str, Any]:
        """Check rights compliance for content in specific region"""
        try:
            # Find rights for content
            content_rights = [
                rights for rights in self.digital_rights.values()
                if rights.content_id == content_id
            ]
            
            if not content_rights:
                return {
                    "content_id": content_id,
                    "compliant": False,
                    "reason": "No rights found for content"
                }
            
            compliance_results = []
            
            for rights in content_rights:
                # Check region compliance
                region_enum = ComplianceRegion.INTERNATIONAL
                try:
                    region_enum = ComplianceRegion(f"{region.lower()}")
                except ValueError:
                    pass
                
                compliance_result = await self.compliance_manager.check_compliance(
                    {"content_id": content_id, "rights_id": rights.rights_id},
                    region_enum
                )
                compliance_results.append(compliance_result)
            
            # Aggregate results
            overall_compliant = all(result["overall_compliant"] for result in compliance_results)
            
            return {
                "content_id": content_id,
                "region": region,
                "overall_compliant": overall_compliant,
                "rights_checked": len(content_rights),
                "detailed_results": compliance_results,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking rights compliance: {str(e)}")
            raise

    async def generate_rights_report(self, owner_id: str) -> Dict[str, Any]:
        """Generate comprehensive rights management report"""
        try:
            # Get all rights for owner
            owner_rights = [
                rights for rights in self.digital_rights.values()
                if rights.owner_id == owner_id
            ]
            
            if not owner_rights:
                return {
                    "owner_id": owner_id,
                    "total_rights": 0,
                    "report": "No rights found for owner"
                }
            
            # Aggregate statistics
            total_rights = len(owner_rights)
            active_rights = sum(1 for r in owner_rights if r.status == RightsStatus.ACTIVE)
            total_value = sum(r.price for r in owner_rights)
            
            # License type distribution
            license_distribution = {}
            for rights in owner_rights:
                license_type = rights.license_type.value
                license_distribution[license_type] = license_distribution.get(license_type, 0) + 1
            
            # Territory analysis
            territory_coverage = set()
            for rights in owner_rights:
                territory_coverage.update(rights.territory)
            
            # Usage analytics
            usage_analytics = {}
            for rights in owner_rights:
                analytics = await self.usage_tracker.get_usage_analytics(rights.rights_id)
                usage_analytics[rights.rights_id] = analytics
            
            report = {
                "owner_id": owner_id,
                "report_generated_at": datetime.utcnow().isoformat(),
                "rights_summary": {
                    "total_rights": total_rights,
                    "active_rights": active_rights,
                    "inactive_rights": total_rights - active_rights,
                    "total_portfolio_value": total_value,
                    "average_rights_value": total_value / total_rights if total_rights > 0 else 0
                },
                "license_distribution": license_distribution,
                "territory_coverage": list(territory_coverage),
                "usage_analytics": usage_analytics,
                "compliance_status": await self._get_portfolio_compliance_status(owner_rights)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating rights report: {str(e)}")
            raise

    async def _validate_licensing_request(self, rights: DigitalRights, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate licensing request against rights"""
        validation_result = {"valid": True, "issues": []}
        
        # Check if rights are active
        if rights.status != RightsStatus.ACTIVE:
            validation_result["valid"] = False
            validation_result["reason"] = f"Rights status: {rights.status.value}"
            validation_result["issues"].append("rights_not_active")
        
        # Check expiry
        if rights.expires_at and datetime.utcnow() > rights.expires_at:
            validation_result["valid"] = False
            validation_result["reason"] = "Rights expired"
            validation_result["issues"].append("rights_expired")
        
        # Check territory
        requested_territories = request.get("territory", [])
        if requested_territories and not set(requested_territories).issubset(set(rights.territory)):
            validation_result["valid"] = False
            validation_result["reason"] = "Territory not covered by rights"
            validation_result["issues"].append("territory_not_covered")
        
        # Check usage types
        requested_usage_types = request.get("usage_types", [])
        if requested_usage_types:
            rights_usage_types = [ut.value for ut in rights.usage_types]
            if not set(requested_usage_types).issubset(set(rights_usage_types)):
                validation_result["valid"] = False
                validation_result["reason"] = "Usage type not permitted"
                validation_result["issues"].append("usage_type_not_permitted")
        
        return validation_result

    async def _get_license_terms(self, license_id: str) -> Dict[str, Any]:
        """Get license terms for license ID"""
        if license_id in self.licensing_engine.active_licenses:
            agreement = self.licensing_engine.active_licenses[license_id]
            return {
                "license_type": "custom",  # Would be derived from agreement
                "terms": agreement.terms,
                "royalty_rate": agreement.royalty_rate,
                "territory": agreement.territory,
                "effective_period": {
                    "from": agreement.effective_from.isoformat(),
                    "until": agreement.effective_until.isoformat() if agreement.effective_until else None
                }
            }
        return {}

    async def _get_portfolio_compliance_status(self, rights_list: List[DigitalRights]) -> Dict[str, Any]:
        """Get compliance status for rights portfolio"""
        try:
            total_rights = len(rights_list)
            if total_rights == 0:
                return {"compliance_rate": 1.0, "status": "compliant"}
            
            compliant_rights = 0
            compliance_issues = []
            
            for rights in rights_list:
                # Mock compliance check
                is_compliant = rights.status == RightsStatus.ACTIVE and (
                    not rights.expires_at or rights.expires_at > datetime.utcnow()
                )
                
                if is_compliant:
                    compliant_rights += 1
                else:
                    compliance_issues.append({
                        "rights_id": rights.rights_id,
                        "issue": "expired" if rights.expires_at and rights.expires_at <= datetime.utcnow() else "inactive"
                    })
            
            compliance_rate = compliant_rights / total_rights
            status = "compliant" if compliance_rate == 1.0 else "partial" if compliance_rate > 0.5 else "non_compliant"
            
            return {
                "compliance_rate": compliance_rate,
                "status": status,
                "compliant_rights": compliant_rights,
                "total_rights": total_rights,
                "issues": compliance_issues
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio compliance status: {str(e)}")
            return {"compliance_rate": 0.0, "status": "error"}

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics"""
        total_rights = len(self.digital_rights)
        active_licenses = len(self.licensing_engine.active_licenses)
        total_usage_records = len(self.usage_tracker.usage_records)
        
        return {
            "version": self.version,
            "total_digital_rights": total_rights,
            "active_licenses": active_licenses,
            "total_usage_records": total_usage_records,
            "compliance_rules_loaded": len(self.compliance_manager.compliance_rules),
            "system_status": "healthy",
            "last_health_check": datetime.utcnow().isoformat()
        }

# Global instance
rights_management_core = RightsManagementCore()

# Export main functions
__all__ = [
    "LicenseType",
    "UsageType",
    "ComplianceRegion",
    "RightsStatus",
    "DigitalRights",
    "LicenseAgreement",
    "UsageRecord",
    "ComplianceRule",
    "RightsManagementCore",
    "rights_management_core"
]

if __name__ == "__main__":
    logger.info("Rights Management Core module loaded successfully")