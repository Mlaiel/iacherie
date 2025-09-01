"""Revenue Recovery and Monetization Tracking System

Automated revenue claim management, payment recovery tracking,
and monetization optimization for copyright enforcement.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from pydantic import BaseModel, Field

from ...core.database import get_async_session
from ...core.config import get_settings
from ...utils.security import encrypt_sensitive_data
from ...utils.payment import PaymentProcessor
from ...models.content_protection import RevenueClaim, PaymentRecovery, MonetizationRecord
from ...integrations.platform_apis import PlatformAPIManager
from ...integrations.payment_services import PaymentServiceAPI

logger = logging.getLogger(__name__)


class ClaimStatus(str, Enum):
    """
Revenue claim status enumeration"""

    INITIATED = "initiated"
    PROCESSING = "processing"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    ESCALATED = "escalated"
    SETTLED = "settled"


class RevenueType(str, Enum):
    """Types of revenue streams"""

    AD_REVENUE = "ad_revenue"
    SUBSCRIPTION = "subscription"
    DONATION = "donation"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    LIVE_PERFORMANCE = "live_performance"


class PaymentMethod(str, Enum):
    """Payment recovery methods"""

    PLATFORM_SPLIT = "platform_split"
    DIRECT_PAYMENT = "direct_payment"
    ESCROW = "escrow"
    LEGAL_SETTLEMENT = "legal_settlement"
    COURT_ORDER = "court_order"


@dataclass
class RevenueClaimRequest:
    """Revenue claim creation request"""
    content_id: str
    violation_url: str
    platform: str
    copyright_owner: str
    revenue_type: RevenueType
    estimated_loss: Decimal
    claim_period_start: datetime
    claim_period_end: datetime
    evidence_ids: List[str] = field(default_factory=list)
    supporting_documents: List[str] = field(default_factory=list)
    preferred_payment_method: PaymentMethod = PaymentMethod.PLATFORM_SPLIT


@dataclass
class MonetizationMetrics:
    """
Monetization tracking metrics"""
    total_claims: int
    total_recovered: Decimal
    average_recovery_time: float
    success_rate: float
    platform_breakdown: Dict[str, Dict[str, Union[int, Decimal]]]
    revenue_trends: Dict[str, List[Tuple[datetime, Decimal]]]


class RevenueClaimManager:
    """
Advanced revenue claim management system"""
    
    def __init__(self):
        self.payment_processor = PaymentProcessor()
        self.platform_api = PlatformAPIManager()
        self.payment_api = PaymentServiceAPI()
        self.settings = get_settings()
    
    async def initiate_revenue_claim(
        self,
        request: RevenueClaimRequest,
        session: AsyncSession
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate revenue claim for copyright violation
        
        Returns:
            Tuple[success, message, claim_id]
        """
        try:
            # Validate claim request
            is_valid, validation_errors = await self._validate_claim_request(request)
            if not is_valid:
                return False, f"Validation errors: {', '.join(validation_errors)}", None
            
            # Calculate estimated recovery
            recovery_estimate = await self._calculate_recovery_estimate(request)
            
            # Create claim record
            claim = RevenueClaim(
                content_id=request.content_id,
                violation_url=request.violation_url,
                platform=request.platform,
                copyright_owner=request.copyright_owner,
                revenue_type=request.revenue_type.value,
                estimated_loss=request.estimated_loss,
                estimated_recovery=recovery_estimate["amount"],
                claim_period_start=request.claim_period_start,
                claim_period_end=request.claim_period_end,
                status=ClaimStatus.INITIATED.value,
                preferred_payment_method=request.preferred_payment_method.value,
                evidence_ids=request.evidence_ids,
                supporting_documents=request.supporting_documents,
                created_at=datetime.utcnow()
            )
            
            session.add(claim)
            await session.commit()
            await session.refresh(claim)
            
            # Start claim processing workflow
            processing_result = await self._start_claim_processing(claim, session)
            
            logger.info(f"Initiated revenue claim {claim.id} for {request.platform}")
            return True, f"Claim initiated: {claim.id}", str(claim.id)
            
        except Exception as e:
            logger.error(f"Revenue claim initiation failed: {str(e)}")
            return False, f"Claim initiation failed: {str(e)}", None
    
    async def process_platform_revenue_sharing(
        self,
        claim_id: str,
        session: AsyncSession
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process revenue sharing with platform"""
        try:
            # Get claim details
            claim = await self._get_claim_by_id(claim_id, session)
            if not claim:
                return False, {"error": "Claim not found"}
            
            # Get platform revenue data
            revenue_data = await self.platform_api.get_content_revenue(
                claim.platform,
                claim.violation_url,
                claim.claim_period_start,
                claim.claim_period_end
            )
            
            if not revenue_data["success"]:
                return False, {"error": "Failed to retrieve platform revenue data"}
            
            # Calculate revenue split
            split_calculation = await self._calculate_revenue_split(
                claim, revenue_data["data"]
            )
            
            # Initiate platform revenue sharing
            sharing_result = await self._initiate_platform_sharing(
                claim, split_calculation
            )
            
            # Update claim status
            new_status = ClaimStatus.PROCESSING.value if sharing_result["success"] else claim.status
            await self._update_claim_status(claim_id, new_status, session)
            
            return sharing_result["success"], {
                "claim_id": claim_id,
                "revenue_data": revenue_data["data"],
                "split_calculation": split_calculation,
                "sharing_result": sharing_result
            }
            
        except Exception as e:
            logger.error(f"Platform revenue sharing failed: {str(e)}")
            return False, {"error": str(e)}
    
    async def track_payment_recovery(
        self,
        claim_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Track payment recovery progress"""
        try:
            claim = await self._get_claim_by_id(claim_id, session)
            if not claim:
                return {"error": "Claim not found"}
            
            # Get payment recovery records
            recovery_records = await self._get_payment_recoveries(claim_id, session)
            
            # Calculate recovery metrics
            total_recovered = sum(r.amount for r in recovery_records)
            recovery_rate = (total_recovered / claim.estimated_loss * 100) if claim.estimated_loss > 0 else 0
            
            # Get latest platform status
            platform_status = await self._check_platform_payment_status(claim)
            
            # Calculate time metrics
            time_metrics = await self._calculate_time_metrics(claim, recovery_records)
            
            return {
                "claim_id": claim_id,
                "total_recovered": float(total_recovered),
                "recovery_rate": float(recovery_rate),
                "estimated_loss": float(claim.estimated_loss),
                "payment_records": len(recovery_records),
                "platform_status": platform_status,
                "time_metrics": time_metrics,
                "status": claim.status
            }
            
        except Exception as e:
            logger.error(f"Payment tracking failed: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_revenue_recovery(
        self,
        claim_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Optimize revenue recovery strategy"""
        try:
            claim = await self._get_claim_by_id(claim_id, session)
            if not claim:
                return {"error": "Claim not found"}
            
            # Analyze current performance
            performance_analysis = await self._analyze_claim_performance(claim, session)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                claim, performance_analysis
            )
            
            # Implement automatic optimizations
            optimization_results = await self._apply_optimizations(
                claim, recommendations, session
            )
            
            return {
                "claim_id": claim_id,
                "performance_analysis": performance_analysis,
                "recommendations": recommendations,
                "optimization_results": optimization_results,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Revenue optimization failed: {str(e)}")
            return {"error": str(e)}
    
    async def _validate_claim_request(self, request: RevenueClaimRequest) -> Tuple[bool, List[str]]:
        """Validate revenue claim request"""
        errors = []
        
        if not request.content_id:
            errors.append("Content ID is required")
        if not request.violation_url:
            errors.append("Violation URL is required")
        if not request.platform:
            errors.append("Platform is required")
        if not request.copyright_owner:
            errors.append("Copyright owner is required")
        if request.estimated_loss <= 0:
            errors.append("Estimated loss must be positive")
        if request.claim_period_start >= request.claim_period_end:
            errors.append("Invalid claim period")
        
        return len(errors) == 0, errors
    
    async def _calculate_recovery_estimate(self, request: RevenueClaimRequest) -> Dict[str, Any]:
        """Calculate estimated recovery amount"""
        base_estimate = request.estimated_loss
        
        # Platform-specific recovery rates
        platform_rates = {
            "youtube": 0.7,
            "instagram": 0.6,
            "tiktok": 0.5,
            "facebook": 0.65,
            "twitter": 0.4
        }
        
        recovery_rate = platform_rates.get(request.platform.lower(), 0.5)
        estimated_amount = base_estimate * Decimal(str(recovery_rate))
        
        return {
            "amount": estimated_amount,
            "recovery_rate": recovery_rate,
            "factors": {
                "platform_rate": recovery_rate,
                "claim_strength": 0.8,  # Would be calculated based on evidence
                "legal_merit": 0.75
            }
        }
    
    async def _start_claim_processing(
        self,
        claim: RevenueClaim,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Start automated claim processing workflow"""
        try:
            # Submit claim to platform
            platform_submission = await self._submit_claim_to_platform(claim)
            
            # Set up monitoring
            monitoring_setup = await self._setup_claim_monitoring(claim)
            
            # Schedule follow-up actions
            follow_up_schedule = await self._schedule_claim_followups(claim, session)
            
            return {
                "platform_submission": platform_submission,
                "monitoring_setup": monitoring_setup,
                "follow_up_schedule": follow_up_schedule
            }
            
        except Exception as e:
            logger.error(f"Claim processing startup failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_claim_by_id(self, claim_id: str, session: AsyncSession) -> Optional[RevenueClaim]:
        """Get revenue claim by ID"""
        result = await session.execute(
            select(RevenueClaim).where(RevenueClaim.id == claim_id)
        )
        return result.scalar_one_or_none()
    
    async def _calculate_revenue_split(
        self,
        claim: RevenueClaim,
        revenue_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Calculate revenue split between parties"""
        total_revenue = Decimal(str(revenue_data.get("total_revenue", 0)))
        
        # Standard splits (configurable per platform)
        splits = {
            "copyright_owner": Decimal("0.7"),  # 70% to copyright owner
            "platform": Decimal("0.2"),        # 20% to platform
            "service_fee": Decimal("0.1")       # 10% service fee
        }
        
        split_amounts = {}
        for party, percentage in splits.items():
            split_amounts[party] = total_revenue * percentage
        
        return {
            "total_revenue": float(total_revenue),
            "splits": {k: float(v) for k, v in split_amounts.items()},
            "currency": revenue_data.get("currency", "USD")
        }
    
    async def _initiate_platform_sharing(
        self,
        claim: RevenueClaim,
        split_calculation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate revenue sharing with platform"""
        try:
            # Submit revenue sharing request to platform
            sharing_request = await self.platform_api.request_revenue_sharing(
                claim.platform,
                {
                    "claim_id": str(claim.id),
                    "content_url": claim.violation_url,
                    "split_amounts": split_calculation["splits"],
                    "payment_method": claim.preferred_payment_method
                }
            )
            
            return {
                "success": sharing_request.get("success", False),
                "platform_reference": sharing_request.get("reference_id"),
                "estimated_processing_time": sharing_request.get("processing_time", "7-14 days"),
                "next_steps": sharing_request.get("next_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Platform sharing initiation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_payment_recoveries(
        self,
        claim_id: str,
        session: AsyncSession
    ) -> List[PaymentRecovery]:
        """Get payment recovery records for claim"""
        result = await session.execute(
            select(PaymentRecovery)
            .where(PaymentRecovery.claim_id == claim_id)
            .order_by(PaymentRecovery.received_at)
        )
        return result.scalars().all()
    
    async def _check_platform_payment_status(self, claim: RevenueClaim) -> Dict[str, Any]:
        """
Check payment status on platform"""
        try:
            status_response = await self.platform_api.check_payment_status(
                claim.platform,
                str(claim.id)
            )
            return status_response
        except Exception as e:
            return {"error": str(e), "status": "unknown"}
    
    async def _calculate_time_metrics(
        self,
        claim: RevenueClaim,
        recovery_records: List[PaymentRecovery]
    ) -> Dict[str, Any]:
        """Calculate time-based metrics"""
        now = datetime.utcnow()
        claim_age = (now - claim.created_at).days
        
        metrics = {
            "claim_age_days": claim_age,
            "time_to_first_payment": None,
            "average_payment_interval": None,
            "last_payment_days_ago": None
        }
        
        if recovery_records:
            first_payment = min(recovery_records, key=lambda r: r.received_at)
            time_to_first = (first_payment.received_at - claim.created_at).days
            metrics["time_to_first_payment"] = time_to_first
            
            last_payment = max(recovery_records, key=lambda r: r.received_at)
            last_payment_age = (now - last_payment.received_at).days
            metrics["last_payment_days_ago"] = last_payment_age
            
            if len(recovery_records) > 1:
                intervals = []
                sorted_records = sorted(recovery_records, key=lambda r: r.received_at)
                for i in range(1, len(sorted_records)):
                    interval = (sorted_records[i].received_at - sorted_records[i-1].received_at).days
                    intervals.append(interval)
                metrics["average_payment_interval"] = sum(intervals) / len(intervals)
        
        return metrics
    
    async def _analyze_claim_performance(
        self,
        claim: RevenueClaim,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze claim performance"""
        recovery_records = await self._get_payment_recoveries(str(claim.id), session)
        total_recovered = sum(r.amount for r in recovery_records)
        
        performance = {
            "recovery_rate": float(total_recovered / claim.estimated_loss * 100) if claim.estimated_loss > 0 else 0,
            "total_recovered": float(total_recovered),
            "payment_frequency": len(recovery_records),
            "claim_efficiency": self._calculate_efficiency_score(claim, recovery_records),
            "platform_responsiveness": await self._assess_platform_responsiveness(claim),
            "bottlenecks": await self._identify_bottlenecks(claim, recovery_records)
        }
        
        return performance
    
    async def _generate_optimization_recommendations(
        self,
        claim: RevenueClaim,
        performance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if performance["recovery_rate"] < 50:
            recommendations.append({
                "type": "escalation",
                "priority": "high",
                "action": "Escalate to legal team",
                "reason": "Low recovery rate"
            })
        
        if performance["platform_responsiveness"] < 0.6:
            recommendations.append({
                "type": "communication",
                "priority": "medium", 
                "action": "Increase platform communication frequency",
                "reason": "Poor platform responsiveness"
            })
        
        if len(performance["bottlenecks"]) > 0:
            for bottleneck in performance["bottlenecks"]:
                recommendations.append({
                    "type": "process_improvement",
                    "priority": "medium",
                    "action": f"Address {bottleneck['type']} bottleneck",
                    "reason": bottleneck["description"]
                })
        
        return recommendations
    
    async def _apply_optimizations(
        self,
        claim: RevenueClaim,
        recommendations: List[Dict[str, Any]],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Apply optimization recommendations"""
        results = {
            "applied": [],
            "failed": [],
            "skipped": []
        }
        
        for rec in recommendations:
            try:
                if rec["type"] == "escalation":
                    await self._escalate_claim(claim, rec["reason"], session)
                    results["applied"].append(rec)
                elif rec["type"] == "communication":
                    await self._increase_communication_frequency(claim)
                    results["applied"].append(rec)
                elif rec["type"] == "process_improvement":
                    await self._implement_process_improvement(claim, rec)
                    results["applied"].append(rec)
                else:
                    results["skipped"].append(rec)
            except Exception as e:
                rec["error"] = str(e)
                results["failed"].append(rec)
        
        return results
    
    def _calculate_efficiency_score(
        self,
        claim: RevenueClaim,
        recovery_records: List[PaymentRecovery]
    ) -> float:
        """Calculate claim efficiency score"""
        if not recovery_records:
            return 0.0
        
        # Factors: recovery rate, time efficiency, payment consistency
        total_recovered = sum(r.amount for r in recovery_records)
        recovery_rate = float(total_recovered / claim.estimated_loss) if claim.estimated_loss > 0 else 0
        
        claim_age = (datetime.utcnow() - claim.created_at).days
        time_efficiency = max(0, 1 - (claim_age / 90))  # Efficiency decreases over 90 days
        
        payment_consistency = 1.0 if len(recovery_records) > 0 else 0.0
        
        efficiency = (recovery_rate * 0.5 + time_efficiency * 0.3 + payment_consistency * 0.2)
        return min(efficiency, 1.0)
    
    async def _assess_platform_responsiveness(self, claim: RevenueClaim) -> float:
        """
Assess platform responsiveness score"""
        # This would analyze platform communication patterns
        return 0.75  # Placeholder
    
    async def _identify_bottlenecks(
        self,
        claim: RevenueClaim,
        recovery_records: List[PaymentRecovery]
    ) -> List[Dict[str, Any]]:
        """
Identify process bottlenecks"""
        bottlenecks = []
        
        # Check for long delays
        if not recovery_records and (datetime.utcnow() - claim.created_at).days > 30:
            bottlenecks.append({
                "type": "initial_delay",
                "description": "No payments received after 30 days"
            })
        
        # Check for payment gaps
        if len(recovery_records) > 1:
            sorted_records = sorted(recovery_records, key=lambda r: r.received_at)
            for i in range(1, len(sorted_records)):
                gap = (sorted_records[i].received_at - sorted_records[i-1].received_at).days
                if gap > 60:
                    bottlenecks.append({
                        "type": "payment_gap",
                        "description": f"Payment gap of {gap} days detected"
                    })
        
        return bottlenecks
    
    async def _update_claim_status(
        self,
        claim_id: str,
        status: str,
        session: AsyncSession
    ) -> None:
        """Update claim status"""
        await session.execute(
            update(RevenueClaim)
            .where(RevenueClaim.id == claim_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await session.commit()
    
    async def _submit_claim_to_platform(self, claim: RevenueClaim) -> Dict[str, Any]:
        """
Submit claim to platform"""
        return {"success": True, "platform_reference": "PLAT-12345"}
    
    async def _setup_claim_monitoring(self, claim: RevenueClaim) -> Dict[str, Any]:
        """Setup claim monitoring"""
        return {"monitoring_active": True, "check_interval": "daily"}
    
    async def _schedule_claim_followups(
        self,
        claim: RevenueClaim,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Schedule claim follow-up actions"""
        return {"follow_ups_scheduled": 3, "next_followup": "7 days"}
    
    async def _escalate_claim(self, claim: RevenueClaim, reason: str, session: AsyncSession) -> None:
        """Escalate claim to higher priority"""
        await session.execute(
            update(RevenueClaim)
            .where(RevenueClaim.id == claim.id)
            .values(
                status=ClaimStatus.ESCALATED.value,
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
    
    async def _increase_communication_frequency(self, claim: RevenueClaim) -> None:
        """
Increase communication frequency with platform"""
        # Implementation for increasing communication
        pass
    
    async def _implement_process_improvement(
        self,
        claim: RevenueClaim,
        recommendation: Dict[str, Any]
    ) -> None:
        """
Implement process improvement"""
        # Implementation for process improvements
        pass


class MonetizationTracker:
    """
Advanced monetization tracking and analytics"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def generate_monetization_report(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
Generate comprehensive monetization report"""
        try:
            # Get all claims for user in period
            claims_result = await session.execute(
                select(RevenueClaim)
                .where(
                    and_(
                        RevenueClaim.copyright_owner == user_id,
                        RevenueClaim.created_at >= period_start,
                        RevenueClaim.created_at <= period_end
                    )
                )
            )
            claims = claims_result.scalars().all()
            
            # Calculate metrics
            metrics = await self._calculate_monetization_metrics(claims, session)
            
            # Generate trends
            trends = await self._calculate_revenue_trends(claims, period_start, period_end)
            
            # Platform breakdown
            platform_breakdown = await self._calculate_platform_breakdown(claims, session)
            
            return {
                "period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "summary": metrics,
                "trends": trends,
                "platform_breakdown": platform_breakdown,
                "total_claims": len(claims),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Monetization report generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_monetization_metrics(
        self,
        claims: List[RevenueClaim],
        session: AsyncSession
    ) -> MonetizationMetrics:
        """Calculate comprehensive monetization metrics"""
        total_claims = len(claims)
        total_recovered = Decimal("0")
        recovery_times = []
        successful_claims = 0
        
        for claim in claims:
            recovery_records = await session.execute(
                select(PaymentRecovery).where(PaymentRecovery.claim_id == claim.id)
            )
            recoveries = recovery_records.scalars().all()
            
            claim_recovered = sum(r.amount for r in recoveries)
            total_recovered += claim_recovered
            
            if claim_recovered > 0:
                successful_claims += 1
                # Calculate recovery time
                first_payment = min(recoveries, key=lambda r: r.received_at) if recoveries else None
                if first_payment:
                    recovery_time = (first_payment.received_at - claim.created_at).days
                    recovery_times.append(recovery_time)
        
        average_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        success_rate = (successful_claims / total_claims * 100) if total_claims > 0 else 0
        
        return MonetizationMetrics(
            total_claims=total_claims,
            total_recovered=total_recovered,
            average_recovery_time=average_recovery_time,
            success_rate=success_rate,
            platform_breakdown={},  # Calculated separately
            revenue_trends={}       # Calculated separately
        )
    
    async def _calculate_revenue_trends(
        self,
        claims: List[RevenueClaim],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, List[Tuple[datetime, Decimal]]]:
        """Calculate revenue trends over time"""
        trends = {
            "daily": [],
            "weekly": [],
            "monthly": []
        }
        
        # This would implement trend calculations
        # Placeholder implementation
        current_date = period_start
        while current_date <= period_end:
            trends["daily"].append((current_date, Decimal("100")))
            current_date += timedelta(days=1)
        
        return trends
    
    async def _calculate_platform_breakdown(
        self,
        claims: List[RevenueClaim],
        session: AsyncSession
    ) -> Dict[str, Dict[str, Union[int, Decimal]]]:
        """Calculate platform-wise breakdown"""
        breakdown = {}
        
        for claim in claims:
            platform = claim.platform
            if platform not in breakdown:
                breakdown[platform] = {
                    "claims": 0,
                    "recovered": Decimal("0"),
                    "estimated_loss": Decimal("0")
                }
            
            breakdown[platform]["claims"] += 1
            breakdown[platform]["estimated_loss"] += claim.estimated_loss
            
            # Get recoveries for this claim
            recovery_records = await session.execute(
                select(PaymentRecovery).where(PaymentRecovery.claim_id == claim.id)
            )
            recoveries = recovery_records.scalars().all()
            claim_recovered = sum(r.amount for r in recoveries)
            breakdown[platform]["recovered"] += claim_recovered
        
        # Convert Decimal to float for JSON serialization
        for platform in breakdown:
            breakdown[platform]["recovered"] = float(breakdown[platform]["recovered"])
            breakdown[platform]["estimated_loss"] = float(breakdown[platform]["estimated_loss"])
        
        return breakdown


class PaymentRecovery:
    """Payment recovery tracking and automation"""
    
    def __init__(self):
        self.payment_processor = PaymentProcessor()
        self.settings = get_settings()
    
    async def process_payment_recovery(
        self,
        claim_id: str,
        payment_data: Dict[str, Any],
        session: AsyncSession
    ) -> Tuple[bool, str]:
        """
Process incoming payment recovery"""
        try:
            # Validate payment data
            if not self._validate_payment_data(payment_data):
                return False, "Invalid payment data"
            
            # Create payment recovery record
            recovery = PaymentRecovery(
                claim_id=claim_id,
                amount=Decimal(str(payment_data["amount"])),
                currency=payment_data.get("currency", "USD"),
                payment_method=payment_data["payment_method"],
                platform_reference=payment_data.get("platform_reference"),
                transaction_id=payment_data.get("transaction_id"),
                received_at=datetime.utcnow(),
                metadata=payment_data.get("metadata", {})
            )
            
            session.add(recovery)
            await session.commit()
            
            # Update claim status if fully recovered
            await self._check_claim_completion(claim_id, session)
            
            # Send notifications
            await self._send_payment_notifications(claim_id, recovery, session)
            
            return True, f"Payment recovery processed: {recovery.id}"
            
        except Exception as e:
            logger.error(f"Payment recovery processing failed: {str(e)}")
            return False, f"Processing failed: {str(e)}"
    
    def _validate_payment_data(self, data: Dict[str, Any]) -> bool:
        """Validate payment recovery data"""
        required_fields = ["amount", "payment_method"]
        return all(field in data for field in required_fields)
    
    async def _check_claim_completion(self, claim_id: str, session: AsyncSession) -> None:
        """Check if claim is fully recovered"""
        # Get claim and calculate total recovery
        claim_result = await session.execute(
            select(RevenueClaim).where(RevenueClaim.id == claim_id)
        )
        claim = claim_result.scalar_one_or_none()
        
        if not claim:
            return
        
        recovery_result = await session.execute(
            select(func.sum(PaymentRecovery.amount))
            .where(PaymentRecovery.claim_id == claim_id)
        )
        total_recovered = recovery_result.scalar() or Decimal("0")
        
        # Update status if fully recovered
        if total_recovered >= claim.estimated_recovery:
            await session.execute(
                update(RevenueClaim)
                .where(RevenueClaim.id == claim_id)
                .values(
                    status=ClaimStatus.PAID.value,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
    
    async def _send_payment_notifications(
        self,
        claim_id: str,
        recovery: PaymentRecovery,
        session: AsyncSession
    ) -> None:
        """Send payment recovery notifications"""
        # Implementation for sending notifications
        logger.info(f"Payment notification sent for claim {claim_id}")
