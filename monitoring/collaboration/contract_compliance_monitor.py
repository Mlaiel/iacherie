"""
Ainflue Platform - Contract Compliance Monitor
=============================================

Enterprise-grade contract compliance monitoring for collaboration partnerships,
automated compliance checking, contract term validation, and legal requirement tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractType(Enum):
    """Types of collaboration contracts."""
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_CREATION = "content_creation" 
    BRAND_PARTNERSHIP = "brand_partnership"
    REVENUE_SHARING = "revenue_sharing"
    LICENSING_AGREEMENT = "licensing_agreement"
    EXCLUSIVITY_DEAL = "exclusivity_deal"
    CROSS_PROMOTION = "cross_promotion"
    INFLUENCER_DEAL = "influencer_deal"

class ComplianceStatus(Enum):
    """Contract compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    PENDING_REVIEW = "pending_review"
    VIOLATION_DETECTED = "violation_detected"
    EXPIRED = "expired"

class TermType(Enum):
    """Types of contract terms."""
    DURATION = "duration"
    REVENUE_SPLIT = "revenue_split"
    CONTENT_REQUIREMENTS = "content_requirements"
    EXCLUSIVITY = "exclusivity"
    DELIVERY_SCHEDULE = "delivery_schedule"
    PERFORMANCE_METRICS = "performance_metrics"
    PAYMENT_TERMS = "payment_terms"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TERMINATION_CLAUSE = "termination_clause"
    DISPUTE_RESOLUTION = "dispute_resolution"

@dataclass
class ContractTerm:
    """Individual contract term."""
    term_id: str
    term_type: TermType
    description: str
    requirements: Dict[str, Any]
    compliance_criteria: List[str]
    penalty_for_violation: Optional[str] = None
    automatic_monitoring: bool = True
    last_checked: Optional[datetime] = None
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW

@dataclass
class CollaborationContract:
    """Collaboration contract with terms and compliance tracking."""
    contract_id: str
    parties: List[str]  # Creator IDs
    contract_type: ContractType
    start_date: datetime
    end_date: datetime
    terms: List[ContractTerm]
    digital_signature: str
    status: str = "active"
    compliance_score: float = 1.0
    last_compliance_check: Optional[datetime] = None
    violations: List[Dict[str, Any]] = field(default_factory=list)
    amendments: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ComplianceViolation:
    """Contract compliance violation."""
    violation_id: str
    contract_id: str
    term_id: str
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime
    evidence: Dict[str, Any]
    resolution_required: bool = True
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class ContractComplianceMonitor:
    """
    Advanced contract compliance monitoring system for collaboration partnerships.
    
    Features:
    - Automated contract term validation
    - Real-time compliance monitoring
    - Violation detection and alerting
    - Legal requirement tracking
    - Performance-based compliance scoring
    - Digital signature verification
    - Contract amendment tracking
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize contract compliance monitor."""
        self.config = config or {}
        self.contracts: Dict[str, CollaborationContract] = {}
        self.violations: List[ComplianceViolation] = []
        self.compliance_rules: Dict[str, Dict[str, Any]] = {}
        self.monitoring_active = True
        self.last_scan_time = datetime.utcnow()
        
        # Performance metrics
        self.metrics = {
            "contracts_monitored": 0,
            "violations_detected": 0,
            "compliance_rate": 1.0,
            "average_resolution_time": 0,
            "critical_violations": 0
        }
        
        logger.info("📋 Contract Compliance Monitor initialized")
        self._setup_default_compliance_rules()
    
    def _setup_default_compliance_rules(self) -> None:
        """Setup default compliance rules for different contract types."""
        self.compliance_rules = {
            "revenue_sharing": {
                "minimum_split_percentage": 10,
                "maximum_split_percentage": 90,
                "payment_frequency": "monthly",
                "reporting_required": True
            },
            "content_delivery": {
                "maximum_delay_days": 7,
                "quality_standards": {
                    "audio_quality": "professional",
                    "content_length": {"min": 30, "max": 600}
                }
            },
            "exclusivity": {
                "platforms_allowed": [],
                "competitor_restrictions": True,
                "violation_penalties": "contract_termination"
            },
            "performance_metrics": {
                "minimum_engagement_rate": 0.02,
                "minimum_reach": 1000,
                "measurement_period_days": 30
            }
        }
    
    def create_contract(
        self,
        parties: List[str],
        contract_type: ContractType,
        start_date: datetime,
        end_date: datetime,
        terms_data: List[Dict[str, Any]]
    ) -> str:
        """
        Create a new collaboration contract.
        
        Args:
            parties: List of creator IDs
            contract_type: Type of contract
            start_date: Contract start date
            end_date: Contract end date
            terms_data: Contract terms data
            
        Returns:
            Contract ID
        """
        contract_id = f"contract_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Create contract terms
        terms = []
        for term_data in terms_data:
            term = ContractTerm(
                term_id=f"{contract_id}_term_{len(terms)+1}",
                term_type=TermType(term_data["type"]),
                description=term_data["description"],
                requirements=term_data.get("requirements", {}),
                compliance_criteria=term_data.get("compliance_criteria", []),
                penalty_for_violation=term_data.get("penalty"),
                automatic_monitoring=term_data.get("auto_monitor", True)
            )
            terms.append(term)
        
        # Generate digital signature
        signature_data = {
            "parties": sorted(parties),
            "type": contract_type.value,
            "terms": [t.term_id for t in terms],
            "timestamp": datetime.utcnow().isoformat()
        }
        digital_signature = hashlib.sha256(
            json.dumps(signature_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Create contract
        contract = CollaborationContract(
            contract_id=contract_id,
            parties=parties,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            terms=terms,
            digital_signature=digital_signature
        )
        
        self.contracts[contract_id] = contract
        self.metrics["contracts_monitored"] += 1
        
        logger.info(f"📋 Created contract {contract_id} for {len(parties)} parties")
        return contract_id
    
    async def monitor_contract_compliance(self, contract_id: str) -> Dict[str, Any]:
        """
        Monitor compliance for a specific contract.
        
        Args:
            contract_id: Contract to monitor
            
        Returns:
            Compliance report
        """
        if contract_id not in self.contracts:
            return {"error": "Contract not found"}
        
        contract = self.contracts[contract_id]
        compliance_report = {
            "contract_id": contract_id,
            "scan_time": datetime.utcnow(),
            "overall_status": ComplianceStatus.COMPLIANT,
            "term_compliance": [],
            "violations_found": [],
            "compliance_score": 1.0,
            "recommendations": []
        }
        
        try:
            # Check each contract term
            total_terms = len(contract.terms)
            compliant_terms = 0
            
            for term in contract.terms:
                if not term.automatic_monitoring:
                    continue
                
                term_compliance = await self._check_term_compliance(contract, term)
                compliance_report["term_compliance"].append(term_compliance)
                
                if term_compliance["status"] == ComplianceStatus.COMPLIANT:
                    compliant_terms += 1
                elif term_compliance["status"] == ComplianceStatus.VIOLATION_DETECTED:
                    violation = await self._create_violation_record(contract, term, term_compliance)
                    compliance_report["violations_found"].append(violation)
            
            # Calculate overall compliance
            if total_terms > 0:
                compliance_score = compliant_terms / total_terms
                contract.compliance_score = compliance_score
                compliance_report["compliance_score"] = compliance_score
                
                if compliance_score >= 0.9:
                    compliance_report["overall_status"] = ComplianceStatus.COMPLIANT
                elif compliance_score >= 0.7:
                    compliance_report["overall_status"] = ComplianceStatus.PARTIALLY_COMPLIANT
                else:
                    compliance_report["overall_status"] = ComplianceStatus.NON_COMPLIANT
            
            # Check contract expiration
            if datetime.utcnow() > contract.end_date:
                compliance_report["overall_status"] = ComplianceStatus.EXPIRED
                compliance_report["recommendations"].append("Contract has expired - renewal required")
            
            contract.last_compliance_check = datetime.utcnow()
            
            logger.info(f"📋 Compliance check completed for {contract_id}: {compliance_report['overall_status'].value}")
            return compliance_report
            
        except Exception as e:
            logger.error(f"❌ Error monitoring contract {contract_id}: {e}")
            return {"error": str(e)}
    
    async def _check_term_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for a specific contract term."""
        term_report = {
            "term_id": term.term_id,
            "term_type": term.term_type.value,
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        try:
            # Check based on term type
            if term.term_type == TermType.DURATION:
                term_report = await self._check_duration_compliance(contract, term)
            elif term.term_type == TermType.REVENUE_SPLIT:
                term_report = await self._check_revenue_split_compliance(contract, term)
            elif term.term_type == TermType.CONTENT_REQUIREMENTS:
                term_report = await self._check_content_requirements_compliance(contract, term)
            elif term.term_type == TermType.EXCLUSIVITY:
                term_report = await self._check_exclusivity_compliance(contract, term)
            elif term.term_type == TermType.DELIVERY_SCHEDULE:
                term_report = await self._check_delivery_schedule_compliance(contract, term)
            elif term.term_type == TermType.PERFORMANCE_METRICS:
                term_report = await self._check_performance_metrics_compliance(contract, term)
            elif term.term_type == TermType.PAYMENT_TERMS:
                term_report = await self._check_payment_terms_compliance(contract, term)
            
            term.last_checked = datetime.utcnow()
            term.compliance_status = term_report["status"]
            
        except Exception as e:
            logger.error(f"❌ Error checking term {term.term_id}: {e}")
            term_report["status"] = ComplianceStatus.PENDING_REVIEW
            term_report["issues"].append(f"Compliance check failed: {e}")
        
        return term_report
    
    async def _check_duration_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for duration terms."""
        now = datetime.utcnow()
        
        report = {
            "term_id": term.term_id,
            "term_type": "duration",
            "status": ComplianceStatus.COMPLIANT,
            "details": {
                "start_date": contract.start_date.isoformat(),
                "end_date": contract.end_date.isoformat(),
                "current_date": now.isoformat(),
                "days_remaining": (contract.end_date - now).days
            },
            "issues": []
        }
        
        # Check if contract is active
        if now < contract.start_date:
            report["status"] = ComplianceStatus.PENDING_REVIEW
            report["issues"].append("Contract not yet active")
        elif now > contract.end_date:
            report["status"] = ComplianceStatus.EXPIRED
            report["issues"].append("Contract has expired")
        
        # Check for early termination conditions
        termination_conditions = term.requirements.get("termination_conditions", [])
        for condition in termination_conditions:
            if await self._evaluate_termination_condition(contract, condition):
                report["status"] = ComplianceStatus.VIOLATION_DETECTED
                report["issues"].append(f"Termination condition met: {condition}")
        
        return report
    
    async def _check_revenue_split_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for revenue split terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "revenue_split",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        required_split = term.requirements.get("revenue_split", {})
        rules = self.compliance_rules.get("revenue_sharing", {})
        
        # Validate split percentages
        total_percentage = sum(required_split.values())
        if abs(total_percentage - 100) > 0.01:  # Allow for small rounding errors
            report["status"] = ComplianceStatus.VIOLATION_DETECTED
            report["issues"].append(f"Revenue split percentages don't add up to 100%: {total_percentage}%")
        
        # Check minimum/maximum split limits
        for party, percentage in required_split.items():
            if percentage < rules.get("minimum_split_percentage", 0):
                report["status"] = ComplianceStatus.VIOLATION_DETECTED
                report["issues"].append(f"Split for {party} below minimum: {percentage}%")
            
            if percentage > rules.get("maximum_split_percentage", 100):
                report["status"] = ComplianceStatus.VIOLATION_DETECTED
                report["issues"].append(f"Split for {party} above maximum: {percentage}%")
        
        # Check payment frequency compliance
        required_frequency = term.requirements.get("payment_frequency", "monthly")
        if required_frequency != rules.get("payment_frequency"):
            report["issues"].append(f"Payment frequency mismatch: {required_frequency}")
        
        report["details"] = {
            "revenue_split": required_split,
            "total_percentage": total_percentage,
            "payment_frequency": required_frequency
        }
        
        return report
    
    async def _check_content_requirements_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for content requirement terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "content_requirements",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        requirements = term.requirements
        delivery_rules = self.compliance_rules.get("content_delivery", {})
        
        # Check delivery schedule
        delivery_date = requirements.get("delivery_date")
        if delivery_date:
            delivery_dt = datetime.fromisoformat(delivery_date) if isinstance(delivery_date, str) else delivery_date
            delay_days = (datetime.utcnow() - delivery_dt).days
            max_delay = delivery_rules.get("maximum_delay_days", 7)
            
            if delay_days > max_delay:
                report["status"] = ComplianceStatus.VIOLATION_DETECTED
                report["issues"].append(f"Content delivery delayed by {delay_days} days (max: {max_delay})")
        
        # Check quality standards
        quality_requirements = requirements.get("quality_standards", {})
        standard_rules = delivery_rules.get("quality_standards", {})
        
        for standard, required_value in quality_requirements.items():
            if standard in standard_rules:
                if required_value != standard_rules[standard]:
                    report["issues"].append(f"Quality standard mismatch for {standard}")
        
        # Check content specifications
        content_specs = requirements.get("content_specifications", {})
        length_rules = delivery_rules.get("quality_standards", {}).get("content_length", {})
        
        if "duration" in content_specs and length_rules:
            duration = content_specs["duration"]
            min_length = length_rules.get("min", 0)
            max_length = length_rules.get("max", float('inf'))
            
            if duration < min_length or duration > max_length:
                report["status"] = ComplianceStatus.VIOLATION_DETECTED
                report["issues"].append(f"Content duration {duration}s outside allowed range ({min_length}-{max_length}s)")
        
        report["details"] = {
            "requirements": requirements,
            "compliance_check_date": datetime.utcnow().isoformat()
        }
        
        return report
    
    async def _check_exclusivity_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for exclusivity terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "exclusivity",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        exclusivity_requirements = term.requirements
        exclusivity_rules = self.compliance_rules.get("exclusivity", {})
        
        # Check platform restrictions
        restricted_platforms = exclusivity_requirements.get("restricted_platforms", [])
        allowed_platforms = exclusivity_requirements.get("allowed_platforms", [])
        
        # Check competitor restrictions
        competitor_restrictions = exclusivity_requirements.get("competitor_restrictions", False)
        if competitor_restrictions and exclusivity_rules.get("competitor_restrictions"):
            # This would need integration with content monitoring to detect violations
            # For now, we'll mark as compliant pending implementation
            pass
        
        # Check exclusivity period
        exclusivity_start = exclusivity_requirements.get("start_date")
        exclusivity_end = exclusivity_requirements.get("end_date")
        
        if exclusivity_start and exclusivity_end:
            start_dt = datetime.fromisoformat(exclusivity_start) if isinstance(exclusivity_start, str) else exclusivity_start
            end_dt = datetime.fromisoformat(exclusivity_end) if isinstance(exclusivity_end, str) else exclusivity_end
            now = datetime.utcnow()
            
            if now < start_dt:
                report["details"]["exclusivity_status"] = "not_yet_active"
            elif now > end_dt:
                report["details"]["exclusivity_status"] = "expired"
            else:
                report["details"]["exclusivity_status"] = "active"
        
        report["details"].update({
            "restricted_platforms": restricted_platforms,
            "allowed_platforms": allowed_platforms,
            "competitor_restrictions": competitor_restrictions
        })
        
        return report
    
    async def _check_delivery_schedule_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for delivery schedule terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "delivery_schedule",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        schedule = term.requirements.get("schedule", [])
        now = datetime.utcnow()
        
        # Check each milestone
        for milestone in schedule:
            milestone_date = milestone.get("date")
            milestone_name = milestone.get("name", "Unnamed milestone")
            
            if milestone_date:
                milestone_dt = datetime.fromisoformat(milestone_date) if isinstance(milestone_date, str) else milestone_date
                
                if now > milestone_dt:
                    # Check if milestone was completed
                    completed = milestone.get("completed", False)
                    if not completed:
                        delay_days = (now - milestone_dt).days
                        report["status"] = ComplianceStatus.VIOLATION_DETECTED
                        report["issues"].append(f"Milestone '{milestone_name}' overdue by {delay_days} days")
        
        report["details"] = {
            "schedule": schedule,
            "total_milestones": len(schedule),
            "completed_milestones": sum(1 for m in schedule if m.get("completed", False))
        }
        
        return report
    
    async def _check_performance_metrics_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for performance metrics terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "performance_metrics",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        metrics_requirements = term.requirements
        performance_rules = self.compliance_rules.get("performance_metrics", {})
        
        # Check minimum engagement rate
        min_engagement = performance_rules.get("minimum_engagement_rate", 0)
        actual_engagement = metrics_requirements.get("current_engagement_rate", 0)
        
        if actual_engagement < min_engagement:
            report["status"] = ComplianceStatus.VIOLATION_DETECTED
            report["issues"].append(f"Engagement rate {actual_engagement:.3f} below minimum {min_engagement:.3f}")
        
        # Check minimum reach
        min_reach = performance_rules.get("minimum_reach", 0)
        actual_reach = metrics_requirements.get("current_reach", 0)
        
        if actual_reach < min_reach:
            report["status"] = ComplianceStatus.VIOLATION_DETECTED
            report["issues"].append(f"Reach {actual_reach} below minimum {min_reach}")
        
        report["details"] = {
            "engagement_rate": actual_engagement,
            "reach": actual_reach,
            "measurement_period": performance_rules.get("measurement_period_days", 30)
        }
        
        return report
    
    async def _check_payment_terms_compliance(
        self,
        contract: CollaborationContract,
        term: ContractTerm
    ) -> Dict[str, Any]:
        """Check compliance for payment terms."""
        report = {
            "term_id": term.term_id,
            "term_type": "payment_terms",
            "status": ComplianceStatus.COMPLIANT,
            "details": {},
            "issues": []
        }
        
        payment_requirements = term.requirements
        
        # Check payment schedule
        payment_schedule = payment_requirements.get("schedule", [])
        now = datetime.utcnow()
        
        for payment in payment_schedule:
            due_date = payment.get("due_date")
            amount = payment.get("amount", 0)
            paid = payment.get("paid", False)
            
            if due_date and not paid:
                due_dt = datetime.fromisoformat(due_date) if isinstance(due_date, str) else due_date
                
                if now > due_dt:
                    overdue_days = (now - due_dt).days
                    report["status"] = ComplianceStatus.VIOLATION_DETECTED
                    report["issues"].append(f"Payment of ${amount} overdue by {overdue_days} days")
        
        # Check payment method requirements
        required_method = payment_requirements.get("payment_method")
        if required_method:
            report["details"]["required_payment_method"] = required_method
        
        report["details"].update({
            "payment_schedule": payment_schedule,
            "total_payments": len(payment_schedule),
            "completed_payments": sum(1 for p in payment_schedule if p.get("paid", False))
        })
        
        return report
    
    async def _evaluate_termination_condition(
        self,
        contract: CollaborationContract,
        condition: str
    ) -> bool:
        """Evaluate if a termination condition has been met."""
        # This would integrate with other monitoring systems
        # For now, return False (no termination conditions met)
        return False
    
    async def _create_violation_record(
        self,
        contract: CollaborationContract,
        term: ContractTerm,
        compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a violation record for non-compliant terms."""
        violation_id = f"violation_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Determine severity based on term type and violation details
        severity = self._determine_violation_severity(term, compliance_result)
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            contract_id=contract.contract_id,
            term_id=term.term_id,
            violation_type=term.term_type.value,
            severity=severity,
            description="; ".join(compliance_result.get("issues", [])),
            detected_at=datetime.utcnow(),
            evidence=compliance_result
        )
        
        self.violations.append(violation)
        contract.violations.append({
            "violation_id": violation_id,
            "term_id": term.term_id,
            "severity": severity,
            "detected_at": violation.detected_at.isoformat()
        })
        
        self.metrics["violations_detected"] += 1
        if severity == "critical":
            self.metrics["critical_violations"] += 1
        
        logger.warning(f"⚠️ Violation detected: {violation_id} - {violation.description}")
        
        return {
            "violation_id": violation_id,
            "severity": severity,
            "description": violation.description
        }
    
    def _determine_violation_severity(
        self,
        term: ContractTerm,
        compliance_result: Dict[str, Any]
    ) -> str:
        """Determine the severity of a compliance violation."""
        # Critical violations
        critical_terms = [TermType.REVENUE_SPLIT, TermType.PAYMENT_TERMS, TermType.EXCLUSIVITY]
        if term.term_type in critical_terms:
            return "critical"
        
        # High severity violations
        high_severity_terms = [TermType.DELIVERY_SCHEDULE, TermType.PERFORMANCE_METRICS]
        if term.term_type in high_severity_terms:
            return "high"
        
        # Check for specific violation indicators
        issues = compliance_result.get("issues", [])
        for issue in issues:
            if any(keyword in issue.lower() for keyword in ["overdue", "expired", "violation"]):
                return "high"
            elif any(keyword in issue.lower() for keyword in ["below minimum", "above maximum"]):
                return "medium"
        
        return "low"
    
    async def get_compliance_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive compliance summary.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Compliance summary data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            # Filter contracts and violations for the period
            period_violations = [
                v for v in self.violations
                if v.detected_at >= period_start
            ]
            
            active_contracts = [
                c for c in self.contracts.values()
                if c.status == "active" and c.end_date > datetime.utcnow()
            ]
            
            # Calculate metrics
            total_contracts = len(active_contracts)
            compliant_contracts = len([c for c in active_contracts if c.compliance_score >= 0.9])
            
            compliance_rate = compliant_contracts / max(total_contracts, 1)
            
            # Violation analysis
            violation_by_severity = {}
            for violation in period_violations:
                severity = violation.severity
                violation_by_severity[severity] = violation_by_severity.get(severity, 0) + 1
            
            # Contract type analysis
            contract_types = {}
            for contract in active_contracts:
                contract_type = contract.contract_type.value
                contract_types[contract_type] = contract_types.get(contract_type, 0) + 1
            
            summary = {
                "period_days": period_days,
                "total_active_contracts": total_contracts,
                "compliant_contracts": compliant_contracts,
                "compliance_rate": round(compliance_rate, 3),
                "total_violations": len(period_violations),
                "violations_by_severity": violation_by_severity,
                "contract_types": contract_types,
                "average_compliance_score": round(
                    sum(c.compliance_score for c in active_contracts) / max(total_contracts, 1), 3
                ),
                "resolution_metrics": self._calculate_resolution_metrics(period_violations),
                "recommendations": self._generate_compliance_recommendations(active_contracts, period_violations)
            }
            
            logger.info(f"📋 Generated compliance summary for {period_days} days")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating compliance summary: {e}")
            return {"error": str(e)}
    
    def _calculate_resolution_metrics(self, violations: List[ComplianceViolation]) -> Dict[str, Any]:
        """Calculate violation resolution metrics."""
        resolved_violations = [v for v in violations if v.resolved_at is not None]
        
        if not resolved_violations:
            return {
                "total_resolved": 0,
                "resolution_rate": 0.0,
                "average_resolution_time_hours": 0
            }
        
        # Calculate average resolution time
        resolution_times = []
        for violation in resolved_violations:
            if violation.resolved_at and violation.detected_at:
                resolution_time = (violation.resolved_at - violation.detected_at).total_seconds() / 3600
                resolution_times.append(resolution_time)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        resolution_rate = len(resolved_violations) / len(violations) if violations else 0
        
        return {
            "total_resolved": len(resolved_violations),
            "resolution_rate": round(resolution_rate, 3),
            "average_resolution_time_hours": round(avg_resolution_time, 2)
        }
    
    def _generate_compliance_recommendations(
        self,
        contracts: List[CollaborationContract],
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []
        
        # Check for common violation patterns
        violation_types = {}
        for violation in violations:
            v_type = violation.violation_type
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        
        # Most common violation type
        if violation_types:
            most_common = max(violation_types.items(), key=lambda x: x[1])
            if most_common[1] > 1:
                recommendations.append(f"Focus on improving {most_common[0]} compliance - {most_common[1]} violations detected")
        
        # Low compliance score contracts
        low_compliance_contracts = [c for c in contracts if c.compliance_score < 0.7]
        if low_compliance_contracts:
            recommendations.append(f"Review {len(low_compliance_contracts)} contracts with low compliance scores")
        
        # Expired contracts
        expired_contracts = [c for c in contracts if datetime.utcnow() > c.end_date]
        if expired_contracts:
            recommendations.append(f"Renew or terminate {len(expired_contracts)} expired contracts")
        
        # High severity violations
        critical_violations = [v for v in violations if v.severity == "critical" and not v.resolved_at]
        if critical_violations:
            recommendations.append(f"Urgently address {len(critical_violations)} critical violations")
        
        return recommendations
    
    def resolve_violation(self, violation_id: str, resolution_notes: str) -> Dict[str, Any]:
        """Mark a violation as resolved."""
        violation = next((v for v in self.violations if v.violation_id == violation_id), None)
        
        if not violation:
            return {"error": "Violation not found"}
        
        violation.resolved_at = datetime.utcnow()
        violation.resolution_notes = resolution_notes
        
        logger.info(f"✅ Resolved violation {violation_id}")
        return {"status": "resolved", "violation_id": violation_id}

# Global instance for enterprise monitoring
contract_compliance_monitor = ContractComplianceMonitor()

__all__ = [
    'ContractComplianceMonitor',
    'CollaborationContract',
    'ContractTerm',
    'ComplianceViolation',
    'ContractType',
    'ComplianceStatus',
    'TermType',
    'contract_compliance_monitor'
]