"""
Legal Compliance Manager for Monetization
=========================================

Professional compliance management system for content monetization.
Handles DMCA compliance, copyright protection, tax reporting,
legal documentation, and regulatory compliance for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import uuid
import json
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from .revenue_calculator import Currency


class ComplianceType(Enum):
    """Types of compliance requirements"""
    DMCA = "dmca"
    COPYRIGHT = "copyright"
    TAX_REPORTING = "tax_reporting"
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    PLATFORM_POLICIES = "platform_policies"
    INTERNATIONAL_TAX = "international_tax"
    LICENSING = "licensing"
    CONTENT_RATING = "content_rating"


class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    EXEMPTED = "exempted"
    UNKNOWN = "unknown"


class ViolationType(Enum):
    """Types of compliance violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    DMCA_VIOLATION = "dmca_violation"
    TAX_EVASION = "tax_evasion"
    PRIVACY_VIOLATION = "privacy_violation"
    PLATFORM_VIOLATION = "platform_violation"
    LICENSING_VIOLATION = "licensing_violation"
    CONTENT_VIOLATION = "content_violation"


class LegalJurisdiction(Enum):
    """Legal jurisdictions"""
    US = "us"
    EU = "eu"
    DE = "de"
    UK = "uk"
    CA = "ca"
    AU = "au"
    INTERNATIONAL = "international"


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""
    requirement_id: str
    compliance_type: ComplianceType
    jurisdiction: LegalJurisdiction
    title: str
    description: str
    mandatory: bool
    deadline: Optional[datetime]
    documentation_required: List[str]
    verification_method: str
    penalty_description: str
    metadata: Dict[str, Any]


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    check_id: str
    user_id: str
    content_id: Optional[str]
    compliance_type: ComplianceType
    status: ComplianceStatus
    check_date: datetime
    next_check_date: datetime
    findings: List[str]
    violations: List[str]
    recommendations: List[str]
    documentation_status: Dict[str, bool]


@dataclass
class DMCANotice:
    """DMCA takedown notice"""
    notice_id: str
    content_id: str
    claimant_info: Dict[str, str]
    infringement_claim: str
    evidence: List[str]
    takedown_requested: bool
    counter_notice_deadline: datetime
    status: str
    created_at: datetime


@dataclass
class TaxReport:
    """Tax reporting document"""
    report_id: str
    user_id: str
    tax_year: int
    jurisdiction: LegalJurisdiction
    total_revenue: Decimal
    deductible_expenses: Decimal
    taxable_income: Decimal
    tax_owed: Decimal
    payment_records: List[Dict]
    filing_status: str
    deadline: datetime


@dataclass
class ComplianceAudit:
    """Compliance audit report"""
    audit_id: str
    user_id: str
    audit_date: datetime
    compliance_score: float
    requirements_checked: int
    compliant_requirements: int
    violations_found: int
    critical_issues: List[str]
    recommendations: List[str]
    next_audit_date: datetime


class ComplianceManager:
    """
    Professional compliance management system for IA Influencer Agent platform.
    
    Provides comprehensive legal compliance management, DMCA protection,
    tax reporting, and regulatory compliance for content creator monetization.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize ComplianceManager.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.audit_frequency = timedelta(days=90)  # Quarterly audits
        self.dmca_response_deadline = timedelta(days=14)
        
        # Compliance requirements by jurisdiction
        self.compliance_requirements = {
            LegalJurisdiction.EU: [
                ComplianceRequirement(
                    requirement_id="eu_gdpr_consent",
                    compliance_type=ComplianceType.GDPR,
                    jurisdiction=LegalJurisdiction.EU,
                    title="GDPR User Consent",
                    description="Obtain explicit consent for data processing",
                    mandatory=True,
                    deadline=None,
                    documentation_required=["consent_forms", "privacy_policy"],
                    verification_method="audit",
                    penalty_description="Up to 4% of annual revenue or €20M",
                    metadata={"regulation": "GDPR Article 6"}
                ),
                ComplianceRequirement(
                    requirement_id="eu_tax_reporting",
                    compliance_type=ComplianceType.TAX_REPORTING,
                    jurisdiction=LegalJurisdiction.EU,
                    title="EU Tax Reporting",
                    description="Report income and pay taxes in EU member states",
                    mandatory=True,
                    deadline=datetime(2024, 3, 31),
                    documentation_required=["income_statements", "expense_records"],
                    verification_method="tax_authority_review",
                    penalty_description="Fines and interest on unpaid taxes",
                    metadata={"tax_year": 2024}
                )
            ],
            LegalJurisdiction.US: [
                ComplianceRequirement(
                    requirement_id="us_dmca_compliance",
                    compliance_type=ComplianceType.DMCA,
                    jurisdiction=LegalJurisdiction.US,
                    title="DMCA Compliance",
                    description="Implement DMCA takedown procedures",
                    mandatory=True,
                    deadline=None,
                    documentation_required=["dmca_policy", "agent_designation"],
                    verification_method="platform_verification",
                    penalty_description="Loss of safe harbor protection",
                    metadata={"law": "Digital Millennium Copyright Act"}
                )
            ]
        }
        
        # Tax thresholds by jurisdiction
        self.tax_thresholds = {
            LegalJurisdiction.US: Decimal('600.00'),   # 1099 threshold
            LegalJurisdiction.EU: Decimal('1000.00'),  # General threshold
            LegalJurisdiction.DE: Decimal('410.00'),   # Minijob threshold
            LegalJurisdiction.UK: Decimal('1000.00')   # Trading allowance
        }
    
    async def perform_compliance_audit(self, user_id: str) -> ComplianceAudit:
        """
        Perform comprehensive compliance audit for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Compliance audit results
        """



        try:
            # Get user's applicable jurisdictions
            user_jurisdictions = await self._get_user_jurisdictions(user_id)
            
            # Collect all applicable requirements
            applicable_requirements = []
            for jurisdiction in user_jurisdictions:
                requirements = self.compliance_requirements.get(jurisdiction, [])
                applicable_requirements.extend(requirements)
            
            # Check compliance for each requirement
            compliance_checks = []
            compliant_count = 0
            violations = []
            critical_issues = []
            
            for requirement in applicable_requirements:
                check = await self._check_compliance_requirement(user_id, requirement)
                compliance_checks.append(check)
                
                if check.status == ComplianceStatus.COMPLIANT:
                    compliant_count += 1
                elif check.status == ComplianceStatus.NON_COMPLIANT:
                    violations.extend(check.violations)
                    if requirement.mandatory:
                        critical_issues.append(
                            f"Critical: {requirement.title} - {requirement.penalty_description}"
                        )
            
            # Calculate compliance score
            total_requirements = len(applicable_requirements)
            compliance_score = (compliant_count / total_requirements * 100) if total_requirements > 0 else 100
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                user_id, compliance_checks, violations
            )
            
            audit = ComplianceAudit(
                audit_id=str(uuid.uuid4()),
                user_id=user_id,
                audit_date=datetime.utcnow(),
                compliance_score=compliance_score,
                requirements_checked=total_requirements,
                compliant_requirements=compliant_count,
                violations_found=len(violations),
                critical_issues=critical_issues,
                recommendations=recommendations,
                next_audit_date=datetime.utcnow() + self.audit_frequency
            )
            
            # Store audit results
            await self._store_compliance_audit(audit)
            
            # Send notifications if critical issues found
            if critical_issues:
                await self._send_compliance_alerts(user_id, critical_issues)
            
            return audit
            
        except Exception as e:
            self.logger.error(f"Error performing compliance audit: {str(e)}")
            return ComplianceAudit(
                audit_id=str(uuid.uuid4()),
                user_id=user_id,
                audit_date=datetime.utcnow(),
                compliance_score=0.0,
                requirements_checked=0,
                compliant_requirements=0,
                violations_found=0,
                critical_issues=["Audit failed to complete"],
                recommendations=["Contact support for compliance assistance"],
                next_audit_date=datetime.utcnow() + timedelta(days=7)
            )
    
    async def process_dmca_notice(self, content_id: str, notice_data: Dict[str, Any]) -> DMCANotice:
        """
        Process DMCA takedown notice.
        
        Args:
            content_id: Content identifier
            notice_data: DMCA notice information
            
        Returns:
            Processed DMCA notice
        """



        try:
            # Validate DMCA notice
            await self._validate_dmca_notice(notice_data)
            
            # Create DMCA notice record
            notice = DMCANotice(
                notice_id=str(uuid.uuid4()),
                content_id=content_id,
                claimant_info={
                    'name': notice_data.get('claimant_name', ''),
                    'contact': notice_data.get('claimant_contact', ''),
                    'organization': notice_data.get('claimant_organization', '')
                },
                infringement_claim=notice_data.get('infringement_description', ''),
                evidence=notice_data.get('evidence_urls', []),
                takedown_requested=notice_data.get('takedown_requested', True),
                counter_notice_deadline=datetime.utcnow() + self.dmca_response_deadline,
                status='received',
                created_at=datetime.utcnow()
            )
            
            # Store notice
            await self._store_dmca_notice(notice)
            
            # Automatically process if valid
            if await self._is_valid_dmca_notice(notice):
                # Temporarily disable content
                await self._disable_content(content_id, "DMCA takedown")
                
                # Notify content owner
                await self._notify_content_owner_dmca(content_id, notice)
                
                # Update status
                notice.status = 'content_disabled'
                await self._update_dmca_notice(notice)
            
            return notice
            
        except Exception as e:
            self.logger.error(f"Error processing DMCA notice: {str(e)}")
            raise
    
    async def generate_tax_report(self, user_id: str, tax_year: int,
                                jurisdiction: LegalJurisdiction) -> TaxReport:
        """
        Generate tax report for user.
        
        Args:
            user_id: User identifier
            tax_year: Tax reporting year
            jurisdiction: Tax jurisdiction
            
        Returns:
            Generated tax report
        """



        try:
            # Get revenue data for tax year
            start_date = datetime(tax_year, 1, 1)
            end_date = datetime(tax_year, 12, 31)
            
            revenue_data = await self._get_tax_revenue_data(user_id, start_date, end_date)
            
            # Calculate total revenue
            total_revenue = sum(Decimal(str(item['amount'])) for item in revenue_data)
            
            # Get deductible expenses
            expenses = await self._get_deductible_expenses(user_id, start_date, end_date)
            total_expenses = sum(Decimal(str(expense['amount'])) for expense in expenses)
            
            # Calculate taxable income
            taxable_income = total_revenue - total_expenses
            
            # Calculate tax owed (simplified - would use actual tax rates)
            tax_rate = await self._get_tax_rate(jurisdiction, taxable_income)
            tax_owed = taxable_income * tax_rate
            
            # Get payment records
            payment_records = await self._get_tax_payment_records(user_id, tax_year)
            
            # Determine filing deadline
            filing_deadline = await self._get_filing_deadline(jurisdiction, tax_year)
            
            report = TaxReport(
                report_id=str(uuid.uuid4()),
                user_id=user_id,
                tax_year=tax_year,
                jurisdiction=jurisdiction,
                total_revenue=total_revenue,
                deductible_expenses=total_expenses,
                taxable_income=taxable_income,
                tax_owed=tax_owed,
                payment_records=payment_records,
                filing_status='pending',
                deadline=filing_deadline
            )
            
            # Store tax report
            await self._store_tax_report(report)
            
            # Generate tax forms if required
            if total_revenue >= self.tax_thresholds.get(jurisdiction, Decimal('0')):
                await self._generate_tax_forms(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating tax report: {str(e)}")
            raise
    
    async def check_content_compliance(self, content_id: str) -> ComplianceCheck:
        """
        Check compliance for specific content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Content compliance check results
        """



        try:
            # Get content metadata
            content_info = await self._get_content_info(content_id)
            
            findings = []
            violations = []
            recommendations = []
            overall_status = ComplianceStatus.COMPLIANT
            
            # Check copyright compliance
            copyright_check = await self._check_copyright_compliance(content_id, content_info)
            if not copyright_check['compliant']:
                violations.extend(copyright_check['violations'])
                overall_status = ComplianceStatus.NON_COMPLIANT
            
            findings.extend(copyright_check['findings'])
            
            # Check platform policy compliance
            platform_check = await self._check_platform_compliance(content_id, content_info)
            if not platform_check['compliant']:
                violations.extend(platform_check['violations'])
                if overall_status == ComplianceStatus.COMPLIANT:
                    overall_status = ComplianceStatus.NON_COMPLIANT
            
            findings.extend(platform_check['findings'])
            
            # Check content rating compliance
            rating_check = await self._check_content_rating_compliance(content_id, content_info)
            findings.extend(rating_check['findings'])
            
            # Generate recommendations
            if violations:
                recommendations.extend([
                    "Review content for copyright infringement",
                    "Ensure proper licensing for all content elements",
                    "Update content metadata with proper attribution"
                ])
            
            check = ComplianceCheck(
                check_id=str(uuid.uuid4()),
                user_id=content_info.get('user_id', ''),
                content_id=content_id,
                compliance_type=ComplianceType.COPYRIGHT,
                status=overall_status,
                check_date=datetime.utcnow(),
                next_check_date=datetime.utcnow() + timedelta(days=30),
                findings=findings,
                violations=violations,
                recommendations=recommendations,
                documentation_status={
                    'copyright_clearance': bool(content_info.get('copyright_clearance')),
                    'licensing_documentation': bool(content_info.get('license_info')),
                    'attribution_provided': bool(content_info.get('attribution'))
                }
            )
            
            # Store compliance check
            await self._store_compliance_check(check)
            
            return check
            
        except Exception as e:
            self.logger.error(f"Error checking content compliance: {str(e)}")
            return ComplianceCheck(
                check_id=str(uuid.uuid4()),
                user_id='',
                content_id=content_id,
                compliance_type=ComplianceType.COPYRIGHT,
                status=ComplianceStatus.UNKNOWN,
                check_date=datetime.utcnow(),
                next_check_date=datetime.utcnow() + timedelta(days=7),
                findings=["Compliance check failed"],
                violations=["Unable to verify compliance"],
                recommendations=["Retry compliance check"],
                documentation_status={}
            )
    
    async def setup_gdpr_compliance(self, user_id: str) -> bool:
        """
        Setup GDPR compliance for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Setup success status
        """



        try:
            # Create privacy policy
            privacy_policy = await self._generate_privacy_policy(user_id)
            
            # Setup consent management
            consent_system = await self._setup_consent_management(user_id)
            
            # Configure data retention policies
            retention_policies = await self._configure_data_retention(user_id)
            
            # Setup data subject rights handling
            rights_handling = await self._setup_data_subject_rights(user_id)
            
            # Create GDPR documentation
            gdpr_docs = {
                'privacy_policy': privacy_policy,
                'consent_system': consent_system,
                'retention_policies': retention_policies,
                'rights_handling': rights_handling,
                'setup_date': datetime.utcnow().isoformat()
            }
            
            # Store GDPR compliance setup
            await self._store_gdpr_setup(user_id, gdpr_docs)
            
            # Schedule compliance monitoring
            await self._schedule_gdpr_monitoring(user_id)
            
            self.logger.info(f"GDPR compliance setup completed for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up GDPR compliance: {str(e)}")
            return False
    
    async def monitor_compliance_deadlines(self) -> List[Dict[str, Any]]:
        """
        Monitor upcoming compliance deadlines.
        
        Returns:
            List of upcoming deadlines and required actions
        """



        try:
            upcoming_deadlines = []
            
            # Get all active compliance requirements
            active_requirements = await self._get_active_compliance_requirements()
            
            for requirement in active_requirements:
                if requirement.deadline:
                    days_until_deadline = (requirement.deadline - datetime.utcnow()).days
                    
                    if days_until_deadline <= 30:  # Alert for deadlines within 30 days
                        upcoming_deadlines.append({
                            'requirement_id': requirement.requirement_id,
                            'title': requirement.title,
                            'deadline': requirement.deadline.isoformat(),
                            'days_remaining': days_until_deadline,
                            'jurisdiction': requirement.jurisdiction.value,
                            'compliance_type': requirement.compliance_type.value,
                            'mandatory': requirement.mandatory,
                            'penalty': requirement.penalty_description,
                            'urgency': 'critical' if days_until_deadline <= 7 else 
                                     'high' if days_until_deadline <= 14 else 'medium'
                        })
            
            # Sort by urgency and deadline
            upcoming_deadlines.sort(key=lambda x: (x['days_remaining'], x['urgency']))
            
            # Send notifications for critical deadlines
            critical_deadlines = [d for d in upcoming_deadlines if d['urgency'] == 'critical']
            if critical_deadlines:
                await self._send_deadline_alerts(critical_deadlines)
            
            return upcoming_deadlines
            
        except Exception as e:
            self.logger.error(f"Error monitoring compliance deadlines: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _get_user_jurisdictions(self, user_id: str) -> List[LegalJurisdiction]:
        """Get applicable legal jurisdictions for user"""
        # Implementation would determine user's jurisdictions based on
        # location, business operations, revenue sources, etc.
        return [LegalJurisdiction.EU, LegalJurisdiction.DE]  # Placeholder
    
    async def _check_compliance_requirement(self, user_id: str,
                                          requirement: ComplianceRequirement) -> ComplianceCheck:
        """Check specific compliance requirement"""
        # Implementation would check specific requirement
        # Placeholder implementation
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            user_id=user_id,
            content_id=None,
            compliance_type=requirement.compliance_type,
            status=ComplianceStatus.COMPLIANT,
            check_date=datetime.utcnow(),
            next_check_date=datetime.utcnow() + timedelta(days=90),
            findings=[f"Checked {requirement.title}"],
            violations=[],
            recommendations=[],
            documentation_status={}
        )
    
    async def _validate_dmca_notice(self, notice_data: Dict[str, Any]):
        """Validate DMCA notice format and content"""
        required_fields = ['claimant_name', 'claimant_contact', 'infringement_description']
        
        for field in required_fields:
            if not notice_data.get(field):
                raise ValueError(f"Missing required DMCA field: {field}")
    
    async def _get_tax_revenue_data(self, user_id: str, start_date: datetime,
                                  end_date: datetime) -> List[Dict]:
        """Get revenue data for tax reporting"""
        # Implementation would query revenue database
        return []  # Placeholder
    
    async def _get_deductible_expenses(self, user_id: str, start_date: datetime,
                                     end_date: datetime) -> List[Dict]:
        """Get deductible business expenses"""
        # Implementation would query expense records
        return []  # Placeholder
    
    async def _get_tax_rate(self, jurisdiction: LegalJurisdiction,
                          taxable_income: Decimal) -> Decimal:
        """Get applicable tax rate"""
        # Simplified tax rate calculation
        tax_rates = {
            LegalJurisdiction.DE: Decimal('0.25'),  # 25%
            LegalJurisdiction.EU: Decimal('0.20'),  # 20%
            LegalJurisdiction.US: Decimal('0.22')   # 22%
        }
        
        return tax_rates.get(jurisdiction, Decimal('0.20'))
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""



        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""



        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    # Additional helper methods would be implemented here for
    # GDPR setup, content compliance checks, deadline monitoring, etc.
