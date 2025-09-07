"""Recovered Revenue Manager - Protection Revenue Recovery Management
==================================================================

Enterprise-grade revenue recovery management system for content protection
violations, providing automated recovery tracking, settlement management,
and financial impact analysis for intellectual property protection.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/recovered_revenue_manager.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class RecoveryStatus(str, Enum):
    """Revenue recovery status."""
    IDENTIFIED = "identified"
    INVESTIGATING = "investigating"
    CLAIMED = "claimed"
    NEGOTIATING = "negotiating"
    SETTLED = "settled"
    REJECTED = "rejected"
    LITIGATION = "litigation"
    RECOVERED = "recovered"
    CANCELLED = "cancelled"


class RecoveryMethod(str, Enum):
    """Revenue recovery methods."""
    DMCA_SETTLEMENT = "dmca_settlement"
    LICENSING_AGREEMENT = "licensing_agreement"
    LEGAL_ACTION = "legal_action"
    PLATFORM_CLAIM = "platform_claim"
    DIRECT_NEGOTIATION = "direct_negotiation"
    AUTOMATED_RECOVERY = "automated_recovery"
    CEASE_AND_DESIST = "cease_and_desist"


class ViolationType(str, Enum):
    """Types of content violations."""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    PIRACY = "piracy"
    PLAGIARISM = "plagiarism"
    COUNTERFEITING = "counterfeiting"
    REVENUE_THEFT = "revenue_theft"


@dataclass
class RecoveryCase:
    """Revenue recovery case details."""
    case_id: str
    creator_id: str
    content_id: str
    violation_type: ViolationType
    violator_info: Dict[str, Any]
    claimed_amount: Decimal
    recovered_amount: Decimal
    recovery_status: RecoveryStatus
    recovery_method: RecoveryMethod
    detection_date: datetime
    claim_date: Optional[datetime]
    settlement_date: Optional[datetime]
    recovery_fees: Decimal
    net_recovery: Decimal
    evidence: List[Dict[str, Any]]
    settlement_terms: Dict[str, Any]
    legal_costs: Decimal
    time_to_resolution_days: Optional[int]
    success_probability: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecoveryMetrics:
    """Revenue recovery performance metrics."""
    creator_id: str
    period_start: datetime
    period_end: datetime
    total_violations_detected: int
    total_amount_claimed: Decimal
    total_amount_recovered: Decimal
    recovery_rate: float
    average_recovery_time_days: float
    success_rate: float
    total_legal_costs: Decimal
    net_recovery_amount: Decimal
    roi: float  # Return on investment for recovery efforts


@dataclass
class RecoveryStrategy:
    """Revenue recovery strategy configuration."""
    strategy_id: str
    creator_id: str
    violation_types: List[ViolationType]
    minimum_claim_amount: Decimal
    preferred_methods: List[RecoveryMethod]
    auto_recovery_enabled: bool
    legal_action_threshold: Decimal
    settlement_acceptance_rate: float  # Percentage of claim amount
    monitoring_frequency: str  # "daily", "weekly", "monthly"
    is_active: bool = True


class RecoveredRevenueManager:
    """
    Advanced revenue recovery management system.
    
    Manages content protection revenue recovery cases,
    tracks settlements, and optimizes recovery strategies.
    """
    
    def __init__(self):
        """Initialize the recovered revenue manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.recovery_cases: Dict[str, RecoveryCase] = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.metrics_cache: Dict[str, RecoveryMetrics] = {}
        self.settlement_history: Dict[str, List[Dict[str, Any]]] = {}
        self.initialized = False
        
        self.logger.info("RecoveredRevenueManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the revenue recovery manager."""
        try:
            await self._load_recovery_data()
            await self._initialize_recovery_strategies()
            
            self.initialized = True
            self.logger.info("RecoveredRevenueManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RecoveredRevenueManager: {e}")
            return False
    
    async def _load_recovery_data(self):
        """Load existing recovery data."""
        # In production, this would load from database
        self.logger.info("Recovery data loaded")
    
    async def _initialize_recovery_strategies(self):
        """Initialize default recovery strategies."""
        default_strategy = RecoveryStrategy(
            strategy_id=str(uuid4()),
            creator_id="default",
            violation_types=[ViolationType.COPYRIGHT_INFRINGEMENT, ViolationType.UNAUTHORIZED_USE],
            minimum_claim_amount=Decimal("50.00"),
            preferred_methods=[RecoveryMethod.DMCA_SETTLEMENT, RecoveryMethod.PLATFORM_CLAIM],
            auto_recovery_enabled=True,
            legal_action_threshold=Decimal("1000.00"),
            settlement_acceptance_rate=0.7,
            monitoring_frequency="daily"
        )
        
        self.recovery_strategies["default"] = default_strategy
        self.logger.info("Default recovery strategies initialized")
    
    async def create_recovery_case(
        self,
        creator_id: str,
        content_id: str,
        violation_type: ViolationType,
        violator_info: Dict[str, Any],
        claimed_amount: Decimal,
        evidence: List[Dict[str, Any]],
        detection_date: Optional[datetime] = None
    ) -> str:
        """Create a new revenue recovery case."""
        try:
            case_id = str(uuid4())
            
            # Calculate success probability based on evidence and claim
            success_probability = await self._calculate_success_probability(
                violation_type, evidence, claimed_amount
            )
            
            recovery_case = RecoveryCase(
                case_id=case_id,
                creator_id=creator_id,
                content_id=content_id,
                violation_type=violation_type,
                violator_info=violator_info,
                claimed_amount=claimed_amount,
                recovered_amount=Decimal("0"),
                recovery_status=RecoveryStatus.IDENTIFIED,
                recovery_method=RecoveryMethod.DMCA_SETTLEMENT,  # Default
                detection_date=detection_date or datetime.now(),
                claim_date=None,
                settlement_date=None,
                recovery_fees=Decimal("0"),
                net_recovery=Decimal("0"),
                evidence=evidence,
                settlement_terms={},
                legal_costs=Decimal("0"),
                time_to_resolution_days=None,
                success_probability=success_probability
            )
            
            self.recovery_cases[case_id] = recovery_case
            
            # Auto-initiate recovery if enabled
            strategy = await self._get_recovery_strategy(creator_id)
            if strategy and strategy.auto_recovery_enabled:
                await self._initiate_auto_recovery(case_id)
            
            self.logger.info(f"Created recovery case {case_id} for creator {creator_id}")
            return case_id
            
        except Exception as e:
            self.logger.error(f"Error creating recovery case: {e}")
            raise
    
    async def _calculate_success_probability(
        self,
        violation_type: ViolationType,
        evidence: List[Dict[str, Any]],
        claimed_amount: Decimal
    ) -> float:
        """Calculate probability of successful recovery."""
        base_probability = {
            ViolationType.COPYRIGHT_INFRINGEMENT: 0.85,
            ViolationType.TRADEMARK_VIOLATION: 0.80,
            ViolationType.UNAUTHORIZED_USE: 0.75,
            ViolationType.PIRACY: 0.70,
            ViolationType.PLAGIARISM: 0.65,
            ViolationType.COUNTERFEITING: 0.90,
            ViolationType.REVENUE_THEFT: 0.60
        }.get(violation_type, 0.70)
        
        # Adjust based on evidence quality
        evidence_score = len(evidence) * 0.1  # More evidence = higher chance
        evidence_bonus = min(evidence_score, 0.2)  # Cap at 20% bonus
        
        # Adjust based on claim amount (smaller claims easier to recover)
        if claimed_amount > Decimal("10000"):
            amount_penalty = 0.1
        elif claimed_amount > Decimal("1000"):
            amount_penalty = 0.05
        else:
            amount_penalty = 0.0
        
        probability = base_probability + evidence_bonus - amount_penalty
        return max(0.1, min(0.95, probability))
    
    async def _get_recovery_strategy(self, creator_id: str) -> Optional[RecoveryStrategy]:
        """Get recovery strategy for creator."""
        return self.recovery_strategies.get(creator_id) or self.recovery_strategies.get("default")
    
    async def _initiate_auto_recovery(self, case_id: str):
        """Initiate automated recovery process."""
        case = self.recovery_cases.get(case_id)
        if not case:
            return
        
        strategy = await self._get_recovery_strategy(case.creator_id)
        if not strategy:
            return
        
        # Check if case meets minimum claim threshold
        if case.claimed_amount < strategy.minimum_claim_amount:
            case.recovery_status = RecoveryStatus.CANCELLED
            self.logger.info(f"Case {case_id} cancelled - below minimum threshold")
            return
        
        # Select appropriate recovery method
        recovery_method = await self._select_recovery_method(case, strategy)
        case.recovery_method = recovery_method
        
        # Initiate recovery process
        await self._execute_recovery_method(case_id, recovery_method)
    
    async def _select_recovery_method(
        self,
        case: RecoveryCase,
        strategy: RecoveryStrategy
    ) -> RecoveryMethod:
        """Select optimal recovery method for case."""
        
        # Check for legal action threshold
        if case.claimed_amount >= strategy.legal_action_threshold:
            if RecoveryMethod.LEGAL_ACTION in strategy.preferred_methods:
                return RecoveryMethod.LEGAL_ACTION
        
        # Use preferred methods in order
        for method in strategy.preferred_methods:
            if await self._is_method_applicable(case, method):
                return method
        
        # Default to DMCA settlement
        return RecoveryMethod.DMCA_SETTLEMENT
    
    async def _is_method_applicable(self, case: RecoveryCase, method: RecoveryMethod) -> bool:
        """Check if recovery method is applicable for case."""
        
        # Check if violator platform supports the method
        platform = case.violator_info.get("platform", "")
        
        if method == RecoveryMethod.PLATFORM_CLAIM:
            supported_platforms = ["youtube", "facebook", "instagram", "tiktok", "twitter"]
            return platform.lower() in supported_platforms
        
        elif method == RecoveryMethod.DMCA_SETTLEMENT:
            return case.violation_type in [
                ViolationType.COPYRIGHT_INFRINGEMENT,
                ViolationType.UNAUTHORIZED_USE
            ]
        
        elif method == RecoveryMethod.LEGAL_ACTION:
            return case.claimed_amount >= Decimal("500.00")
        
        return True  # Most methods are generally applicable
    
    async def _execute_recovery_method(self, case_id: str, method: RecoveryMethod):
        """Execute the selected recovery method."""
        case = self.recovery_cases.get(case_id)
        if not case:
            return
        
        case.recovery_status = RecoveryStatus.CLAIMED
        case.claim_date = datetime.now()
        case.updated_at = datetime.now()
        
        if method == RecoveryMethod.DMCA_SETTLEMENT:
            await self._execute_dmca_settlement(case_id)
        elif method == RecoveryMethod.PLATFORM_CLAIM:
            await self._execute_platform_claim(case_id)
        elif method == RecoveryMethod.LEGAL_ACTION:
            await self._execute_legal_action(case_id)
        elif method == RecoveryMethod.DIRECT_NEGOTIATION:
            await self._execute_direct_negotiation(case_id)
        
        self.logger.info(f"Executed {method.value} for case {case_id}")
    
    async def _execute_dmca_settlement(self, case_id: str):
        """Execute DMCA settlement process."""
        case = self.recovery_cases[case_id]
        
        # Simulate DMCA process
        case.recovery_status = RecoveryStatus.NEGOTIATING
        
        # In production, this would interface with DMCA services
        # For now, simulate outcome based on success probability
        import random
        if random.random() < case.success_probability:
            # Successful settlement
            settlement_rate = 0.6 + random.random() * 0.3  # 60-90% of claim
            await self._process_settlement(case_id, settlement_rate, "DMCA Settlement Agreement")
        else:
            case.recovery_status = RecoveryStatus.REJECTED
            case.updated_at = datetime.now()
    
    async def _execute_platform_claim(self, case_id: str):
        """Execute platform-specific claim process."""
        case = self.recovery_cases[case_id]
        
        platform = case.violator_info.get("platform", "unknown")
        case.recovery_status = RecoveryStatus.NEGOTIATING
        
        # Platform-specific success rates
        platform_success_rates = {
            "youtube": 0.85,
            "facebook": 0.80,
            "instagram": 0.75,
            "tiktok": 0.70,
            "twitter": 0.65
        }
        
        success_rate = platform_success_rates.get(platform.lower(), 0.60)
        adjusted_probability = case.success_probability * success_rate
        
        import random
        if random.random() < adjusted_probability:
            settlement_rate = 0.5 + random.random() * 0.4  # 50-90% of claim
            await self._process_settlement(case_id, settlement_rate, f"{platform.title()} Platform Settlement")
        else:
            case.recovery_status = RecoveryStatus.REJECTED
            case.updated_at = datetime.now()
    
    async def _execute_legal_action(self, case_id: str):
        """Execute legal action process."""
        case = self.recovery_cases[case_id]
        
        case.recovery_status = RecoveryStatus.LITIGATION
        
        # Legal action is more expensive but potentially more rewarding
        legal_costs = case.claimed_amount * Decimal("0.3")  # 30% legal fees
        case.legal_costs = legal_costs
        
        # Higher success rate but takes longer
        enhanced_probability = min(case.success_probability * 1.2, 0.95)
        
        import random
        if random.random() < enhanced_probability:
            # Legal action typically recovers higher amounts
            settlement_rate = 0.8 + random.random() * 0.2  # 80-100% of claim
            await self._process_settlement(case_id, settlement_rate, "Legal Settlement Agreement")
        else:
            case.recovery_status = RecoveryStatus.REJECTED
            case.updated_at = datetime.now()
    
    async def _execute_direct_negotiation(self, case_id: str):
        """Execute direct negotiation process."""
        case = self.recovery_cases[case_id]
        
        case.recovery_status = RecoveryStatus.NEGOTIATING
        
        # Direct negotiation can be faster but less predictable
        negotiation_success = case.success_probability * 0.9  # Slightly lower success rate
        
        import random
        if random.random() < negotiation_success:
            settlement_rate = 0.4 + random.random() * 0.5  # 40-90% of claim
            await self._process_settlement(case_id, settlement_rate, "Direct Negotiation Agreement")
        else:
            case.recovery_status = RecoveryStatus.REJECTED
            case.updated_at = datetime.now()
    
    async def _process_settlement(self, case_id: str, settlement_rate: float, settlement_type: str):
        """Process successful settlement."""
        case = self.recovery_cases[case_id]
        
        # Calculate recovered amount
        recovered_amount = case.claimed_amount * Decimal(str(settlement_rate))
        
        # Calculate fees (typically 15-25% of recovery)
        fee_rate = 0.15 + (0.1 * (1 - settlement_rate))  # Higher fees for lower settlements
        recovery_fees = recovered_amount * Decimal(str(fee_rate))
        
        # Update case
        case.recovered_amount = recovered_amount
        case.recovery_fees = recovery_fees
        case.net_recovery = recovered_amount - recovery_fees - case.legal_costs
        case.recovery_status = RecoveryStatus.SETTLED
        case.settlement_date = datetime.now()
        case.settlement_terms = {
            "settlement_type": settlement_type,
            "settlement_rate": settlement_rate,
            "fee_rate": fee_rate,
            "settlement_date": case.settlement_date.isoformat()
        }
        
        # Calculate resolution time
        if case.claim_date:
            resolution_time = (case.settlement_date - case.claim_date).days
            case.time_to_resolution_days = resolution_time
        
        case.updated_at = datetime.now()
        
        # Mark as recovered if payment is expected
        case.recovery_status = RecoveryStatus.RECOVERED
        
        # Store settlement history
        if case.creator_id not in self.settlement_history:
            self.settlement_history[case.creator_id] = []
        
        self.settlement_history[case.creator_id].append({
            "case_id": case_id,
            "settlement_date": case.settlement_date.isoformat(),
            "claimed_amount": float(case.claimed_amount),
            "recovered_amount": float(case.recovered_amount),
            "net_recovery": float(case.net_recovery),
            "settlement_type": settlement_type
        })
        
        self.logger.info(f"Settlement processed for case {case_id}: ${case.net_recovery}")
    
    async def update_case_status(
        self,
        case_id: str,
        status: RecoveryStatus,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update recovery case status."""
        try:
            case = self.recovery_cases.get(case_id)
            if not case:
                self.logger.error(f"Case {case_id} not found")
                return False
            
            case.recovery_status = status
            case.updated_at = datetime.now()
            
            if additional_info:
                if "recovered_amount" in additional_info:
                    case.recovered_amount = Decimal(str(additional_info["recovered_amount"]))
                
                if "settlement_terms" in additional_info:
                    case.settlement_terms.update(additional_info["settlement_terms"])
                
                if "legal_costs" in additional_info:
                    case.legal_costs = Decimal(str(additional_info["legal_costs"]))
            
            # Recalculate net recovery if amounts changed
            case.net_recovery = case.recovered_amount - case.recovery_fees - case.legal_costs
            
            self.logger.info(f"Updated case {case_id} status to {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating case status: {e}")
            return False
    
    async def get_recovery_metrics(
        self,
        creator_id: str,
        period_days: int = 90
    ) -> RecoveryMetrics:
        """Get recovery performance metrics for a creator."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Filter cases for creator and period
        creator_cases = [
            case for case in self.recovery_cases.values()
            if case.creator_id == creator_id and start_date <= case.created_at <= end_date
        ]
        
        if not creator_cases:
            return RecoveryMetrics(
                creator_id=creator_id,
                period_start=start_date,
                period_end=end_date,
                total_violations_detected=0,
                total_amount_claimed=Decimal("0"),
                total_amount_recovered=Decimal("0"),
                recovery_rate=0.0,
                average_recovery_time_days=0.0,
                success_rate=0.0,
                total_legal_costs=Decimal("0"),
                net_recovery_amount=Decimal("0"),
                roi=0.0
            )
        
        # Calculate metrics
        total_violations = len(creator_cases)
        total_claimed = sum(case.claimed_amount for case in creator_cases)
        total_recovered = sum(case.recovered_amount for case in creator_cases)
        total_legal_costs = sum(case.legal_costs for case in creator_cases)
        net_recovery = sum(case.net_recovery for case in creator_cases)
        
        recovery_rate = float(total_recovered / total_claimed) if total_claimed > 0 else 0.0
        
        # Calculate success rate (settled or recovered cases)
        successful_cases = [
            case for case in creator_cases
            if case.recovery_status in [RecoveryStatus.SETTLED, RecoveryStatus.RECOVERED]
        ]
        success_rate = len(successful_cases) / total_violations if total_violations > 0 else 0.0
        
        # Calculate average recovery time
        resolved_cases_with_time = [
            case for case in successful_cases
            if case.time_to_resolution_days is not None
        ]
        avg_recovery_time = (
            sum(case.time_to_resolution_days for case in resolved_cases_with_time) / len(resolved_cases_with_time)
            if resolved_cases_with_time else 0.0
        )
        
        # Calculate ROI
        total_investment = total_legal_costs + sum(case.recovery_fees for case in creator_cases)
        roi = float(net_recovery / total_investment) if total_investment > 0 else 0.0
        
        return RecoveryMetrics(
            creator_id=creator_id,
            period_start=start_date,
            period_end=end_date,
            total_violations_detected=total_violations,
            total_amount_claimed=total_claimed,
            total_amount_recovered=total_recovered,
            recovery_rate=recovery_rate,
            average_recovery_time_days=avg_recovery_time,
            success_rate=success_rate,
            total_legal_costs=total_legal_costs,
            net_recovery_amount=net_recovery,
            roi=roi
        )
    
    async def create_recovery_strategy(
        self,
        creator_id: str,
        violation_types: List[ViolationType],
        minimum_claim_amount: Decimal,
        preferred_methods: List[RecoveryMethod],
        auto_recovery_enabled: bool = True,
        legal_action_threshold: Decimal = Decimal("1000.00"),
        settlement_acceptance_rate: float = 0.7
    ) -> str:
        """Create custom recovery strategy for creator."""
        strategy_id = str(uuid4())
        
        strategy = RecoveryStrategy(
            strategy_id=strategy_id,
            creator_id=creator_id,
            violation_types=violation_types,
            minimum_claim_amount=minimum_claim_amount,
            preferred_methods=preferred_methods,
            auto_recovery_enabled=auto_recovery_enabled,
            legal_action_threshold=legal_action_threshold,
            settlement_acceptance_rate=settlement_acceptance_rate,
            monitoring_frequency="daily"
        )
        
        self.recovery_strategies[creator_id] = strategy
        
        self.logger.info(f"Created recovery strategy for creator {creator_id}")
        return strategy_id
    
    async def get_case_status(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a recovery case."""
        case = self.recovery_cases.get(case_id)
        if not case:
            return None
        
        return {
            "case_id": case_id,
            "recovery_status": case.recovery_status.value,
            "claimed_amount": float(case.claimed_amount),
            "recovered_amount": float(case.recovered_amount),
            "net_recovery": float(case.net_recovery),
            "success_probability": case.success_probability,
            "time_to_resolution_days": case.time_to_resolution_days,
            "settlement_terms": case.settlement_terms,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat()
        }
    
    async def get_creator_cases(
        self,
        creator_id: str,
        status_filter: Optional[RecoveryStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get all cases for a creator."""
        creator_cases = [
            case for case in self.recovery_cases.values()
            if case.creator_id == creator_id
        ]
        
        if status_filter:
            creator_cases = [case for case in creator_cases if case.recovery_status == status_filter]
        
        return [
            {
                "case_id": case.case_id,
                "content_id": case.content_id,
                "violation_type": case.violation_type.value,
                "recovery_status": case.recovery_status.value,
                "claimed_amount": float(case.claimed_amount),
                "recovered_amount": float(case.recovered_amount),
                "net_recovery": float(case.net_recovery),
                "recovery_method": case.recovery_method.value,
                "created_at": case.created_at.isoformat()
            }
            for case in creator_cases
        ]


# Global instance
_recovered_revenue_manager = None


async def get_recovered_revenue_manager() -> RecoveredRevenueManager:
    """Get the global recovered revenue manager instance."""
    global _recovered_revenue_manager
    
    if _recovered_revenue_manager is None:
        _recovered_revenue_manager = RecoveredRevenueManager()
        await _recovered_revenue_manager.initialize()
    
    return _recovered_revenue_manager


# Example usage
async def main():
    """Example usage of RecoveredRevenueManager."""
    manager = await get_recovered_revenue_manager()
    
    creator_id = "creator_123"
    
    # Create custom recovery strategy
    strategy_id = await manager.create_recovery_strategy(
        creator_id=creator_id,
        violation_types=[ViolationType.COPYRIGHT_INFRINGEMENT, ViolationType.UNAUTHORIZED_USE],
        minimum_claim_amount=Decimal("25.00"),
        preferred_methods=[RecoveryMethod.DMCA_SETTLEMENT, RecoveryMethod.PLATFORM_CLAIM],
        auto_recovery_enabled=True,
        legal_action_threshold=Decimal("500.00"),
        settlement_acceptance_rate=0.75
    )
    
    print(f"Created recovery strategy: {strategy_id}")
    
    # Create recovery case
    case_id = await manager.create_recovery_case(
        creator_id=creator_id,
        content_id="content_456",
        violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
        violator_info={
            "platform": "youtube",
            "channel_id": "violator_channel_123",
            "video_id": "copied_video_789",
            "views": 50000
        },
        claimed_amount=Decimal("250.00"),
        evidence=[
            {"type": "original_content", "url": "https://original.com/content"},
            {"type": "violation_screenshot", "url": "https://evidence.com/screenshot"},
            {"type": "metadata_comparison", "similarity": 0.95}
        ]
    )
    
    print(f"Created recovery case: {case_id}")
    
    # Simulate waiting for settlement
    await asyncio.sleep(1)
    
    # Check case status
    status = await manager.get_case_status(case_id)
    if status:
        print(f"\n📋 Case Status:")
        print(f"Status: {status['recovery_status']}")
        print(f"Claimed: ${status['claimed_amount']:.2f}")
        print(f"Recovered: ${status['recovered_amount']:.2f}")
        print(f"Net Recovery: ${status['net_recovery']:.2f}")
        print(f"Success Probability: {status['success_probability']:.1%}")
    
    # Get recovery metrics
    metrics = await manager.get_recovery_metrics(creator_id, period_days=30)
    
    print(f"\n📊 Recovery Metrics (Last 30 days):")
    print(f"Violations Detected: {metrics.total_violations_detected}")
    print(f"Total Claimed: ${metrics.total_amount_claimed:.2f}")
    print(f"Total Recovered: ${metrics.total_amount_recovered:.2f}")
    print(f"Recovery Rate: {metrics.recovery_rate:.1%}")
    print(f"Success Rate: {metrics.success_rate:.1%}")
    print(f"Net Recovery: ${metrics.net_recovery_amount:.2f}")
    print(f"ROI: {metrics.roi:.1f}x")
    
    # Get all creator cases
    cases = await manager.get_creator_cases(creator_id)
    print(f"\n📋 Creator Cases ({len(cases)}):")
    for case in cases:
        print(f"  • {case['case_id'][:8]}: {case['violation_type']} - ${case['net_recovery']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())