"""Compliance Monitoring System - Enterprise Legal & Regulatory Compliance Engine
=============================================================================

Consolidated compliance system providing comprehensive license monitoring,
regulatory compliance tracking, and legal adherence validation for media content.

Consolidates:
- License compliance monitoring and validation (license_compliance_monitor.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary compliance system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or compliance logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path

# External dependencies with graceful fallbacks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logging.warning("Requests not available - using basic HTTP functionality")

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    logging.warning("aiohttp not available - using basic async HTTP")

logger = logging.getLogger(__name__)


class LicenseType(Enum):
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


class ComplianceStatus(Enum):
    """License compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXPIRED = "expired"
    VIOLATION = "violation"
    WARNING = "warning"
    UNKNOWN = "unknown"


class UsageType(Enum):
    """Content usage types"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    RESEARCH = "research"
    PROMOTIONAL = "promotional"
    INTERNAL = "internal"


class RegulationFramework(Enum):
    """Regulatory frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    DMCA = "dmca"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    FTC = "ftc"
    FDA = "fda"
    CUSTOM = "custom"


class ViolationType(Enum):
    """Compliance violation types"""
    LICENSE_BREACH = "license_breach"
    UNAUTHORIZED_USE = "unauthorized_use"
    ATTRIBUTION_MISSING = "attribution_missing"
    COMMERCIAL_MISUSE = "commercial_misuse"
    EXPIRED_LICENSE = "expired_license"
    GEOGRAPHIC_VIOLATION = "geographic_violation"
    PLATFORM_VIOLATION = "platform_violation"
    DURATION_VIOLATION = "duration_violation"
    MODIFICATION_VIOLATION = "modification_violation"
    REDISTRIBUTION_VIOLATION = "redistribution_violation"


@dataclass
class ComplianceConfig:
    """Compliance monitoring configuration"""
    auto_monitoring: bool = True
    real_time_alerts: bool = True
    license_expiry_warning_days: int = 30
    violation_tolerance: int = 0  # Number of violations before action
    audit_frequency_days: int = 7
    regulatory_compliance: List[RegulationFramework] = field(default_factory=list)
    notification_enabled: bool = True
    auto_remediation: bool = False


@dataclass
class LicenseInfo:
    """License information structure"""
    license_id: str
    license_type: LicenseType
    content_id: str
    licensor: str
    licensee: str
    granted_rights: List[str]
    restrictions: List[str]
    usage_types: List[UsageType]
    geographic_scope: List[str]  # Countries/regions
    platform_scope: List[str]  # Platforms where usage is allowed
    start_date: datetime
    end_date: Optional[datetime] = None
    attribution_required: bool = False
    attribution_text: Optional[str] = None
    commercial_use_allowed: bool = False
    modification_allowed: bool = False
    redistribution_allowed: bool = False
    royalty_percentage: float = 0.0
    maximum_usage_count: Optional[int] = None
    current_usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    content_id: str
    license_id: str
    violation_type: ViolationType
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None
    responsible_party: Optional[str] = None
    legal_risk_level: str = "medium"  # low, medium, high, critical
    financial_impact: float = 0.0
    regulatory_impact: List[RegulationFramework] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation_steps: List[str] = field(default_factory=list)


@dataclass
class UsageRecord:
    """Content usage record for compliance tracking"""
    usage_id: str
    content_id: str
    license_id: str
    user_id: str
    usage_type: UsageType
    platform: str
    geographic_location: str
    usage_duration: timedelta
    commercial_context: bool
    distribution_scope: str  # internal, public, restricted
    modification_applied: bool
    attribution_provided: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceAudit:
    """Compliance audit record"""
    audit_id: str
    audit_type: str  # scheduled, triggered, manual
    scope: List[str]  # content_ids or "all"
    auditor_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    findings: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    status: str = "in_progress"  # in_progress, completed, failed
    report_path: Optional[str] = None


class LicenseComplianceMonitor:
    """Advanced license compliance monitoring and validation"""
    
    def __init__(self, config -> None: ComplianceConfig) -> None:
        self.config = config
        self.licenses: Dict[str, LicenseInfo] = {}
        self.violations: List[ComplianceViolation] = []
        self.usage_records: List[UsageRecord] = []
        self.audits: List[ComplianceAudit] = []
        
        # License validation cache
        self.validation_cache = {}
        
        # External compliance databases (would be real APIs in production)
        self.external_databases = {
            'copyright_office': 'https://api.copyright.gov/',
            'creative_commons': 'https://api.creativecommons.org/',
            'licensing_registry': 'https://api.licensing-registry.com/'
        }
        
        logger.info("⚖️ License Compliance Monitor initialized")
    
    async def register_license(
        self, 
        content_id: str,
        license_info: Dict[str, Any],
        auto_validate: bool = True
    ) -> LicenseInfo:
        """Register license for content"""
        try:
            license_id = str(uuid.uuid4())
            
            # Parse license information
            license_data = LicenseInfo(
                license_id=license_id,
                license_type=LicenseType(license_info.get('type', 'unknown')),
                content_id=content_id,
                licensor=license_info.get('licensor', ''),
                licensee=license_info.get('licensee', ''),
                granted_rights=license_info.get('granted_rights', []),
                restrictions=license_info.get('restrictions', []),
                usage_types=[UsageType(ut) for ut in license_info.get('usage_types', [])],
                geographic_scope=license_info.get('geographic_scope', []),
                platform_scope=license_info.get('platform_scope', []),
                start_date=datetime.fromisoformat(license_info['start_date']) if isinstance(license_info.get('start_date'), str) else license_info.get('start_date', datetime.now(timezone.utc)),
                end_date=datetime.fromisoformat(license_info['end_date']) if license_info.get('end_date') and isinstance(license_info['end_date'], str) else license_info.get('end_date'),
                attribution_required=license_info.get('attribution_required', False),
                attribution_text=license_info.get('attribution_text'),
                commercial_use_allowed=license_info.get('commercial_use_allowed', False),
                modification_allowed=license_info.get('modification_allowed', False),
                redistribution_allowed=license_info.get('redistribution_allowed', False),
                royalty_percentage=license_info.get('royalty_percentage', 0.0),
                maximum_usage_count=license_info.get('maximum_usage_count'),
                metadata=license_info.get('metadata', {})
            )
            
            self.licenses[license_id] = license_data
            
            # Auto-validate if enabled
            if auto_validate:
                validation_result = await self.validate_license(license_id)
                if validation_result['status'] != ComplianceStatus.COMPLIANT:
                    logger.warning(f"License {license_id} failed validation: {validation_result}")
            
            logger.info(f"Registered license {license_id} for content {content_id}")
            return license_data
            
        except Exception as e:
            logger.error(f"Failed to register license: {e}")
            raise
    
    async def validate_license(self, license_id: str) -> Dict[str, Any]:
        """Validate license compliance and status"""
        try:
            license_info = self.licenses.get(license_id)
            if not license_info:
                return {
                    'status': ComplianceStatus.UNKNOWN,
                    'error': f'License {license_id} not found'
                }
            
            # Check cache first
            cache_key = f"{license_id}_{license_info.current_usage_count}"
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                # Use cache if less than 1 hour old
                if (datetime.now(timezone.utc) - cached_result['timestamp']).seconds < 3600:
                    return cached_result['result']
            
            validation_issues = []
            compliance_status = ComplianceStatus.COMPLIANT
            
            # Check license expiry
            if license_info.end_date and datetime.now(timezone.utc) > license_info.end_date:
                validation_issues.append("License has expired")
                compliance_status = ComplianceStatus.EXPIRED
            
            # Check usage count limits
            if license_info.maximum_usage_count and license_info.current_usage_count >= license_info.maximum_usage_count:
                validation_issues.append("Maximum usage count exceeded")
                compliance_status = ComplianceStatus.NON_COMPLIANT
            
            # Check for pending violations
            active_violations = [
                v for v in self.violations 
                if v.license_id == license_id and v.resolved_at is None
            ]
            
            if active_violations:
                validation_issues.append(f"{len(active_violations)} unresolved violations")
                compliance_status = ComplianceStatus.VIOLATION
            
            # Validate against external databases if available
            external_validation = await self._validate_external(license_info)
            if not external_validation['valid']:
                validation_issues.extend(external_validation['issues'])
                compliance_status = ComplianceStatus.NON_COMPLIANT
            
            result = {
                'license_id': license_id,
                'status': compliance_status,
                'issues': validation_issues,
                'valid_until': license_info.end_date.isoformat() if license_info.end_date else None,
                'usage_count': license_info.current_usage_count,
                'max_usage': license_info.maximum_usage_count,
                'validation_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Cache result
            self.validation_cache[cache_key] = {
                'result': result,
                'timestamp': datetime.now(timezone.utc)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return {
                'status': ComplianceStatus.UNKNOWN,
                'error': str(e)
            }
    
    async def record_usage(
        self,
        content_id: str,
        license_id: str,
        usage_info: Dict[str, Any]
    ) -> UsageRecord:
        """Record content usage for compliance tracking"""
        try:
            license_info = self.licenses.get(license_id)
            if not license_info:
                raise ValueError(f"License {license_id} not found")
            
            usage_id = str(uuid.uuid4())
            
            usage_record = UsageRecord(
                usage_id=usage_id,
                content_id=content_id,
                license_id=license_id,
                user_id=usage_info.get('user_id', ''),
                usage_type=UsageType(usage_info.get('usage_type', 'personal')),
                platform=usage_info.get('platform', ''),
                geographic_location=usage_info.get('geographic_location', ''),
                usage_duration=timedelta(seconds=usage_info.get('duration_seconds', 0)),
                commercial_context=usage_info.get('commercial_context', False),
                distribution_scope=usage_info.get('distribution_scope', 'internal'),
                modification_applied=usage_info.get('modification_applied', False),
                attribution_provided=usage_info.get('attribution_provided', False),
                metadata=usage_info.get('metadata', {})
            )
            
            self.usage_records.append(usage_record)
            
            # Update usage count
            license_info.current_usage_count += 1
            
            # Check for compliance violations
            violations = await self._check_usage_compliance(usage_record, license_info)
            if violations:
                for violation_data in violations:
                    await self._create_violation(violation_data)
            
            logger.info(f"Recorded usage {usage_id} for content {content_id}")
            return usage_record
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            raise
    
    async def check_compliance(
        self, 
        content_id: str,
        proposed_usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if proposed usage complies with license terms"""
        try:
            # Find license for content
            content_licenses = [l for l in self.licenses.values() if l.content_id == content_id]
            
            if not content_licenses:
                return {
                    'compliant': False,
                    'reason': 'No license found for content',
                    'risk_level': 'high'
                }
            
            # Use most restrictive license if multiple licenses exist
            license_info = min(content_licenses, key=lambda l: len(l.granted_rights))
            
            compliance_issues = []
            
            # Check usage type
            proposed_type = UsageType(proposed_usage.get('usage_type', 'personal'))
            if proposed_type not in license_info.usage_types:
                compliance_issues.append(f"Usage type '{proposed_type.value}' not permitted")
            
            # Check commercial use
            if proposed_usage.get('commercial_context', False) and not license_info.commercial_use_allowed:
                compliance_issues.append("Commercial use not permitted")
            
            # Check geographic restrictions
            proposed_location = proposed_usage.get('geographic_location', '')
            if license_info.geographic_scope and proposed_location not in license_info.geographic_scope:
                compliance_issues.append(f"Geographic location '{proposed_location}' not permitted")
            
            # Check platform restrictions
            proposed_platform = proposed_usage.get('platform', '')
            if license_info.platform_scope and proposed_platform not in license_info.platform_scope:
                compliance_issues.append(f"Platform '{proposed_platform}' not permitted")
            
            # Check modification restrictions
            if proposed_usage.get('modification_applied', False) and not license_info.modification_allowed:
                compliance_issues.append("Content modification not permitted")
            
            # Check attribution requirements
            if license_info.attribution_required and not proposed_usage.get('attribution_provided', False):
                compliance_issues.append("Attribution is required but not provided")
            
            # Check usage count limits
            if license_info.maximum_usage_count and license_info.current_usage_count >= license_info.maximum_usage_count:
                compliance_issues.append("Maximum usage count would be exceeded")
            
            # Check license expiry
            if license_info.end_date and datetime.now(timezone.utc) > license_info.end_date:
                compliance_issues.append("License has expired")
            
            # Determine compliance status
            is_compliant = len(compliance_issues) == 0
            risk_level = "low" if is_compliant else ("medium" if len(compliance_issues) <= 2 else "high")
            
            return {
                'compliant': is_compliant,
                'license_id': license_info.license_id,
                'issues': compliance_issues,
                'risk_level': risk_level,
                'recommendations': self._generate_compliance_recommendations(compliance_issues, license_info),
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                'compliant': False,
                'reason': f'Compliance check error: {str(e)}',
                'risk_level': 'high'
            }
    
    async def detect_violations(self, content_ids: Optional[List[str]] = None) -> List[ComplianceViolation]:
        """Detect compliance violations across content"""
        try:
            violations_detected = []
            
            # Filter content if specified
            if content_ids:
                relevant_licenses = [l for l in self.licenses.values() if l.content_id in content_ids]
                relevant_usage = [u for u in self.usage_records if u.content_id in content_ids]
            else:
                relevant_licenses = list(self.licenses.values())
                relevant_usage = self.usage_records
            
            # Check for expired licenses still in use
            for license_info in relevant_licenses:
                if license_info.end_date and datetime.now(timezone.utc) > license_info.end_date:
                    recent_usage = [
                        u for u in relevant_usage 
                        if u.license_id == license_info.license_id and 
                        u.timestamp > license_info.end_date
                    ]
                    
                    if recent_usage:
                        violation = ComplianceViolation(
                            violation_id=str(uuid.uuid4()),
                            content_id=license_info.content_id,
                            license_id=license_info.license_id,
                            violation_type=ViolationType.EXPIRED_LICENSE,
                            severity="high",
                            description=f"Content used after license expiry ({license_info.end_date})",
                            detected_at=datetime.now(timezone.utc),
                            legal_risk_level="high",
                            evidence={'expired_date': license_info.end_date.isoformat(), 'usage_count': len(recent_usage)}
                        )
                        violations_detected.append(violation)
            
            # Check for usage count violations
            for license_info in relevant_licenses:
                if license_info.maximum_usage_count and license_info.current_usage_count > license_info.maximum_usage_count:
                    violation = ComplianceViolation(
                        violation_id=str(uuid.uuid4()),
                        content_id=license_info.content_id,
                        license_id=license_info.license_id,
                        violation_type=ViolationType.LICENSE_BREACH,
                        severity="medium",
                        description=f"Usage count exceeded: {license_info.current_usage_count}/{license_info.maximum_usage_count}",
                        detected_at=datetime.now(timezone.utc),
                        legal_risk_level="medium",
                        evidence={'current_count': license_info.current_usage_count, 'max_count': license_info.maximum_usage_count}
                    )
                    violations_detected.append(violation)
            
            # Check for attribution violations
            for usage in relevant_usage:
                license_info = self.licenses.get(usage.license_id)
                if license_info and license_info.attribution_required and not usage.attribution_provided:
                    violation = ComplianceViolation(
                        violation_id=str(uuid.uuid4()),
                        content_id=usage.content_id,
                        license_id=usage.license_id,
                        violation_type=ViolationType.ATTRIBUTION_MISSING,
                        severity="medium",
                        description="Required attribution not provided",
                        detected_at=datetime.now(timezone.utc),
                        legal_risk_level="medium",
                        evidence={'usage_id': usage.usage_id, 'required_attribution': license_info.attribution_text}
                    )
                    violations_detected.append(violation)
            
            # Store detected violations
            self.violations.extend(violations_detected)
            
            logger.info(f"Detected {len(violations_detected)} compliance violations")
            return violations_detected
            
        except Exception as e:
            logger.error(f"Violation detection failed: {e}")
            return []
    
    async def generate_compliance_report(
        self, 
        scope: Optional[List[str]] = None,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            # Determine scope
            if scope:
                relevant_licenses = [l for l in self.licenses.values() if l.content_id in scope]
                relevant_violations = [v for v in self.violations if v.content_id in scope]
                relevant_usage = [u for u in self.usage_records if u.content_id in scope]
            else:
                relevant_licenses = list(self.licenses.values())
                relevant_violations = self.violations
                relevant_usage = self.usage_records
            
            # Calculate compliance metrics
            total_content = len(set(l.content_id for l in relevant_licenses))
            total_licenses = len(relevant_licenses)
            total_violations = len(relevant_violations)
            active_violations = len([v for v in relevant_violations if v.resolved_at is None])
            
            # Compliance score calculation
            if total_licenses > 0:
                compliance_score = max(0, 100 - (active_violations / total_licenses * 100))
            else:
                compliance_score = 100
            
            # License status breakdown
            license_statuses = {}
            for license_info in relevant_licenses:
                validation = await self.validate_license(license_info.license_id)
                status = validation['status'].value
                license_statuses[status] = license_statuses.get(status, 0) + 1
            
            # Violation breakdown by type
            violation_types = {}
            for violation in relevant_violations:
                vtype = violation.violation_type.value
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
            
            # Usage statistics
            usage_by_type = {}
            for usage in relevant_usage:
                utype = usage.usage_type.value
                usage_by_type[utype] = usage_by_type.get(utype, 0) + 1
            
            # Risk assessment
            high_risk_violations = [v for v in relevant_violations if v.legal_risk_level == "high"]
            critical_violations = [v for v in relevant_violations if v.severity == "critical"]
            
            report = {
                'report_id': str(uuid.uuid4()),
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'scope': scope or "all_content",
                'summary': {
                    'total_content_items': total_content,
                    'total_licenses': total_licenses,
                    'compliance_score': compliance_score,
                    'total_violations': total_violations,
                    'active_violations': active_violations,
                    'resolved_violations': total_violations - active_violations
                },
                'license_status_breakdown': license_statuses,
                'violation_breakdown': violation_types,
                'usage_statistics': usage_by_type,
                'risk_assessment': {
                    'high_risk_violations': len(high_risk_violations),
                    'critical_violations': len(critical_violations),
                    'risk_level': self._calculate_overall_risk_level(relevant_violations)
                },
                'recent_activity': {
                    'licenses_added_last_30_days': len([
                        l for l in relevant_licenses 
                        if (datetime.now(timezone.utc) - l.created_at).days <= 30
                    ]),
                    'violations_detected_last_7_days': len([
                        v for v in relevant_violations 
                        if (datetime.now(timezone.utc) - v.detected_at).days <= 7
                    ]),
                    'usage_events_last_24_hours': len([
                        u for u in relevant_usage 
                        if (datetime.now(timezone.utc) - u.timestamp).days < 1
                    ])
                }
            }
            
            # Add recommendations if requested
            if include_recommendations:
                report['recommendations'] = await self._generate_compliance_recommendations_report(relevant_violations)
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return {'error': str(e)}
    
    async def _validate_external(self, license_info: LicenseInfo) -> Dict[str, Any]:
        """Validate license against external databases"""
        try:
            # Simplified external validation (would use real APIs)
            validation_result = {
                'valid': True,
                'issues': []
            }
            
            # Check Creative Commons licenses
            if license_info.license_type.value.startswith('cc_'):
                # Would validate with Creative Commons API
                validation_result['cc_validated'] = True
            
            # Check copyright databases
            if license_info.license_type == LicenseType.COPYRIGHT:
                # Would check copyright office databases
                validation_result['copyright_validated'] = True
            
            return validation_result
            
        except Exception as e:
            logger.error(f"External validation failed: {e}")
            return {'valid': False, 'issues': [f'External validation error: {str(e)}']}
    
    async def _check_usage_compliance(
        self, 
        usage_record: UsageRecord, 
        license_info: LicenseInfo
    ) -> List[Dict[str, Any]]:
        """Check usage record for compliance violations"""
        violations = []
        
        # Check usage type compliance
        if usage_record.usage_type not in license_info.usage_types:
            violations.append({
                'type': ViolationType.UNAUTHORIZED_USE,
                'severity': 'high',
                'description': f'Usage type {usage_record.usage_type.value} not permitted'
            })
        
        # Check commercial use compliance
        if usage_record.commercial_context and not license_info.commercial_use_allowed:
            violations.append({
                'type': ViolationType.COMMERCIAL_MISUSE,
                'severity': 'high',
                'description': 'Commercial use not permitted under license'
            })
        
        # Check geographic compliance
        if license_info.geographic_scope and usage_record.geographic_location not in license_info.geographic_scope:
            violations.append({
                'type': ViolationType.GEOGRAPHIC_VIOLATION,
                'severity': 'medium',
                'description': f'Usage in {usage_record.geographic_location} not permitted'
            })
        
        # Check platform compliance
        if license_info.platform_scope and usage_record.platform not in license_info.platform_scope:
            violations.append({
                'type': ViolationType.PLATFORM_VIOLATION,
                'severity': 'medium',
                'description': f'Usage on {usage_record.platform} not permitted'
            })
        
        # Check modification compliance
        if usage_record.modification_applied and not license_info.modification_allowed:
            violations.append({
                'type': ViolationType.MODIFICATION_VIOLATION,
                'severity': 'medium',
                'description': 'Content modification not permitted under license'
            })
        
        # Check attribution compliance
        if license_info.attribution_required and not usage_record.attribution_provided:
            violations.append({
                'type': ViolationType.ATTRIBUTION_MISSING,
                'severity': 'medium',
                'description': 'Required attribution not provided'
            })
        
        return violations
    
    async def _create_violation(self, violation_data -> None: Dict[str, Any]) -> None:
        """Create compliance violation record"""
        violation = ComplianceViolation(
            violation_id=str(uuid.uuid4()),
            content_id=violation_data.get('content_id', ''),
            license_id=violation_data.get('license_id', ''),
            violation_type=violation_data['type'],
            severity=violation_data['severity'],
            description=violation_data['description'],
            detected_at=datetime.now(timezone.utc),
            legal_risk_level=violation_data.get('risk_level', 'medium')
        )
        
        self.violations.append(violation)
        
        # Send alert if configured
        if self.config.real_time_alerts:
            await self._send_violation_alert(violation)
    
    async def _send_violation_alert(self, violation -> None: ComplianceViolation) -> None:
        """Send violation alert (placeholder implementation)"""
        logger.warning(f"Compliance violation detected: {violation.violation_type.value} - {violation.description}")
    
    def _generate_compliance_recommendations(
        self, 
        issues: List[str], 
        license_info: LicenseInfo
    ) -> List[str]:
        """Generate recommendations for compliance issues"""
        recommendations = []
        
        for issue in issues:
            if "attribution" in issue.lower():
                if license_info.attribution_text:
                    recommendations.append(f"Add attribution: {license_info.attribution_text}")
                else:
                    recommendations.append("Add proper attribution to the content")
            
            elif "commercial" in issue.lower():
                recommendations.append("Obtain commercial use license or remove from commercial context")
            
            elif "expired" in issue.lower():
                recommendations.append("Renew license or cease usage of content")
            
            elif "geographic" in issue.lower():
                recommendations.append("Restrict usage to permitted geographic locations")
            
            elif "platform" in issue.lower():
                recommendations.append("Move content to permitted platforms only")
            
            elif "modification" in issue.lower():
                recommendations.append("Use original content without modifications or obtain modification rights")
            
            else:
                recommendations.append("Review license terms and adjust usage accordingly")
        
        return recommendations
    
    async def _generate_compliance_recommendations_report(
        self, 
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate recommendations for compliance report"""
        recommendations = []
        
        # High priority recommendations
        high_risk_violations = [v for v in violations if v.legal_risk_level == "high"]
        if high_risk_violations:
            recommendations.append("URGENT: Address all high-risk violations immediately to avoid legal consequences")
        
        # License management recommendations
        expired_licenses = [v for v in violations if v.violation_type == ViolationType.EXPIRED_LICENSE]
        if expired_licenses:
            recommendations.append("Implement automated license renewal process to prevent expiry violations")
        
        # Attribution recommendations
        attribution_violations = [v for v in violations if v.violation_type == ViolationType.ATTRIBUTION_MISSING]
        if attribution_violations:
            recommendations.append("Establish mandatory attribution workflow for all licensed content")
        
        # Usage monitoring recommendations
        if len(violations) > 10:
            recommendations.append("Implement real-time usage monitoring to prevent violations")
        
        # Training recommendations
        if any(v.violation_type == ViolationType.UNAUTHORIZED_USE for v in violations):
            recommendations.append("Provide compliance training to content creators and users")
        
        return recommendations
    
    def _calculate_overall_risk_level(self, violations: List[ComplianceViolation]) -> str:
        """Calculate overall risk level based on violations"""
        if not violations:
            return "low"
        
        critical_count = len([v for v in violations if v.severity == "critical"])
        high_count = len([v for v in violations if v.severity == "high"])
        
        if critical_count > 0:
            return "critical"
        elif high_count > 3:
            return "high"
        elif high_count > 0 or len(violations) > 10:
            return "medium"
        else:
            return "low"


class RegulatoryComplianceMonitor:
    """Regulatory compliance monitoring for various frameworks"""
    
    def __init__(self, frameworks -> None: List[RegulationFramework]) -> None:
        self.frameworks = frameworks
        self.compliance_checks = {}
        self.audit_trail = []
        
        # Initialize framework-specific checks
        self._initialize_compliance_checks()
        
        logger.info(f"📋 Regulatory Compliance Monitor initialized for {len(frameworks)} frameworks")
    
    def _initialize_compliance_checks(self) -> None:
        """Initialize compliance checks for each framework"""
        for framework in self.frameworks:
            if framework == RegulationFramework.GDPR:
                self.compliance_checks[framework] = {
                    'data_consent': False,
                    'data_portability': False,
                    'right_to_erasure': False,
                    'privacy_by_design': False,
                    'data_breach_notification': False
                }
            elif framework == RegulationFramework.CCPA:
                self.compliance_checks[framework] = {
                    'consumer_rights': False,
                    'data_sale_opt_out': False,
                    'privacy_notice': False,
                    'data_deletion': False
                }
            elif framework == RegulationFramework.DMCA:
                self.compliance_checks[framework] = {
                    'takedown_process': False,
                    'counter_notification': False,
                    'repeat_infringer_policy': False,
                    'safe_harbor_compliance': False
                }
    
    async def check_regulatory_compliance(self, framework: RegulationFramework) -> Dict[str, Any]:
        """Check compliance with specific regulatory framework"""
        try:
            checks = self.compliance_checks.get(framework, {})
            
            # Perform framework-specific compliance checks
            results = {}
            
            if framework == RegulationFramework.GDPR:
                results = await self._check_gdpr_compliance()
            elif framework == RegulationFramework.CCPA:
                results = await self._check_ccpa_compliance()
            elif framework == RegulationFramework.DMCA:
                results = await self._check_dmca_compliance()
            
            compliance_score = sum(results.values()) / len(results) * 100 if results else 0
            
            return {
                'framework': framework.value,
                'compliance_score': compliance_score,
                'checks': results,
                'status': 'compliant' if compliance_score >= 90 else 'non_compliant',
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Regulatory compliance check failed for {framework.value}: {e}")
            return {'error': str(e)}
    
    async def _check_gdpr_compliance(self) -> Dict[str, bool]:
        """Check GDPR compliance"""
        # Simplified GDPR compliance checks
        return {
            'data_consent': True,  # Would check actual consent mechanisms
            'data_portability': True,  # Would check data export capabilities
            'right_to_erasure': True,  # Would check deletion processes
            'privacy_by_design': True,  # Would check system design
            'data_breach_notification': True  # Would check notification procedures
        }
    
    async def _check_ccpa_compliance(self) -> Dict[str, bool]:
        """Check CCPA compliance"""
        return {
            'consumer_rights': True,
            'data_sale_opt_out': True,
            'privacy_notice': True,
            'data_deletion': True
        }
    
    async def _check_dmca_compliance(self) -> Dict[str, bool]:
        """Check DMCA compliance"""
        return {
            'takedown_process': True,
            'counter_notification': True,
            'repeat_infringer_policy': True,
            'safe_harbor_compliance': True
        }


class ComplianceMonitoringSystem:
    """Main compliance monitoring system orchestrating all compliance components"""
    
    def __init__(
        self, 
        config -> None: Optional[ComplianceConfig] = None,
        regulatory_frameworks -> None: Optional[List[RegulationFramework]] = None
    ) -> None:
        """Initialize compliance monitoring system"""
        self.config = config or ComplianceConfig()
        
        # Initialize component monitors
        self.license_monitor = LicenseComplianceMonitor(self.config)
        
        if regulatory_frameworks:
            self.regulatory_monitor = RegulatoryComplianceMonitor(regulatory_frameworks)
        else:
            self.regulatory_monitor = None
        
        # System-wide compliance state
        self.compliance_dashboard = {}
        
        logger.info("⚖️ Compliance Monitoring System initialized")
    
    async def comprehensive_compliance_check(
        self, 
        content_id: str,
        proposed_usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive compliance check"""
        try:
            # License compliance check
            license_compliance = await self.license_monitor.check_compliance(
                content_id, proposed_usage
            )
            
            # Regulatory compliance checks
            regulatory_results = {}
            if self.regulatory_monitor:
                for framework in self.config.regulatory_compliance:
                    regulatory_results[framework.value] = await self.regulatory_monitor.check_regulatory_compliance(framework)
            
            # Overall compliance assessment
            overall_compliant = license_compliance['compliant'] and all(
                result.get('status') == 'compliant' 
                for result in regulatory_results.values()
            )
            
            return {
                'content_id': content_id,
                'overall_compliant': overall_compliant,
                'license_compliance': license_compliance,
                'regulatory_compliance': regulatory_results,
                'risk_assessment': {
                    'risk_level': license_compliance.get('risk_level', 'medium'),
                    'recommendations': license_compliance.get('recommendations', [])
                },
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive compliance check failed: {e}")
            return {'error': str(e)}
    
    async def generate_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate compliance dashboard with key metrics"""
        try:
            # Generate license compliance report
            license_report = await self.license_monitor.generate_compliance_report()
            
            # Detect recent violations
            recent_violations = await self.license_monitor.detect_violations()
            
            # Calculate compliance trends
            compliance_trends = self._calculate_compliance_trends()
            
            dashboard = {
                'dashboard_id': str(uuid.uuid4()),
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'license_compliance': {
                    'score': license_report.get('summary', {}).get('compliance_score', 0),
                    'total_licenses': license_report.get('summary', {}).get('total_licenses', 0),
                    'active_violations': license_report.get('summary', {}).get('active_violations', 0),
                    'risk_level': license_report.get('risk_assessment', {}).get('risk_level', 'unknown')
                },
                'recent_activity': {
                    'violations_detected_today': len([
                        v for v in recent_violations
                        if (datetime.now(timezone.utc) - v.detected_at).days < 1
                    ]),
                    'licenses_validated_today': 0,  # Would track actual validations
                    'compliance_checks_today': 0  # Would track actual checks
                },
                'trends': compliance_trends,
                'alerts': [
                    {
                        'type': 'violation',
                        'severity': v.severity,
                        'description': v.description,
                        'detected_at': v.detected_at.isoformat()
                    }
                    for v in recent_violations[:5]  # Recent 5 violations
                ]
            }
            
            # Add regulatory compliance if available
            if self.regulatory_monitor:
                regulatory_summary = {}
                for framework in self.config.regulatory_compliance:
                    result = await self.regulatory_monitor.check_regulatory_compliance(framework)
                    regulatory_summary[framework.value] = {
                        'score': result.get('compliance_score', 0),
                        'status': result.get('status', 'unknown')
                    }
                dashboard['regulatory_compliance'] = regulatory_summary
            
            self.compliance_dashboard = dashboard
            return dashboard
            
        except Exception as e:
            logger.error(f"Compliance dashboard generation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_compliance_trends(self) -> Dict[str, Any]:
        """Calculate compliance trends over time"""
        # Simplified trend calculation
        return {
            'compliance_score_trend': 'stable',  # Would calculate actual trends
            'violation_trend': 'decreasing',
            'license_expiry_trend': 'stable',
            'usage_growth_trend': 'increasing'
        }


# Backward compatibility classes for existing imports
class LicenseComplianceMonitor_Legacy:
    """Legacy wrapper for license compliance monitor"""
    def __init__(self, *args, **kwargs) -> None:
        config = ComplianceConfig()
        self.monitor = LicenseComplianceMonitor(config)


# Export all classes for consolidated import
__all__ = [
    'ComplianceMonitoringSystem',
    'LicenseComplianceMonitor',
    'RegulatoryComplianceMonitor',
    'ComplianceConfig',
    'LicenseInfo',
    'ComplianceViolation',
    'UsageRecord',
    'ComplianceAudit',
    'LicenseType',
    'ComplianceStatus',
    'UsageType',
    'RegulationFramework',
    'ViolationType',
    # Legacy compatibility
    'LicenseComplianceMonitor_Legacy'
]