"""IA Influencer Agent - Licensing Automation Metrics Collector
Enterprise metrics for automated licensing and rights management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Automated licensing transaction tracking
- Rights negotiation performance metrics
- License compliance monitoring
- Revenue generation analytics
- Contract lifecycle management
- Intellectual property protection metrics
"""import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from prometheus_client import Counter, Histogram, Gauge, Summary

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager

logger = get_logger(__name__)


class LicenseType(Enum):
    """Types of content licenses"""    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"
    NON_PROFIT = "non_profit"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"


class LicenseStatus(Enum):
    """License transaction status"""    PENDING = "pending"
    NEGOTIATING = "negotiating"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ACTIVE = "active"
    COMPLETED = "completed"


class NegotiationPhase(Enum):
    """License negotiation phases"""    INITIAL_REQUEST = "initial_request"
    TERMS_PROPOSAL = "terms_proposal"
    COUNTER_OFFER = "counter_offer"
    LEGAL_REVIEW = "legal_review"
    FINAL_APPROVAL = "final_approval"
    CONTRACT_SIGNING = "contract_signing"


class ComplianceLevel(Enum):
    """License compliance levels"""    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL_VIOLATION = "critical_violation"


@dataclass
class LicenseTransaction:
    """License transaction details"""    transaction_id: str
    license_type: LicenseType
    content_id: str
    licensee_id: str
    licensor_id: str
    amount: Decimal
    currency: str
    status: LicenseStatus
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class RightsNegotiation:
    """Rights negotiation session"""    negotiation_id: str
    content_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    current_phase: NegotiationPhase
    start_time: datetime
    proposed_amount: Decimal
    final_amount: Optional[Decimal] = None


class LicensingAutomationMetricsCollector:
    """    Comprehensive metrics collector for licensing automation
    
    Tracks:
    - License transaction volumes and values
    - Automated negotiation performance
    - Rights compliance monitoring
    - Revenue generation efficiency
    - Contract lifecycle metrics
    - IP protection effectiveness
    """    
    def __init__(self, prometheus_manager=None):
        self.prometheus_manager = prometheus_manager
        self.redis_manager = RedisManager()
        self.logger = logger
        self._active_negotiations: Dict[str, RightsNegotiation] = {}
        self._active_licenses: Dict[str, LicenseTransaction] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics for licensing automation"""        
        if not self.prometheus_manager:
            self.logger.warning("No Prometheus manager provided, metrics disabled")
            return
        
        # License Transaction Metrics
        self.license_transactions_total = Counter(
            'ia_influencer_license_transactions_total',
            'Total license transactions by type and status',
            ['license_type', 'status', 'currency', 'licensor_id', 'tenant_id']
        )
        
        self.license_transaction_value = Histogram(
            'ia_influencer_license_transaction_value',
            'License transaction values by currency',
            ['license_type', 'currency', 'licensor_type'],
            buckets=[1, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
        )
        
        self.license_processing_duration = Histogram(
            'ia_influencer_license_processing_duration_seconds',
            'Time to process license from request to approval',
            ['license_type', 'automation_level'],
            buckets=[60, 300, 900, 1800, 3600, 7200, 14400, 86400, 259200, 604800]
        )
        
        # Automated Negotiation Metrics
        self.negotiations_started_total = Counter(
            'ia_influencer_negotiations_started_total',
            'Total negotiations started by license type',
            ['license_type', 'content_type', 'automation_enabled']
        )
        
        self.negotiation_success_rate = Gauge(
            'ia_influencer_negotiation_success_rate_percent',
            'Success rate of automated negotiations',
            ['license_type', 'time_window', 'automation_level']
        )
        
        self.negotiation_rounds = Histogram(
            'ia_influencer_negotiation_rounds_count',
            'Number of negotiation rounds to reach agreement',
            ['license_type', 'outcome'],
            buckets=[1, 2, 3, 4, 5, 7, 10, 15, 20, 30]
        )
        
        self.negotiation_duration = Histogram(
            'ia_influencer_negotiation_duration_hours',
            'Duration of rights negotiations',
            ['license_type', 'outcome', 'automation_level'],
            buckets=[0.5, 1, 2, 6, 12, 24, 48, 72, 168, 336, 720]
        )
        
        # Revenue and Financial Metrics
        self.licensing_revenue_total = Counter(
            'ia_influencer_licensing_revenue_total',
            'Total licensing revenue by currency and type',
            ['currency', 'license_type', 'licensor_id', 'revenue_type']
        )
        
        self.average_license_value = Gauge(
            'ia_influencer_average_license_value',
            'Average license value by type and time window',
            ['license_type', 'currency', 'time_window']
        )
        
        self.commission_earned_total = Counter(
            'ia_influencer_commission_earned_total',
            'Total commission earned from licensing',
            ['currency', 'commission_type', 'licensor_id']
        )
        
        # Rights Compliance Metrics
        self.license_compliance_checks_total = Counter(
            'ia_influencer_license_compliance_checks_total',
            'Total compliance checks performed',
            ['license_type', 'check_type', 'result']
        )
        
        self.compliance_violations_detected_total = Counter(
            'ia_influencer_compliance_violations_detected_total',
            'Compliance violations detected by severity',
            ['violation_type', 'severity', 'license_type', 'licensee_id']
        )
        
        self.compliance_score = Gauge(
            'ia_influencer_compliance_score',
            'Compliance score by licensee and license type',
            ['licensee_id', 'license_type', 'time_window']
        )
        
        # Contract Lifecycle Metrics
        self.active_licenses_count = Gauge(
            'ia_influencer_active_licenses_count',
            'Number of currently active licenses',
            ['license_type', 'licensor_id']
        )
        
        self.license_renewals_total = Counter(
            'ia_influencer_license_renewals_total',
            'Total license renewals by type and outcome',
            ['license_type', 'renewal_outcome', 'auto_renewed']
        )
        
        self.license_expirations_total = Counter(
            'ia_influencer_license_expirations_total',
            'Total license expirations by type and action taken',
            ['license_type', 'expiration_action', 'renewed']
        )
        
        # AI Automation Performance Metrics
        self.ai_license_recommendations_total = Counter(
            'ia_influencer_ai_license_recommendations_total',
            'AI-generated license recommendations',
            ['recommendation_type', 'accepted', 'confidence_level']
        )
        
        self.ai_pricing_accuracy = Gauge(
            'ia_influencer_ai_pricing_accuracy_percent',
            'Accuracy of AI-generated pricing recommendations',
            ['license_type', 'time_window']
        )
        
        self.ai_contract_generation_time = Histogram(
            'ia_influencer_ai_contract_generation_time_seconds',
            'Time for AI to generate license contracts',
            ['contract_type', 'complexity'],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800]
        )
        
        # Platform Integration Metrics
        self.platform_licensing_requests_total = Counter(
            'ia_influencer_platform_licensing_requests_total',
            'Licensing requests from external platforms',
            ['platform', 'request_type', 'status']
        )
        
        self.platform_integration_latency = Histogram(
            'ia_influencer_platform_integration_latency_seconds',
            'Latency of platform licensing integrations',
            ['platform', 'operation_type'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
        )
        
        # Register all metrics
        self._register_metrics()
        
        self.logger.info("Licensing automation metrics initialized")
    
    def _register_metrics(self) -> None:
        """Register all metrics with Prometheus manager"""        
        metrics_to_register = [
            self.license_transactions_total,
            self.license_transaction_value,
            self.license_processing_duration,
            self.negotiations_started_total,
            self.negotiation_success_rate,
            self.negotiation_rounds,
            self.negotiation_duration,
            self.licensing_revenue_total,
            self.average_license_value,
            self.commission_earned_total,
            self.license_compliance_checks_total,
            self.compliance_violations_detected_total,
            self.compliance_score,
            self.active_licenses_count,
            self.license_renewals_total,
            self.license_expirations_total,
            self.ai_license_recommendations_total,
            self.ai_pricing_accuracy,
            self.ai_contract_generation_time,
            self.platform_licensing_requests_total,
            self.platform_integration_latency
        ]
        
        for metric in metrics_to_register:
            self.prometheus_manager.register_metric(metric)
    
    async def record_license_transaction(
        self,
        transaction: LicenseTransaction,
        processing_time_seconds: float,
        automation_level: str = "full",
        tenant_id: str = "default"
    ) -> None:
        """Record a new license transaction"""        
        # Store transaction
        self._active_licenses[transaction.transaction_id] = transaction
        
        # Update metrics
        self.license_transactions_total.labels(
            license_type=transaction.license_type.value,
            status=transaction.status.value,
            currency=transaction.currency,
            licensor_id=transaction.licensor_id,
            tenant_id=tenant_id
        ).inc()
        
        self.license_transaction_value.labels(
            license_type=transaction.license_type.value,
            currency=transaction.currency,
            licensor_type="creator"  # Could be determined from licensor_id
        ).observe(float(transaction.amount))
        
        self.license_processing_duration.labels(
            license_type=transaction.license_type.value,
            automation_level=automation_level
        ).observe(processing_time_seconds)
        
        # Update revenue metrics if approved
        if transaction.status == LicenseStatus.APPROVED:
            self.licensing_revenue_total.labels(
                currency=transaction.currency,
                license_type=transaction.license_type.value,
                licensor_id=transaction.licensor_id,
                revenue_type="license_fee"
            ).inc(float(transaction.amount))
            
            # Calculate and record commission (e.g., 10%)
            commission = transaction.amount * Decimal('0.10')
            self.commission_earned_total.labels(
                currency=transaction.currency,
                commission_type="licensing",
                licensor_id=transaction.licensor_id
            ).inc(float(commission))
        
        # Update active licenses count
        if transaction.status == LicenseStatus.ACTIVE:
            self.active_licenses_count.labels(
                license_type=transaction.license_type.value,
                licensor_id=transaction.licensor_id
            ).inc()
        
        # Store in Redis for persistence
        await self.redis_manager.set(
            f"license_transaction:{transaction.transaction_id}",
            transaction.__dict__,
            ttl=31536000  # 1 year
        )
        
        self.logger.info(
            f"Recorded license transaction {transaction.transaction_id}: "
            f"{transaction.license_type.value} - {transaction.currency}{transaction.amount}"
        )
    
    async def start_rights_negotiation(
        self,
        negotiation: RightsNegotiation,
        automation_enabled: bool = True
    ) -> None:
        """Start a new rights negotiation session"""        
        self._active_negotiations[negotiation.negotiation_id] = negotiation
        
        # Update metrics
        self.negotiations_started_total.labels(
            license_type=negotiation.license_type.value,
            content_type="unknown",  # Could be extracted from content_id
            automation_enabled=str(automation_enabled).lower()
        ).inc()
        
        # Store in Redis
        await self.redis_manager.set(
            f"rights_negotiation:{negotiation.negotiation_id}",
            negotiation.__dict__,
            ttl=2592000  # 30 days
        )
        
        self.logger.info(f"Started rights negotiation {negotiation.negotiation_id}")
    
    async def update_negotiation_phase(
        self,
        negotiation_id: str,
        new_phase: NegotiationPhase,
        rounds_completed: int = 0
    ) -> None:
        """Update negotiation phase and progress"""        
        if negotiation_id not in self._active_negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found")
            return
        
        negotiation = self._active_negotiations[negotiation_id]
        old_phase = negotiation.current_phase
        negotiation.current_phase = new_phase
        
        # Update Redis
        await self.redis_manager.set(
            f"rights_negotiation:{negotiation_id}",
            negotiation.__dict__,
            ttl=2592000
        )
        
        self.logger.info(
            f"Negotiation {negotiation_id} phase updated: {old_phase.value} -> {new_phase.value}"
        )
    
    async def complete_negotiation(
        self,
        negotiation_id: str,
        outcome: str,  # "success" or "failure"
        final_amount: Optional[Decimal] = None,
        rounds_completed: int = 1,
        automation_level: str = "full"
    ) -> None:
        """Complete a rights negotiation"""        
        if negotiation_id not in self._active_negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found")
            return
        
        negotiation = self._active_negotiations[negotiation_id]
        end_time = datetime.utcnow()
        duration_hours = (end_time - negotiation.start_time).total_seconds() / 3600
        
        if final_amount:
            negotiation.final_amount = final_amount
        
        # Update metrics
        self.negotiation_rounds.labels(
            license_type=negotiation.license_type.value,
            outcome=outcome
        ).observe(rounds_completed)
        
        self.negotiation_duration.labels(
            license_type=negotiation.license_type.value,
            outcome=outcome,
            automation_level=automation_level
        ).observe(duration_hours)
        
        # Clean up active negotiation
        del self._active_negotiations[negotiation_id]
        
        # Store completed negotiation in Redis with longer TTL
        await self.redis_manager.set(
            f"completed_negotiation:{negotiation_id}",
            {**negotiation.__dict__, "outcome": outcome, "end_time": end_time.isoformat()},
            ttl=31536000  # 1 year
        )
        
        self.logger.info(
            f"Completed negotiation {negotiation_id}: {outcome}, "
            f"duration: {duration_hours:.2f}h, rounds: {rounds_completed}"
        )
    
    async def record_compliance_check(
        self,
        license_type: LicenseType,
        licensee_id: str,
        check_type: str,
        result: str,
        compliance_level: ComplianceLevel,
        violation_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record license compliance check"""        
        self.license_compliance_checks_total.labels(
            license_type=license_type.value,
            check_type=check_type,
            result=result
        ).inc()
        
        # Record violations if any
        if compliance_level in [ComplianceLevel.VIOLATION, ComplianceLevel.CRITICAL_VIOLATION]:
            severity = "critical" if compliance_level == ComplianceLevel.CRITICAL_VIOLATION else "warning"
            
            self.compliance_violations_detected_total.labels(
                violation_type=check_type,
                severity=severity,
                license_type=license_type.value,
                licensee_id=licensee_id
            ).inc()
            
            # Store violation details
            if violation_details:
                await self.redis_manager.lpush(
                    f"compliance_violations:{licensee_id}",
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "license_type": license_type.value,
                        "check_type": check_type,
                        "severity": severity,
                        "details": violation_details
                    }
                )
        
        self.logger.info(
            f"Compliance check for {licensee_id}: {check_type} - {result} ({compliance_level.value})"
        )
    
    async def record_ai_recommendation(
        self,
        recommendation_type: str,
        accepted: bool,
        confidence_level: str,
        license_type: Optional[LicenseType] = None
    ) -> None:
        """Record AI-generated licensing recommendation"""        
        self.ai_license_recommendations_total.labels(
            recommendation_type=recommendation_type,
            accepted=str(accepted).lower(),
            confidence_level=confidence_level
        ).inc()
        
        self.logger.info(
            f"AI recommendation: {recommendation_type} - "
            f"{'accepted' if accepted else 'rejected'} (confidence: {confidence_level})"
        )
    
    async def record_contract_generation(
        self,
        contract_type: str,
        complexity: str,
        generation_time_seconds: float
    ) -> None:
        """Record AI contract generation performance"""        
        self.ai_contract_generation_time.labels(
            contract_type=contract_type,
            complexity=complexity
        ).observe(generation_time_seconds)
        
        self.logger.info(
            f"AI contract generated: {contract_type} ({complexity}) "
            f"in {generation_time_seconds:.2f}s"
        )
    
    async def record_platform_request(
        self,
        platform: str,
        request_type: str,
        status: str,
        response_time_seconds: float
    ) -> None:
        """Record external platform licensing request"""        
        self.platform_licensing_requests_total.labels(
            platform=platform,
            request_type=request_type,
            status=status
        ).inc()
        
        self.platform_integration_latency.labels(
            platform=platform,
            operation_type=request_type
        ).observe(response_time_seconds)
        
        self.logger.info(
            f"Platform request: {platform} - {request_type} - {status} "
            f"({response_time_seconds:.3f}s)"
        )
    
    async def update_success_rates(self) -> None:
        """Update calculated success rate metrics"""        
        # This would typically query historical data from metrics storage
        # For demonstration, we'll calculate from current data
        
        for license_type in LicenseType:
            # Calculate negotiation success rate (placeholder logic)
            success_rate = 85.0  # Would be calculated from actual data
            
            self.negotiation_success_rate.labels(
                license_type=license_type.value,
                time_window="24h",
                automation_level="full"
            ).set(success_rate)
    
    async def update_pricing_accuracy(
        self,
        license_type: LicenseType,
        accuracy_percent: float,
        time_window: str = "24h"
    ) -> None:
        """Update AI pricing recommendation accuracy"""        
        self.ai_pricing_accuracy.labels(
            license_type=license_type.value,
            time_window=time_window
        ).set(accuracy_percent)
    
    async def get_licensing_summary(self) -> Dict[str, Any]:
        """Get comprehensive licensing operations summary"""        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_negotiations": len(self._active_negotiations),
            "active_licenses": len(self._active_licenses),
            "negotiation_breakdown": {},
            "license_breakdown": {},
            "total_revenue_tracked": 0.0  # Would be calculated from metrics
        }
        
        # Breakdown by license type
        for license_type in LicenseType:
            negotiations = [
                n for n in self._active_negotiations.values()
                if n.license_type == license_type
            ]
            licenses = [
                l for l in self._active_licenses.values()
                if l.license_type == license_type
            ]
            
            summary["negotiation_breakdown"][license_type.value] = len(negotiations)
            summary["license_breakdown"][license_type.value] = len(licenses)
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the licensing metrics collector"""        
        return {
            "status": "healthy",
            "active_negotiations": len(self._active_negotiations),
            "active_licenses": len(self._active_licenses),
            "metrics_initialized": self.prometheus_manager is not None,
            "redis_connected": self.redis_manager is not None,
            "last_updated": datetime.utcnow().isoformat()
        }
