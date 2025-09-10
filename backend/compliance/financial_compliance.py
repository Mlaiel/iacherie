"""
Financial Compliance - Financial Regulations and Compliance Management

Comprehensive financial compliance system for payment processing, anti-money laundering,
financial data protection, taxation compliance, and financial regulatory adherence.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import json
import logging
import math
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import aioredis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class FinancialRegulation(Enum):
    """Financial regulations and standards"""
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    SOX = "sox"  # Sarbanes-Oxley Act
    GDPR_FINANCIAL = "gdpr_financial"  # GDPR for financial data
    PSD2 = "psd2"  # Payment Services Directive 2
    MIFID_II = "mifid_ii"  # Markets in Financial Instruments Directive
    BASEL_III = "basel_iii"  # Basel III banking regulations
    FATCA = "fatca"  # Foreign Account Tax Compliance Act
    CRS = "crs"  # Common Reporting Standard
    AML_DIRECTIVE = "aml_directive"  # Anti-Money Laundering Directive
    KYC_REQUIREMENTS = "kyc_requirements"  # Know Your Customer
    SEPA = "sepa"  # Single Euro Payments Area
    SWIFT_CSP = "swift_csp"  # SWIFT Customer Security Programme
    FFIEC = "ffiec"  # Federal Financial Institutions Examination Council
    GDPR_RIGHT_TO_BE_FORGOTTEN = "gdpr_right_to_be_forgotten"


class PaymentMethod(Enum):
    """Payment processing methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    PREPAID_CARD = "prepaid_card"
    DIRECT_DEBIT = "direct_debit"
    WIRE_TRANSFER = "wire_transfer"
    ACH_TRANSFER = "ach_transfer"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class TransactionRiskLevel(Enum):
    """Transaction risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    SUSPICIOUS = "suspicious"


class ComplianceStatus(Enum):
    """Financial compliance status"""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"
    UNDER_INVESTIGATION = "under_investigation"


class AMLStatus(Enum):
    """Anti-Money Laundering status"""
    CLEARED = "cleared"
    UNDER_REVIEW = "under_review"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    REPORTED = "reported"


class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_VAT = "eu_vat"
    UK_TAX = "uk_tax"
    CANADA_GST = "canada_gst"
    AUSTRALIA_GST = "australia_gst"
    SINGAPORE_GST = "singapore_gst"
    JAPAN_CONSUMPTION = "japan_consumption"
    SWITZERLAND_VAT = "switzerland_vat"
    GLOBAL_WITHHOLDING = "global_withholding"


@dataclass
class FinancialTransaction:
    """Financial transaction data structure"""
    transaction_id: str
    user_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    transaction_type: str
    timestamp: datetime
    merchant_id: Optional[str]
    description: str
    risk_level: TransactionRiskLevel
    aml_status: AMLStatus
    compliance_flags: List[str]
    geo_location: Optional[str]
    ip_address: Optional[str]
    device_fingerprint: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentCompliance:
    """Payment processing compliance assessment"""
    assessment_id: str
    payment_processor: str
    pci_dss_level: str
    compliance_certifications: List[str]
    security_measures: List[str]
    data_encryption_status: str
    tokenization_enabled: bool
    fraud_detection_enabled: bool
    compliance_score: float
    last_audit_date: datetime
    next_audit_date: datetime
    recommendations: List[str]


@dataclass
class AMLAssessment:
    """Anti-Money Laundering assessment"""
    assessment_id: str
    customer_id: str
    risk_score: float
    risk_factors: List[str]
    transaction_patterns: Dict[str, Any]
    geographic_risk: str
    source_of_funds: str
    due_diligence_level: str
    sanctions_screening_result: str
    pep_status: bool  # Politically Exposed Person
    adverse_media_findings: List[str]
    assessment_date: datetime
    next_review_date: datetime
    status: AMLStatus
    recommendations: List[str]


@dataclass
class KYCProfile:
    """Know Your Customer profile"""
    profile_id: str
    customer_id: str
    identity_verification_status: str
    document_verification_status: str
    address_verification_status: str
    phone_verification_status: str
    email_verification_status: str
    risk_rating: str
    customer_type: str  # individual, business, institutional
    business_nature: Optional[str]
    expected_transaction_volume: str
    source_of_wealth: str
    kyc_completion_date: datetime
    kyc_expiry_date: datetime
    compliance_issues: List[str]
    required_documents: List[str]


@dataclass
class TaxCompliance:
    """Tax compliance tracking"""
    compliance_id: str
    jurisdiction: TaxJurisdiction
    tax_year: int
    total_revenue: Decimal
    taxable_amount: Decimal
    tax_rate: float
    tax_collected: Decimal
    tax_remitted: Decimal
    outstanding_tax: Decimal
    filing_status: str
    filing_deadline: datetime
    last_filing_date: Optional[datetime]
    compliance_status: ComplianceStatus
    penalties: List[Dict[str, Any]]
    exemptions_claimed: List[str]
    supporting_documents: List[str]


class FinancialTransactionRecord(Base):
    """Database model for financial transactions"""
    __tablename__ = "financial_transactions"
    
    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_method = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    merchant_id = Column(String)
    description = Column(Text)
    risk_level = Column(String, nullable=False)
    aml_status = Column(String, nullable=False)
    compliance_flags = Column(JSON, default=[])
    geo_location = Column(String)
    ip_address = Column(String)
    device_fingerprint = Column(String)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentComplianceRecord(Base):
    """Database model for payment compliance"""
    __tablename__ = "payment_compliance"
    
    assessment_id = Column(String, primary_key=True)
    payment_processor = Column(String, nullable=False)
    pci_dss_level = Column(String)
    compliance_certifications = Column(JSON, default=[])
    security_measures = Column(JSON, default=[])
    data_encryption_status = Column(String)
    tokenization_enabled = Column(Boolean, default=False)
    fraud_detection_enabled = Column(Boolean, default=False)
    compliance_score = Column(Float)
    last_audit_date = Column(DateTime)
    next_audit_date = Column(DateTime)
    recommendations = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AMLAssessmentRecord(Base):
    """Database model for AML assessments"""
    __tablename__ = "aml_assessments"
    
    assessment_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(JSON, default=[])
    transaction_patterns = Column(JSON, default={})
    geographic_risk = Column(String)
    source_of_funds = Column(String)
    due_diligence_level = Column(String)
    sanctions_screening_result = Column(String)
    pep_status = Column(Boolean, default=False)
    adverse_media_findings = Column(JSON, default=[])
    assessment_date = Column(DateTime, nullable=False)
    next_review_date = Column(DateTime)
    status = Column(String, nullable=False)
    recommendations = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)


class KYCProfileRecord(Base):
    """Database model for KYC profiles"""
    __tablename__ = "kyc_profiles"
    
    profile_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    identity_verification_status = Column(String)
    document_verification_status = Column(String)
    address_verification_status = Column(String)
    phone_verification_status = Column(String)
    email_verification_status = Column(String)
    risk_rating = Column(String)
    customer_type = Column(String)
    business_nature = Column(String)
    expected_transaction_volume = Column(String)
    source_of_wealth = Column(String)
    kyc_completion_date = Column(DateTime)
    kyc_expiry_date = Column(DateTime)
    compliance_issues = Column(JSON, default=[])
    required_documents = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TaxComplianceRecord(Base):
    """Database model for tax compliance"""
    __tablename__ = "tax_compliance"
    
    compliance_id = Column(String, primary_key=True)
    jurisdiction = Column(String, nullable=False)
    tax_year = Column(Integer, nullable=False)
    total_revenue = Column(Numeric(15, 2))
    taxable_amount = Column(Numeric(15, 2))
    tax_rate = Column(Float)
    tax_collected = Column(Numeric(15, 2))
    tax_remitted = Column(Numeric(15, 2))
    outstanding_tax = Column(Numeric(15, 2))
    filing_status = Column(String)
    filing_deadline = Column(DateTime)
    last_filing_date = Column(DateTime)
    compliance_status = Column(String)
    penalties = Column(JSON, default=[])
    exemptions_claimed = Column(JSON, default=[])
    supporting_documents = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentSecurityManager:
    """Payment security and PCI DSS compliance management"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    async def assess_payment_compliance(self, 
                                      payment_processor: str,
                                      processor_config: Dict[str, Any]) -> PaymentCompliance:
        """Assess payment processing compliance"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Assess PCI DSS compliance level
            pci_level = await self._assess_pci_dss_level(processor_config)
            
            # Check compliance certifications
            certifications = await self._verify_compliance_certifications(payment_processor, processor_config)
            
            # Evaluate security measures
            security_measures = await self._evaluate_security_measures(processor_config)
            
            # Check data encryption status
            encryption_status = await self._check_encryption_status(processor_config)
            
            # Verify tokenization
            tokenization_enabled = processor_config.get("tokenization_enabled", False)
            
            # Check fraud detection
            fraud_detection_enabled = processor_config.get("fraud_detection_enabled", False)
            
            # Calculate compliance score
            compliance_score = await self._calculate_payment_compliance_score(
                pci_level, certifications, security_measures, encryption_status,
                tokenization_enabled, fraud_detection_enabled
            )
            
            # Generate recommendations
            recommendations = await self._generate_payment_recommendations(
                compliance_score, pci_level, security_measures
            )
            
            assessment = PaymentCompliance(
                assessment_id=assessment_id,
                payment_processor=payment_processor,
                pci_dss_level=pci_level,
                compliance_certifications=certifications,
                security_measures=security_measures,
                data_encryption_status=encryption_status,
                tokenization_enabled=tokenization_enabled,
                fraud_detection_enabled=fraud_detection_enabled,
                compliance_score=compliance_score,
                last_audit_date=datetime.utcnow() - timedelta(days=90),  # Mock
                next_audit_date=datetime.utcnow() + timedelta(days=275),  # Annual
                recommendations=recommendations
            )
            
            # Store assessment
            await self._store_payment_compliance(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Payment compliance assessment failed: {str(e)}")
            raise
    
    async def _assess_pci_dss_level(self, processor_config: Dict[str, Any]) -> str:
        """Assess PCI DSS compliance level"""
        transaction_volume = processor_config.get("annual_transaction_volume", 0)
        
        # PCI DSS levels based on transaction volume
        if transaction_volume >= 6000000:  # 6M+ transactions
            return "level_1"
        elif transaction_volume >= 1000000:  # 1M - 6M transactions
            return "level_2"
        elif transaction_volume >= 20000:  # 20K - 1M transactions
            return "level_3"
        else:  # < 20K transactions
            return "level_4"
    
    async def _verify_compliance_certifications(self, 
                                              processor: str,
                                              config: Dict[str, Any]) -> List[str]:
        """Verify compliance certifications"""
        certifications = []
        
        # Check for PCI DSS certification
        if config.get("pci_dss_certified", False):
            certifications.append("PCI_DSS")
        
        # Check for ISO certifications
        if config.get("iso_27001_certified", False):
            certifications.append("ISO_27001")
        
        if config.get("iso_27018_certified", False):
            certifications.append("ISO_27018")
        
        # Check for SOC certifications
        if config.get("soc2_type2_certified", False):
            certifications.append("SOC2_Type2")
        
        # Regional certifications
        if config.get("gdpr_compliant", False):
            certifications.append("GDPR")
        
        if config.get("ccpa_compliant", False):
            certifications.append("CCPA")
        
        return certifications
    
    async def _evaluate_security_measures(self, config: Dict[str, Any]) -> List[str]:
        """Evaluate implemented security measures"""
        security_measures = []
        
        # Encryption measures
        if config.get("data_at_rest_encrypted", False):
            security_measures.append("data_at_rest_encryption")
        
        if config.get("data_in_transit_encrypted", False):
            security_measures.append("data_in_transit_encryption")
        
        # Access controls
        if config.get("multi_factor_authentication", False):
            security_measures.append("multi_factor_authentication")
        
        if config.get("role_based_access_control", False):
            security_measures.append("role_based_access_control")
        
        # Network security
        if config.get("network_segmentation", False):
            security_measures.append("network_segmentation")
        
        if config.get("intrusion_detection", False):
            security_measures.append("intrusion_detection_system")
        
        # Monitoring and logging
        if config.get("audit_logging", False):
            security_measures.append("comprehensive_audit_logging")
        
        if config.get("real_time_monitoring", False):
            security_measures.append("real_time_security_monitoring")
        
        # Data protection
        if config.get("tokenization", False):
            security_measures.append("payment_tokenization")
        
        if config.get("data_loss_prevention", False):
            security_measures.append("data_loss_prevention")
        
        return security_measures
    
    async def _check_encryption_status(self, config: Dict[str, Any]) -> str:
        """Check data encryption status"""
        at_rest_encrypted = config.get("data_at_rest_encrypted", False)
        in_transit_encrypted = config.get("data_in_transit_encrypted", False)
        end_to_end_encrypted = config.get("end_to_end_encryption", False)
        
        if end_to_end_encrypted and at_rest_encrypted and in_transit_encrypted:
            return "fully_encrypted"
        elif at_rest_encrypted and in_transit_encrypted:
            return "encrypted"
        elif at_rest_encrypted or in_transit_encrypted:
            return "partially_encrypted"
        else:
            return "not_encrypted"
    
    async def _calculate_payment_compliance_score(self, 
                                                pci_level: str,
                                                certifications: List[str],
                                                security_measures: List[str],
                                                encryption_status: str,
                                                tokenization_enabled: bool,
                                                fraud_detection_enabled: bool) -> float:
        """Calculate payment compliance score"""
        score = 0.0
        
        # PCI DSS level scoring
        pci_scores = {"level_1": 1.0, "level_2": 0.9, "level_3": 0.8, "level_4": 0.7}
        score += pci_scores.get(pci_level, 0.5) * 0.3
        
        # Certifications scoring
        cert_score = min(1.0, len(certifications) / 5)  # Max 5 certifications
        score += cert_score * 0.2
        
        # Security measures scoring
        security_score = min(1.0, len(security_measures) / 10)  # Max 10 measures
        score += security_score * 0.2
        
        # Encryption scoring
        encryption_scores = {
            "fully_encrypted": 1.0,
            "encrypted": 0.8,
            "partially_encrypted": 0.5,
            "not_encrypted": 0.0
        }
        score += encryption_scores.get(encryption_status, 0.0) * 0.15
        
        # Tokenization scoring
        score += (0.1 if tokenization_enabled else 0.0)
        
        # Fraud detection scoring
        score += (0.05 if fraud_detection_enabled else 0.0)
        
        return min(1.0, score)
    
    async def _generate_payment_recommendations(self, 
                                              compliance_score: float,
                                              pci_level: str,
                                              security_measures: List[str]) -> List[str]:
        """Generate payment compliance recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if compliance_score < 0.7:
            recommendations.append("Urgent: Implement comprehensive security measures")
            recommendations.append("Conduct immediate PCI DSS compliance audit")
        
        # PCI DSS level recommendations
        if pci_level in ["level_3", "level_4"]:
            recommendations.append("Consider upgrading PCI DSS compliance level")
        
        # Security measure recommendations
        if "multi_factor_authentication" not in security_measures:
            recommendations.append("Implement multi-factor authentication")
        
        if "payment_tokenization" not in security_measures:
            recommendations.append("Enable payment card tokenization")
        
        if "real_time_security_monitoring" not in security_measures:
            recommendations.append("Implement real-time security monitoring")
        
        if "comprehensive_audit_logging" not in security_measures:
            recommendations.append("Enable comprehensive audit logging")
        
        # General recommendations
        recommendations.extend([
            "Regular security vulnerability assessments",
            "Employee security training programs",
            "Incident response plan development",
            "Regular compliance audits and reviews"
        ])
        
        return recommendations
    
    async def _store_payment_compliance(self, assessment: PaymentCompliance) -> None:
        """Store payment compliance assessment"""
        try:
            record = PaymentComplianceRecord(
                assessment_id=assessment.assessment_id,
                payment_processor=assessment.payment_processor,
                pci_dss_level=assessment.pci_dss_level,
                compliance_certifications=assessment.compliance_certifications,
                security_measures=assessment.security_measures,
                data_encryption_status=assessment.data_encryption_status,
                tokenization_enabled=assessment.tokenization_enabled,
                fraud_detection_enabled=assessment.fraud_detection_enabled,
                compliance_score=assessment.compliance_score,
                last_audit_date=assessment.last_audit_date,
                next_audit_date=assessment.next_audit_date,
                recommendations=assessment.recommendations
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store payment compliance assessment: {str(e)}")
            raise


class AMLMonitor:
    """Anti-Money Laundering monitoring and compliance"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    async def conduct_aml_assessment(self, 
                                   customer_id: str,
                                   customer_data: Dict[str, Any],
                                   transaction_history: List[FinancialTransaction]) -> AMLAssessment:
        """Conduct comprehensive AML assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Calculate AML risk score
            risk_score = await self._calculate_aml_risk_score(customer_data, transaction_history)
            
            # Identify risk factors
            risk_factors = await self._identify_aml_risk_factors(customer_data, transaction_history)
            
            # Analyze transaction patterns
            transaction_patterns = await self._analyze_transaction_patterns(transaction_history)
            
            # Assess geographic risk
            geographic_risk = await self._assess_geographic_risk(customer_data)
            
            # Check sanctions screening
            sanctions_result = await self._conduct_sanctions_screening(customer_data)
            
            # Check PEP status
            pep_status = await self._check_pep_status(customer_data)
            
            # Check adverse media
            adverse_media = await self._check_adverse_media(customer_data)
            
            # Determine due diligence level
            due_diligence_level = await self._determine_due_diligence_level(risk_score, risk_factors)
            
            # Determine AML status
            aml_status = await self._determine_aml_status(risk_score, sanctions_result, pep_status)
            
            # Generate recommendations
            recommendations = await self._generate_aml_recommendations(
                risk_score, risk_factors, aml_status
            )
            
            assessment = AMLAssessment(
                assessment_id=assessment_id,
                customer_id=customer_id,
                risk_score=risk_score,
                risk_factors=risk_factors,
                transaction_patterns=transaction_patterns,
                geographic_risk=geographic_risk,
                source_of_funds=customer_data.get("source_of_funds", "unknown"),
                due_diligence_level=due_diligence_level,
                sanctions_screening_result=sanctions_result,
                pep_status=pep_status,
                adverse_media_findings=adverse_media,
                assessment_date=datetime.utcnow(),
                next_review_date=datetime.utcnow() + timedelta(days=365),
                status=aml_status,
                recommendations=recommendations
            )
            
            # Store assessment
            await self._store_aml_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"AML assessment failed: {str(e)}")
            raise
    
    async def _calculate_aml_risk_score(self, 
                                      customer_data: Dict[str, Any],
                                      transactions: List[FinancialTransaction]) -> float:
        """Calculate AML risk score"""
        risk_score = 0.0
        
        # Geographic risk scoring
        country = customer_data.get("country", "").lower()
        high_risk_countries = ["afghanistan", "iran", "north_korea", "somalia", "syria"]
        if country in high_risk_countries:
            risk_score += 0.3
        
        # Customer type risk
        customer_type = customer_data.get("customer_type", "individual")
        if customer_type == "business":
            risk_score += 0.1
        elif customer_type == "institutional":
            risk_score += 0.05
        
        # Transaction volume risk
        if transactions:
            total_volume = sum(float(t.amount) for t in transactions)
            monthly_volume = total_volume / max(1, len(transactions) / 30)
            
            if monthly_volume > 100000:  # $100K+ monthly
                risk_score += 0.2
            elif monthly_volume > 50000:  # $50K+ monthly
                risk_score += 0.1
        
        # Transaction pattern risk
        if transactions:
            # Check for cash-intensive transactions
            cash_transactions = [t for t in transactions if "cash" in t.transaction_type.lower()]
            cash_ratio = len(cash_transactions) / len(transactions)
            risk_score += cash_ratio * 0.15
            
            # Check for frequent small transactions (structuring)
            small_transactions = [t for t in transactions if float(t.amount) < 10000]
            if len(small_transactions) > len(transactions) * 0.8:
                risk_score += 0.1
        
        # Business nature risk
        business_nature = customer_data.get("business_nature", "").lower()
        high_risk_businesses = ["money_exchange", "casino", "precious_metals", "art_dealing"]
        if any(business in business_nature for business in high_risk_businesses):
            risk_score += 0.2
        
        return min(1.0, risk_score)
    
    async def _identify_aml_risk_factors(self, 
                                       customer_data: Dict[str, Any],
                                       transactions: List[FinancialTransaction]) -> List[str]:
        """Identify specific AML risk factors"""
        risk_factors = []
        
        # Geographic risks
        country = customer_data.get("country", "").lower()
        if country in ["afghanistan", "iran", "north_korea", "somalia", "syria"]:
            risk_factors.append("high_risk_jurisdiction")
        
        # Customer profile risks
        if customer_data.get("pep_status", False):
            risk_factors.append("politically_exposed_person")
        
        if customer_data.get("sanctions_match", False):
            risk_factors.append("sanctions_list_match")
        
        # Transaction pattern risks
        if transactions:
            # Large cash transactions
            large_cash = [t for t in transactions if "cash" in t.transaction_type.lower() and float(t.amount) > 10000]
            if large_cash:
                risk_factors.append("large_cash_transactions")
            
            # Rapid movement of funds
            rapid_movements = 0
            for i in range(1, len(transactions)):
                time_diff = (transactions[i].timestamp - transactions[i-1].timestamp).total_seconds()
                if time_diff < 3600:  # Less than 1 hour between transactions
                    rapid_movements += 1
            
            if rapid_movements > len(transactions) * 0.3:
                risk_factors.append("rapid_fund_movement")
            
            # Cross-border transactions
            cross_border = [t for t in transactions if t.geo_location and t.geo_location != customer_data.get("country")]
            if len(cross_border) > len(transactions) * 0.5:
                risk_factors.append("frequent_cross_border_transactions")
        
        # Business-related risks
        business_nature = customer_data.get("business_nature", "").lower()
        if any(business in business_nature for business in ["casino", "money_exchange", "cryptocurrency"]):
            risk_factors.append("high_risk_business_sector")
        
        return risk_factors
    
    async def _analyze_transaction_patterns(self, transactions: List[FinancialTransaction]) -> Dict[str, Any]:
        """Analyze transaction patterns for suspicious activity"""
        patterns = {
            "total_transactions": len(transactions),
            "total_volume": 0.0,
            "average_amount": 0.0,
            "transaction_frequency": {},
            "geographic_distribution": {},
            "time_patterns": {},
            "suspicious_patterns": []
        }
        
        if not transactions:
            return patterns
        
        # Basic statistics
        amounts = [float(t.amount) for t in transactions]
        patterns["total_volume"] = sum(amounts)
        patterns["average_amount"] = patterns["total_volume"] / len(transactions)
        
        # Transaction frequency analysis
        daily_counts = defaultdict(int)
        for t in transactions:
            day = t.timestamp.date()
            daily_counts[day] += 1
        
        patterns["transaction_frequency"] = {
            "daily_average": sum(daily_counts.values()) / max(1, len(daily_counts)),
            "max_daily": max(daily_counts.values()) if daily_counts else 0,
            "min_daily": min(daily_counts.values()) if daily_counts else 0
        }
        
        # Geographic distribution
        geo_counts = defaultdict(int)
        for t in transactions:
            if t.geo_location:
                geo_counts[t.geo_location] += 1
        
        patterns["geographic_distribution"] = dict(geo_counts)
        
        # Time pattern analysis
        hour_counts = defaultdict(int)
        for t in transactions:
            hour = t.timestamp.hour
            hour_counts[hour] += 1
        
        patterns["time_patterns"] = dict(hour_counts)
        
        # Suspicious pattern detection
        # Structuring detection (many transactions just under reporting threshold)
        under_threshold = [t for t in transactions if 9000 <= float(t.amount) < 10000]
        if len(under_threshold) > 5:
            patterns["suspicious_patterns"].append("potential_structuring")
        
        # Layering detection (rapid succession of transactions)
        rapid_sequences = 0
        for i in range(1, len(transactions)):
            time_diff = (transactions[i].timestamp - transactions[i-1].timestamp).total_seconds()
            if time_diff < 300:  # Less than 5 minutes
                rapid_sequences += 1
        
        if rapid_sequences > len(transactions) * 0.2:
            patterns["suspicious_patterns"].append("potential_layering")
        
        # Round number bias (suspicious round amounts)
        round_amounts = [t for t in transactions if float(t.amount) % 1000 == 0]
        if len(round_amounts) > len(transactions) * 0.7:
            patterns["suspicious_patterns"].append("round_number_bias")
        
        return patterns
    
    async def _assess_geographic_risk(self, customer_data: Dict[str, Any]) -> str:
        """Assess geographic risk based on customer location"""
        country = customer_data.get("country", "").lower()
        
        # FATF high-risk jurisdictions
        high_risk_countries = [
            "afghanistan", "iran", "north_korea", "myanmar", "somalia", "syria", "yemen"
        ]
        
        # Countries with strategic deficiencies
        strategic_deficiency_countries = [
            "albania", "barbados", "burkina_faso", "cambodia", "cayman_islands",
            "haiti", "jamaica", "jordan", "mali", "morocco", "nicaragua",
            "panama", "philippines", "senegal", "south_sudan", "uganda", "zimbabwe"
        ]
        
        if country in high_risk_countries:
            return "high_risk"
        elif country in strategic_deficiency_countries:
            return "medium_risk"
        else:
            return "low_risk"
    
    async def _conduct_sanctions_screening(self, customer_data: Dict[str, Any]) -> str:
        """Conduct sanctions list screening"""
        # Mock sanctions screening - would integrate with actual sanctions databases
        name = customer_data.get("name", "").lower()
        
        # Mock sanctions list entries
        mock_sanctions = ["john_doe_terrorist", "jane_smith_sanctions", "evil_corp"]
        
        for entry in mock_sanctions:
            if entry in name:
                return "match_found"
        
        return "no_match"
    
    async def _check_pep_status(self, customer_data: Dict[str, Any]) -> bool:
        """Check if customer is a Politically Exposed Person"""
        # Mock PEP check - would integrate with PEP databases
        pep_indicators = ["minister", "president", "ambassador", "government", "political"]
        
        occupation = customer_data.get("occupation", "").lower()
        return any(indicator in occupation for indicator in pep_indicators)
    
    async def _check_adverse_media(self, customer_data: Dict[str, Any]) -> List[str]:
        """Check for adverse media mentions"""
        # Mock adverse media check - would integrate with media monitoring services
        adverse_findings = []
        
        name = customer_data.get("name", "").lower()
        
        # Mock adverse media database
        if "criminal" in name:
            adverse_findings.append("Criminal activity allegations")
        
        if "fraud" in name:
            adverse_findings.append("Fraud investigation reports")
        
        return adverse_findings
    
    async def _determine_due_diligence_level(self, risk_score: float, risk_factors: List[str]) -> str:
        """Determine required due diligence level"""
        if risk_score >= 0.7 or "sanctions_list_match" in risk_factors:
            return "enhanced_due_diligence"
        elif risk_score >= 0.4 or "politically_exposed_person" in risk_factors:
            return "customer_due_diligence"
        else:
            return "simplified_due_diligence"
    
    async def _determine_aml_status(self, 
                                  risk_score: float,
                                  sanctions_result: str,
                                  pep_status: bool) -> AMLStatus:
        """Determine AML status"""
        if sanctions_result == "match_found":
            return AMLStatus.BLOCKED
        elif risk_score >= 0.8:
            return AMLStatus.FLAGGED
        elif risk_score >= 0.6 or pep_status:
            return AMLStatus.UNDER_REVIEW
        else:
            return AMLStatus.CLEARED
    
    async def _generate_aml_recommendations(self, 
                                          risk_score: float,
                                          risk_factors: List[str],
                                          status: AMLStatus) -> List[str]:
        """Generate AML compliance recommendations"""
        recommendations = []
        
        # Status-based recommendations
        if status == AMLStatus.BLOCKED:
            recommendations.extend([
                "Block all transactions immediately",
                "Report to regulatory authorities",
                "Conduct thorough investigation"
            ])
        
        elif status == AMLStatus.FLAGGED:
            recommendations.extend([
                "Enhanced monitoring required",
                "Manual review of all transactions",
                "Consider filing suspicious activity report"
            ])
        
        elif status == AMLStatus.UNDER_REVIEW:
            recommendations.extend([
                "Increased transaction monitoring",
                "Additional documentation required",
                "Regular periodic reviews"
            ])
        
        # Risk factor specific recommendations
        if "high_risk_jurisdiction" in risk_factors:
            recommendations.append("Enhanced due diligence for geographic risk")
        
        if "politically_exposed_person" in risk_factors:
            recommendations.append("Senior management approval required")
        
        if "large_cash_transactions" in risk_factors:
            recommendations.append("Additional source of funds verification")
        
        # General recommendations
        if risk_score > 0.5:
            recommendations.extend([
                "Ongoing transaction monitoring",
                "Regular risk assessment updates",
                "Staff training on risk indicators"
            ])
        
        return recommendations
    
    async def _store_aml_assessment(self, assessment: AMLAssessment) -> None:
        """Store AML assessment in database"""
        try:
            record = AMLAssessmentRecord(
                assessment_id=assessment.assessment_id,
                customer_id=assessment.customer_id,
                risk_score=assessment.risk_score,
                risk_factors=assessment.risk_factors,
                transaction_patterns=assessment.transaction_patterns,
                geographic_risk=assessment.geographic_risk,
                source_of_funds=assessment.source_of_funds,
                due_diligence_level=assessment.due_diligence_level,
                sanctions_screening_result=assessment.sanctions_screening_result,
                pep_status=assessment.pep_status,
                adverse_media_findings=assessment.adverse_media_findings,
                assessment_date=assessment.assessment_date,
                next_review_date=assessment.next_review_date,
                status=assessment.status.value,
                recommendations=assessment.recommendations
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store AML assessment: {str(e)}")
            raise


class TaxComplianceManager:
    """Tax compliance management and reporting"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    async def assess_tax_compliance(self, 
                                  jurisdiction: TaxJurisdiction,
                                  tax_year: int,
                                  financial_data: Dict[str, Any]) -> TaxCompliance:
        """Assess tax compliance for specific jurisdiction"""
        try:
            compliance_id = str(uuid.uuid4())
            
            # Calculate tax obligations
            tax_calculations = await self._calculate_tax_obligations(jurisdiction, financial_data)
            
            # Determine filing requirements
            filing_requirements = await self._determine_filing_requirements(jurisdiction, tax_year)
            
            # Assess compliance status
            compliance_status = await self._assess_tax_compliance_status(
                tax_calculations, filing_requirements
            )
            
            # Check for penalties
            penalties = await self._check_tax_penalties(jurisdiction, tax_year, compliance_status)
            
            # Identify exemptions
            exemptions = await self._identify_tax_exemptions(jurisdiction, financial_data)
            
            compliance = TaxCompliance(
                compliance_id=compliance_id,
                jurisdiction=jurisdiction,
                tax_year=tax_year,
                total_revenue=Decimal(str(financial_data.get("total_revenue", 0))),
                taxable_amount=Decimal(str(tax_calculations["taxable_amount"])),
                tax_rate=tax_calculations["tax_rate"],
                tax_collected=Decimal(str(financial_data.get("tax_collected", 0))),
                tax_remitted=Decimal(str(financial_data.get("tax_remitted", 0))),
                outstanding_tax=Decimal(str(tax_calculations["tax_due"] - financial_data.get("tax_remitted", 0))),
                filing_status=filing_requirements["status"],
                filing_deadline=filing_requirements["deadline"],
                last_filing_date=financial_data.get("last_filing_date"),
                compliance_status=compliance_status,
                penalties=penalties,
                exemptions_claimed=exemptions,
                supporting_documents=financial_data.get("supporting_documents", [])
            )
            
            # Store compliance record
            await self._store_tax_compliance(compliance)
            
            return compliance
            
        except Exception as e:
            logger.error(f"Tax compliance assessment failed: {str(e)}")
            raise
    
    async def _calculate_tax_obligations(self, 
                                       jurisdiction: TaxJurisdiction,
                                       financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate tax obligations for jurisdiction"""
        total_revenue = financial_data.get("total_revenue", 0)
        deductions = financial_data.get("deductions", 0)
        
        # Tax rates by jurisdiction (simplified)
        tax_rates = {
            TaxJurisdiction.US_FEDERAL: 0.21,  # Corporate rate
            TaxJurisdiction.EU_VAT: 0.20,     # Standard VAT rate
            TaxJurisdiction.UK_TAX: 0.19,     # Corporation tax
            TaxJurisdiction.CANADA_GST: 0.05, # GST rate
            TaxJurisdiction.AUSTRALIA_GST: 0.10, # GST rate
            TaxJurisdiction.SINGAPORE_GST: 0.07, # GST rate
            TaxJurisdiction.JAPAN_CONSUMPTION: 0.10, # Consumption tax
        }
        
        tax_rate = tax_rates.get(jurisdiction, 0.20)  # Default 20%
        taxable_amount = max(0, total_revenue - deductions)
        tax_due = taxable_amount * tax_rate
        
        return {
            "taxable_amount": taxable_amount,
            "tax_rate": tax_rate,
            "tax_due": tax_due,
            "deductions_applied": deductions
        }
    
    async def _determine_filing_requirements(self, 
                                           jurisdiction: TaxJurisdiction,
                                           tax_year: int) -> Dict[str, Any]:
        """Determine tax filing requirements"""
        # Filing deadlines by jurisdiction
        filing_deadlines = {
            TaxJurisdiction.US_FEDERAL: datetime(tax_year + 1, 3, 15),  # March 15
            TaxJurisdiction.EU_VAT: datetime(tax_year + 1, 1, 31),      # January 31
            TaxJurisdiction.UK_TAX: datetime(tax_year + 1, 12, 31),     # December 31
            TaxJurisdiction.CANADA_GST: datetime(tax_year + 1, 3, 31),  # March 31
        }
        
        deadline = filing_deadlines.get(jurisdiction, datetime(tax_year + 1, 3, 31))
        
        # Determine filing status
        current_date = datetime.utcnow()
        if current_date < deadline:
            status = "pending"
        elif current_date <= deadline + timedelta(days=30):
            status = "due_soon"
        else:
            status = "overdue"
        
        return {
            "deadline": deadline,
            "status": status,
            "filing_required": True
        }
    
    async def _assess_tax_compliance_status(self, 
                                          tax_calculations: Dict[str, Any],
                                          filing_requirements: Dict[str, Any]) -> ComplianceStatus:
        """Assess overall tax compliance status"""
        filing_status = filing_requirements["status"]
        
        if filing_status == "overdue":
            return ComplianceStatus.NON_COMPLIANT
        elif filing_status == "due_soon":
            return ComplianceStatus.REQUIRES_ACTION
        elif filing_status == "pending":
            return ComplianceStatus.PENDING_REVIEW
        else:
            return ComplianceStatus.COMPLIANT
    
    async def _check_tax_penalties(self, 
                                 jurisdiction: TaxJurisdiction,
                                 tax_year: int,
                                 compliance_status: ComplianceStatus) -> List[Dict[str, Any]]:
        """Check for applicable tax penalties"""
        penalties = []
        
        if compliance_status == ComplianceStatus.NON_COMPLIANT:
            # Late filing penalty
            penalties.append({
                "type": "late_filing",
                "amount": 500.0,  # Mock penalty amount
                "description": "Late filing penalty for overdue tax return",
                "applied_date": datetime.utcnow().isoformat()
            })
            
            # Interest on unpaid tax
            penalties.append({
                "type": "interest_on_unpaid_tax",
                "rate": 0.05,  # 5% annual interest
                "description": "Interest charges on unpaid tax amount",
                "calculation_method": "compound_daily"
            })
        
        return penalties
    
    async def _identify_tax_exemptions(self, 
                                     jurisdiction: TaxJurisdiction,
                                     financial_data: Dict[str, Any]) -> List[str]:
        """Identify applicable tax exemptions"""
        exemptions = []
        
        business_type = financial_data.get("business_type", "")
        revenue = financial_data.get("total_revenue", 0)
        
        # Small business exemptions
        if revenue < 50000:  # Under $50K revenue
            exemptions.append("small_business_exemption")
        
        # Non-profit exemptions
        if business_type == "non_profit":
            exemptions.append("non_profit_exemption")
        
        # R&D exemptions
        rd_expenses = financial_data.get("rd_expenses", 0)
        if rd_expenses > 0:
            exemptions.append("research_development_credit")
        
        # Export exemptions (for VAT jurisdictions)
        if jurisdiction in [TaxJurisdiction.EU_VAT, TaxJurisdiction.UK_TAX]:
            export_revenue = financial_data.get("export_revenue", 0)
            if export_revenue > 0:
                exemptions.append("export_exemption")
        
        return exemptions
    
    async def _store_tax_compliance(self, compliance: TaxCompliance) -> None:
        """Store tax compliance record"""
        try:
            record = TaxComplianceRecord(
                compliance_id=compliance.compliance_id,
                jurisdiction=compliance.jurisdiction.value,
                tax_year=compliance.tax_year,
                total_revenue=compliance.total_revenue,
                taxable_amount=compliance.taxable_amount,
                tax_rate=compliance.tax_rate,
                tax_collected=compliance.tax_collected,
                tax_remitted=compliance.tax_remitted,
                outstanding_tax=compliance.outstanding_tax,
                filing_status=compliance.filing_status,
                filing_deadline=compliance.filing_deadline,
                last_filing_date=compliance.last_filing_date,
                compliance_status=compliance.compliance_status.value,
                penalties=compliance.penalties,
                exemptions_claimed=compliance.exemptions_claimed,
                supporting_documents=compliance.supporting_documents
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store tax compliance record: {str(e)}")
            raise


# Main Financial Compliance Engine
class FinancialCompliance:
    """Main financial compliance management engine"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
        # Initialize components
        self.payment_security = PaymentSecurityManager(db_session, redis_client)
        self.aml_monitor = AMLMonitor(db_session, redis_client)
        self.tax_manager = TaxComplianceManager(db_session, redis_client)
        
    async def conduct_comprehensive_financial_compliance_assessment(self, 
                                                                  organization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive financial compliance assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Payment compliance assessment
            payment_compliance = None
            if "payment_processors" in organization_data:
                payment_assessments = []
                for processor_info in organization_data["payment_processors"]:
                    assessment = await self.payment_security.assess_payment_compliance(
                        processor_info["name"],
                        processor_info["config"]
                    )
                    payment_assessments.append(assessment.__dict__)
                payment_compliance = payment_assessments
            
            # AML assessments for customers
            aml_assessments = []
            if "customers" in organization_data:
                for customer in organization_data["customers"][:5]:  # Limit to 5 for demo
                    transactions = customer.get("transactions", [])
                    financial_transactions = [
                        FinancialTransaction(
                            transaction_id=t["id"],
                            user_id=customer["id"],
                            amount=Decimal(str(t["amount"])),
                            currency=t.get("currency", "USD"),
                            payment_method=PaymentMethod(t.get("payment_method", "credit_card")),
                            transaction_type=t.get("type", "payment"),
                            timestamp=datetime.fromisoformat(t["timestamp"]) if "timestamp" in t else datetime.utcnow(),
                            merchant_id=t.get("merchant_id"),
                            description=t.get("description", ""),
                            risk_level=TransactionRiskLevel.LOW,
                            aml_status=AMLStatus.CLEARED,
                            compliance_flags=[],
                            geo_location=t.get("geo_location"),
                            ip_address=t.get("ip_address"),
                            device_fingerprint=t.get("device_fingerprint")
                        ) for t in transactions
                    ]
                    
                    aml_assessment = await self.aml_monitor.conduct_aml_assessment(
                        customer["id"],
                        customer,
                        financial_transactions
                    )
                    aml_assessments.append(aml_assessment.__dict__)
            
            # Tax compliance assessments
            tax_assessments = []
            if "tax_jurisdictions" in organization_data:
                for jurisdiction_data in organization_data["tax_jurisdictions"]:
                    jurisdiction = TaxJurisdiction(jurisdiction_data["jurisdiction"])
                    tax_assessment = await self.tax_manager.assess_tax_compliance(
                        jurisdiction,
                        jurisdiction_data.get("tax_year", datetime.utcnow().year),
                        jurisdiction_data["financial_data"]
                    )
                    tax_assessments.append(tax_assessment.__dict__)
            
            # Calculate overall financial compliance score
            overall_score = await self._calculate_overall_financial_compliance_score(
                payment_compliance, aml_assessments, tax_assessments
            )
            
            # Generate comprehensive recommendations
            recommendations = await self._generate_financial_compliance_recommendations(
                payment_compliance, aml_assessments, tax_assessments, overall_score
            )
            
            # Determine compliance status
            compliance_status = await self._determine_financial_compliance_status(overall_score)
            
            comprehensive_assessment = {
                "assessment_id": assessment_id,
                "payment_compliance": payment_compliance,
                "aml_assessments": aml_assessments,
                "tax_compliance": tax_assessments,
                "overall_compliance_score": overall_score,
                "compliance_status": compliance_status,
                "recommendations": recommendations,
                "assessment_date": datetime.utcnow().isoformat(),
                "next_review_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
            
            # Cache assessment
            await self.redis.setex(f"financial_compliance_assessment:{assessment_id}", 3600 * 24 * 7,
                                  json.dumps(comprehensive_assessment, default=str))
            
            return comprehensive_assessment
            
        except Exception as e:
            logger.error(f"Financial compliance assessment failed: {str(e)}")
            raise
    
    async def _calculate_overall_financial_compliance_score(self, 
                                                          payment_compliance: Optional[List[Dict[str, Any]]],
                                                          aml_assessments: List[Dict[str, Any]],
                                                          tax_assessments: List[Dict[str, Any]]) -> float:
        """Calculate overall financial compliance score"""
        scores = []
        weights = []
        
        # Payment compliance score
        if payment_compliance:
            payment_scores = [assessment["compliance_score"] for assessment in payment_compliance]
            if payment_scores:
                scores.append(sum(payment_scores) / len(payment_scores))
                weights.append(0.3)
        
        # AML compliance score
        if aml_assessments:
            aml_scores = []
            for assessment in aml_assessments:
                # Convert risk score to compliance score (inverse relationship)
                risk_score = assessment.get("risk_score", 0.5)
                compliance_score = 1.0 - risk_score
                aml_scores.append(compliance_score)
            
            if aml_scores:
                scores.append(sum(aml_scores) / len(aml_scores))
                weights.append(0.4)
        
        # Tax compliance score
        if tax_assessments:
            tax_scores = []
            for assessment in tax_assessments:
                status = assessment.get("compliance_status", "pending_review")
                if status == "compliant":
                    tax_scores.append(1.0)
                elif status == "partially_compliant":
                    tax_scores.append(0.7)
                elif status == "pending_review":
                    tax_scores.append(0.6)
                elif status == "requires_action":
                    tax_scores.append(0.4)
                else:  # non_compliant
                    tax_scores.append(0.2)
            
            if tax_scores:
                scores.append(sum(tax_scores) / len(tax_scores))
                weights.append(0.3)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            weighted_score = sum(score * weight for score, weight in zip(scores, normalized_weights))
            return max(0.0, min(1.0, weighted_score))
        
        return 0.5  # Default score if no data
    
    async def _generate_financial_compliance_recommendations(self, 
                                                           payment_compliance: Optional[List[Dict[str, Any]]],
                                                           aml_assessments: List[Dict[str, Any]],
                                                           tax_assessments: List[Dict[str, Any]],
                                                           overall_score: float) -> List[str]:
        """Generate comprehensive financial compliance recommendations"""
        recommendations = []
        
        # Overall score recommendations
        if overall_score < 0.6:
            recommendations.append("Urgent: Comprehensive financial compliance review required")
            recommendations.append("Engage financial compliance specialists immediately")
        
        # Payment compliance recommendations
        if payment_compliance:
            for assessment in payment_compliance:
                if assessment.get("compliance_score", 0) < 0.7:
                    recommendations.extend(assessment.get("recommendations", []))
        
        # AML recommendations
        high_risk_customers = [a for a in aml_assessments if a.get("risk_score", 0) > 0.7]
        if high_risk_customers:
            recommendations.append("Enhanced monitoring for high-risk customers required")
            recommendations.append("Review and update AML policies and procedures")
        
        # Tax compliance recommendations
        non_compliant_tax = [a for a in tax_assessments if a.get("compliance_status") == "non_compliant"]
        if non_compliant_tax:
            recommendations.append("Immediate action required for tax compliance issues")
            recommendations.append("Consult with tax professionals for remediation")
        
        # General financial compliance recommendations
        recommendations.extend([
            "Implement comprehensive financial compliance management system",
            "Regular staff training on financial regulations",
            "Establish financial compliance monitoring and reporting",
            "Regular external compliance audits",
            "Maintain up-to-date compliance documentation"
        ])
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations
    
    async def _determine_financial_compliance_status(self, overall_score: float) -> str:
        """Determine overall financial compliance status"""
        if overall_score >= 0.9:
            return "excellent_compliance"
        elif overall_score >= 0.8:
            return "good_compliance"
        elif overall_score >= 0.7:
            return "adequate_compliance"
        elif overall_score >= 0.5:
            return "needs_improvement"
        else:
            return "critical_compliance_issues"


# Export main classes
__all__ = [
    "FinancialCompliance",
    "PaymentSecurityManager",
    "AMLMonitor",
    "TaxComplianceManager",
    "FinancialRegulation",
    "PaymentMethod",
    "TransactionRiskLevel",
    "ComplianceStatus",
    "AMLStatus",
    "TaxJurisdiction",
    "FinancialTransaction",
    "PaymentCompliance",
    "AMLAssessment",
    "KYCProfile",
    "TaxCompliance"
]
