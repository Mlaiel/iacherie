"""
🛡️ MLOps Operations & Reliability - Service Level Enforcer
===========================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise service level enforcer for Creator Economy SLA/SLO management.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json


class SLIType(Enum):
    """Service Level Indicator types"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    CUSTOM = "custom"


class SLOViolationSeverity(Enum):
    """SLO violation severity levels"""
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ServiceTier(Enum):
    """Service tier levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"
    BREACH = "breach"


@dataclass
class ServiceLevelIndicator:
    """Service Level Indicator definition"""
    sli_id: str
    name: str
    service_id: str
    sli_type: SLIType
    measurement_query: str
    measurement_window: timedelta
    good_events_query: str
    total_events_query: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceLevelObjective:
    """Service Level Objective definition"""
    slo_id: str
    name: str
    service_id: str
    sli_id: str
    target_percentage: float
    time_window: timedelta
    service_tier: ServiceTier
    creator_facing: bool = True
    alert_threshold: float = 0.95  # Alert when SLO compliance drops below 95%
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceLevelAgreement:
    """Service Level Agreement definition"""
    sla_id: str
    name: str
    service_id: str
    slo_ids: List[str]
    service_tier: ServiceTier
    penalties: Dict[str, float]  # Penalty rates for violations
    credits: Dict[str, float]    # Credit rates for violations
    reporting_period: timedelta
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SLOViolation:
    """SLO violation record"""
    violation_id: str
    slo_id: str
    service_id: str
    severity: SLOViolationSeverity
    detected_at: datetime
    actual_value: float
    target_value: float
    duration: timedelta
    creator_impact: float
    resolved_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorBudget:
    """Error budget tracking"""
    budget_id: str
    slo_id: str
    service_id: str
    time_window: timedelta
    total_budget: float
    consumed_budget: float
    remaining_budget: float
    burn_rate: float
    projected_exhaustion: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)


class ServiceLevelEnforcer:
    """
    Enterprise service level enforcer for Creator Economy SLA/SLO management.
    
    Provides comprehensive SLI/SLO/SLA monitoring, error budget tracking,
    and automated compliance enforcement for creator services.
    """
    
    def __init__(self):
        """Initialize service level enforcer"""
        self.logger = logging.getLogger(__name__)
        self.slis = {}
        self.slos = {}
        self.slas = {}
        self.violations = []
        self.error_budgets = {}
        self.compliance_history = {}
        
        # Monitoring data
        self.sli_measurements = {}
        self.slo_compliance = {}
        
        # Initialize default SLIs/SLOs
        self._setup_default_service_levels()
        
        self.logger.info("ServiceLevelEnforcer initialized")
    
    def _setup_default_service_levels(self):
        """Setup default SLIs and SLOs for creator services"""
        # Creator API SLIs
        api_availability_sli = ServiceLevelIndicator(
            sli_id="creator_api_availability",
            name="Creator API Availability",
            service_id="creator_api",
            sli_type=SLIType.AVAILABILITY,
            measurement_query="success_rate",
            measurement_window=timedelta(minutes=5),
            good_events_query="http_requests_total{status!~'5..'}",
            total_events_query="http_requests_total"
        )
        
        api_latency_sli = ServiceLevelIndicator(
            sli_id="creator_api_latency",
            name="Creator API Response Time",
            service_id="creator_api",
            sli_type=SLIType.LATENCY,
            measurement_query="p95_latency",
            measurement_window=timedelta(minutes=5),
            good_events_query="http_request_duration_seconds_bucket{le='2.0'}",
            total_events_query="http_request_duration_seconds_bucket{le='+Inf'}"
        )
        
        # Content delivery SLIs
        cdn_availability_sli = ServiceLevelIndicator(
            sli_id="cdn_availability",
            name="CDN Availability",
            service_id="content_delivery",
            sli_type=SLIType.AVAILABILITY,
            measurement_query="cdn_success_rate",
            measurement_window=timedelta(minutes=1),
            good_events_query="cdn_requests_total{status!~'5..'}",
            total_events_query="cdn_requests_total"
        )
        
        # Payment system SLIs
        payment_availability_sli = ServiceLevelIndicator(
            sli_id="payment_availability",
            name="Payment System Availability",
            service_id="payment_system",
            sli_type=SLIType.AVAILABILITY,
            measurement_query="payment_success_rate",
            measurement_window=timedelta(minutes=5),
            good_events_query="payment_transactions_total{status='success'}",
            total_events_query="payment_transactions_total"
        )
        
        # Store SLIs
        for sli in [api_availability_sli, api_latency_sli, cdn_availability_sli, payment_availability_sli]:
            self.slis[sli.sli_id] = sli
        
        # Create corresponding SLOs
        api_availability_slo = ServiceLevelObjective(
            slo_id="creator_api_availability_slo",
            name="Creator API 99.9% Availability",
            service_id="creator_api",
            sli_id="creator_api_availability",
            target_percentage=99.9,
            time_window=timedelta(days=30),
            service_tier=ServiceTier.PREMIUM,
            creator_facing=True
        )
        
        api_latency_slo = ServiceLevelObjective(
            slo_id="creator_api_latency_slo",
            name="Creator API P95 < 2s",
            service_id="creator_api",
            sli_id="creator_api_latency",
            target_percentage=95.0,
            time_window=timedelta(days=30),
            service_tier=ServiceTier.PREMIUM,
            creator_facing=True
        )
        
        cdn_availability_slo = ServiceLevelObjective(
            slo_id="cdn_availability_slo",
            name="CDN 99.95% Availability",
            service_id="content_delivery",
            sli_id="cdn_availability",
            target_percentage=99.95,
            time_window=timedelta(days=30),
            service_tier=ServiceTier.ENTERPRISE,
            creator_facing=True
        )
        
        payment_availability_slo = ServiceLevelObjective(
            slo_id="payment_availability_slo",
            name="Payment System 99.99% Availability",
            service_id="payment_system",
            sli_id="payment_availability",
            target_percentage=99.99,
            time_window=timedelta(days=30),
            service_tier=ServiceTier.ENTERPRISE,
            creator_facing=True
        )
        
        # Store SLOs
        for slo in [api_availability_slo, api_latency_slo, cdn_availability_slo, payment_availability_slo]:
            self.slos[slo.slo_id] = slo
        
        # Create SLA
        creator_platform_sla = ServiceLevelAgreement(
            sla_id="creator_platform_sla",
            name="Creator Platform Service Level Agreement",
            service_id="creator_platform",
            slo_ids=["creator_api_availability_slo", "creator_api_latency_slo", 
                    "cdn_availability_slo", "payment_availability_slo"],
            service_tier=ServiceTier.ENTERPRISE,
            penalties={
                "99.9_breach": 0.05,   # 5% penalty for availability below 99.9%
                "99.0_breach": 0.10,   # 10% penalty for availability below 99.0%
                "95.0_breach": 0.25    # 25% penalty for availability below 95.0%
            },
            credits={
                "99.9_breach": 0.10,   # 10% credit for availability below 99.9%
                "99.0_breach": 0.25,   # 25% credit for availability below 99.0%
                "95.0_breach": 0.50    # 50% credit for availability below 95.0%
            },
            reporting_period=timedelta(days=30),
            notification_channels=["sre_team", "creator_success", "executive"]
        )
        
        self.slas[creator_platform_sla.sla_id] = creator_platform_sla
        
        # Initialize error budgets
        for slo_id, slo in self.slos.items():
            self._initialize_error_budget(slo)
    
    def _initialize_error_budget(self, slo: ServiceLevelObjective):
        """Initialize error budget for SLO"""
        # Calculate total budget based on SLO target
        total_minutes = slo.time_window.total_seconds() / 60
        error_budget_minutes = total_minutes * (100 - slo.target_percentage) / 100
        
        budget = ErrorBudget(
            budget_id=f"budget_{slo.slo_id}",
            slo_id=slo.slo_id,
            service_id=slo.service_id,
            time_window=slo.time_window,
            total_budget=error_budget_minutes,
            consumed_budget=0.0,
            remaining_budget=error_budget_minutes,
            burn_rate=0.0
        )
        
        self.error_budgets[slo.slo_id] = budget
    
    async def collect_sli_measurement(
        self,
        sli_id: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Collect SLI measurement
        
        Args:
            sli_id: SLI identifier
            value: Measured value
            timestamp: Measurement timestamp (default: now)
            
        Returns:
            True if measurement collected successfully
        """
        try:
            if sli_id not in self.slis:
                raise ValueError(f"SLI {sli_id} not found")
            
            if timestamp is None:
                timestamp = datetime.now()
            
            # Store measurement
            if sli_id not in self.sli_measurements:
                self.sli_measurements[sli_id] = []
            
            measurement = {
                'timestamp': timestamp,
                'value': value,
                'sli_id': sli_id
            }
            
            self.sli_measurements[sli_id].append(measurement)
            
            # Keep only recent measurements (last 7 days)
            cutoff_time = datetime.now() - timedelta(days=7)
            self.sli_measurements[sli_id] = [
                m for m in self.sli_measurements[sli_id]
                if m['timestamp'] >= cutoff_time
            ]
            
            # Update SLO compliance
            await self._update_slo_compliance(sli_id, value, timestamp)
            
            self.logger.debug(f"Collected SLI measurement: {sli_id} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting SLI measurement: {str(e)}")
            raise
    
    async def _update_slo_compliance(
        self,
        sli_id: str,
        value: float,
        timestamp: datetime
    ):
        """Update SLO compliance based on SLI measurement"""
        # Find SLOs that use this SLI
        related_slos = [slo for slo in self.slos.values() if slo.sli_id == sli_id]
        
        for slo in related_slos:
            # Calculate current compliance
            compliance = await self._calculate_slo_compliance(slo.slo_id)
            
            # Update compliance history
            if slo.slo_id not in self.slo_compliance:
                self.slo_compliance[slo.slo_id] = []
            
            self.slo_compliance[slo.slo_id].append({
                'timestamp': timestamp,
                'compliance_percentage': compliance,
                'current_value': value
            })
            
            # Check for violations
            if compliance < slo.alert_threshold * slo.target_percentage:
                await self._detect_slo_violation(slo, compliance, value, timestamp)
            
            # Update error budget
            await self._update_error_budget(slo, compliance, timestamp)
    
    async def _calculate_slo_compliance(self, slo_id: str) -> float:
        """Calculate current SLO compliance percentage"""
        if slo_id not in self.slos:
            return 0.0
        
        slo = self.slos[slo_id]
        sli_id = slo.sli_id
        
        if sli_id not in self.sli_measurements:
            return 100.0  # No data means compliant by default
        
        # Get measurements within time window
        cutoff_time = datetime.now() - slo.time_window
        recent_measurements = [
            m for m in self.sli_measurements[sli_id]
            if m['timestamp'] >= cutoff_time
        ]
        
        if not recent_measurements:
            return 100.0
        
        # Calculate compliance based on SLI type
        sli = self.slis[sli_id]
        
        if sli.sli_type == SLIType.AVAILABILITY:
            # For availability, calculate percentage of successful measurements
            successful_measurements = len([m for m in recent_measurements if m['value'] >= slo.target_percentage])
            compliance = (successful_measurements / len(recent_measurements)) * 100
        elif sli.sli_type == SLIType.LATENCY:
            # For latency, calculate percentage meeting target
            target_threshold = 2000  # 2 seconds for demo
            successful_measurements = len([m for m in recent_measurements if m['value'] <= target_threshold])
            compliance = (successful_measurements / len(recent_measurements)) * 100
        elif sli.sli_type == SLIType.ERROR_RATE:
            # For error rate, calculate percentage below threshold
            error_threshold = 1.0  # 1% error rate
            successful_measurements = len([m for m in recent_measurements if m['value'] <= error_threshold])
            compliance = (successful_measurements / len(recent_measurements)) * 100
        else:
            # Generic calculation
            avg_value = statistics.mean([m['value'] for m in recent_measurements])
            compliance = min(100.0, avg_value)
        
        return max(0.0, min(100.0, compliance))
    
    async def _detect_slo_violation(
        self,
        slo: ServiceLevelObjective,
        compliance: float,
        current_value: float,
        timestamp: datetime
    ):
        """Detect and record SLO violation"""
        # Determine violation severity
        if compliance < 50.0:
            severity = SLOViolationSeverity.CRITICAL
        elif compliance < 75.0:
            severity = SLOViolationSeverity.MAJOR
        elif compliance < 90.0:
            severity = SLOViolationSeverity.MINOR
        else:
            severity = SLOViolationSeverity.WARNING
        
        # Check if this is a new violation or continuation
        recent_violations = [
            v for v in self.violations
            if v.slo_id == slo.slo_id and v.resolved_at is None
            and (timestamp - v.detected_at) < timedelta(hours=1)
        ]
        
        if recent_violations:
            # Update existing violation
            violation = recent_violations[0]
            violation.actual_value = compliance
            violation.duration = timestamp - violation.detected_at
        else:
            # Create new violation
            violation_id = f"violation_{slo.slo_id}_{int(time.time())}"
            
            violation = SLOViolation(
                violation_id=violation_id,
                slo_id=slo.slo_id,
                service_id=slo.service_id,
                severity=severity,
                detected_at=timestamp,
                actual_value=compliance,
                target_value=slo.target_percentage,
                duration=timedelta(0),
                creator_impact=self._estimate_creator_impact(slo, compliance)
            )
            
            self.violations.append(violation)
            
            self.logger.warning(f"SLO violation detected: {slo.slo_id} "
                              f"(compliance: {compliance:.2f}%, target: {slo.target_percentage}%)")
    
    def _estimate_creator_impact(self, slo: ServiceLevelObjective, compliance: float) -> float:
        """Estimate creator impact of SLO violation"""
        if not slo.creator_facing:
            return 0.0
        
        # Base impact on compliance level
        impact_percentage = max(0, (slo.target_percentage - compliance) / slo.target_percentage * 100)
        
        # Amplify based on service tier
        tier_multipliers = {
            ServiceTier.BASIC: 1.0,
            ServiceTier.STANDARD: 1.2,
            ServiceTier.PREMIUM: 1.5,
            ServiceTier.ENTERPRISE: 2.0
        }
        
        multiplier = tier_multipliers.get(slo.service_tier, 1.0)
        
        return min(100.0, impact_percentage * multiplier)
    
    async def _update_error_budget(
        self,
        slo: ServiceLevelObjective,
        compliance: float,
        timestamp: datetime
    ):
        """Update error budget consumption"""
        if slo.slo_id not in self.error_budgets:
            return
        
        budget = self.error_budgets[slo.slo_id]
        
        # Calculate budget consumption
        if compliance < slo.target_percentage:
            # Calculate how much budget is consumed
            error_rate = (slo.target_percentage - compliance) / 100
            time_delta = (timestamp - budget.last_updated).total_seconds() / 60  # minutes
            consumed = error_rate * time_delta
            
            budget.consumed_budget += consumed
            budget.remaining_budget = max(0, budget.total_budget - budget.consumed_budget)
        
        # Update burn rate (consumption per hour)
        if budget.consumed_budget > 0:
            elapsed_hours = (timestamp - (timestamp - budget.time_window)).total_seconds() / 3600
            budget.burn_rate = budget.consumed_budget / max(1, elapsed_hours)
            
            # Project when budget will be exhausted
            if budget.burn_rate > 0 and budget.remaining_budget > 0:
                hours_to_exhaustion = budget.remaining_budget / budget.burn_rate
                budget.projected_exhaustion = timestamp + timedelta(hours=hours_to_exhaustion)
            else:
                budget.projected_exhaustion = None
        
        budget.last_updated = timestamp
    
    async def get_slo_status(self, slo_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an SLO"""
        if slo_id not in self.slos:
            return None
        
        slo = self.slos[slo_id]
        compliance = await self._calculate_slo_compliance(slo_id)
        
        # Get error budget
        budget = self.error_budgets.get(slo_id)
        
        # Get recent violations
        recent_violations = [
            v for v in self.violations
            if v.slo_id == slo_id and v.detected_at >= datetime.now() - timedelta(days=7)
        ]
        
        # Determine compliance status
        if compliance >= slo.target_percentage:
            status = ComplianceStatus.COMPLIANT
        elif compliance >= slo.target_percentage * 0.95:
            status = ComplianceStatus.AT_RISK
        elif compliance >= slo.target_percentage * 0.90:
            status = ComplianceStatus.VIOLATED
        else:
            status = ComplianceStatus.BREACH
        
        return {
            'slo_id': slo.slo_id,
            'name': slo.name,
            'service_id': slo.service_id,
            'target_percentage': slo.target_percentage,
            'current_compliance': compliance,
            'compliance_status': status.value,
            'error_budget': {
                'total_minutes': budget.total_budget if budget else 0,
                'consumed_minutes': budget.consumed_budget if budget else 0,
                'remaining_minutes': budget.remaining_budget if budget else 0,
                'burn_rate_per_hour': budget.burn_rate if budget else 0,
                'projected_exhaustion': budget.projected_exhaustion.isoformat() if budget and budget.projected_exhaustion else None
            },
            'recent_violations': len(recent_violations),
            'creator_facing': slo.creator_facing,
            'service_tier': slo.service_tier.value
        }
    
    async def get_sla_compliance_report(
        self,
        sla_id: str,
        period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Generate SLA compliance report"""
        if sla_id not in self.slas:
            raise ValueError(f"SLA {sla_id} not found")
        
        sla = self.slas[sla_id]
        if period is None:
            period = sla.reporting_period
        
        report = {
            'sla_id': sla.sla_id,
            'name': sla.name,
            'service_id': sla.service_id,
            'service_tier': sla.service_tier.value,
            'reporting_period_days': period.days,
            'slo_compliance': {},
            'overall_compliance': 0.0,
            'violations_summary': {},
            'penalties_incurred': 0.0,
            'credits_due': 0.0,
            'creator_impact_total': 0.0
        }
        
        # Calculate compliance for each SLO
        total_compliance = 0.0
        compliant_slos = 0
        
        for slo_id in sla.slo_ids:
            if slo_id in self.slos:
                compliance = await self._calculate_slo_compliance(slo_id)
                slo_status = await self.get_slo_status(slo_id)
                
                report['slo_compliance'][slo_id] = {
                    'name': self.slos[slo_id].name,
                    'target': self.slos[slo_id].target_percentage,
                    'actual': compliance,
                    'status': slo_status['compliance_status'] if slo_status else 'unknown'
                }
                
                total_compliance += compliance
                if compliance >= self.slos[slo_id].target_percentage:
                    compliant_slos += 1
        
        # Calculate overall compliance
        if sla.slo_ids:
            report['overall_compliance'] = total_compliance / len(sla.slo_ids)
        
        # Calculate violations
        period_start = datetime.now() - period
        period_violations = [
            v for v in self.violations
            if v.service_id == sla.service_id and v.detected_at >= period_start
        ]
        
        # Group violations by severity
        violation_counts = {}
        total_creator_impact = 0.0
        
        for violation in period_violations:
            severity = violation.severity.value
            violation_counts[severity] = violation_counts.get(severity, 0) + 1
            total_creator_impact += violation.creator_impact
        
        report['violations_summary'] = violation_counts
        report['creator_impact_total'] = total_creator_impact
        
        # Calculate penalties and credits
        for breach_level, penalty_rate in sla.penalties.items():
            if self._is_breach_level_met(report['overall_compliance'], breach_level):
                report['penalties_incurred'] += penalty_rate
        
        for breach_level, credit_rate in sla.credits.items():
            if self._is_breach_level_met(report['overall_compliance'], breach_level):
                report['credits_due'] += credit_rate
        
        return report
    
    def _is_breach_level_met(self, compliance: float, breach_level: str) -> bool:
        """Check if breach level threshold is met"""
        threshold_map = {
            "99.9_breach": 99.9,
            "99.0_breach": 99.0,
            "95.0_breach": 95.0
        }
        
        threshold = threshold_map.get(breach_level, 100.0)
        return compliance < threshold
    
    async def get_error_budget_status(
        self,
        service_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get error budget status for all or specific service"""
        budget_status = []
        
        for budget in self.error_budgets.values():
            if service_id and budget.service_id != service_id:
                continue
            
            slo = self.slos.get(budget.slo_id)
            if not slo:
                continue
            
            # Calculate budget health
            budget_health = "healthy"
            if budget.remaining_budget <= 0:
                budget_health = "exhausted"
            elif budget.remaining_budget / budget.total_budget < 0.1:
                budget_health = "critical"
            elif budget.remaining_budget / budget.total_budget < 0.25:
                budget_health = "warning"
            
            status = {
                'budget_id': budget.budget_id,
                'slo_id': budget.slo_id,
                'slo_name': slo.name,
                'service_id': budget.service_id,
                'total_budget_minutes': budget.total_budget,
                'consumed_minutes': budget.consumed_budget,
                'remaining_minutes': budget.remaining_budget,
                'consumption_percentage': (budget.consumed_budget / budget.total_budget) * 100 if budget.total_budget > 0 else 0,
                'burn_rate_per_hour': budget.burn_rate,
                'budget_health': budget_health,
                'projected_exhaustion': budget.projected_exhaustion.isoformat() if budget.projected_exhaustion else None,
                'last_updated': budget.last_updated.isoformat()
            }
            
            budget_status.append(status)
        
        return budget_status
    
    def get_enforcer_status(self) -> Dict[str, Any]:
        """Get service level enforcer status"""
        return {
            'enforcer_name': 'ServiceLevelEnforcer',
            'version': '1.0.0',
            'status': 'active',
            'slis_monitored': len(self.slis),
            'slos_tracked': len(self.slos),
            'slas_managed': len(self.slas),
            'active_violations': len([v for v in self.violations if v.resolved_at is None]),
            'error_budgets': len(self.error_budgets),
            'supported_sli_types': [sli_type.value for sli_type in SLIType],
            'supported_service_tiers': [tier.value for tier in ServiceTier]
        }


# Export main classes and enums
__all__ = [
    'ServiceLevelEnforcer',
    'SLIType',
    'SLOViolationSeverity',
    'ServiceTier',
    'ComplianceStatus',
    'ServiceLevelIndicator',
    'ServiceLevelObjective',
    'ServiceLevelAgreement',
    'SLOViolation',
    'ErrorBudget'
]