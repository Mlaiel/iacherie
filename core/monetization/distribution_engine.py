"""
Advanced Distribution Engine
Automated revenue distribution and payout management system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field

from ...database.models import User, Payout, CollaborationAgreement, RevenueShare
from .payment_processor import PaymentProcessor, PaymentRequest, PaymentGateway
from ...security.fraud_detection import FraudDetectionEngine
from ...ai.collaboration.revenue_optimizer import RevenueOptimizer


class PayoutStatus(Enum):
    """Payout processing status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PayoutMethod(Enum):
    """Payout delivery methods"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTO = "crypto"
    CHECK = "check"


class CollaborationType(Enum):
    """Types of collaboration agreements"""
    SPLIT_REVENUE = "split_revenue"
    PERCENTAGE_BASED = "percentage_based"
    FIXED_AMOUNT = "fixed_amount"
    MILESTONE_BASED = "milestone_based"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class CollaboratorShare:
    """Individual collaborator's revenue share"""
    user_id: int
    name: str
    email: str
    percentage: Decimal
    fixed_amount: Optional[Decimal] = None
    role: str = "collaborator"
    contribution_type: str = "creative"
    payment_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    bank_details: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Validate collaborator share"""
        if self.percentage < 0 or self.percentage > 100:
            raise ValueError("Percentage must be between 0 and 100")


@dataclass
class DistributionRules:
    """Revenue distribution rules"""
    primary_creator_percentage: Decimal
    platform_fee_percentage: Decimal
    collaborator_shares: List[CollaboratorShare] = field(default_factory=list)
    minimum_payout_amount: Decimal = Decimal("25.00")
    payout_frequency: str = "monthly"  # weekly, monthly, quarterly
    auto_payout_enabled: bool = True
    tax_withholding_enabled: bool = False
    currency: str = "EUR"
    
    def validate(self) -> bool:
        """Validate distribution rules"""
        total_percentage = self.primary_creator_percentage + self.platform_fee_percentage
        total_percentage += sum(share.percentage for share in self.collaborator_shares)
        
        return abs(total_percentage - 100) < Decimal("0.01")  # Allow small rounding differences


@dataclass
class PayoutCalculation:
    """Detailed payout calculation"""
    user_id: int
    total_revenue: Decimal
    platform_fees: Decimal
    collaborator_deductions: Decimal
    tax_withholding: Decimal
    net_payout: Decimal
    currency: str
    calculation_date: datetime
    breakdown: Dict[str, Decimal] = field(default_factory=dict)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get calculation summary"""



        return {
            "user_id": self.user_id,
            "total_revenue": float(self.total_revenue),
            "platform_fees": float(self.platform_fees),
            "collaborator_deductions": float(self.collaborator_deductions),
            "tax_withholding": float(self.tax_withholding),
            "net_payout": float(self.net_payout),
            "currency": self.currency,
            "calculation_date": self.calculation_date.isoformat(),
            "breakdown": {k: float(v) for k, v in self.breakdown.items()}
        }


class PayoutRequest(BaseModel):
    """Payout request data model"""
    user_id: int
    amount: Decimal = Field(..., gt=0)
    currency: str = "EUR"
    method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    bank_details: Optional[Dict[str, str]] = None
    notes: Optional[str] = None
    priority: bool = False
    
    class Config:
        use_enum_values = True


class DistributionEngine:
    """Advanced revenue distribution and payout management"""
    
    def __init__(
        self,
        payment_processor: PaymentProcessor,
        fraud_detection: FraudDetectionEngine,
        revenue_optimizer: RevenueOptimizer
    ):
        self.payment_processor = payment_processor
        self.fraud_detection = fraud_detection
        self.revenue_optimizer = revenue_optimizer
        self.logger = logging.getLogger(__name__)
        self.distribution_rules: Dict[int, DistributionRules] = {}
        
    async def calculate_user_payout(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> PayoutCalculation:
        """Calculate comprehensive payout for user"""



        try:
            # Get user's total revenue for period
            total_revenue = await self._get_user_revenue(
                user_id, start_date, end_date, session
            )
            
            # Get distribution rules for user
            rules = await self._get_distribution_rules(user_id, session)
            
            # Calculate platform fees
            platform_fees = total_revenue * (rules.platform_fee_percentage / 100)
            
            # Calculate collaborator deductions
            collaborator_deductions = await self._calculate_collaborator_deductions(
                user_id, total_revenue, rules, session
            )
            
            # Calculate tax withholding
            tax_withholding = await self._calculate_tax_withholding(
                user_id, total_revenue, rules, session
            )
            
            # Calculate net payout
            net_payout = (
                total_revenue - 
                platform_fees - 
                collaborator_deductions - 
                tax_withholding
            )
            
            # Create detailed breakdown
            breakdown = {
                "gross_revenue": total_revenue,
                "streaming_revenue": await self._get_streaming_revenue(user_id, start_date, end_date, session),
                "licensing_revenue": await self._get_licensing_revenue(user_id, start_date, end_date, session),
                "sponsorship_revenue": await self._get_sponsorship_revenue(user_id, start_date, end_date, session),
                "platform_fees": platform_fees,
                "collaborator_shares": collaborator_deductions,
                "tax_withholding": tax_withholding
            }
            
            return PayoutCalculation(
                user_id=user_id,
                total_revenue=total_revenue,
                platform_fees=platform_fees,
                collaborator_deductions=collaborator_deductions,
                tax_withholding=tax_withholding,
                net_payout=max(net_payout, Decimal("0")),
                currency=rules.currency,
                calculation_date=datetime.now(),
                breakdown=breakdown
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate payout for user {user_id}: {str(e)}")
            raise
    
    async def process_automated_payouts(
        self,
        session: AsyncSession,
        force_process: bool = False
    ) -> Dict[str, Any]:
        """Process automated payouts for all eligible users"""



        try:
            results = {
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "total_amount": Decimal("0"),
                "details": []
            }
            
            # Get users eligible for payout
            eligible_users = await self._get_eligible_users_for_payout(session, force_process)
            
            for user_id in eligible_users:
                try:
                    # Calculate payout
                    calculation = await self._calculate_payout_for_automated_processing(
                        user_id, session
                    )
                    
                    # Check minimum payout amount
                    rules = await self._get_distribution_rules(user_id, session)
                    if calculation.net_payout < rules.minimum_payout_amount and not force_process:
                        results["skipped"] += 1
                        continue
                    
                    # Process payout
                    payout_result = await self._process_single_payout(
                        user_id, calculation, session
                    )
                    
                    if payout_result["success"]:
                        results["processed"] += 1
                        results["total_amount"] += calculation.net_payout
                    else:
                        results["failed"] += 1
                    
                    results["details"].append({
                        "user_id": user_id,
                        "amount": float(calculation.net_payout),
                        "status": "processed" if payout_result["success"] else "failed",
                        "error": payout_result.get("error")
                    })
                    
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "user_id": user_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    self.logger.error(f"Failed to process payout for user {user_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Automated payout processing failed: {str(e)}")
            raise
    
    async def create_manual_payout(
        self,
        payout_request: PayoutRequest,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Create manual payout for user"""



        try:
            # Fraud detection check
            fraud_score = await self.fraud_detection.analyze_payout_request(payout_request)
            if fraud_score > 0.8:  # High fraud risk
                return {
                    "success": False,
                    "error": "Payout blocked due to fraud risk",
                    "fraud_score": fraud_score
                }
            
            # Validate user eligibility
            user = await session.get(User, payout_request.user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check available balance
            available_balance = await self._get_user_available_balance(
                payout_request.user_id, session
            )
            
            if payout_request.amount > available_balance:
                return {
                    "success": False,
                    "error": "Insufficient balance",
                    "available_balance": float(available_balance),
                    "requested_amount": float(payout_request.amount)
                }
            
            # Create payout record
            payout = Payout(
                user_id=payout_request.user_id,
                amount=payout_request.amount,
                currency=payout_request.currency,
                method=payout_request.method.value,
                status=PayoutStatus.PENDING.value,
                bank_details=payout_request.bank_details,
                notes=payout_request.notes,
                priority=payout_request.priority
            )
            
            session.add(payout)
            await session.commit()
            await session.refresh(payout)
            
            # Process payment
            payment_result = await self._execute_payout_payment(payout, session)
            
            return {
                "success": payment_result["success"],
                "payout_id": payout.id,
                "transaction_id": payment_result.get("transaction_id"),
                "estimated_arrival": payment_result.get("estimated_arrival"),
                "error": payment_result.get("error")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create manual payout: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def distribute_collaboration_revenue(
        self,
        content_id: str,
        total_revenue: Decimal,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Distribute revenue among collaborators"""



        try:
            # Get collaboration agreement
            result = await session.execute(
                select(CollaborationAgreement).where(
                    CollaborationAgreement.content_id == content_id
                )
            )
            agreement = result.scalar_one_or_none()
            
            if not agreement:
                return {"success": False, "error": "No collaboration agreement found"}
            
            # Parse collaborator shares
            shares = json.loads(agreement.revenue_shares)
            distributions = []
            
            for share_data in shares:
                collaborator = CollaboratorShare(**share_data)
                
                # Calculate share amount
                if collaborator.fixed_amount:
                    share_amount = collaborator.fixed_amount
                else:
                    share_amount = total_revenue * (collaborator.percentage / 100)
                
                # Create distribution record
                distribution = {
                    "user_id": collaborator.user_id,
                    "name": collaborator.name,
                    "amount": share_amount,
                    "percentage": collaborator.percentage,
                    "role": collaborator.role
                }
                
                # Queue payout for collaborator
                await self._queue_collaborator_payout(
                    collaborator, share_amount, content_id, session
                )
                
                distributions.append(distribution)
            
            return {
                "success": True,
                "total_distributed": sum(d["amount"] for d in distributions),
                "distributions": distributions
            }
            
        except Exception as e:
            self.logger.error(f"Failed to distribute collaboration revenue: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_user_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get total revenue for user in date range"""
        from ...database.models import RevenueRecord
        
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.status == "confirmed"
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_streaming_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get streaming-specific revenue"""
        from ...database.models import RevenueRecord
        
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.source == "streaming",
                RevenueRecord.status == "confirmed"
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_licensing_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get licensing-specific revenue"""
        from ...database.models import RevenueRecord
        
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.source == "licensing",
                RevenueRecord.status == "confirmed"
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_sponsorship_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get sponsorship-specific revenue"""
        from ...database.models import RevenueRecord
        
        result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.source == "sponsorship",
                RevenueRecord.status == "confirmed"
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_distribution_rules(
        self,
        user_id: int,
        session: AsyncSession
    ) -> DistributionRules:
        """Get distribution rules for user"""
        # Check if rules are cached
        if user_id in self.distribution_rules:
            return self.distribution_rules[user_id]
        
        # Load from database or create default
        rules = DistributionRules(
            primary_creator_percentage=Decimal("85.0"),
            platform_fee_percentage=Decimal("15.0"),
            minimum_payout_amount=Decimal("25.00"),
            payout_frequency="monthly",
            auto_payout_enabled=True
        )
        
        # Cache rules
        self.distribution_rules[user_id] = rules
        
        return rules
    
    async def _calculate_collaborator_deductions(
        self,
        user_id: int,
        total_revenue: Decimal,
        rules: DistributionRules,
        session: AsyncSession
    ) -> Decimal:
        """Calculate total collaborator deductions"""
        total_deductions = Decimal("0")
        
        for collaborator in rules.collaborator_shares:
            if collaborator.fixed_amount:
                total_deductions += collaborator.fixed_amount
            else:
                share_amount = total_revenue * (collaborator.percentage / 100)
                total_deductions += share_amount
        
        return total_deductions
    
    async def _calculate_tax_withholding(
        self,
        user_id: int,
        total_revenue: Decimal,
        rules: DistributionRules,
        session: AsyncSession
    ) -> Decimal:
        """Calculate tax withholding if applicable"""
        if not rules.tax_withholding_enabled:
            return Decimal("0")
        
        # Get user's tax information
        user = await session.get(User, user_id)
        if not user:
            return Decimal("0")
        
        # Apply country-specific tax rates
        tax_rate = await self._get_tax_rate(user.country, total_revenue)
        return total_revenue * (tax_rate / 100)
    
    async def _get_tax_rate(self, country: str, revenue: Decimal) -> Decimal:
        """Get tax withholding rate for country and revenue level"""
        # Simplified tax rates - would integrate with tax service
        tax_rates = {
            "US": Decimal("24.0"),    # US tax withholding
            "GB": Decimal("20.0"),    # UK basic rate
            "DE": Decimal("26.375"),  # German withholding tax
            "CA": Decimal("15.0"),    # Canadian withholding
            "AU": Decimal("32.5"),    # Australian resident rate
        }
        
        return tax_rates.get(country, Decimal("0"))
    
    async def _get_eligible_users_for_payout(
        self,
        session: AsyncSession,
        force_process: bool = False
    ) -> List[int]:
        """Get users eligible for automated payout"""
        # Get users with pending revenue above minimum threshold
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        from ...database.models import RevenueRecord
        result = await session.execute(
            select(RevenueRecord.user_id).where(
                RevenueRecord.date >= thirty_days_ago,
                RevenueRecord.status == "confirmed"
            ).group_by(RevenueRecord.user_id).having(
                func.sum(RevenueRecord.amount) >= Decimal("25.00")
            )
        )
        
        return [row[0] for row in result]
    
    async def _calculate_payout_for_automated_processing(
        self,
        user_id: int,
        session: AsyncSession
    ) -> PayoutCalculation:
        """Calculate payout for automated processing"""
        # Get last payout date
        last_payout_date = await self._get_last_payout_date(user_id, session)
        if not last_payout_date:
            last_payout_date = datetime.now() - timedelta(days=30)
        
        end_date = datetime.now()
        
        return await self.calculate_user_payout(
            user_id, last_payout_date, end_date, session
        )
    
    async def _get_last_payout_date(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[datetime]:
        """Get date of last payout for user"""
        result = await session.execute(
            select(func.max(Payout.created_at)).where(
                Payout.user_id == user_id,
                Payout.status.in_([PayoutStatus.COMPLETED.value, PayoutStatus.PROCESSING.value])
            )
        )
        
        return result.scalar()
    
    async def _process_single_payout(
        self,
        user_id: int,
        calculation: PayoutCalculation,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Process a single automated payout"""



        try:
            # Create payout record
            payout = Payout(
                user_id=user_id,
                amount=calculation.net_payout,
                currency=calculation.currency,
                method=PayoutMethod.BANK_TRANSFER.value,  # Default method
                status=PayoutStatus.PENDING.value,
                calculation_data=calculation.get_summary()
            )
            
            session.add(payout)
            await session.commit()
            await session.refresh(payout)
            
            # Execute payment
            payment_result = await self._execute_payout_payment(payout, session)
            
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Failed to process single payout: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_payout_payment(
        self,
        payout: Payout,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Execute payout payment through payment processor"""



        try:
            # Get user details
            user = await session.get(User, payout.user_id)
            if not user:
                raise ValueError("User not found")
            
            # Create payment request
            payment_request = PaymentRequest(
                user_id=payout.user_id,
                amount=payout.amount,
                currency=payout.currency,
                gateway=PaymentGateway.STRIPE,  # Default gateway
                description=f"Revenue payout for {user.name}",
                recipient_email=user.email,
                recipient_bank_details=payout.bank_details
            )
            
            # Process payment
            payment_response = await self.payment_processor.process_payment(
                payment_request, session
            )
            
            # Update payout status
            payout.status = PayoutStatus.PROCESSING.value
            payout.transaction_id = payment_response.gateway_transaction_id
            payout.processed_at = datetime.now()
            
            await session.commit()
            
            return {
                "success": True,
                "transaction_id": payment_response.gateway_transaction_id,
                "estimated_arrival": payment_response.estimated_arrival
            }
            
        except Exception as e:
            # Update payout status to failed
            payout.status = PayoutStatus.FAILED.value
            payout.error_message = str(e)
            await session.commit()
            
            return {"success": False, "error": str(e)}
    
    async def _get_user_available_balance(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Decimal:
        """Get user's available balance for payout"""
        # Total revenue minus previous payouts
        from ...database.models import RevenueRecord
        
        # Get total confirmed revenue
        revenue_result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.status == "confirmed"
            )
        )
        total_revenue = revenue_result.scalar() or 0
        
        # Get total completed payouts
        payout_result = await session.execute(
            select(func.sum(Payout.amount)).where(
                Payout.user_id == user_id,
                Payout.status.in_([
                    PayoutStatus.COMPLETED.value,
                    PayoutStatus.PROCESSING.value
                ])
            )
        )
        total_payouts = payout_result.scalar() or 0
        
        return Decimal(str(total_revenue)) - Decimal(str(total_payouts))
    
    async def _queue_collaborator_payout(
        self,
        collaborator: CollaboratorShare,
        amount: Decimal,
        content_id: str,
        session: AsyncSession
    ) -> None:
        """Queue payout for collaborator"""
        payout = Payout(
            user_id=collaborator.user_id,
            amount=amount,
            currency="EUR",
            method=collaborator.payment_method.value,
            status=PayoutStatus.PENDING.value,
            bank_details=collaborator.bank_details,
            notes=f"Collaboration revenue for content {content_id}",
            collaboration_content_id=content_id
        )
        
        session.add(payout)
        await session.commit()


class PayoutManager:
    """High-level payout management interface"""
    
    def __init__(self, distribution_engine: DistributionEngine):
        self.distribution_engine = distribution_engine
        self.logger = logging.getLogger(__name__)
    
    async def get_user_payout_history(
        self,
        user_id: int,
        session: AsyncSession,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's payout history"""
        result = await session.execute(
            select(Payout).where(
                Payout.user_id == user_id
            ).order_by(Payout.created_at.desc()).limit(limit)
        )
        
        payouts = result.scalars().all()
        
        return [
            {
                "payout_id": payout.id,
                "amount": float(payout.amount),
                "currency": payout.currency,
                "method": payout.method,
                "status": payout.status,
                "created_at": payout.created_at.isoformat(),
                "processed_at": payout.processed_at.isoformat() if payout.processed_at else None,
                "transaction_id": payout.transaction_id,
                "notes": payout.notes
            }
            for payout in payouts
        ]
    
    async def get_payout_statistics(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get user's payout statistics"""
        # Total payouts
        total_result = await session.execute(
            select(
                func.sum(Payout.amount).label('total_amount'),
                func.count(Payout.id).label('total_count')
            ).where(
                Payout.user_id == user_id,
                Payout.status == PayoutStatus.COMPLETED.value
            )
        )
        total_row = total_result.first()
        
        # Monthly statistics
        monthly_result = await session.execute(
            select(
                func.date_trunc('month', Payout.created_at).label('month'),
                func.sum(Payout.amount).label('amount'),
                func.count(Payout.id).label('count')
            ).where(
                Payout.user_id == user_id,
                Payout.status == PayoutStatus.COMPLETED.value,
                Payout.created_at >= datetime.now() - timedelta(days=365)
            ).group_by(
                func.date_trunc('month', Payout.created_at)
            ).order_by(
                func.date_trunc('month', Payout.created_at)
            )
        )
        
        monthly_data = [
            {
                "month": row.month.isoformat(),
                "amount": float(row.amount),
                "count": row.count
            }
            for row in monthly_result
        ]
        
        return {
            "total_amount": float(total_row.total_amount) if total_row.total_amount else 0,
            "total_count": total_row.total_count or 0,
            "monthly_breakdown": monthly_data,
            "average_payout": float(total_row.total_amount / total_row.total_count) if total_row.total_count else 0
        }
    
    async def schedule_recurring_payouts(self) -> None:
        """Schedule and process recurring automated payouts"""
        while True:
            try:
                self.logger.info("Starting automated payout processing")
                
                # This would be called with a database session
                # await self.distribution_engine.process_automated_payouts(session)
                
                # Wait 24 hours before next run
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                self.logger.error(f"Automated payout processing failed: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
