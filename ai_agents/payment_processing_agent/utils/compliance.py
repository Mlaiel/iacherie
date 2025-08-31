"""
Compliance Management System - Industrial Regulatory Compliance

Comprehensive compliance engine for tax calculations, KYC verification,
AML screening, and regulatory reporting for international payments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .models import PaymentTransaction, TaxConfiguration, PaymentMethod
from .exceptions import ComplianceError, KYCError, AMLError, TaxCalculationError
from .config import PaymentConfig

logger = logging.getLogger(__name__)


class ComplianceStatus(str, Enum):
    """Compliance verification status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    EXPIRED = "expired"


class KYCLevel(str, Enum):
    """KYC verification levels"""
    BASIC = "basic"          # Basic identity verification
    STANDARD = "standard"    # Enhanced verification
    PREMIUM = "premium"      # Full verification with source of funds


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class KYCVerification:
    """KYC verification data structure"""
    creator_id: str
    verification_level: KYCLevel
    status: ComplianceStatus
    documents_verified: List[str] = field(default_factory=list)
    verification_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verification_provider: Optional[str] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AMLScreening:
    """AML screening result data structure"""
    creator_id: str
    screening_date: datetime
    risk_level: RiskLevel
    flagged: bool = False
    flags: List[str] = field(default_factory=list)
    sanctions_check: bool = False
    pep_check: bool = False
    adverse_media: bool = False
    screening_provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaxCalculation:
    """Tax calculation result"""
    creator_id: str
    gross_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    tax_rate: Decimal
    jurisdiction: str
    tax_type: str
    calculation_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """Compliance report data structure"""
    report_type: str
    creator_id: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    jurisdiction: str = "DE"
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceManager:
    """
    Industrial compliance management system.
    
    Handles KYC verification, AML screening, tax calculations,
    regulatory reporting, and compliance monitoring.
    """

    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        db_session: Optional[Session] = None
    ):
        """Initialize compliance manager"""
        self.config = config or PaymentConfig()
        self.db_session = db_session
        
        # Tax rates by jurisdiction (would be loaded from database/external service)
        self.tax_rates = {
            "DE": {"income_tax": Decimal("0.19"), "vat": Decimal("0.19")},
            "US": {"income_tax": Decimal("0.24"), "state_tax": Decimal("0.08")},
            "GB": {"income_tax": Decimal("0.20"), "vat": Decimal("0.20")},
            "FR": {"income_tax": Decimal("0.30"), "vat": Decimal("0.20")},
            "CA": {"income_tax": Decimal("0.26"), "gst": Decimal("0.05")}
        }
        
        # Sanctioned countries and entities (would be loaded from official lists)
        self.sanctioned_countries = {'IR', 'KP', 'SY', 'AF', 'MM'}
        self.sanctioned_entities = set()  # Would be loaded from OFAC/EU lists
        
        # PEP (Politically Exposed Persons) database (would integrate with external service)
        self.pep_database = set()
        
        # Compliance thresholds
        self.thresholds = {
            "kyc_required": Decimal("500.00"),      # KYC required above €500
            "enhanced_dd": Decimal("3000.00"),      # Enhanced due diligence above €3000
            "suspicious_activity": Decimal("10000.00"),  # SAR threshold €10,000
            "ctr_reporting": Decimal("10000.00")    # Currency transaction reporting
        }

    async def verify_kyc(
        self,
        creator_id: str,
        documents: Dict[str, Any],
        verification_level: KYCLevel = KYCLevel.STANDARD
    ) -> KYCVerification:
        """
        Perform KYC verification for creator.
        
        Args:
            creator_id: Creator account identifier
            documents: Verification documents and data
            verification_level: Required verification level
            
        Returns:
            KYCVerification result
            
        Raises:
            KYCError: If verification fails
        """



        try:
            logger.info(f"Starting KYC verification for creator {creator_id}")
            
            # Validate required documents
            required_docs = await self._get_required_documents(verification_level)
            provided_docs = list(documents.keys())
            
            missing_docs = set(required_docs) - set(provided_docs)
            if missing_docs:
                raise KYCError(
                    f"Missing required documents: {', '.join(missing_docs)}",
                    kyc_status="incomplete"
                )
            
            # Document verification
            verification_results = await self._verify_documents(creator_id, documents)
            
            # Identity verification
            identity_check = await self._perform_identity_verification(creator_id, documents)
            
            # Address verification
            address_check = await self._perform_address_verification(creator_id, documents)
            
            # Calculate risk score
            risk_score = await self._calculate_kyc_risk_score(
                creator_id, documents, verification_results
            )
            
            # Determine verification status
            if (verification_results["passed"] and 
                identity_check["passed"] and 
                address_check["passed"] and 
                risk_score < 0.5):
                status = ComplianceStatus.APPROVED
            elif risk_score > 0.8:
                status = ComplianceStatus.REJECTED
            else:
                status = ComplianceStatus.REQUIRES_REVIEW
            
            # Create verification record
            verification = KYCVerification(
                creator_id=creator_id,
                verification_level=verification_level,
                status=status,
                documents_verified=provided_docs,
                verification_date=datetime.utcnow() if status == ComplianceStatus.APPROVED else None,
                expiry_date=datetime.utcnow() + timedelta(days=365) if status == ComplianceStatus.APPROVED else None,
                verification_provider="internal",
                risk_score=risk_score,
                metadata={
                    "verification_results": verification_results,
                    "identity_check": identity_check,
                    "address_check": address_check,
                    "verification_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"KYC verification completed for {creator_id}: {status.value}")
            return verification
            
        except KYCError:
            raise
        except Exception as e:
            logger.error(f"KYC verification failed for {creator_id}: {str(e)}")
            raise KYCError(f"KYC verification failed: {str(e)}")

    async def perform_aml_screening(
        self,
        creator_id: str,
        creator_data: Dict[str, Any]
    ) -> AMLScreening:
        """
        Perform AML screening and sanctions checking.
        
        Args:
            creator_id: Creator account identifier
            creator_data: Creator personal and business data
            
        Returns:
            AMLScreening result
            
        Raises:
            AMLError: If screening indicates high risk
        """



        try:
            logger.info(f"Starting AML screening for creator {creator_id}")
            
            flags = []
            risk_level = RiskLevel.LOW
            flagged = False
            
            # Sanctions list checking
            sanctions_check = await self._check_sanctions_lists(creator_data)
            if sanctions_check["flagged"]:
                flags.extend(sanctions_check["flags"])
                risk_level = RiskLevel.CRITICAL
                flagged = True
            
            # PEP (Politically Exposed Person) check
            pep_check = await self._check_pep_status(creator_data)
            if pep_check["flagged"]:
                flags.append("politically_exposed_person")
                risk_level = max(risk_level, RiskLevel.HIGH)
                flagged = True
            
            # Adverse media screening
            adverse_media = await self._check_adverse_media(creator_data)
            if adverse_media["flagged"]:
                flags.extend(adverse_media["flags"])
                risk_level = max(risk_level, RiskLevel.MEDIUM)
                flagged = True
            
            # Geographic risk assessment
            geographic_risk = await self._assess_geographic_risk(creator_data)
            if geographic_risk["high_risk"]:
                flags.append("high_risk_jurisdiction")
                risk_level = max(risk_level, RiskLevel.HIGH)
                flagged = True
            
            # Business activity risk
            activity_risk = await self._assess_business_activity_risk(creator_data)
            if activity_risk["high_risk"]:
                flags.extend(activity_risk["flags"])
                risk_level = max(risk_level, RiskLevel.MEDIUM)
            
            # Create screening record
            screening = AMLScreening(
                creator_id=creator_id,
                screening_date=datetime.utcnow(),
                risk_level=risk_level,
                flagged=flagged,
                flags=flags,
                sanctions_check=sanctions_check["flagged"],
                pep_check=pep_check["flagged"],
                adverse_media=adverse_media["flagged"],
                screening_provider="internal",
                metadata={
                    "sanctions_results": sanctions_check,
                    "pep_results": pep_check,
                    "adverse_media_results": adverse_media,
                    "geographic_risk": geographic_risk,
                    "activity_risk": activity_risk,
                    "screening_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Flag for manual review if high risk
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                raise AMLError(
                    f"AML screening flagged high-risk creator: {', '.join(flags)}",
                    aml_flags=flags
                )
            
            logger.info(f"AML screening completed for {creator_id}: {risk_level.value}")
            return screening
            
        except AMLError:
            raise
        except Exception as e:
            logger.error(f"AML screening failed for {creator_id}: {str(e)}")
            raise AMLError(f"AML screening failed: {str(e)}")

    async def calculate_taxes(
        self,
        creator_id: str,
        gross_amount: Decimal,
        currency: str,
        jurisdiction: str = "DE",
        transaction_type: str = "revenue"
    ) -> TaxCalculation:
        """
        Calculate tax obligations for transaction.
        
        Args:
            creator_id: Creator account identifier
            gross_amount: Gross transaction amount
            currency: Currency code
            jurisdiction: Tax jurisdiction
            transaction_type: Type of transaction
            
        Returns:
            TaxCalculation result
            
        Raises:
            TaxCalculationError: If calculation fails
        """



        try:
            logger.info(f"Calculating taxes for {creator_id}: {gross_amount} {currency}")
            
            # Get tax configuration for creator
            tax_config = await self._get_tax_configuration(creator_id, jurisdiction)
            
            # Determine applicable tax rate
            tax_rate = await self._determine_tax_rate(
                creator_id, gross_amount, jurisdiction, transaction_type, tax_config
            )
            
            # Calculate tax amount
            tax_amount = (gross_amount * tax_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            # Calculate net amount
            net_amount = gross_amount - tax_amount
            
            # Apply minimum thresholds
            if gross_amount < tax_config.get("minimum_taxable_amount", Decimal("0.00")):
                tax_amount = Decimal("0.00")
                net_amount = gross_amount
            
            # Create tax calculation record
            calculation = TaxCalculation(
                creator_id=creator_id,
                gross_amount=gross_amount,
                tax_amount=tax_amount,
                net_amount=net_amount,
                tax_rate=tax_rate,
                jurisdiction=jurisdiction,
                tax_type=transaction_type,
                calculation_date=datetime.utcnow(),
                metadata={
                    "currency": currency,
                    "tax_config": tax_config,
                    "calculation_method": "standard",
                    "exemptions_applied": [],
                    "calculation_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Tax calculated: {tax_amount} {currency} from {gross_amount} {currency}")
            return calculation
            
        except Exception as e:
            logger.error(f"Tax calculation failed for {creator_id}: {str(e)}")
            raise TaxCalculationError(f"Tax calculation failed: {str(e)}")

    async def generate_tax_report(
        self,
        creator_id: str,
        year: int,
        country: str = "DE"
    ) -> ComplianceReport:
        """
        Generate annual tax report for creator.
        
        Args:
            creator_id: Creator account identifier
            year: Tax year
            country: Country code for tax jurisdiction
            
        Returns:
            ComplianceReport with tax data
        """



        try:
            logger.info(f"Generating tax report for {creator_id} - Year {year}")
            
            # Define reporting period
            period_start = datetime(year, 1, 1, tzinfo=timezone.utc)
            period_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            
            # Get transactions for the year
            transactions = await self._get_transactions_for_period(
                creator_id, period_start, period_end
            )
            
            # Calculate summary totals
            summary = await self._calculate_tax_summary(transactions, country)
            
            # Generate transaction details for report
            transaction_details = []
            for transaction in transactions:
                transaction_details.append({
                    "id": str(transaction.id),
                    "date": transaction.created_at.isoformat(),
                    "type": transaction.transaction_type,
                    "gross_amount": str(transaction.amount),
                    "tax_amount": str(transaction.taxes),
                    "net_amount": str(transaction.net_amount),
                    "currency": transaction.currency,
                    "source": transaction.source
                })
            
            # Create compliance report
            report = ComplianceReport(
                report_type="annual_tax_report",
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                jurisdiction=country,
                transactions=transaction_details,
                summary=summary,
                generated_at=datetime.utcnow(),
                metadata={
                    "year": year,
                    "transaction_count": len(transactions),
                    "reporting_currency": "EUR",
                    "generated_by": "compliance_manager",
                    "report_version": "1.0"
                }
            )
            
            logger.info(f"Tax report generated for {creator_id}: {len(transactions)} transactions")
            return report
            
        except Exception as e:
            logger.error(f"Tax report generation failed for {creator_id}: {str(e)}")
            raise ComplianceError(f"Tax report generation failed: {str(e)}")

    async def check_transaction_compliance(
        self,
        transaction: PaymentTransaction
    ) -> Dict[str, Any]:
        """
        Check transaction compliance requirements.
        
        Args:
            transaction: Payment transaction to check
            
        Returns:
            Dict with compliance check results
        """



        try:
            compliance_result = {
                "compliant": True,
                "warnings": [],
                "required_actions": [],
                "risk_level": "low"
            }
            
            # Check transaction amount thresholds
            amount_checks = await self._check_amount_thresholds(transaction)
            if not amount_checks["compliant"]:
                compliance_result["compliant"] = False
                compliance_result["required_actions"].extend(amount_checks["actions"])
            
            # Check KYC requirements
            kyc_check = await self._check_kyc_requirements(transaction)
            if not kyc_check["compliant"]:
                compliance_result["compliant"] = False
                compliance_result["required_actions"].extend(kyc_check["actions"])
                compliance_result["risk_level"] = "high"
            
            # Check AML requirements
            aml_check = await self._check_aml_requirements(transaction)
            if not aml_check["compliant"]:
                compliance_result["compliant"] = False
                compliance_result["required_actions"].extend(aml_check["actions"])
                compliance_result["risk_level"] = "critical"
            
            # Check reporting requirements
            reporting_check = await self._check_reporting_requirements(transaction)
            if reporting_check["reporting_required"]:
                compliance_result["required_actions"].extend(reporting_check["actions"])
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance check failed for transaction {transaction.id}: {str(e)}")
            raise ComplianceError(f"Transaction compliance check failed: {str(e)}")

    # Private methods for compliance operations
    async def _get_required_documents(self, verification_level: KYCLevel) -> List[str]:
        """Get required documents for KYC level"""
        if verification_level == KYCLevel.BASIC:
            return ["government_id", "proof_of_address"]
        elif verification_level == KYCLevel.STANDARD:
            return ["government_id", "proof_of_address", "selfie", "bank_statement"]
        else:  # PREMIUM
            return [
                "government_id", "proof_of_address", "selfie", 
                "bank_statement", "tax_return", "source_of_funds"
            ]

    async def _verify_documents(
        self, 
        creator_id: str, 
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify submitted documents"""
        # Mock implementation - would integrate with document verification service
        return {
            "passed": True,
            "verified_documents": list(documents.keys()),
            "confidence_scores": {doc: 0.95 for doc in documents.keys()}
        }

    async def _perform_identity_verification(
        self, 
        creator_id: str, 
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform identity verification checks"""
        # Mock implementation - would integrate with identity verification service
        return {
            "passed": True,
            "identity_match": True,
            "liveness_check": True,
            "document_authenticity": True
        }

    async def _perform_address_verification(
        self, 
        creator_id: str, 
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform address verification"""
        # Mock implementation - would verify address documents
        return {
            "passed": True,
            "address_verified": True,
            "document_date_valid": True
        }

    async def _calculate_kyc_risk_score(
        self,
        creator_id: str,
        documents: Dict[str, Any],
        verification_results: Dict[str, Any]
    ) -> float:
        """Calculate KYC risk score"""
        # Mock implementation - would use ML models for risk scoring
        base_risk = 0.1
        
        # Adjust based on document quality
        doc_quality = verification_results.get("confidence_scores", {})
        avg_confidence = sum(doc_quality.values()) / len(doc_quality) if doc_quality else 0.8
        
        if avg_confidence < 0.7:
            base_risk += 0.3
        elif avg_confidence < 0.8:
            base_risk += 0.1
        
        return min(base_risk, 1.0)

    async def _check_sanctions_lists(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check against sanctions lists"""
        flags = []
        flagged = False
        
        # Check nationality/residence country
        country = creator_data.get("country", "").upper()
        if country in self.sanctioned_countries:
            flags.append(f"sanctioned_country_{country}")
            flagged = True
        
        # Check name against sanctions lists (simplified)
        name = creator_data.get("full_name", "").lower()
        # In real implementation, would check against OFAC, EU, UN lists
        
        return {"flagged": flagged, "flags": flags}

    async def _check_pep_status(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for Politically Exposed Person status"""
        # Mock implementation - would check against PEP databases
        return {"flagged": False, "risk_level": "low"}

    async def _check_adverse_media(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check adverse media mentions"""
        # Mock implementation - would check news/media databases
        return {"flagged": False, "flags": []}

    async def _assess_geographic_risk(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess geographic risk factors"""
        high_risk_countries = {'AF', 'IR', 'KP', 'SY', 'MM', 'SO'}
        country = creator_data.get("country", "").upper()
        
        return {
            "high_risk": country in high_risk_countries,
            "risk_factors": [f"high_risk_jurisdiction_{country}"] if country in high_risk_countries else []
        }

    async def _assess_business_activity_risk(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business activity risk"""
        high_risk_activities = {'cryptocurrency', 'gambling', 'adult_content'}
        activity = creator_data.get("business_activity", "").lower()
        
        return {
            "high_risk": activity in high_risk_activities,
            "flags": [f"high_risk_activity_{activity}"] if activity in high_risk_activities else []
        }

    async def _get_tax_configuration(
        self, 
        creator_id: str, 
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Get tax configuration for creator and jurisdiction"""
        # Would query database for creator's tax settings
        default_config = {
            "income_tax_rate": self.tax_rates.get(jurisdiction, {}).get("income_tax", Decimal("0.19")),
            "vat_rate": self.tax_rates.get(jurisdiction, {}).get("vat", Decimal("0.00")),
            "minimum_taxable_amount": Decimal("600.00"),  # US threshold
            "tax_exemption": False
        }
        
        return default_config

    async def _determine_tax_rate(
        self,
        creator_id: str,
        amount: Decimal,
        jurisdiction: str,
        transaction_type: str,
        tax_config: Dict[str, Any]
    ) -> Decimal:
        """Determine applicable tax rate"""
        if tax_config.get("tax_exemption"):
            return Decimal("0.00")
        
        # Use income tax rate for revenue transactions
        if transaction_type in ["revenue", "royalties"]:
            return tax_config["income_tax_rate"] * 100  # Convert to percentage
        
        return Decimal("0.00")

    async def _get_transactions_for_period(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[PaymentTransaction]:
        """Get transactions for reporting period"""
        if not self.db_session:
            return []
        
        return self.db_session.query(PaymentTransaction).filter(
            and_(
                PaymentTransaction.creator_id == creator_id,
                PaymentTransaction.created_at >= start_date,
                PaymentTransaction.created_at <= end_date,
                PaymentTransaction.status == "completed"
            )
        ).all()

    async def _calculate_tax_summary(
        self, 
        transactions: List[PaymentTransaction], 
        country: str
    ) -> Dict[str, Any]:
        """Calculate tax summary from transactions"""
        total_gross = sum(t.amount for t in transactions)
        total_taxes = sum(t.taxes for t in transactions)
        total_net = sum(t.net_amount for t in transactions)
        
        return {
            "total_gross_income": str(total_gross),
            "total_taxes_withheld": str(total_taxes),
            "total_net_income": str(total_net),
            "transaction_count": len(transactions),
            "reporting_currency": "EUR",
            "tax_jurisdiction": country
        }

    async def _check_amount_thresholds(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check transaction amount against compliance thresholds"""
        result = {"compliant": True, "actions": []}
        
        if transaction.amount >= self.thresholds["ctr_reporting"]:
            result["actions"].append("currency_transaction_reporting_required")
        
        if transaction.amount >= self.thresholds["suspicious_activity"]:
            result["actions"].append("suspicious_activity_monitoring")
        
        return result

    async def _check_kyc_requirements(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check KYC requirements for transaction"""
        result = {"compliant": True, "actions": []}
        
        if transaction.amount >= self.thresholds["kyc_required"]:
            # Would check if creator has valid KYC
            kyc_valid = await self._is_kyc_valid(transaction.creator_id)
            if not kyc_valid:
                result["compliant"] = False
                result["actions"].append("kyc_verification_required")
        
        return result

    async def _check_aml_requirements(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check AML requirements for transaction"""
        result = {"compliant": True, "actions": []}
        
        # Would check AML screening status
        aml_valid = await self._is_aml_screening_valid(transaction.creator_id)
        if not aml_valid:
            result["compliant"] = False
            result["actions"].append("aml_screening_required")
        
        return result

    async def _check_reporting_requirements(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check reporting requirements"""
        result = {"reporting_required": False, "actions": []}
        
        if transaction.amount >= self.thresholds["ctr_reporting"]:
            result["reporting_required"] = True
            result["actions"].append("file_currency_transaction_report")
        
        return result

    async def _is_kyc_valid(self, creator_id: str) -> bool:
        """Check if creator has valid KYC verification"""
        # Would check database for valid KYC record
        return True  # Mock implementation

    async def _is_aml_screening_valid(self, creator_id: str) -> bool:
        """Check if creator has valid AML screening"""
        # Would check database for valid AML screening
        return True  # Mock implementation
