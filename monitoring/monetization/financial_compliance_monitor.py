"""
Ainflue Platform - Financial Compliance Monitor
=============================================

Enterprise-grade financial compliance monitoring system for the Ainflue platform.
Ensures adherence to financial regulations, anti-money laundering (AML) requirements,
and international compliance standards for global payment processing.

Features:
- Real-time compliance monitoring
- AML transaction screening
- Regulatory reporting automation
- Multi-jurisdiction compliance
- Risk assessment and scoring
- Audit trail management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceRegulation(Enum):
    """Supported compliance regulations."""
    PCI_DSS = "pci_dss"              # Payment Card Industry Data Security Standard
    GDPR = "gdpr"                    # General Data Protection Regulation
    SOX = "sox"                      # Sarbanes-Oxley Act
    AML = "aml"                      # Anti-Money Laundering
    KYC = "kyc"                      # Know Your Customer
    CCPA = "ccpa"                    # California Consumer Privacy Act
    MiFID_II = "mifid_ii"            # Markets in Financial Instruments Directive
    FATCA = "fatca"                  # Foreign Account Tax Compliance Act

class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    PENDING_REVIEW = "pending_review"

class RiskLevel(Enum):
    """Compliance risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AMLRiskCategory(Enum):
    """AML risk categories."""
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    PROHIBITED = "prohibited"

@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    rule_id: str
    regulation: ComplianceRegulation
    name: str
    description: str
    risk_level: RiskLevel
    conditions: Dict[str, Any]
    actions: List[str]
    active: bool = True
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    violation_id: str
    rule_id: str
    regulation: ComplianceRegulation
    entity_id: str  # Customer, transaction, or entity ID
    entity_type: str  # customer, transaction, payment
    severity: RiskLevel
    description: str
    details: Dict[str, Any]
    detected_at: datetime = field(default_factory=datetime.now)
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class AMLAlert:
    """Anti-Money Laundering alert."""
    alert_id: str
    customer_id: str
    transaction_ids: List[str]
    alert_type: str
    risk_score: float
    risk_category: AMLRiskCategory
    triggers: List[str]
    amount_involved: float
    currency: str
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    investigator_notes: Optional[str] = None

@dataclass
class ComplianceMetrics:
    """Compliance monitoring metrics."""
    total_checks: int = 0
    compliant_checks: int = 0
    warnings: int = 0
    violations: int = 0
    critical_issues: int = 0
    compliance_rate: float = 0.0
    avg_resolution_time_hours: float = 0.0
    pending_reviews: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

class FinancialComplianceMonitor:
    """
    Enterprise financial compliance monitoring system for the Ainflue platform.
    
    Monitors compliance with financial regulations, performs AML screening,
    and ensures adherence to international compliance standards.
    """
    
    def __init__(self):
        """Initialize the financial compliance monitor."""
        self.compliance_rules: List[ComplianceRule] = []
        self.violations: List[ComplianceViolation] = []
        self.aml_alerts: List[AMLAlert] = []
        self.metrics = ComplianceMetrics()
        self.sanctioned_entities: Dict[str, Any] = {}
        self.high_risk_countries: List[str] = []
        self.compliance_thresholds: Dict[str, float] = {}
        self.audit_trail: List[Dict[str, Any]] = []
        
        logger.info("Initializing Financial Compliance Monitor")
        self._initialize_compliance_rules()
        self._load_sanctions_lists()
        self._setup_compliance_thresholds()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance monitoring rules."""
        self.compliance_rules = [
            # PCI DSS Rules
            ComplianceRule(
                rule_id="pci_001",
                regulation=ComplianceRegulation.PCI_DSS,
                name="Card Data Encryption",
                description="Ensure all card data is properly encrypted",
                risk_level=RiskLevel.CRITICAL,
                conditions={"data_encryption": True, "pci_compliance": True},
                actions=["encrypt_data", "audit_access", "notify_security_team"]
            ),
            ComplianceRule(
                rule_id="pci_002",
                regulation=ComplianceRegulation.PCI_DSS,
                name="Access Control Monitoring",
                description="Monitor access to cardholder data",
                risk_level=RiskLevel.HIGH,
                conditions={"access_logging": True, "authentication_required": True},
                actions=["log_access", "verify_authentication", "review_permissions"]
            ),
            
            # AML Rules
            ComplianceRule(
                rule_id="aml_001",
                regulation=ComplianceRegulation.AML,
                name="Large Transaction Monitoring",
                description="Monitor transactions above AML thresholds",
                risk_level=RiskLevel.HIGH,
                conditions={"transaction_amount": {"operator": ">", "value": 10000}},
                actions=["file_ctr", "investigate_source", "verify_identity"]
            ),
            ComplianceRule(
                rule_id="aml_002",
                regulation=ComplianceRegulation.AML,
                name="Suspicious Pattern Detection",
                description="Detect suspicious transaction patterns",
                risk_level=RiskLevel.MEDIUM,
                conditions={"pattern_score": {"operator": ">", "value": 0.7}},
                actions=["generate_sar", "investigate_pattern", "monitor_activity"]
            ),
            ComplianceRule(
                rule_id="aml_003",
                regulation=ComplianceRegulation.AML,
                name="Sanctions Screening",
                description="Screen against sanctions lists",
                risk_level=RiskLevel.CRITICAL,
                conditions={"sanctions_check": True},
                actions=["block_transaction", "report_authorities", "freeze_account"]
            ),
            
            # KYC Rules
            ComplianceRule(
                rule_id="kyc_001",
                regulation=ComplianceRegulation.KYC,
                name="Customer Identity Verification",
                description="Verify customer identity before onboarding",
                risk_level=RiskLevel.HIGH,
                conditions={"identity_verified": True, "documents_provided": True},
                actions=["verify_documents", "perform_background_check", "risk_assessment"]
            ),
            ComplianceRule(
                rule_id="kyc_002",
                regulation=ComplianceRegulation.KYC,
                name="Enhanced Due Diligence",
                description="Enhanced checks for high-risk customers",
                risk_level=RiskLevel.HIGH,
                conditions={"customer_risk": "high", "enhanced_checks": True},
                actions=["source_of_funds_verification", "ongoing_monitoring", "senior_approval"]
            ),
            
            # GDPR Rules
            ComplianceRule(
                rule_id="gdpr_001",
                regulation=ComplianceRegulation.GDPR,
                name="Data Processing Consent",
                description="Ensure valid consent for data processing",
                risk_level=RiskLevel.HIGH,
                conditions={"consent_obtained": True, "purpose_defined": True},
                actions=["document_consent", "limit_processing", "enable_withdrawal"]
            ),
            ComplianceRule(
                rule_id="gdpr_002",
                regulation=ComplianceRegulation.GDPR,
                name="Data Retention Compliance",
                description="Ensure data is not retained beyond legal limits",
                risk_level=RiskLevel.MEDIUM,
                conditions={"retention_period_valid": True, "deletion_scheduled": True},
                actions=["schedule_deletion", "anonymize_data", "update_records"]
            )
        ]
    
    def _load_sanctions_lists(self):
        """Load sanctions and watchlists."""
        # Sample sanctioned entities (in production, would integrate with OFAC, UN, EU lists)
        self.sanctioned_entities = {
            "individuals": [
                {"name": "BLOCKED PERSON ONE", "id": "BL001", "source": "OFAC"},
                {"name": "SANCTIONED INDIVIDUAL", "id": "BL002", "source": "UN"}
            ],
            "entities": [
                {"name": "BLOCKED ENTITY CORP", "id": "BE001", "source": "OFAC"},
                {"name": "SANCTIONED COMPANY LLC", "id": "BE002", "source": "EU"}
            ],
            "countries": [
                {"code": "XX", "name": "SANCTIONED COUNTRY", "risk_level": "prohibited"},
                {"code": "YY", "name": "HIGH RISK COUNTRY", "risk_level": "high"}
            ]
        }
        
        # High-risk countries for enhanced monitoring
        self.high_risk_countries = ["XX", "YY", "ZZ"]  # Placeholder codes
        
        logger.info("Loaded sanctions lists and high-risk countries")
    
    def _setup_compliance_thresholds(self):
        """Setup compliance monitoring thresholds."""
        self.compliance_thresholds = {
            "aml_transaction_threshold": 10000.0,
            "currency_transaction_report": 10000.0,
            "suspicious_activity_report": 5000.0,
            "enhanced_due_diligence": 25000.0,
            "wire_transfer_threshold": 3000.0,
            "cash_equivalent_threshold": 10000.0,
            "pattern_detection_score": 0.7,
            "risk_score_threshold": 0.8
        }
    
    def check_transaction_compliance(
        self,
        transaction_id: str,
        customer_id: str,
        amount: float,
        currency: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check transaction compliance against all regulations."""
        
        compliance_results = []
        violations = []
        warnings = []
        
        # Check each compliance rule
        for rule in self.compliance_rules:
            if not rule.active:
                continue
            
            check_result = self._evaluate_compliance_rule(
                rule, transaction_id, customer_id, amount, currency, transaction_data
            )
            
            compliance_results.append(check_result)
            
            if check_result["status"] == "violation":
                violation = self._create_violation(rule, transaction_id, check_result)
                violations.append(violation)
            elif check_result["status"] == "warning":
                warnings.append({
                    "rule_id": rule.rule_id,
                    "regulation": rule.regulation.value,
                    "message": check_result["message"]
                })
        
        # Perform AML screening
        aml_result = self._perform_aml_screening(transaction_id, customer_id, amount, currency, transaction_data)
        if aml_result["alerts"]:
            for alert in aml_result["alerts"]:
                violations.append(alert)
        
        # Calculate overall compliance status
        overall_status = self._determine_overall_status(compliance_results, violations, warnings)
        
        # Update metrics
        self._update_compliance_metrics(overall_status, violations, warnings)
        
        # Log compliance check
        self._log_compliance_check(transaction_id, overall_status, violations, warnings)
        
        result = {
            "transaction_id": transaction_id,
            "compliance_status": overall_status,
            "regulations_checked": len(self.compliance_rules),
            "violations": len(violations),
            "warnings": len(warnings),
            "aml_alerts": len(aml_result["alerts"]),
            "risk_score": self._calculate_compliance_risk_score(violations, warnings),
            "required_actions": self._get_required_actions(violations),
            "compliance_details": {
                "violations": [
                    {
                        "rule_id": v.rule_id,
                        "regulation": v.regulation.value,
                        "severity": v.severity.value,
                        "description": v.description
                    } for v in violations
                ],
                "warnings": warnings,
                "aml_screening": aml_result
            },
            "next_review_date": self._calculate_next_review_date(overall_status),
            "checked_at": datetime.now().isoformat()
        }
        
        logger.info(f"Compliance check for transaction {transaction_id}: {overall_status}, {len(violations)} violations")
        return result
    
    def _evaluate_compliance_rule(
        self,
        rule: ComplianceRule,
        transaction_id: str,
        customer_id: str,
        amount: float,
        currency: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a specific compliance rule."""
        
        try:
            # Rule-specific evaluation logic
            if rule.regulation == ComplianceRegulation.PCI_DSS:
                return self._check_pci_compliance(rule, transaction_data)
            
            elif rule.regulation == ComplianceRegulation.AML:
                return self._check_aml_compliance(rule, amount, currency, transaction_data)
            
            elif rule.regulation == ComplianceRegulation.KYC:
                return self._check_kyc_compliance(rule, customer_id, transaction_data)
            
            elif rule.regulation == ComplianceRegulation.GDPR:
                return self._check_gdpr_compliance(rule, customer_id, transaction_data)
            
            else:
                # Generic rule evaluation
                return self._evaluate_generic_rule(rule, transaction_data)
        
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return {
                "rule_id": rule.rule_id,
                "status": "error",
                "message": f"Rule evaluation failed: {str(e)}"
            }
    
    def _check_pci_compliance(self, rule: ComplianceRule, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PCI DSS compliance."""
        
        if rule.rule_id == "pci_001":
            # Check data encryption
            encryption_enabled = transaction_data.get("encryption_enabled", False)
            pci_compliant = transaction_data.get("pci_compliant", False)
            
            if not encryption_enabled or not pci_compliant:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": "Card data encryption not properly implemented"
                }
        
        elif rule.rule_id == "pci_002":
            # Check access controls
            access_logged = transaction_data.get("access_logged", False)
            auth_required = transaction_data.get("authentication_required", False)
            
            if not access_logged:
                return {
                    "rule_id": rule.rule_id,
                    "status": "warning",
                    "message": "Access to cardholder data not properly logged"
                }
        
        return {
            "rule_id": rule.rule_id,
            "status": "compliant",
            "message": "PCI DSS requirements met"
        }
    
    def _check_aml_compliance(
        self,
        rule: ComplianceRule,
        amount: float,
        currency: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check AML compliance."""
        
        if rule.rule_id == "aml_001":
            # Large transaction threshold
            threshold = self.compliance_thresholds["aml_transaction_threshold"]
            if amount >= threshold:
                return {
                    "rule_id": rule.rule_id,
                    "status": "warning",
                    "message": f"Transaction above AML threshold: {amount} {currency}"
                }
        
        elif rule.rule_id == "aml_002":
            # Suspicious pattern detection
            pattern_score = transaction_data.get("pattern_risk_score", 0.0)
            if pattern_score > 0.7:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": f"Suspicious transaction pattern detected: score {pattern_score}"
                }
        
        elif rule.rule_id == "aml_003":
            # Sanctions screening (handled separately)
            pass
        
        return {
            "rule_id": rule.rule_id,
            "status": "compliant",
            "message": "AML requirements met"
        }
    
    def _check_kyc_compliance(self, rule: ComplianceRule, customer_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check KYC compliance."""
        
        customer_data = transaction_data.get("customer_data", {})
        
        if rule.rule_id == "kyc_001":
            # Identity verification
            identity_verified = customer_data.get("identity_verified", False)
            documents_provided = customer_data.get("documents_provided", False)
            
            if not identity_verified or not documents_provided:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": "Customer identity not properly verified"
                }
        
        elif rule.rule_id == "kyc_002":
            # Enhanced due diligence
            customer_risk = customer_data.get("risk_level", "low")
            enhanced_checks = customer_data.get("enhanced_due_diligence", False)
            
            if customer_risk == "high" and not enhanced_checks:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": "Enhanced due diligence required for high-risk customer"
                }
        
        return {
            "rule_id": rule.rule_id,
            "status": "compliant",
            "message": "KYC requirements met"
        }
    
    def _check_gdpr_compliance(self, rule: ComplianceRule, customer_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR compliance."""
        
        customer_data = transaction_data.get("customer_data", {})
        
        if rule.rule_id == "gdpr_001":
            # Data processing consent
            consent_obtained = customer_data.get("gdpr_consent", False)
            purpose_defined = customer_data.get("processing_purpose_defined", False)
            
            if not consent_obtained or not purpose_defined:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": "Valid GDPR consent not obtained or purpose not defined"
                }
        
        elif rule.rule_id == "gdpr_002":
            # Data retention
            retention_valid = customer_data.get("retention_period_valid", True)
            deletion_scheduled = customer_data.get("deletion_scheduled", True)
            
            if not retention_valid or not deletion_scheduled:
                return {
                    "rule_id": rule.rule_id,
                    "status": "warning",
                    "message": "Data retention period may exceed GDPR limits"
                }
        
        return {
            "rule_id": rule.rule_id,
            "status": "compliant",
            "message": "GDPR requirements met"
        }
    
    def _evaluate_generic_rule(self, rule: ComplianceRule, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate generic compliance rule."""
        
        conditions = rule.conditions
        
        for condition_key, condition_value in conditions.items():
            data_value = transaction_data.get(condition_key)
            
            if isinstance(condition_value, dict) and "operator" in condition_value:
                operator = condition_value["operator"]
                threshold = condition_value["value"]
                
                if operator == ">" and (data_value is None or data_value <= threshold):
                    return {
                        "rule_id": rule.rule_id,
                        "status": "violation",
                        "message": f"Condition not met: {condition_key} {operator} {threshold}"
                    }
                elif operator == "<" and (data_value is None or data_value >= threshold):
                    return {
                        "rule_id": rule.rule_id,
                        "status": "violation", 
                        "message": f"Condition not met: {condition_key} {operator} {threshold}"
                    }
            
            elif data_value != condition_value:
                return {
                    "rule_id": rule.rule_id,
                    "status": "violation",
                    "message": f"Condition not met: {condition_key} = {condition_value}"
                }
        
        return {
            "rule_id": rule.rule_id,
            "status": "compliant",
            "message": "All conditions met"
        }
    
    def _perform_aml_screening(
        self,
        transaction_id: str,
        customer_id: str,
        amount: float,
        currency: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive AML screening."""
        
        alerts = []
        
        # Sanctions screening
        sanctions_result = self._screen_against_sanctions(customer_id, transaction_data)
        if sanctions_result["match_found"]:
            alert = AMLAlert(
                alert_id=f"aml_{uuid.uuid4().hex[:8]}",
                customer_id=customer_id,
                transaction_ids=[transaction_id],
                alert_type="sanctions_match",
                risk_score=1.0,
                risk_category=AMLRiskCategory.PROHIBITED,
                triggers=sanctions_result["matches"],
                amount_involved=amount,
                currency=currency
            )
            alerts.append(alert)
            self.aml_alerts.append(alert)
        
        # Pattern analysis
        pattern_result = self._analyze_transaction_patterns(customer_id, transaction_id, amount, transaction_data)
        if pattern_result["suspicious"]:
            alert = AMLAlert(
                alert_id=f"aml_{uuid.uuid4().hex[:8]}",
                customer_id=customer_id,
                transaction_ids=[transaction_id],
                alert_type="suspicious_pattern",
                risk_score=pattern_result["risk_score"],
                risk_category=self._categorize_aml_risk(pattern_result["risk_score"]),
                triggers=pattern_result["triggers"],
                amount_involved=amount,
                currency=currency
            )
            alerts.append(alert)
            self.aml_alerts.append(alert)
        
        # High-value transaction check
        if amount >= self.compliance_thresholds["currency_transaction_report"]:
            alert = AMLAlert(
                alert_id=f"aml_{uuid.uuid4().hex[:8]}",
                customer_id=customer_id,
                transaction_ids=[transaction_id],
                alert_type="large_transaction",
                risk_score=0.6,
                risk_category=AMLRiskCategory.MEDIUM_RISK,
                triggers=["large_amount"],
                amount_involved=amount,
                currency=currency
            )
            alerts.append(alert)
            self.aml_alerts.append(alert)
        
        return {
            "screening_completed": True,
            "alerts": alerts,
            "sanctions_checked": True,
            "pattern_analysis_completed": True,
            "risk_assessment": self._assess_overall_aml_risk(alerts)
        }
    
    def _screen_against_sanctions(self, customer_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen customer and transaction against sanctions lists."""
        
        matches = []
        customer_data = transaction_data.get("customer_data", {})
        
        # Customer name screening
        customer_name = customer_data.get("name", "").upper()
        for individual in self.sanctioned_entities["individuals"]:
            if individual["name"] in customer_name or customer_name in individual["name"]:
                matches.append(f"Name match: {individual['name']} ({individual['source']})")
        
        # Entity screening (if business customer)
        if customer_data.get("entity_type") == "business":
            entity_name = customer_data.get("business_name", "").upper()
            for entity in self.sanctioned_entities["entities"]:
                if entity["name"] in entity_name or entity_name in entity["name"]:
                    matches.append(f"Entity match: {entity['name']} ({entity['source']})")
        
        # Country screening
        customer_country = customer_data.get("country", "")
        if customer_country in self.high_risk_countries:
            matches.append(f"High-risk country: {customer_country}")
        
        return {
            "match_found": len(matches) > 0,
            "matches": matches,
            "screening_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_transaction_patterns(
        self,
        customer_id: str,
        transaction_id: str,
        amount: float,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze transaction patterns for suspicious activity."""
        
        triggers = []
        risk_factors = []
        
        # Velocity analysis
        recent_transactions = transaction_data.get("recent_transactions", [])
        if len(recent_transactions) > 10:  # High velocity
            triggers.append("high_transaction_velocity")
            risk_factors.append(0.3)
        
        # Amount patterns
        if amount > transaction_data.get("average_transaction_amount", 0) * 5:
            triggers.append("unusually_large_amount")
            risk_factors.append(0.4)
        
        # Geographic patterns
        if transaction_data.get("geographic_anomaly", False):
            triggers.append("geographic_anomaly")
            risk_factors.append(0.3)
        
        # Time patterns
        transaction_hour = datetime.now().hour
        if transaction_hour < 6 or transaction_hour > 22:  # Unusual hours
            triggers.append("unusual_transaction_time")
            risk_factors.append(0.2)
        
        # Structuring detection
        if self._detect_structuring(customer_id, amount, recent_transactions):
            triggers.append("potential_structuring")
            risk_factors.append(0.6)
        
        # Calculate overall risk score
        risk_score = min(1.0, sum(risk_factors)) if risk_factors else 0.0
        
        return {
            "suspicious": risk_score > 0.5,
            "risk_score": risk_score,
            "triggers": triggers,
            "pattern_analysis_timestamp": datetime.now().isoformat()
        }
    
    def _detect_structuring(self, customer_id: str, amount: float, recent_transactions: List[Dict]) -> bool:
        """Detect potential structuring (breaking large amounts into smaller transactions)."""
        
        # Check for multiple transactions just below reporting threshold
        threshold = self.compliance_thresholds["currency_transaction_report"]
        
        recent_large_transactions = [
            t for t in recent_transactions 
            if t.get("amount", 0) > threshold * 0.8 and t.get("amount", 0) < threshold
        ]
        
        # If multiple transactions just below threshold within short time period
        if len(recent_large_transactions) >= 3:
            total_amount = sum(t.get("amount", 0) for t in recent_large_transactions)
            if total_amount > threshold * 1.5:
                return True
        
        return False
    
    def _categorize_aml_risk(self, risk_score: float) -> AMLRiskCategory:
        """Categorize AML risk based on score."""
        if risk_score >= 0.9:
            return AMLRiskCategory.PROHIBITED
        elif risk_score >= 0.7:
            return AMLRiskCategory.HIGH_RISK
        elif risk_score >= 0.4:
            return AMLRiskCategory.MEDIUM_RISK
        else:
            return AMLRiskCategory.LOW_RISK
    
    def _assess_overall_aml_risk(self, alerts: List[AMLAlert]) -> Dict[str, Any]:
        """Assess overall AML risk for the transaction."""
        
        if not alerts:
            return {"risk_level": "low", "risk_score": 0.1}
        
        max_risk_score = max(alert.risk_score for alert in alerts)
        risk_categories = [alert.risk_category for alert in alerts]
        
        if AMLRiskCategory.PROHIBITED in risk_categories:
            risk_level = "prohibited"
        elif AMLRiskCategory.HIGH_RISK in risk_categories:
            risk_level = "high"
        elif AMLRiskCategory.MEDIUM_RISK in risk_categories:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": max_risk_score,
            "alert_count": len(alerts),
            "immediate_action_required": risk_level in ["prohibited", "high"]
        }
    
    def _create_violation(self, rule: ComplianceRule, entity_id: str, check_result: Dict[str, Any]) -> ComplianceViolation:
        """Create compliance violation record."""
        
        violation = ComplianceViolation(
            violation_id=f"viol_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            regulation=rule.regulation,
            entity_id=entity_id,
            entity_type="transaction",
            severity=rule.risk_level,
            description=check_result["message"],
            details=check_result
        )
        
        self.violations.append(violation)
        return violation
    
    def _determine_overall_status(
        self,
        compliance_results: List[Dict[str, Any]],
        violations: List[ComplianceViolation],
        warnings: List[Dict[str, Any]]
    ) -> str:
        """Determine overall compliance status."""
        
        critical_violations = [v for v in violations if v.severity == RiskLevel.CRITICAL]
        high_violations = [v for v in violations if v.severity == RiskLevel.HIGH]
        
        if critical_violations:
            return ComplianceStatus.CRITICAL.value
        elif high_violations:
            return ComplianceStatus.VIOLATION.value
        elif violations:
            return ComplianceStatus.WARNING.value
        elif warnings:
            return ComplianceStatus.WARNING.value
        else:
            return ComplianceStatus.COMPLIANT.value
    
    def _calculate_compliance_risk_score(
        self,
        violations: List[ComplianceViolation],
        warnings: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall compliance risk score."""
        
        if not violations and not warnings:
            return 0.1
        
        risk_scores = []
        
        # Add violation scores
        for violation in violations:
            if violation.severity == RiskLevel.CRITICAL:
                risk_scores.append(1.0)
            elif violation.severity == RiskLevel.HIGH:
                risk_scores.append(0.8)
            elif violation.severity == RiskLevel.MEDIUM:
                risk_scores.append(0.6)
            else:
                risk_scores.append(0.4)
        
        # Add warning scores
        for warning in warnings:
            risk_scores.append(0.3)
        
        return min(1.0, max(risk_scores) if risk_scores else 0.1)
    
    def _get_required_actions(self, violations: List[ComplianceViolation]) -> List[str]:
        """Get required actions based on violations."""
        
        actions = []
        
        for violation in violations:
            # Find the rule and get its actions
            for rule in self.compliance_rules:
                if rule.rule_id == violation.rule_id:
                    actions.extend(rule.actions)
                    break
        
        # Remove duplicates and return
        return list(set(actions))
    
    def _calculate_next_review_date(self, status: str) -> str:
        """Calculate next compliance review date."""
        
        if status == ComplianceStatus.CRITICAL.value:
            next_review = datetime.now() + timedelta(hours=1)
        elif status == ComplianceStatus.VIOLATION.value:
            next_review = datetime.now() + timedelta(hours=4)
        elif status == ComplianceStatus.WARNING.value:
            next_review = datetime.now() + timedelta(days=1)
        else:
            next_review = datetime.now() + timedelta(days=7)
        
        return next_review.isoformat()
    
    def _update_compliance_metrics(
        self,
        status: str,
        violations: List[ComplianceViolation],
        warnings: List[Dict[str, Any]]
    ):
        """Update compliance metrics."""
        
        self.metrics.total_checks += 1
        
        if status == ComplianceStatus.COMPLIANT.value:
            self.metrics.compliant_checks += 1
        elif status == ComplianceStatus.WARNING.value:
            self.metrics.warnings += 1
        elif status == ComplianceStatus.VIOLATION.value:
            self.metrics.violations += 1
        elif status == ComplianceStatus.CRITICAL.value:
            self.metrics.critical_issues += 1
        
        # Update compliance rate
        if self.metrics.total_checks > 0:
            self.metrics.compliance_rate = self.metrics.compliant_checks / self.metrics.total_checks
        
        self.metrics.last_updated = datetime.now()
    
    def _log_compliance_check(
        self,
        entity_id: str,
        status: str,
        violations: List[ComplianceViolation],
        warnings: List[Dict[str, Any]]
    ):
        """Log compliance check for audit trail."""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "entity_id": entity_id,
            "check_type": "transaction_compliance",
            "status": status,
            "violations_count": len(violations),
            "warnings_count": len(warnings),
            "regulations_checked": [rule.regulation.value for rule in self.compliance_rules],
            "check_id": f"check_{uuid.uuid4().hex[:8]}"
        }
        
        self.audit_trail.append(log_entry)
        
        # Keep only recent audit entries (last 10000)
        if len(self.audit_trail) > 10000:
            self.audit_trail = self.audit_trail[-10000:]
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive compliance monitoring dashboard."""
        
        # Recent violations
        recent_violations = [v for v in self.violations if (datetime.now() - v.detected_at).days <= 7]
        
        # AML alerts by category
        aml_alerts_by_category = defaultdict(int)
        for alert in self.aml_alerts:
            aml_alerts_by_category[alert.risk_category.value] += 1
        
        # Compliance by regulation
        compliance_by_regulation = defaultdict(lambda: {"total": 0, "compliant": 0, "violations": 0})
        for violation in self.violations:
            reg = violation.regulation.value
            compliance_by_regulation[reg]["violations"] += 1
        
        return {
            "overview": {
                "total_compliance_checks": self.metrics.total_checks,
                "compliance_rate": round(self.metrics.compliance_rate, 3),
                "total_violations": len(self.violations),
                "critical_issues": self.metrics.critical_issues,
                "pending_reviews": len([v for v in self.violations if v.status == ComplianceStatus.PENDING_REVIEW]),
                "aml_alerts": len(self.aml_alerts)
            },
            "performance_metrics": {
                "compliance_rate_7d": round(self._calculate_recent_compliance_rate(7), 3),
                "average_resolution_time_hours": self._calculate_avg_resolution_time(),
                "false_positive_rate": 0.05,  # Simulated
                "regulatory_coverage": len(self.compliance_rules)
            },
            "violation_breakdown": {
                "critical": len([v for v in recent_violations if v.severity == RiskLevel.CRITICAL]),
                "high": len([v for v in recent_violations if v.severity == RiskLevel.HIGH]),
                "medium": len([v for v in recent_violations if v.severity == RiskLevel.MEDIUM]),
                "low": len([v for v in recent_violations if v.severity == RiskLevel.LOW])
            },
            "aml_monitoring": {
                "total_alerts": len(self.aml_alerts),
                "alerts_by_category": dict(aml_alerts_by_category),
                "sanctions_screening_enabled": True,
                "pattern_detection_active": True
            },
            "regulatory_compliance": dict(compliance_by_regulation),
            "recent_activity": self._get_recent_compliance_activity(),
            "recommendations": self._get_compliance_recommendations(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_recent_compliance_rate(self, days: int) -> float:
        """Calculate compliance rate for recent period."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_checks = [log for log in self.audit_trail if datetime.fromisoformat(log["timestamp"]) > cutoff_date]
        
        if not recent_checks:
            return 1.0
        
        compliant_checks = len([check for check in recent_checks if check["status"] == "compliant"])
        return compliant_checks / len(recent_checks)
    
    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average violation resolution time."""
        
        resolved_violations = [v for v in self.violations if v.resolved_at is not None]
        
        if not resolved_violations:
            return 0.0
        
        resolution_times = [
            (v.resolved_at - v.detected_at).total_seconds() / 3600  # Convert to hours
            for v in resolved_violations
        ]
        
        return round(statistics.mean(resolution_times), 2)
    
    def _get_recent_compliance_activity(self) -> List[Dict[str, Any]]:
        """Get recent compliance activity."""
        
        activities = []
        
        # Recent violations
        recent_violations = sorted(
            [v for v in self.violations if (datetime.now() - v.detected_at).days <= 3],
            key=lambda x: x.detected_at,
            reverse=True
        )[:5]
        
        for violation in recent_violations:
            activities.append({
                "type": "violation",
                "description": f"{violation.regulation.value.upper()} violation: {violation.description}",
                "severity": violation.severity.value,
                "timestamp": violation.detected_at.isoformat()
            })
        
        # Recent AML alerts
        recent_alerts = sorted(
            [a for a in self.aml_alerts if (datetime.now() - a.created_at).days <= 3],
            key=lambda x: x.created_at,
            reverse=True
        )[:3]
        
        for alert in recent_alerts:
            activities.append({
                "type": "aml_alert",
                "description": f"AML alert: {alert.alert_type} (Risk: {alert.risk_category.value})",
                "severity": "high" if alert.risk_category in [AMLRiskCategory.HIGH_RISK, AMLRiskCategory.PROHIBITED] else "medium",
                "timestamp": alert.created_at.isoformat()
            })
        
        return sorted(activities, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    def _get_compliance_recommendations(self) -> List[str]:
        """Get compliance improvement recommendations."""
        
        recommendations = []
        
        # Based on violation patterns
        if self.metrics.critical_issues > 5:
            recommendations.append("Review and strengthen critical compliance controls")
        
        if self.metrics.compliance_rate < 0.95:
            recommendations.append("Implement additional compliance monitoring rules")
        
        # AML-specific recommendations
        high_risk_alerts = len([a for a in self.aml_alerts if a.risk_category in [AMLRiskCategory.HIGH_RISK, AMLRiskCategory.PROHIBITED]])
        if high_risk_alerts > 10:
            recommendations.append("Enhance AML screening procedures and customer due diligence")
        
        # Regulatory-specific recommendations
        gdpr_violations = len([v for v in self.violations if v.regulation == ComplianceRegulation.GDPR])
        if gdpr_violations > 3:
            recommendations.append("Strengthen GDPR data protection and consent management")
        
        return recommendations[:5]
    
    def resolve_violation(self, violation_id: str, resolution_notes: str) -> bool:
        """Resolve a compliance violation."""
        
        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.status = ComplianceStatus.RESOLVED
                violation.resolved_at = datetime.now()
                violation.resolution_notes = resolution_notes
                
                logger.info(f"Resolved compliance violation {violation_id}")
                return True
        
        logger.error(f"Violation {violation_id} not found")
        return False

# Initialize the global financial compliance monitor
financial_compliance_monitor = FinancialComplianceMonitor()

def create_compliance_config() -> Dict[str, Any]:
    """Create default configuration for financial compliance monitoring."""
    return {
        "supported_regulations": [reg.value for reg in ComplianceRegulation],
        "compliance_thresholds": financial_compliance_monitor.compliance_thresholds,
        "aml_screening_enabled": True,
        "sanctions_screening_enabled": True,
        "real_time_monitoring": True,
        "audit_trail_retention_days": 2555,  # 7 years
        "automated_reporting": True
    }

# Export main components
__all__ = [
    'FinancialComplianceMonitor',
    'ComplianceRegulation',
    'ComplianceStatus',
    'RiskLevel',
    'AMLRiskCategory',
    'ComplianceRule',
    'ComplianceViolation',
    'AMLAlert',
    'financial_compliance_monitor',
    'create_compliance_config'
]